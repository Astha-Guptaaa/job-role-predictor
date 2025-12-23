// profile.js
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
        const edu = u.education || {};

        document.getElementById("degree").textContent = edu.degree || "-";
        document.getElementById("specialization").textContent = edu.specialization || "-";
        document.getElementById("cgpa").textContent = edu.cgpa || "-";

        document.getElementById("certifications").textContent =
             (edu.certifications && edu.certifications.join(", ")) || "-";


// Display basic info
document.getElementById("name").textContent = u.username || "";
document.getElementById("email").textContent = u.email || "";
document.getElementById("about").textContent = u.about || "";


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
        document.getElementById("edit_about").value = u.about || "";

        
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
        about: edit_about.value.trim()
    };

    

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
