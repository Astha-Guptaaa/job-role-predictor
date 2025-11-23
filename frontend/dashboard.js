window.onload = async () => {
    const token = localStorage.getItem("token");
    const googleUser = JSON.parse(localStorage.getItem("googleUser") || "null");

    if (!token) {
        // Not logged in
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
            alert(result.error || "Failed to load profile");
            if (res.status === 401) {
                // token issue → redirect to login
                localStorage.removeItem("token");
                localStorage.removeItem("googleUser");
                window.location.href = "login.html";
            }
            return;
        }

        const user = result.user;

        // Welcome message
        document.getElementById("user_name").textContent = user.username || user.email;

        // Profile info
        document.getElementById("name").textContent = user.username || "";
        document.getElementById("email").textContent = user.email || "";
        document.getElementById("degree").textContent = user.degree || "-";
        document.getElementById("specialization").textContent = user.specialization || "-";
        document.getElementById("cgpa").textContent = user.cgpa || "-";
        document.getElementById("certifications").textContent = user.certifications || "-";

        // Google picture
        if (googleUser && googleUser.picture) {
            const img = document.getElementById("profile_pic");
            img.src = googleUser.picture;
            img.style.display = "block";
        } else {
            document.getElementById("profile_pic").style.display = "none";
        }

    } catch (err) {
        alert("Network error. Make sure backend is running.");
    }
};

// Edit button opens form
document.getElementById("editBtn").onclick = () => {
    document.getElementById("editForm").style.display = "block";

    document.getElementById("edit_name").value = document.getElementById("name").innerText;
    document.getElementById("edit_degree").value = document.getElementById("degree").innerText === "-" ? "" : document.getElementById("degree").innerText;
    document.getElementById("edit_specialization").value = document.getElementById("specialization").innerText === "-" ? "" : document.getElementById("specialization").innerText;
    document.getElementById("edit_cgpa").value = document.getElementById("cgpa").innerText === "-" ? "" : document.getElementById("cgpa").innerText;
    document.getElementById("edit_certifications").value = document.getElementById("certifications").innerText === "-" ? "" : document.getElementById("certifications").innerText;
};

// Save button → PATCH update
document.getElementById("saveBtn").onclick = async () => {
    const token = localStorage.getItem("token");
    const msgEl = document.getElementById("update_msg");
    msgEl.innerText = "";

    if (!token) { window.location.href = "login.html"; return; }

    const body = {
        username: document.getElementById("edit_name").value.trim(),
        degree: document.getElementById("edit_degree").value.trim(),
        specialization: document.getElementById("edit_specialization").value.trim(),
        cgpa: document.getElementById("edit_cgpa").value.trim(),
        certifications: document.getElementById("edit_certifications").value.trim(),
    };

    // Client-side CGPA check
    if (body.cgpa && (isNaN(body.cgpa) || body.cgpa < 0 || body.cgpa > 10)) {
        msgEl.innerText = "CGPA must be 0-10";
        msgEl.style.color = "red";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:5000/profile/edit", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        if (res.ok) {
            msgEl.innerText = data.message || "Profile updated successfully!";
            msgEl.style.color = "green";
            // update visible fields
            document.getElementById("name").textContent = body.username || document.getElementById("name").textContent;
            document.getElementById("degree").textContent = body.degree || "-";
            document.getElementById("specialization").textContent = body.specialization || "-";
            document.getElementById("cgpa").textContent = body.cgpa || "-";
            document.getElementById("certifications").textContent = body.certifications || "-";
            // hide form after short delay
            setTimeout(() => {
                document.getElementById("editForm").style.display = "none";
                msgEl.innerText = "";
            }, 1200);
        } else {
            msgEl.innerText = data.error || "Update failed!";
            msgEl.style.color = "red";
        }
    } catch (err) {
        msgEl.innerText = "Network error";
        msgEl.style.color = "red";
    }
};

// Profile button navigates to profile.html
document.getElementById("profileBtn").addEventListener("click", () => {
    window.location.href = "profile.html";
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("token");
    localStorage.removeItem("googleUser");
    window.location.href = "login.html";
});
