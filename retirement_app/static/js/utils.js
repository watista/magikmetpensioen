document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("birthDateInput");

  input.addEventListener("input", function () {
    let value = input.value.replace(/\D/g, "");  // remove non-digits
    if (value.length > 8) value = value.slice(0, 8);

    let formatted = "";
    if (value.length >= 2) {
      formatted += value.slice(0, 2);
      if (value.length >= 4) {
        formatted += "-" + value.slice(2, 4);
        if (value.length > 4) {
          formatted += "-" + value.slice(4);
        }
      } else {
        formatted += "-" + value.slice(2);
      }
    } else {
      formatted += value;
    }

    input.value = formatted;
  });
});
