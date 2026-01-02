//admin_logs.js

const token = localStorage.getItem("token");

if (!token) {
    alert("Admin not logged in");
    window.location.href = "login.html";
}



function loadFeedback() {
  fetch("http://127.0.0.1:5000/admin/feedback", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const table = document.querySelector("#feedbackTable tbody");
    table.innerHTML = "";

    data.forEach(fb => {
      table.innerHTML += `
        <tr>
          <td>${fb.user}</td>
          <td>${fb.role || "N/A"}</td>
          <td>${fb.rating}</td>
          <td>${fb.comment || "-"}</td>
          <td>${fb.timestamp}</td>
        </tr>
      `;
    });
  });
}


function loadLogs() {
  fetch("http://127.0.0.1:5000/admin/prediction-logs", {
    headers: {
      "Authorization": "Bearer " + token
    }
  })
  .then(res => res.json())
  .then(data => {
    const table = document.querySelector("#logsTable tbody");
    table.innerHTML = "";

    data.forEach(log => {
      table.innerHTML += `
        <tr>
          <td>${log.user}</td>
          <td>${log.predicted_role}</td>
          <td>${log.confidence}%</td>
          <td>${log.timestamp}</td>
          <td>${log.flagged ? "🚩 Flagged" : "OK"}</td>
          <td>
            ${
              log.flagged
              ? "<span style='color:red;'>Flagged</span>"
              : `<button class="flag-btn" onclick="flag('${log.timestamp}')">Flag</button>`
            }
          </td>
        </tr>
      `;
    });
  });
}
loadLogs();

function flag(ts) {
  fetch("http://127.0.0.1:5000/admin/flag-prediction", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ timestamp: ts })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
    loadLogs(); // refresh table
  });
}



function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}
