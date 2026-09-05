document.addEventListener("DOMContentLoaded", () => {
  // Surah selector navigation
  const surahSelect = document.getElementById("surah");
  if (surahSelect) {
    surahSelect.addEventListener("change", () => {
      location.href = "/surah/" + surahSelect.value;
    });
  }

  // Scroll the selected verse into view on the surah page
  const selectedVerse = document.querySelector(".verse.selected-verse");
  if (selectedVerse) {
    selectedVerse.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // Copy verse text to the clipboard
  document.querySelectorAll(".copy-verse").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.dataset.copyText || "";
      const original = button.textContent;

      try {
        await navigator.clipboard.writeText(text);
        copied(button, original);
      } catch (error) {
        // Clipboard API may be unavailable outside a secure context.
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();

        try {
          document.execCommand("copy");
          copied(button, original);
        } finally {
          area.remove();
        }
      }
    });
  });

  // Auto-size the passage search textarea
  const textareas = document.querySelectorAll(".passage-form textarea");
  textareas.forEach((area) => {
    const resize = () => {
      area.style.height = "auto";
      area.style.height = area.scrollHeight + "px";
    };
    area.addEventListener("input", resize);
    resize();
  });

  // Press "/" to focus the main search box
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "/" &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.altKey &&
      document.activeElement.tagName !== "INPUT" &&
      document.activeElement.tagName !== "TEXTAREA"
    ) {
      const searchInput = document.querySelector('.search-form input[name="q"]');
      if (searchInput) {
        event.preventDefault();
        searchInput.focus();
      }
    }
  });

  function copied(button, original) {
    const label = original || "نسخ الآية";
    button.textContent = "تم النسخ ✓";
    button.classList.add("copied");
    setTimeout(() => {
      button.textContent = label;
      button.classList.remove("copied");
    }, 1500);
  }
});