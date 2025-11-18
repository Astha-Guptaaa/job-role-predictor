// profile.js - matches backend output (result.user.username etc.)

window.onload = async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("No token found. Please login.");
    window.location.href = "login.html";
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/profile", {
      method: "GET",
      headers: { "Authorization": "Bearer " + token }
    });

    const result = await res.json();

    if (res.ok) {
      // backend returns { "user": { "username": "...", "email":"...", ... } }
      const u = result.user;
      document.getElementById("name").textContent = u.username || "";
      document.getElementById("email").textContent = u.email || "";

      document.getElementById("degree").value = u.degree || "";
      document.getElementById("specialization").value = u.specialization || "";
      document.getElementById("cgpa").value = u.cgpa || "";
      document.getElementById("certifications").value = u.certifications || "";
    } else {
      document.getElementById("msg").textContent = result.error || "Failed to load profile";
    }
  } catch (err) {
    document.getElementById("msg").textContent = "Network error";
  }
};

// Update Profile
document.getElementById("updateBtn").addEventListener("click", async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please login first");
    window.location.href = "login.html";
    return;
  }

  const data = {
    degree: document.getElementById("degree").value,
    specialization: document.getElementById("specialization").value,
    cgpa: document.getElementById("cgpa").value,
    certifications: document.getElementById("certifications").value
  };

  try {
    const res = await fetch("http://127.0.0.1:5000/profile/update", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    if (res.ok) {
      document.getElementById("msg").textContent = result.message || "Updated";
    } else {
      document.getElementById("msg").textContent = result.error || "Update failed";
    }
  } catch (err) {
    document.getElementById("msg").textContent = "Network error";
  }
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("token");
  window.location.href = "login.html";
});
