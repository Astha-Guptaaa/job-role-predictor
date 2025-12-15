document.addEventListener("DOMContentLoaded", async () => {
  const email = localStorage.getItem("email");

  if (!email) {
    alert("Please login again");
    window.location.href = "login.html";
    return;
  }

  const fields = [
    "programming",
    "data_analysis",
    "ml",
    "web",
    "sql",
    "cloud",
    "communication",
    "problem_solving"
  ];

  // 🔹 live value update
  fields.forEach(id => {
    const input = document.getElementById(id);
    const span = document.getElementById(id + "_val");

    span.innerText = input.value;
    input.addEventListener("input", () => {
      span.innerText = input.value;
    });
  });

  // 🔹 load saved skills
  try {
    const res = await fetch(`http://127.0.0.1:5000/skills/get/${email}`);
    const data = await res.json();

    if (res.ok && data.skills) {
      Object.keys(data.skills).forEach(key => {
        const input = document.getElementById(key);
        const span = document.getElementById(key + "_val");

        if (input) {
          input.value = data.skills[key];
          span.innerText = data.skills[key];
        }
      });
    }
  } catch (err) {
    console.log("No previous skills found");
  }

  // 🔹 save skills
  document.getElementById("saveSkillsBtn").addEventListener("click", async () => {
    const skills = {};
    fields.forEach(id => skills[id] = Number(document.getElementById(id).value));

    try {
      const res = await fetch("http://127.0.0.1:5000/skills/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, skills })
      });

      const data = await res.json();

      if (res.ok) {
        alert("Skills saved successfully");
        window.location.href = "dashboard.html";
      } else {
        alert(data.error || "Failed to save skills");
      }
    } catch {
      alert("Server error");
    }
  });
});
