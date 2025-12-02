document.addEventListener("DOMContentLoaded", function () {
    const saveBtn = document.getElementById("saveBtn");

    saveBtn.addEventListener("click", async function () {
        // Read values
        const degree = document.getElementById("degree").value.trim();
        const specialization = document.getElementById("specialization").value.trim();
        const cgpa = document.getElementById("cgpa").value.trim();
        const year = document.getElementById("year").value.trim();
        const certifications = document.getElementById("certifications").value.trim();

        // Clear previous errors
        document.getElementById("degreeError").innerText = "";
        document.getElementById("specializationError").innerText = "";
        document.getElementById("cgpaError").innerText = "";
        document.getElementById("yearError").innerText = "";

        // Client-side validation (quick)
        let valid = true;
        const currentYear = new Date().getFullYear();

        if (!degree) {
            document.getElementById("degreeError").innerText = "Required";
            valid = false;
        }
        if (!specialization) {
            document.getElementById("specializationError").innerText = "Required";
            valid = false;
        }
        const cgpaNum = parseFloat(cgpa);
        if (isNaN(cgpaNum) || cgpaNum < 0 || cgpaNum > 10) {
            document.getElementById("cgpaError").innerText = "Enter CGPA between 0 and 10";
            valid = false;
        }
        const yearNum = parseInt(year, 10);
        if (isNaN(yearNum) || year.length !== 4 || yearNum < 2000 || yearNum > currentYear) {
            document.getElementById("yearError").innerText = `Enter valid year (2000–${currentYear})`;
            valid = false;
        }

        if (!valid) return;

        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please login first.");
            return;
        }

        try {
            const res = await fetch("http://127.0.0.1:5000/education/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    degree,
                    specialization,
                    cgpa: cgpaNum,
                    year: yearNum,
                    certifications
                })
            });

            const result = await res.json();

            if (res.ok) {
                alert("Education details saved successfully!");
                // optionally show success UI or redirect
                window.location.href = "dashboard.html";
                return;
            }

            // If not ok, show validation errors if present
            if (result && result.errors) {
                if (result.errors.degree) document.getElementById("degreeError").innerText = result.errors.degree;
                if (result.errors.specialization) document.getElementById("specializationError").innerText = result.errors.specialization;
                if (result.errors.cgpa) document.getElementById("cgpaError").innerText = result.errors.cgpa;
                if (result.errors.year) document.getElementById("yearError").innerText = result.errors.year;
                return;
            }

            // Generic message fallback
            alert(result.message || result.error || "Failed to save education details");

        } catch (err) {
            console.error("Network or server error:", err);
            alert("Network error — please make sure backend is running at http://127.0.0.1:5000");
        }
    });
});
