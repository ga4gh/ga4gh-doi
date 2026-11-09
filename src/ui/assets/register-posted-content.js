const postedContentRegisterForm = document.querySelector('form[data-form="register"]');
const postedContentTypeSelect = document.getElementById("doi-type-select");
const postedContentSection = document.querySelector('.doi-fields[data-doi-type="posted-content"]');
const postedContentTypeField = postedContentSection.querySelector('[name="posted_content_type"]');
const postedContentRegistrantNameField = document.querySelector('[name="registrant_name"]');
const postedContentRegistrantEmailField = document.querySelector('[name="registrant_email"]');
const postedContentQueueBody = document.querySelector("#posted-content-queue-table tbody");
const postedContentSubmitSpinner = document.getElementById("register-submit-spinner");
const postedContentUploadButton = document.getElementById("posted-content-upload-btn");
const postedContentUploadInput = document.getElementById("posted-content-upload-input");
const postedContentContributorRows = document.getElementById("posted-content-contributor-rows");
const postedContentContributorAdd = document.getElementById("posted-content-contributor-add");
const postedContentContributorRemove = document.getElementById("posted-content-contributor-remove");
const postedContentCitationRows = document.getElementById("posted-content-citation-rows");
const postedContentCitationAdd = document.getElementById("posted-content-citation-add");
const postedContentCitationRemove = document.getElementById("posted-content-citation-remove");

const postedContentQueue = [];
let uploadedPostedContentCsvText = null;

// Crossref's schema only strictly requires a surname, but GA4GH's own policy for
// posted content requires first name, last name, and affiliation for every contributor.
const POSTED_CONTENT_REQUIRED_CONTRIBUTOR_FIELDS = ["first_name", "last_name", "affiliation"];

postedContentContributorAdd.addEventListener("click", () =>
  addContributorRow(postedContentContributorRows, POSTED_CONTENT_REQUIRED_CONTRIBUTOR_FIELDS)
);
postedContentContributorRemove.addEventListener("click", () => removeLastContributorRow(postedContentContributorRows));

function addCitationRow(container) {
  const row = document.createElement("div");
  row.className = "contributor-row";
  row.innerHTML = `
    <label>DOI <input type="text" class="citation-doi" /></label>
    <label>Citation Text <input type="text" class="citation-text" /></label>
  `;
  container.appendChild(row);
}

function removeLastCitationRow(container) {
  container.lastElementChild?.remove();
}

function collectCitations(container) {
  return Array.from(container.children)
    .map((row, index) => ({
      key: `ref${index + 1}`,
      doi: row.querySelector(".citation-doi").value.trim(),
      unstructured_citation: row.querySelector(".citation-text").value.trim(),
    }))
    .filter((citation) => citation.doi || citation.unstructured_citation);
}

postedContentCitationAdd.addEventListener("click", () => addCitationRow(postedContentCitationRows));
postedContentCitationRemove.addEventListener("click", () => removeLastCitationRow(postedContentCitationRows));

function buildInstitution(values) {
  const name = values.institution_name || "";
  const ror = values.institution_ror || "";
  const acronym = values.institution_acronym || "";
  const place = values.institution_place || "";
  const department = values.institution_department || "";

  delete values.institution_name;
  delete values.institution_ror;
  delete values.institution_acronym;
  delete values.institution_place;
  delete values.institution_department;

  if (!name && !ror && !acronym && !place && !department) {
    return {};
  }
  return { name, ids: ror ? [{ type: "ror", value: ror }] : [], acronym, place, department };
}

function collectPostedContentRow() {
  const values = {};
  const missing = [];

  postedContentSection.querySelectorAll("[data-sample]").forEach((field) => {
    const value = fieldValue(field);
    if (!value && field.required) {
      missing.push(field.name);
    }
    values[field.name] = value;
  });

  values.posted_content_type = postedContentTypeField.value || "preprint";
  values.institution = buildInstitution(values);
  // Crossref allows an institution with no name as long as it has an ID (e.g. ROR)
  // instead, but requires one or the other whenever any institution info is given.
  if (Object.keys(values.institution).length && !values.institution.name && !values.institution.ids.length) {
    missing.push("Institution Name or Institution ROR");
  }

  values.contributors = collectContributors(postedContentContributorRows).map((contributor) => ({
    first_name: contributor.first_name,
    last_name: contributor.last_name,
    orcid: contributor.orcid,
    affiliations: contributor.affiliation ? [{ name: contributor.affiliation }] : [],
  }));
  if (!values.contributors.length) {
    missing.push("Contributors (at least one)");
  }
  missing.push(...validateContributorRows(postedContentContributorRows, POSTED_CONTENT_REQUIRED_CONTRIBUTOR_FIELDS));

  values.citations = collectCitations(postedContentCitationRows);

  return { values, missing };
}

function resetPostedContentFields() {
  postedContentSection.querySelectorAll("[data-sample]").forEach(armSampleField);
  postedContentContributorRows.innerHTML = "";
  postedContentCitationRows.innerHTML = "";
  postedContentTypeField.value = "preprint";
}

function renderPostedContentQueueRow(title, resourceUrl) {
  const row = document.createElement("tr");
  const titleCell = document.createElement("td");
  titleCell.textContent = title;
  const resourceCell = document.createElement("td");
  resourceCell.textContent = resourceUrl;
  row.append(titleCell, resourceCell);
  postedContentQueueBody.appendChild(row);
}

function handleAddPostedContent() {
  const { values, missing } = collectPostedContentRow();
  if (missing.length) {
    alert(`Please fill in: ${missing.join(", ")}`);
    return;
  }

  uploadedPostedContentCsvText = null;
  postedContentQueue.push(values);
  renderPostedContentQueueRow(values.title, values.resource_url);
  resetPostedContentFields();
}

// Mirrors the register form's own constraints so an uploaded CSV is held to the same rules as manual entry.
const POSTED_CONTENT_CSV_VALIDATION = {
  requiredFields: [
    ["<title>", "Title"],
    ["<resource>", "Resource URL"],
    ["<registrant>", "Registrant"],
    ["<email_address>", "Email Address"],
  ],
  dateFields: [
    { month: "<posted_month>", day: "<posted_day>", year: "<posted_year>", label: "Posted Date" },
    { month: "<acceptance_month>", day: "<acceptance_day>", year: "<acceptance_year>", label: "Acceptance Date", required: false },
  ],
  urlFields: [["<resource>", "Resource URL"]],
  emailFields: [["<email_address>", "Email Address"]],
  nonEmptyJsonListFields: [["<contributors>", "Contributors"]],
  jsonListFields: [["<citations>", "Citations"]],
  customValidators: [
    // Each contributor needs first/last/affiliation (see POSTED_CONTENT_REQUIRED_CONTRIBUTOR_FIELDS above).
    (get) => {
      let contributors;
      try {
        contributors = JSON.parse(get("<contributors>") || "[]");
      } catch {
        return null; // already reported by nonEmptyJsonListFields
      }
      if (!Array.isArray(contributors)) return null;

      const problems = contributors
        .map((contributor, index) => {
          const missingFields = POSTED_CONTENT_REQUIRED_CONTRIBUTOR_FIELDS.filter((field) => !contributor?.[field]);
          return missingFields.length ? `Contributor ${index + 1} missing ${missingFields.join(", ")}` : null;
        })
        .filter(Boolean);
      return problems.length ? problems.join("; ") : null;
    },
    // Institution needs a name or an ID (e.g. ROR) whenever any institution info is given.
    (get) => {
      let institution;
      try {
        institution = get("<institution>") ? JSON.parse(get("<institution>")) : {};
      } catch {
        return "Institution must be a valid object";
      }
      if (!institution || typeof institution !== "object") return null;

      const hasAnyInfo = institution.name || institution.acronym || institution.place || institution.department
        || (Array.isArray(institution.ids) && institution.ids.length);
      const hasNameOrId = institution.name || (Array.isArray(institution.ids) && institution.ids.length);
      if (hasAnyInfo && !hasNameOrId) {
        return "Institution Name or an Institution ID (e.g. ROR) is required when institution info is provided";
      }
      return null;
    },
  ],
};

function handlePostedContentCsvUpload(file) {
  const reader = new FileReader();
  reader.onload = () => {
    const rows = parseCsv(reader.result);
    if (!rows.length) {
      return;
    }

    const [header, ...dataRows] = rows;
    const errors = validateCsvRows(header, dataRows, POSTED_CONTENT_CSV_VALIDATION);
    if (errors.length) {
      alert(`CSV does not pass validation:\n\n${errors.join("\n")}`);
      postedContentUploadInput.value = "";
      return;
    }

    const titleIndex = header.indexOf("<title>");
    const resourceIndex = header.indexOf("<resource>");

    postedContentQueue.length = 0;
    postedContentQueueBody.innerHTML = "";
    dataRows.forEach((cells) => {
      renderPostedContentQueueRow(cells[titleIndex] || "", cells[resourceIndex] || "");
    });

    uploadedPostedContentCsvText = reader.result;
  };
  reader.readAsText(file);
}

postedContentUploadButton.addEventListener("click", () => postedContentUploadInput.click());
postedContentUploadInput.addEventListener("change", () => {
  if (postedContentUploadInput.files.length) {
    handlePostedContentCsvUpload(postedContentUploadInput.files[0]);
  }
});

async function handleSubmitPostedContent() {
  if (!postedContentQueue.length && !uploadedPostedContentCsvText) {
    alert("Add at least one posted content item or upload a CSV before submitting.");
    return;
  }

  const deposited_by = fieldValue(postedContentRegistrantNameField);
  const depositor_email = fieldValue(postedContentRegistrantEmailField);
  const missing = [];
  if (!deposited_by) missing.push("Name");
  if (!depositor_email) missing.push("Email");
  if (missing.length) {
    alert(`Please fill in: ${missing.join(", ")}`);
    return;
  }

  const body = uploadedPostedContentCsvText
    ? { csv_text: uploadedPostedContentCsvText, deposited_by, depositor_email }
    : { posted_content: postedContentQueue, deposited_by, depositor_email };

  const addButton = postedContentRegisterForm.querySelector('button[type="add"]');
  const submitButton = postedContentRegisterForm.querySelector('button[type="submit"]');
  addButton.disabled = true;
  submitButton.disabled = true;
  postedContentSubmitSpinner.hidden = false;

  try {
    const response = await fetch("/posted-content/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      alert(`Submission failed: ${error.detail || response.status}`);
      return;
    }

    const result = await response.json();
    alert(`Submitted batch ${result.batch_id}.`);

    postedContentQueue.length = 0;
    postedContentQueueBody.innerHTML = "";
    uploadedPostedContentCsvText = null;
    postedContentUploadInput.value = "";
  } catch (error) {
    alert(`Submission failed: ${error.message}`);
  } finally {
    addButton.disabled = false;
    submitButton.disabled = false;
    postedContentSubmitSpinner.hidden = true;
  }
}

postedContentRegisterForm.addEventListener("submit", (event) => {
  if (postedContentTypeSelect.value !== "posted-content") {
    return;
  }

  event.preventDefault();
  event.stopImmediatePropagation();

  if (event.submitter.getAttribute("type") === "add") {
    handleAddPostedContent();
  } else {
    handleSubmitPostedContent();
  }
});
