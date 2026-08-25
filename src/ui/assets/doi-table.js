function formatCell(value) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function compareValues(a, b) {
  const aNum = typeof a === "number" ? a : parseFloat(a);
  const bNum = typeof b === "number" ? b : parseFloat(b);
  if (a !== "" && b !== "" && !Number.isNaN(aNum) && !Number.isNaN(bNum)) {
    return aNum - bNum;
  }
  return String(a).localeCompare(String(b), undefined, { sensitivity: "base" });
}

const DEFAULT_PAGE_SIZE = 10;
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];
const CARD_VISIBLE_COUNT = 3;
const RESPONSIVE_QUERY = window.matchMedia("(pointer: coarse), (max-width: 768px)");

document.querySelectorAll("table[data-api]").forEach((table) => {
  const tbody = table.querySelector("tbody");
  const headerCells = Array.from(table.querySelectorAll("thead th"));
  const columns = headerCells.map((th) => th.dataset.field);
  const columnLabels = headerCells.map((th) => th.textContent.trim());
  const searchInput = table.closest(".table-page")?.querySelector("[data-table-search]");
  const paginationEl = table.closest(".table-page")?.querySelector("[data-table-pagination]");
  const pageSizeEl = table.closest(".table-page")?.querySelector("[data-table-page-size]");

  let allRows = [];
  let sortField = null;
  let sortDir = null;
  let currentPage = 1;
  let pageSize = DEFAULT_PAGE_SIZE;

  // Rows-per-page is always 10 on responsive/touch viewports — the
  // page-size buttons only show (and only apply) on the desktop table.
  const getEffectivePageSize = () => (RESPONSIVE_QUERY.matches ? DEFAULT_PAGE_SIZE : pageSize);

  const showMessage = (message) => {
    tbody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = columns.length + 1;
    cell.textContent = message;
    row.appendChild(cell);
    tbody.appendChild(row);
    if (paginationEl) paginationEl.innerHTML = "";
  };

  const getFilteredRows = () => {
    const term = (searchInput?.value || "").trim().toLowerCase();
    if (!term) return allRows;
    return allRows.filter((row) =>
      columns.some((field) => formatCell(row[field]).toLowerCase().includes(term))
    );
  };

  const getVisibleRows = () => {
    const filtered = getFilteredRows();
    if (!sortField || !sortDir) return filtered;
    const sorted = [...filtered].sort((rowA, rowB) => {
      const result = compareValues(rowA[sortField] ?? "", rowB[sortField] ?? "");
      return sortDir === "asc" ? result : -result;
    });
    return sorted;
  };

  const renderPageSizeControls = () => {
    if (!pageSizeEl) return;
    pageSizeEl.innerHTML = "";

    const label = document.createElement("span");
    label.className = "page-size-label";
    label.textContent = "Results per page:";
    pageSizeEl.appendChild(label);

    PAGE_SIZE_OPTIONS.forEach((option) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "page-size-btn";
      btn.textContent = String(option);
      if (option === pageSize) btn.classList.add("active");
      btn.addEventListener("click", () => {
        pageSize = option;
        currentPage = 1;
        render();
      });
      pageSizeEl.appendChild(btn);
    });
  };

  const renderPagination = (totalRows) => {
    if (!paginationEl) return;
    paginationEl.innerHTML = "";
    const pageCount = Math.max(1, Math.ceil(totalRows / getEffectivePageSize()));
    if (pageCount <= 1) return;

    const makeSpan = (label, { className = "", disabled = false, page = null, active = false } = {}) => {
      const span = document.createElement("span");
      if (className) span.className = className;
      if (active) span.classList.add("active");
      if (disabled) span.classList.add("is-disabled");
      span.textContent = label;
      if (!disabled && page !== null) {
        span.addEventListener("click", () => {
          currentPage = page;
          render();
        });
      }
      return span;
    };

    paginationEl.appendChild(
      makeSpan("Previous", { className: "page-prev", disabled: currentPage <= 1, page: currentPage - 1 })
    );
    for (let page = 1; page <= pageCount; page += 1) {
      paginationEl.appendChild(makeSpan(String(page), { page, active: page === currentPage }));
    }
    paginationEl.appendChild(
      makeSpan("Next", { className: "page-next", disabled: currentPage >= pageCount, page: currentPage + 1 })
    );
  };

  const render = () => {
    renderPageSizeControls();
    const visibleRows = getVisibleRows();

    if (!visibleRows.length) {
      showMessage(allRows.length ? "No matching records." : "No records found.");
      return;
    }

    const effectivePageSize = getEffectivePageSize();
    const pageCount = Math.max(1, Math.ceil(visibleRows.length / effectivePageSize));
    currentPage = Math.min(currentPage, pageCount);
    const start = (currentPage - 1) * effectivePageSize;
    const pageRows = visibleRows.slice(start, start + effectivePageSize);

    tbody.innerHTML = "";
    pageRows.forEach((row) => {
      const tr = document.createElement("tr");
      columns.forEach((field, index) => {
        const td = document.createElement("td");
        td.textContent = formatCell(row[field]);
        td.dataset.header = columnLabels[index];
        if (index >= CARD_VISIBLE_COUNT) {
          td.classList.add("card-field-extra");
        }
        tr.appendChild(td);
      });

      if (columns.length > CARD_VISIBLE_COUNT) {
        const toggleCell = document.createElement("td");
        toggleCell.className = "card-toggle-cell";
        const toggleBtn = document.createElement("button");
        toggleBtn.type = "button";
        toggleBtn.className = "card-toggle-btn";
        toggleBtn.textContent = "Show more";
        toggleBtn.addEventListener("click", () => {
          const expanded = tr.classList.toggle("card-expanded");
          toggleBtn.classList.toggle("active", expanded);
          toggleBtn.textContent = expanded ? "Show less" : "Show more";
        });
        toggleCell.appendChild(toggleBtn);
        tr.appendChild(toggleCell);
      }

      tbody.appendChild(tr);
    });

    renderPagination(visibleRows.length);
  };

  headerCells.forEach((th) => {
    th.addEventListener("click", () => {
      if (sortField === th.dataset.field) {
        sortDir = sortDir === "asc" ? "desc" : "asc";
      } else {
        sortField = th.dataset.field;
        sortDir = "asc";
      }
      headerCells.forEach((cell) => cell.classList.remove("sorted-asc", "sorted-desc"));
      th.classList.add(sortDir === "asc" ? "sorted-asc" : "sorted-desc");
      currentPage = 1;
      render();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      currentPage = 1;
      render();
    });
  }

  RESPONSIVE_QUERY.addEventListener("change", () => {
    currentPage = 1;
    render();
  });

  showMessage("Loading…");

  fetch(table.dataset.api)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }
      return response.json();
    })
    .then((rows) => {
      allRows = rows;
      render();
    })
    .catch((error) => {
      showMessage(`Failed to load records: ${error.message}`);
    });
});
