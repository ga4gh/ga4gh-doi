const doiTypeSelect = document.getElementById("doi-type-select");

if (doiTypeSelect) {
  doiTypeSelect.addEventListener("change", () => {
    document.querySelectorAll(".doi-fields").forEach((section) => {
      const isSelected = section.dataset.doiType === doiTypeSelect.value;
      section.hidden = !isSelected;
      section.querySelectorAll("input, textarea, select").forEach((field) => {
        field.disabled = !isSelected;
      });
    });
    document.querySelectorAll("[data-queue-for]").forEach((section) => {
      section.hidden = section.dataset.queueFor !== doiTypeSelect.value;
    });
  });
}
