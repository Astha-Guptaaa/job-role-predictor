// education.js
// ================== EDUCATION PAGE SCRIPT ==================

window.onload = async () => {
  populateGradYears();
  setupDegreeSpecialization();
  setupOtherCertificateToggle();
  setupFormSubmit();
  setupBackButton();

  await loadEducationData();
};

// ---------------- LOAD EDUCATION DATA ----------------
async function loadEducationData() {
  try {
    const token = localStorage.getItem("token");
    if (!token) return;

    const res = await fetch("http://127.0.0.1:5000/education/get", {
      headers: { Authorization: "Bearer " + token }
    });

    const data = await res.json();
    if (!data.education) return;

    const edu = data.education;

    const degreeSelect = document.getElementById("degree");
    const specializationSelect = document.getElementById("specialization");

    degreeSelect.value = edu.degree;
    degreeSelect.dispatchEvent(new Event("change")); // load specializations

    specializationSelect.value = edu.specialization;
    document.getElementById("cgpa").value = edu.cgpa || "";
    document.getElementById("gradYear").value = edu.year || "";
    document.getElementById("collegeTier").value = edu.collegeTier || "";
    document.getElementById("internship").value = edu.internship || "";
    document.getElementById("projects").value = edu.projects || "";
    document.getElementById("backlogs").value = edu.backlogs || "";

    // Certifications
    if (Array.isArray(edu.certifications)) {
      edu.certifications.forEach(cert => {
        const checkbox = document.querySelector(
          `.cert-item input[value="${cert}"]`
        );
        if (checkbox) checkbox.checked = true;
      });
    }

  } catch (err) {
    console.error("Failed to load education data", err);
  }
}

// ---------------- GRAD YEAR DROPDOWN ----------------
function populateGradYears() {
  const gradYearSelect = document.getElementById("gradYear");
  const currentYear = new Date().getFullYear();

  gradYearSelect.innerHTML = `<option value="">Select Year</option>`;

  for (let year = currentYear; year >= 2000; year--) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    gradYearSelect.appendChild(option);
  }
}

// ---------------- DEGREE → SPECIALIZATION ----------------
function setupDegreeSpecialization() {
  const specializationMap = {
    "B.Tech": ["Computer Science", "Information Technology", "Artificial Intelligence", "Data Science", "Electronics", "Mechanical", "Civil"],
    "B.E": ["Computer Engineering", "Electrical", "Mechanical", "Civil"],
    "BCA": ["Computer Applications", "Data Analytics"],
    "B.Sc": ["Computer Science", "Mathematics", "Statistics", "Physics"],
    "B.Com": ["Accounting", "Finance"],
    "BBA": ["Management", "Marketing"],
    "M.Tech": ["Computer Science", "AI & ML", "Data Science", "Cyber Security"],
    "MCA": ["Software Development", "Data Science"],
    "M.Sc": ["Computer Science", "Data Science"],
    "MBA": ["HR", "Marketing", "Finance", "Business Analytics"]
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
}

// ---------------- OTHER CERTIFICATE ----------------
function setupOtherCertificateToggle() {
  const otherCheck = document.getElementById("certOtherCheck");
  const otherInput = document.getElementById("otherCertificate");

  otherCheck.addEventListener("change", () => {
    otherInput.style.display = otherCheck.checked ? "block" : "none";
    if (!otherCheck.checked) otherInput.value = "";
  });
}

// ---------------- FORM SUBMIT ----------------
function setupFormSubmit() {
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
        const otherInput = document.getElementById("otherCertificate");
        if (otherInput.value.trim()) certifications.push(otherInput.value.trim());
      } else {
        certifications.push(cb.value);
      }
    });

    const educationData = {
      degree: document.getElementById("degree").value,
      specialization: document.getElementById("specialization").value,
      cgpa: document.getElementById("cgpa").value,
      year: document.getElementById("gradYear").value,
      collegeTier: document.getElementById("collegeTier").value,
      internship: document.getElementById("internship").value,
      projects: document.getElementById("projects").value,
      backlogs: document.getElementById("backlogs").value,
      certifications
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
}

// ---------------- BACK BUTTON ----------------
function setupBackButton() {
  document.getElementById("backBtn").addEventListener("click", () => {
    window.location.href = "profile.html";
  });
}
