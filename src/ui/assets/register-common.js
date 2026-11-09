// Shared helpers used by every doi_type's register-*.js file.

function fieldValue(field) {
  return field.classList.contains("is-sample") ? "" : field.value;
}

// Parses full CSV text into rows of cells, honoring quoted fields and ignoring empty rows. Returns an array of arrays of strings.
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (inQuotes) {
      if (char === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\r") {
      // ignore; \n (below) ends the row
    } else if (char === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }

  return rows.filter((cells) => cells.length > 1 || cells[0] !== "");
}

function isValidUrl(value) {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

// Generic CSV-row validation mirroring a register form's own constraints, so an
// uploaded CSV is held to the same rules as manual entry. `config` fields:
//   requiredFields: [[column, label]]
//   dateFields: [{ month, day, year, label, required }] - month/day/year are column names
//   urlFields / emailFields / numberFields: [[column, label]]
//   jsonListFields: [[column, label]] - column must be empty or a JSON array
//   nonEmptyJsonListFields: [[column, label]] - column must be a JSON array with at least one entry
//   customValidators: [(get) => errorMessageOrNull] - for rules too specific to generalize;
//     `get(column)` reads a trimmed cell value for the current row, same as internally.
function validateCsvRows(header, dataRows, config) {
  const {
    requiredFields = [],
    dateFields = [],
    urlFields = [],
    emailFields = [],
    numberFields = [],
    jsonListFields = [],
    nonEmptyJsonListFields = [],
    customValidators = [],
  } = config;
  const errors = [];

  dataRows.forEach((cells, rowIndex) => {
    const rowLabel = `Row ${rowIndex + 2}`; // +2: row 1 is the header
    const get = (column) => {
      const index = header.indexOf(column);
      return (index === -1 ? "" : cells[index] || "").trim();
    };

    requiredFields.forEach(([column, label]) => {
      if (!get(column)) {
        errors.push(`${rowLabel}: ${label} is required`);
      }
    });

    dateFields.forEach(({ month, day, year, label, required = true }) => {
      const m = get(month);
      const d = get(day);
      const y = get(year);
      if (!m && !d && !y) {
        if (required) {
          errors.push(`${rowLabel}: ${label} is required`);
        }
        return;
      }
      if (!m || !d || !y || Number.isNaN(new Date(`${y}-${m}-${d}`).getTime())) {
        errors.push(`${rowLabel}: ${label} is invalid`);
      }
    });

    urlFields.forEach(([column, label]) => {
      const value = get(column);
      if (value && !isValidUrl(value)) {
        errors.push(`${rowLabel}: ${label} must be a valid URL`);
      }
    });

    emailFields.forEach(([column, label]) => {
      const value = get(column);
      if (value && !isValidEmail(value)) {
        errors.push(`${rowLabel}: ${label} must be a valid email`);
      }
    });

    numberFields.forEach(([column, label]) => {
      const value = get(column);
      if (value && Number.isNaN(Number(value))) {
        errors.push(`${rowLabel}: ${label} must be a number`);
      }
    });

    jsonListFields.forEach(([column, label]) => {
      const value = get(column);
      if (!value) return;
      try {
        if (!Array.isArray(JSON.parse(value))) {
          throw new Error("not a list");
        }
      } catch {
        errors.push(`${rowLabel}: ${label} must be a valid list`);
      }
    });

    nonEmptyJsonListFields.forEach(([column, label]) => {
      const value = get(column);
      let parsed;
      try {
        parsed = value ? JSON.parse(value) : [];
      } catch {
        errors.push(`${rowLabel}: ${label} must be a valid list`);
        return;
      }
      if (!Array.isArray(parsed) || parsed.length === 0) {
        errors.push(`${rowLabel}: at least one ${label.toLowerCase()} entry is required`);
      }
    });

    customValidators.forEach((validate) => {
      const message = validate(get);
      if (message) {
        errors.push(`${rowLabel}: ${message}`);
      }
    });
  });

  return errors;
}

// Contributor row (+/-) helpers, parameterized by container so each doi_type's
// register-*.js can keep its own container element and queue state.
// requiredFields (e.g. ["first_name", "last_name", "affiliation"]) shows the
// standard red-asterisk indicator on those labels; fields left out stay
// unmarked. Standards passes none of these (contributors stay fully optional
// there); Posted Content requires first/last/affiliation.
//
// Deliberately NOT a native `required` attribute: these inputs have no
// sample-arming trick, so a real `required` would make the browser's native
// constraint validation silently block the Add button before validateContributorRows()
// ever runs (same failure mode as an earlier bug with the Standard Designator
// dropdown). The marker is purely visual here; enforcement happens in JS via
// validateContributorRows() and the matching CSV customValidators.
function addContributorRow(container, requiredFields = []) {
  const index = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "contributor-row";
  const labelClass = (field) => (requiredFields.includes(field) ? "label-text is-required" : "label-text");
  row.innerHTML = `
    <span class="contributor-row-label">Author ${index}</span>
    <label><span class="${labelClass("first_name")}">First Name</span> <input type="text" class="contributor-first-name" /></label>
    <label><span class="${labelClass("last_name")}">Last Name</span> <input type="text" class="contributor-last-name" /></label>
    <label><span class="${labelClass("affiliation")}">Affiliation</span> <input type="text" class="contributor-affiliation" /></label>
    <label><span class="label-text">ORCID</span> <input type="text" class="contributor-orcid" /></label>
  `;
  container.appendChild(row);
}

function removeLastContributorRow(container) {
  container.lastElementChild?.remove();
}

function collectContributors(container) {
  return Array.from(container.children)
    .map((row) => ({
      first_name: row.querySelector(".contributor-first-name").value.trim(),
      last_name: row.querySelector(".contributor-last-name").value.trim(),
      affiliation: row.querySelector(".contributor-affiliation").value.trim(),
      orcid: row.querySelector(".contributor-orcid").value.trim(),
    }))
    .filter((contributor) => contributor.first_name || contributor.last_name);
}

const CONTRIBUTOR_FIELD_LABELS = {
  first_name: "First Name",
  last_name: "Last Name",
  affiliation: "Affiliation",
  orcid: "ORCID",
};

// Flags any contributor row that has SOME content but is missing one of
// requiredFields - a fully blank row (no content at all) is a harmless leftover
// and is ignored here, same as collectContributors() silently drops it.
function validateContributorRows(container, requiredFields) {
  const errors = [];
  Array.from(container.children).forEach((row, index) => {
    const values = {
      first_name: row.querySelector(".contributor-first-name").value.trim(),
      last_name: row.querySelector(".contributor-last-name").value.trim(),
      affiliation: row.querySelector(".contributor-affiliation").value.trim(),
      orcid: row.querySelector(".contributor-orcid").value.trim(),
    };
    const hasAnyContent = Object.values(values).some(Boolean);
    if (!hasAnyContent) return;

    const missingFields = requiredFields.filter((field) => !values[field]);
    if (missingFields.length) {
      const labels = missingFields.map((field) => CONTRIBUTOR_FIELD_LABELS[field]).join(", ");
      errors.push(`Contributor ${index + 1}: ${labels} required`);
    }
  });
  return errors;
}
