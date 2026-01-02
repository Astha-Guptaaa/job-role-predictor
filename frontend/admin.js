//admin.js
const role = localStorage.getItem("role");

if (role !== "admin") {
    alert("Unauthorized access");
    window.location.href = "dashboard.html";
}

const BASE_URL = "http://127.0.0.1:5000";

function uploadDataset() {
    const fileInput = document.getElementById("datasetFile");
    const status = document.getElementById("adminStatus");

    if (!fileInput.files.length) {
        status.innerText = "Please select a CSV file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch(`${BASE_URL}/admin/upload-dataset`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        status.innerText = data.message || "Dataset uploaded successfully.";
    })
    .catch(err => {
        status.innerText = "Dataset upload failed.";
        console.error(err);
    });
}

function retrainModel() {
    const status = document.getElementById("adminStatus");

    fetch(`${BASE_URL}/admin/retrain-model`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    })
    .then(res => res.json())
    .then(data => {
        status.innerText = data.message || "Model retraining started.";
    })
    .catch(err => {
        status.innerText = "Retraining failed.";
        console.error(err);
    });
}


function flag(ts) {
  fetch("http://127.0.0.1:5000/admin/flag-prediction", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`
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
