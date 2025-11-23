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
            if (res.status === 401) {
                localStorage.removeItem("token");
                localStorage.removeItem("googleUser");
                window.location.href = "login.html";
            }
            return; 
        }

        const u = result.user;

        // Google login info
        if (googleUser) {
            document.getElementById("name").textContent = googleUser.username || u.username;
            document.getElementById("email").textContent = googleUser.email || u.email;
            if (googleUser.picture) {
                const img = document.getElementById("g_pic");
                img.src = googleUser.picture;
                img.style.display = "block";
            }
            document.getElementById("g_name").textContent = googleUser.username || "";
            document.getElementById("g_email").textContent = googleUser.email || "";
        } else {
            document.getElementById("name").textContent = u.username || "";
            document.getElementById("email").textContent = u.email || "";
        }

        // Pre-fill edit fields
        document.getElementById("edit_name").value = u.username || "";
        document.getElementById("edit_degree").value = u.degree || "";
        document.getElementById("edit_specialization").value = u.specialization || "";
        document.getElementById("edit_cgpa").value = u.cgpa || "";
        document.getElementById("edit_certifications").value = u.certifications || "";

    } catch (err) {
        document.getElementById("msg").textContent = "Network error";
    }
};

// Save updated profile (profile page)
document.getElementById("saveBtn").addEventListener("click", async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    if (!token) { window.location.href="login.html"; return; }

    const data = {
        username: document.getElementById("edit_name").value.trim(),
        degree: document.getElementById("edit_degree").value.trim(),
        specialization: document.getElementById("edit_specialization").value.trim(),
        cgpa: document.getElementById("edit_cgpa").value.trim(),
        certifications: document.getElementById("edit_certifications").value.trim()
    };

    if (data.cgpa && (isNaN(data.cgpa) || data.cgpa < 0 || data.cgpa > 10)) {
        document.getElementById("update_msg").textContent = "CGPA must be 0-10";
        document.getElementById("update_msg").style.color = "red";
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
            document.getElementById("update_msg").textContent = result.message || "Updated successfully";
            document.getElementById("update_msg").style.color = "green";
            // update visible fields
            document.getElementById("name").textContent = data.username || document.getElementById("name").textContent;
            setTimeout(()=>{ document.getElementById("update_msg").textContent=""; }, 2000);
        } else {
            document.getElementById("update_msg").textContent = result.error || "Update failed";
            document.getElementById("update_msg").style.color = "red";
        }
    } catch (err) {
        document.getElementById("update_msg").textContent="Network error";
        document.getElementById("update_msg").style.color = "red";
    }
});

// Back to dashboard
document.getElementById("backBtn").addEventListener("click", () => {
    window.location.href = "dashboard.html";
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", ()=>{
    localStorage.removeItem("token");
    localStorage.removeItem("googleUser");
    window.location.href="login.html";
});
