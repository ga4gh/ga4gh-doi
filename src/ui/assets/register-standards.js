const registerForm = document.querySelector('form[data-form="register"]');
const standardsTypeSelect = document.getElementById("doi-type-select");
const standardsSection = document.querySelector('.doi-fields[data-doi-type="standards"]');
const registrantNameField = document.querySelector('[name="registrant_name"]');
const registrantEmailField = document.querySelector('[name="registrant_email"]');
const queueBody = document.querySelector("#standards-queue-table tbody");
const submitSpinner = document.getElementById("standards-submit-spinner");
const uploadButton = document.getElementById("standards-upload-btn");
const uploadInput = document.getElementById("standards-upload-input");
const contributorRowsContainer = document.getElementById("standards-contributor-rows");
const contributorAddButton = document.getElementById("standards-contributor-add");
const contributorRemoveButton = document.getElementById("standards-contributor-remove");

const standardsQueue = [];
let uploadedCsvText = null;

function addContributorRow() {
  const index = contributorRowsContainer.children.length + 1;
  const row = document.createElement("div");
  row.className = "contributor-row";
  row.innerHTML = `
    <span class="contributor-row-label">Author ${index}</span>
    <label>First Name <input type="text" class="contributor-first-name" /></label>
    <label>Last Name <input type="text" class="contributor-last-name" /></label>
  `;
  contributorRowsContainer.appendChild(row);
}

function removeLastContributorRow() {
  contributorRowsContainer.lastElementChild?.remove();
}

function collectContributors() {
  return Array.from(contributorRowsContainer.children)
    .map((row) => ({
      first_name: row.querySelector(".contributor-first-name").value.trim(),
      last_name: row.querySelector(".contributor-last-name").value.trim(),
    }))
    .filter((contributor) => contributor.first_name || contributor.last_name);
}

contributorAddButton.addEventListener("click", addContributorRow);
contributorRemoveButton.addEventListener("click", removeLastContributorRow);

function fieldValue(field) {
  return field.classList.contains("is-sample") ? "" : field.value;
}

function collectStandardsRow() {
  const values = {};
  const missing = [];

  standardsSection.querySelectorAll("[data-sample]").forEach((field) => {
    const value = fieldValue(field);
    if (!value && field.required) {
      missing.push(field.name);
    }
    values[field.name] = value;
  });
  values.contributors = collectContributors();

  return { values, missing };
}

function resetStandardsFields() {
  standardsSection.querySelectorAll("[data-sample]").forEach(armSampleField);
  contributorRowsContainer.innerHTML = "";
}

function renderQueueRow(title, resourceUrl) {
  const row = document.createElement("tr");
  const titleCell = document.createElement("td");
  titleCell.textContent = title;
  const resourceCell = document.createElement("td");
  resourceCell.textContent = resourceUrl;
  row.append(titleCell, resourceCell);
  queueBody.appendChild(row);
}

function handleAddStandard() {
  const { values, missing } = collectStandardsRow();
  if (missing.length) {
    alert(`Please fill in: ${missing.join(", ")}`);
    return;
  }

  uploadedCsvText = null;
  standardsQueue.push(values);
  renderQueueRow(values.title, values.resource_url);
  resetStandardsFields();
}

// Parses full CSV text into rows of cells, honoring quoted fields (so commas,
// quotes, and newlines embedded in a cell - e.g. the JSON contributors column -
// don't get mistaken for delimiters).
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

// Mirrors the register form's own constraints (required fields, type="url",
// type="email") so an uploaded CSV is held to the same rules as manual entry.
const REQUIRED_CSV_FIELDS = [
  ["<title>", "Title"],
  ["<resource>", "Resource URL"],
  ["<publisher_place>", "Publisher Place"],
  ["<std_designator>", "Standard Designator"],
  ["<standards_body_acronym>", "Standards Body Acronym"],
  ["<registrant>", "Registrant"],
  ["<publisher_name>", "Publisher Name"],
  ["<standards_body_name>", "Standards Body Name"],
  ["<organization>", "Organization"],
  ["<email_address>", "Email Address"],
];

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

function validateCsvRows(header, dataRows) {
  const errors = [];

  dataRows.forEach((cells, rowIndex) => {
    const rowLabel = `Row ${rowIndex + 2}`; // +2: row 1 is the header
    const get = (column) => {
      const index = header.indexOf(column);
      return (index === -1 ? "" : cells[index] || "").trim();
    };

    REQUIRED_CSV_FIELDS.forEach(([column, label]) => {
      if (!get(column)) {
        errors.push(`${rowLabel}: ${label} is required`);
      }
    });

    const month = get("<month>");
    const day = get("<day>");
    const year = get("<year>");
    if (!month || !day || !year) {
      errors.push(`${rowLabel}: Publish Date is required`);
    } else if (Number.isNaN(new Date(`${year}-${month}-${day}`).getTime())) {
      errors.push(`${rowLabel}: Publish Date is invalid`);
    }

    const resource = get("<resource>");
    if (resource && !isValidUrl(resource)) {
      errors.push(`${rowLabel}: Resource URL must be a valid URL`);
    }

    const email = get("<email_address>");
    if (email && !isValidEmail(email)) {
      errors.push(`${rowLabel}: Email Address must be a valid email`);
    }

    const itemNumber = get("<item_number>");
    if (itemNumber && Number.isNaN(Number(itemNumber))) {
      errors.push(`${rowLabel}: Item Number must be a number`);
    }

    const contributors = get("<contributors>");
    if (contributors) {
      try {
        if (!Array.isArray(JSON.parse(contributors))) {
          throw new Error("not a list");
        }
      } catch {
        errors.push(`${rowLabel}: Contributors must be a valid list`);
      }
    }
  });

  return errors;
}

function handleCsvUpload(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const rows = parseCsv(reader.result);
    if (!rows.length) {
      return;
    }

    const [header, ...dataRows] = rows;
    const errors = validateCsvRows(header, dataRows);
    if (errors.length) {
      alert(`CSV does not pass validation:\n\n${errors.join("\n")}`);
      uploadInput.value = "";
      return;
    }

    const titleIndex = header.indexOf("<title>");
    const resourceIndex = header.indexOf("<resource>");

    standardsQueue.length = 0;
    queueBody.innerHTML = "";
    dataRows.forEach((cells) => {
      renderQueueRow(cells[titleIndex] || "", cells[resourceIndex] || "");
    });

    uploadedCsvText = reader.result;
  };
  reader.readAsText(file);
}

uploadButton.addEventListener("click", () => uploadInput.click());
uploadInput.addEventListener("change", () => {
  if (uploadInput.files.length) {
    handleCsvUpload(uploadInput.files[0]);
  }
});

async function handleSubmitStandards() {
  if (!standardsQueue.length && !uploadedCsvText) {
    alert("Add at least one standard or upload a CSV before submitting.");
    return;
  }

  const deposited_by = fieldValue(registrantNameField);
  const depositor_email = fieldValue(registrantEmailField);
  const missing = [];
  if (!deposited_by) missing.push("Name");
  if (!depositor_email) missing.push("Email");
  if (missing.length) {
    alert(`Please fill in: ${missing.join(", ")}`);
    return;
  }

  const body = uploadedCsvText
    ? { csv_text: uploadedCsvText, deposited_by, depositor_email }
    : { standards: standardsQueue, deposited_by, depositor_email };

  const addButton = registerForm.querySelector('button[type="add"]');
  const submitButton = registerForm.querySelector('button[type="submit"]');
  addButton.disabled = true;
  submitButton.disabled = true;
  submitSpinner.hidden = false;

  try {
    const response = await fetch("/standards/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      submitSpinner.hidden = true;
      alert(`Submission failed: ${error.detail || response.status}`);
      return;
    }

    const result = await response.json();
    submitSpinner.hidden = true;
    alert(`Submitted batch ${result.batch_id}.`);

    standardsQueue.length = 0;
    queueBody.innerHTML = "";
    uploadedCsvText = null;
    uploadInput.value = "";
  } catch (error) {
    submitSpinner.hidden = true;
    alert(`Submission failed: ${error.message}`);
  } finally {
    addButton.disabled = false;
    submitButton.disabled = false;
    submitSpinner.hidden = true;
  }
}

registerForm.addEventListener("submit", (event) => {
  if (standardsTypeSelect.value !== "standards") {
    return;
  }

  event.preventDefault();
  event.stopImmediatePropagation();

  if (event.submitter.getAttribute("type") === "add") {
    handleAddStandard();
  } else {
    handleSubmitStandards();
  }
});
