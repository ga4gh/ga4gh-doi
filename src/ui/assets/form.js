function armSampleField(field) {
  field.value = field.dataset.sample;
  field.classList.add("is-sample");

  field.addEventListener(
    "focus",
    () => {
      if (field.classList.contains("is-sample")) {
        field.value = "";
        field.classList.remove("is-sample");
      }
    },
    { once: true }
  );
}

document.querySelectorAll("[data-sample]").forEach((field) => {
  armSampleField(field);
  field.addEventListener("input", () => {
    field.classList.remove("is-sample");
  });
});

document.querySelectorAll('input[type="date"], input[type="datetime-local"], input[type="time"]').forEach((field) => {
  field.addEventListener("change", () => {
    field.blur();
  });
});

document.querySelectorAll(".info-icon").forEach((icon) => {
  icon.addEventListener("click", (event) => {
    event.preventDefault();
    const wasActive = icon.classList.contains("is-active");
    document.querySelectorAll(".info-icon.is-active").forEach((other) => other.classList.remove("is-active"));
    icon.classList.toggle("is-active", !wasActive);
  });
});

document.addEventListener("click", (event) => {
  if (!event.target.classList.contains("info-icon")) {
    document.querySelectorAll(".info-icon.is-active").forEach((icon) => icon.classList.remove("is-active"));
  }
});

document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const data = new FormData(form);
    form.querySelectorAll("[data-sample].is-sample:not(:disabled)").forEach((field) => {
      data.set(field.name, "");
    });

    console.log(`Submitted form: ${form.dataset.form}`, Object.fromEntries(data.entries()));
  });
});
