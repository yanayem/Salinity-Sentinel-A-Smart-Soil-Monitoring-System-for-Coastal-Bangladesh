document.addEventListener("DOMContentLoaded", function() {
  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ====== Search Filter ======
  const searchInput = document.getElementById("searchInput");
  searchInput.addEventListener("keyup", function () {
    const filter = searchInput.value.toLowerCase();
    document.querySelectorAll("#soilTable tbody tr").forEach(row => {
      const name = row.cells[0].textContent.toLowerCase();
      row.style.display = name.includes(filter) ? "" : "none";
    });
  });

  // ====== pH Filter ======
  const phMinInput = document.getElementById("phMin");
  const phMaxInput = document.getElementById("phMax");
  const phFilterBtn = document.getElementById("phFilterBtn");
  const phResetBtn = document.getElementById("phResetBtn");

  phFilterBtn.addEventListener("click", function () {
    const min = phMinInput.value ? parseFloat(phMinInput.value) : -Infinity;
    const max = phMaxInput.value ? parseFloat(phMaxInput.value) : Infinity;

    document.querySelectorAll("#soilTable tbody tr").forEach(row => {
      const phRange = row.cells[2].textContent.split("-").map(p => parseFloat(p.trim()));
      const phMin = phRange[0] || 0;
      const phMax = phRange[1] || 14;
      row.style.display = (phMin >= min && phMax <= max) ? "" : "none";
    });
  });

  phResetBtn.addEventListener("click", function () {
    phMinInput.value = "";
    phMaxInput.value = "";
    searchInput.value = "";
    document.querySelectorAll("#soilTable tbody tr").forEach(row => row.style.display = "");
  });

  // ====== Inline Edit / Save ======
  window.editRow = function(btn) {
    const row = btn.closest("tr");
    row.querySelectorAll("td").forEach((cell, index) => {
      if (index < 5) {
        const text = cell.innerText;
        cell.innerHTML = `<input type="text" value="${text}" />`;
      }
    });
    row.querySelector(".edit-icon").style.display = "none";
    row.querySelector(".save-icon").style.display = "inline-block";
  };

  window.saveRow = function(btn) {
    const row = btn.closest("tr");
    const id = row.dataset.id;
    const inputs = row.querySelectorAll("td input");
    const data = {
      name: inputs[0].value,
      description: inputs[1].value,
      ph_min: inputs[2].value.split(" - ")[0].trim(),
      ph_max: inputs[2].value.split(" - ")[1].trim(),
      suitable_crops: inputs[3].value,
      location: inputs[4].value
    };

    fetch(`/soil-types/edit/${id}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(data),
    })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        // update row visually
        row.cells[0].innerText = data.name;
        row.cells[1].innerText = data.description;
        row.cells[2].innerText = `${data.ph_min} - ${data.ph_max}`;
        row.cells[3].innerText = data.suitable_crops;
        row.cells[4].innerText = data.location;

        row.querySelector(".edit-icon").style.display = "inline-block";
        row.querySelector(".save-icon").style.display = "none";
      } else {
        alert("Update failed!");
      }
    })
    .catch(err => {
      console.error(err);
      alert("Network error!");
    });
  };
});
