window.onload = async () => {
    const token = localStorage.getItem("token");
    const googleUser = JSON.parse(localStorage.getItem("googleUser") || "null");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/profile", {
            method: "GET",
            headers: { "Authorization": "Bearer " + token }
        });

        const result = await res.json();
        if (!res.ok) {
            document.getElementById("msg").textContent = result.error || "Failed to load profile";
            return;
        }

        const u = result.user;

// Display basic info
document.getElementById("name").textContent = u.username || "";
document.getElementById("email").textContent = u.email || "";

// Google info
if (googleUser) {
    document.getElementById("g_name").textContent = googleUser.username || "";
    document.getElementById("g_email").textContent = googleUser.email || "";

    if (googleUser.picture) {
        const img = document.getElementById("g_pic");
        img.src = googleUser.picture;
        img.style.display = "block";

        // hide letter avatar when photo exists
        const letter = document.getElementById("avatar-letter");
        if (letter) letter.style.display = "none";
    }
}


        // Autofill edit fields (SYNC WITH ML INPUT)
        document.getElementById("edit_name").value = u.username || "";
        document.getElementById("edit_degree").value = u.degree || "";
        document.getElementById("edit_specialization").value = u.specialization || "";
        document.getElementById("edit_cgpa").value = u.cgpa || "";
        document.getElementById("edit_certifications").value =
            Array.isArray(u.certifications) ? u.certifications.join(", ") : (u.certifications || "");

    } catch {
        document.getElementById("msg").textContent = "Network error";
    }
};

// Save profile
document.getElementById("saveBtn").addEventListener("click", async () => {
    const token = localStorage.getItem("token");
    const msg = document.getElementById("update_msg");
    msg.textContent = "";

    const data = {
        username: edit_name.value.trim(),
        degree: edit_degree.value.trim(),
        specialization: edit_specialization.value.trim(),
        cgpa: edit_cgpa.value.trim(),
        certifications: edit_certifications.value.trim()
    };

    // Required validation (ML needs these)
    if (!data.degree || !data.specialization || !data.cgpa) {
        msg.textContent = "Degree, Specialization and CGPA are required";
        msg.style.color = "red";
        return;
    }

    if (isNaN(data.cgpa) || data.cgpa < 0 || data.cgpa > 10) {
        msg.textContent = "CGPA must be between 0 and 10";
        msg.style.color = "red";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/profile/edit", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        if (res.ok) {
            msg.textContent = "Profile updated successfully";
            msg.style.color = "green";
            document.getElementById("name").textContent = data.username;
        } else {
            msg.textContent = result.error || "Update failed";
            msg.style.color = "red";
        }
    } catch {
        msg.textContent = "Network error";
        msg.style.color = "red";
    }
});

// Navigation
backBtn.onclick = () => window.location.href = "dashboard.html";
logoutBtn.onclick = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("googleUser");
    window.location.href = "login.html";
};
