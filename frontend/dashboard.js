// dashboard.js
// =======================
// AUTH + PROFILE LOAD
// =======================
const BASE_URL = "http://127.0.0.1:5000";
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
            alert(result.error || "Failed to load profile");
            localStorage.clear();
            window.location.href = "login.html";
            return;
        }

        const user = result.user;

        // Welcome
        document.getElementById("user_name").textContent =
            user.username || user.email;

        // Profile data
        document.getElementById("name").textContent = user.username || "-";
        document.getElementById("email").textContent = user.email || "-";
        document.getElementById("about").textContent = user.about || "-";
        
        // ✅ Education should come from education object
        const edu = user.education || {};
        document.getElementById("degree").textContent = edu.degree || "-";
        document.getElementById("specialization").textContent = edu.specialization || "-";
        document.getElementById("cgpa").textContent = edu.cgpa || "-";
        document.getElementById("certifications").textContent =
            (edu.certifications && edu.certifications.join(", ")) || "-";

        // Google image
        if (googleUser?.picture) {
            const img = document.getElementById("profile_pic");
            img.src = googleUser.picture;
            img.style.display = "block";
        }

    } catch {
        alert("Backend not running");
    }
};

// =======================
// EDIT PROFILE
// =======================
document.getElementById("editBtn").onclick = () => {
    document.getElementById("editForm").style.display = "block";

    document.getElementById("edit_name").value =
        document.getElementById("name").innerText;
    document.getElementById("edit_about").value =
        document.getElementById("about").innerText === "-" ? "" :
         document.getElementById("about").innerText;
    };

document.getElementById("saveBtn").onclick = async () => {
    const token = localStorage.getItem("token");
    const msg = document.getElementById("update_msg");

    const body = {
        username: document.getElementById("edit_name").value.trim(),
        about: document.getElementById("edit_about").value.trim(),
    };

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
        msg.innerText = "Profile updated";
        msg.style.color = "green";
        setTimeout(() => location.reload(), 800);
    } else {
        msg.innerText = data.error || "Update failed";
        msg.style.color = "red";
    }
};

// =======================
// LOGOUT
// =======================
document.getElementById("logoutBtn").onclick = () => {
    localStorage.clear();
    window.location.href = "login.html";
};

// =======================
// PROFILE
// =======================
document.getElementById("profileBtn").onclick = () => {
    window.location.href = "profile.html";
};



// ================== JOB PREDICTION (FINAL FIX) ==================

// 🔒 store current prediction safely
let latestPrediction = null;


// ------------------ PREDICT BUTTON ------------------
document.getElementById("predictBtn").addEventListener("click", async (e) => {
    e.preventDefault();   // ❌ stop page reload

    const token = localStorage.getItem("token");

    const degree = document.getElementById("degree").innerText;
    const specialization = document.getElementById("specialization").innerText;
    const cgpaText = document.getElementById("cgpa").innerText;
    const cgpa = cgpaText === "-" ? null : Number(cgpaText);
    const certText = document.getElementById("certifications").innerText;

    if (degree === "-" || specialization === "-") {
        alert("Please fill education details first");
        return;
    }

    const payload = {
        degree,
        specialization,
        cgpa,
        certifications: certText === "-" ? [] : certText.split(",").map(c => c.trim())
    };

    try {
        const res = await fetch("http://127.0.0.1:5000/predict-job-role", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.message || "Prediction failed");
            return;
        }

        const predictions =
          data.all_predictions || data.predictions || data.result;

        if (!predictions || predictions.length === 0) {
          alert("Prediction data missing");
          return;
        }

        latestPrediction = predictions;
        localStorage.setItem("latestPrediction", JSON.stringify(predictions));


        // ✅ save current prediction in JS memory
        latestPrediction = data.all_predictions;

        // ✅ also save in browser (VERY IMPORTANT)
        localStorage.setItem("latestPrediction", JSON.stringify(latestPrediction));

        // ✅ show immediately
        renderPrediction(latestPrediction);

        // ✅ update history list only
        loadPredictionHistory();

        loadCareerInsights();


    } catch (err) {
        console.error(err);
        alert("Prediction server error");
    }
});

fetch(`${BASE_URL}/profile`, {
  headers: {
    "Authorization": `Bearer ${localStorage.getItem("token")}`
  }
})
.then(res => res.json())
.then(user => {
  document.getElementById("username").innerText = user.username;

  if (user.role === "admin") {
    document.getElementById("adminBtn").style.display = "block";
  } else {
    document.getElementById("adminBtn").style.display = "none";
  }
});


// ------------------ RENDER CURRENT PREDICTION ------------------
function renderPrediction(recommendations) {

    const resultBox = document.getElementById("predictionResult");
    const emptyText = document.getElementById("noPredictionText");

    emptyText.style.display = "none";
    resultBox.style.display = "block";

    resultBox.innerHTML = "<h4>Latest Prediction</h4>";

    recommendations.forEach((rec, index) => {
        resultBox.innerHTML += `
            <div style="margin-bottom:12px;">
                <strong>${index === 0 ? "⭐ " : ""}${rec.job_role}</strong>
                <div style="background:#eee;border-radius:6px;">
                    <div style="
                        width:${rec.confidence}%;
                        background:#4caf50;
                        color:white;
                        padding:4px 6px;
                        border-radius:6px;">
                        ${rec.confidence}%
                    </div>
                </div>
            </div>
        `;
    });
}


// ------------------ LOAD HISTORY ONLY ------------------
function loadPredictionHistory() {

    fetch("http://127.0.0.1:5000/prediction-history", {
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    })
    .then(res => res.json())
    .then(data => {

        const historyDiv = document.getElementById("predictionHistory");
        historyDiv.innerHTML = "";

        if (!data || data.length === 0) return;

        historyDiv.innerHTML = "<h4>Previous Predictions</h4>";

        data.slice().reverse().forEach(item => {
            historyDiv.innerHTML += `
                <div style="margin-bottom:8px;">
                    <strong>${item.predictions?.[0]?.job_role}</strong><br>
                    <small>${item.timestamp}</small>
                </div>
            `;
        });
    })
    .catch(err => console.error(err));
}


// ------------------ PAGE LOAD ------------------
document.addEventListener("DOMContentLoaded", () => {

    // 🔁 restore prediction after refresh/navigation
    const saved = localStorage.getItem("latestPrediction");
    if (saved) {
        latestPrediction = JSON.parse(saved);
        renderPrediction(latestPrediction);
    }

    loadPredictionHistory();
    loadCareerInsights();

});

async function loadCharts() {

  const barData = await fetch("http://127.0.0.1:5000/api/visualizations/degree-job")
    .then(res => res.json());

  new Chart(document.getElementById("degreeJobChart"), {
    type: "bar",
    data: {
      labels: Object.keys(barData),
      datasets: [{
        label: "Predicted Count",
        data: Object.values(barData),
        backgroundColor: "#3b82f6"
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  const pieData = await fetch("http://127.0.0.1:5000/api/visualizations/job-domain")
    .then(res => res.json());

  new Chart(document.getElementById("jobDomainChart"), {
    type: "doughnut",
    data: {
      labels: Object.keys(pieData),
      datasets: [{
        data: Object.values(pieData),
        backgroundColor: [
         "#0f172a", // very dark navy
  "#1e293b",
  "#1e3a8a",
  "#1d4ed8",
  "#2563eb",
  "#3b82f6",
  "#60a5fa",
  "#93c5fd",
  "#bfdbfe",
  "#dbeafe",

  "#082f49",
  "#0c4a6e",
  "#0369a1",
  "#0284c7",
  "#0ea5e9",
  "#38bdf8",
  "#7dd3fc",
  "#bae6fd",
  "#e0f2fe",
  "#f0f9ff"
        ]
      }]
    },
    options: {
      plugins: {
        legend: { position: "bottom" }
      }
    }
  });
}

loadCharts();





// =============================
// CAREER INSIGHTS
// =============================

function displayCareerInsights(data) {
  if (!data || !data.career_insight) {
    document.getElementById("careerInsight").innerText =
      "No insights available";
    return;
  }

  // ✅ Insight message
  document.getElementById("careerInsight").innerText =
    data.career_insight.message;

  // ✅ Alternative roles
  const ul = document.getElementById("alternativeRoles");
  ul.innerHTML = "";

  data.alternative_roles.forEach(role => {
    const li = document.createElement("li");
    li.innerText = role;
    ul.appendChild(li);
  });
}


async function loadCareerInsights() {
  try {
    const token = localStorage.getItem("token");
    if (!token) return;

    const res = await fetch(
      "http://127.0.0.1:5000/api/career-insights",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    const data = await res.json();
    displayCareerInsights(data);

  } catch (err) {
    console.error("Career Insights load failed", err);
  }
}



document.getElementById("adminBtn")?.addEventListener("click", () => {
  window.location.href = "http://127.0.0.1:5000/admin";
});

function goToAdmin() {
    window.location.href = "admin.html";
}

function submitFeedback() {
  const predictions = JSON.parse(localStorage.getItem("latestPrediction"));

  fetch("http://127.0.0.1:5000/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`
    },
    body: JSON.stringify({
      job_role: predictions?.[0]?.job_role || "N/A",
      rating: document.getElementById("rating").value,
      comment: document.getElementById("comment").value
    })
  })
  .then(res => res.json())
  .then(data => alert(data.message));
}


function scrollToSection(id) {
  document.getElementById(id).scrollIntoView({
    behavior: "smooth"
  });
}
