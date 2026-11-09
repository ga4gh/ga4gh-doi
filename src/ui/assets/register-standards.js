const registerForm = document.querySelector('form[data-form="register"]');
const standardsTypeSelect = document.getElementById("doi-type-select");
const standardsSection = document.querySelector('.doi-fields[data-doi-type="standards"]');
const registrantNameField = document.querySelector('[name="registrant_name"]');
const registrantEmailField = document.querySelector('[name="registrant_email"]');
const queueBody = document.querySelector("#standards-queue-table tbody");
const submitSpinner = document.getElementById("register-submit-spinner");
const uploadButton = document.getElementById("standards-upload-btn");
const uploadInput = document.getElementById("standards-upload-input");
const contributorRowsContainer = document.getElementById("standards-contributor-rows");
const contributorAddButton = document.getElementById("standards-contributor-add");
const contributorRemoveButton = document.getElementById("standards-contributor-remove");
const stdDesignatorPrefix = document.getElementById("std-designator-prefix");

const standardsQueue = [];
let uploadedCsvText = null;

contributorAddButton.addEventListener("click", () => addContributorRow(contributorRowsContainer));
contributorRemoveButton.addEventListener("click", () => removeLastContributorRow(contributorRowsContainer));

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
  values.contributors = collectContributors(contributorRowsContainer);

  const designatorPrefix = stdDesignatorPrefix.value;
  if (!designatorPrefix) {
    missing.push("std_designator (originating group)");
  } else if (values.std_designator) {
    values.std_designator = `${designatorPrefix}_${values.std_designator}`;
  }

  return { values, missing };
}

function resetStandardsFields() {
  standardsSection.querySelectorAll("[data-sample]").forEach(armSampleField);
  contributorRowsContainer.innerHTML = "";
  stdDesignatorPrefix.value = "";
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

// Mirrors the register form's own constraints (required fields, type="url",
// type="email") so an uploaded CSV is held to the same rules as manual entry.
const STANDARDS_CSV_VALIDATION = {
  requiredFields: [
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
  ],
  dateFields: [{ month: "<month>", day: "<day>", year: "<year>", label: "Publish Date" }],
  urlFields: [["<resource>", "Resource URL"]],
  emailFields: [["<email_address>", "Email Address"]],
  numberFields: [["<item_number>", "Item Number"]],
  jsonListFields: [["<contributors>", "Contributors"]],
};

function handleCsvUpload(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const rows = parseCsv(reader.result);
    if (!rows.length) {
      return;
    }

    const [header, ...dataRows] = rows;
    const errors = validateCsvRows(header, dataRows, STANDARDS_CSV_VALIDATION);
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
