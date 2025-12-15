window.onload = () => {

  // ---------- Populate Graduation Years ----------
  const gradYearSelect = document.getElementById("gradYear");
  const currentYear = new Date().getFullYear();

  for (let year = currentYear; year >= 2000; year--) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    gradYearSelect.appendChild(option);
  }

  // ---------- Degree → Specialization Mapping (Expanded) ----------
  const specializationMap = {
    "B.Tech": [
      "Computer Science",
      "Information Technology",
      "Artificial Intelligence",
      "Data Science",
      "Electronics",
      "Mechanical",
      "Civil"
    ],
    "B.E": [
      "Computer Engineering",
      "Electrical",
      "Mechanical",
      "Civil"
    ],
    "BCA": [
      "Computer Applications",
      "Data Analytics"
    ],
    "B.Sc": [
      "Computer Science",
      "Mathematics",
      "Statistics",
      "Physics"
    ],
    "B.Com": [
      "Accounting",
      "Finance"
    ],
    "BBA": [
      "Management",
      "Marketing"
    ],
    "M.Tech": [
      "Computer Science",
      "AI & ML",
      "Data Science",
      "Cyber Security"
    ],
    "MCA": [
      "Software Development",
      "Data Science"
    ],
    "M.Sc": [
      "Computer Science",
      "Data Science"
    ],
    "MBA": [
      "HR",
      "Marketing",
      "Finance",
      "Business Analytics"
    ]
  };

  const degreeSelect = document.getElementById("degree");
  const specializationSelect = document.getElementById("specialization");

  degreeSelect.addEventListener("change", () => {
    specializationSelect.innerHTML = `<option value="">Select Specialization</option>`;
    const specs = specializationMap[degreeSelect.value] || [];

    specs.forEach(spec => {
      const option = document.createElement("option");
      option.value = spec;
      option.textContent = spec;
      specializationSelect.appendChild(option);
    });
  });

  // ---------- Other Certificate Toggle ----------
  const otherCheck = document.getElementById("certOtherCheck");
  const otherInput = document.getElementById("otherCertificate");

  otherCheck.addEventListener("change", () => {
    if (otherCheck.checked) {
      otherInput.style.display = "block";
    } else {
      otherInput.style.display = "none";
      otherInput.value = "";
    }
  });

  // ---------- Form Submit ----------
  document.getElementById("educationForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login again");
      window.location.href = "login.html";
      return;
    }

    const certifications = [];
    document.querySelectorAll(".cert-item input:checked").forEach(cb => {
      if (cb.value === "Other") {
        if (otherInput.value.trim()) {
          certifications.push(otherInput.value.trim());
        }
      } else {
        certifications.push(cb.value);
      }
    });

    const educationData = {
      degree: degreeSelect.value,
      specialization: specializationSelect.value,
      cgpa: document.getElementById("cgpa").value,
      year: gradYearSelect.value,
      collegeTier: document.getElementById("collegeTier").value,
      internship: document.getElementById("internship").value,
      projects: document.getElementById("projects").value,
      backlogs: document.getElementById("backlogs").value,
      certifications: certifications
    };

    try {
      const res = await fetch("http://127.0.0.1:5000/education/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify(educationData)
      });

      const data = await res.json();

      if (res.ok) {
        alert("Education details saved successfully");
        window.location.href = "dashboard.html";
      } else {
        alert("Error: " + JSON.stringify(data.errors || data.error));
      }

    } catch (err) {
      console.error(err);
      alert("Network error");
    }
  });

  // ---------- Back Button ----------
  document.getElementById("backBtn").addEventListener("click", () => {
    window.location.href = "profile.html";
  });

};
