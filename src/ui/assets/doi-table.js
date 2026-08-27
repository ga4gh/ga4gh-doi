function formatCell(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

document.querySelectorAll("table[data-api]").forEach((table) => {
  const tbody = table.querySelector("tbody");
  const columns = Array.from(table.querySelectorAll("thead th")).map((th) => th.dataset.field);
  const searchInput = table.closest(".table-page")?.querySelector("[data-table-search]");

  const showMessage = (message) => {
    tbody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = columns.length;
    cell.textContent = message;
    row.appendChild(cell);
    tbody.appendChild(row);
  };

  const applyFilter = () => {
    const term = (searchInput?.value || "").trim().toLowerCase();
    tbody.querySelectorAll("tr").forEach((row) => {
      row.hidden = term.length > 0 && !row.textContent.toLowerCase().includes(term);
    });
  };

  if (searchInput) {
    searchInput.addEventListener("input", applyFilter);
  }

  showMessage("Loading…");

  fetch(table.dataset.api)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    })
    .then((rows) => {
      if (!rows.length) {
        showMessage("No records found.");
        return;
      }
      tbody.innerHTML = "";
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        columns.forEach((field) => {
          const td = document.createElement("td");
          td.textContent = formatCell(row[field]);
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      applyFilter();
    })
    .catch((error) => {
      showMessage(`Failed to load records: ${error.message}`);
    });
});
