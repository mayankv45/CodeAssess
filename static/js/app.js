/* =========================================================
   FLASH MESSAGE AUTO-HIDE
   ========================================================= */

setTimeout(() => {
  document.querySelectorAll(".flash").forEach((element) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(-5px)";

    setTimeout(() => {
      element.remove();
    }, 350);
  });
}, 3500);


/* =========================================================
   DASHBOARD / SIDEBAR TOGGLE
   ========================================================= */

(() => {
  const shell = document.querySelector(".app-shell");
  const topButton = document.getElementById("sidebarToggleTop");
  const floatingButton = document.getElementById("sidebarToggle");

  // Stop if the current page does not contain the application layout.
  if (!shell) {
    return;
  }

  // Restore the saved sidebar state.
  const savedState = localStorage.getItem(
    "codeassess-sidebar-collapsed"
  );

  if (savedState === "true") {
    shell.classList.add("sidebar-collapsed");
    document.body.classList.add("sidebar-collapsed");
  }

  // Update accessibility labels for both toggle buttons.
  const updateLabels = () => {
    const isCollapsed = shell.classList.contains("sidebar-collapsed");

    const label = isCollapsed
      ? "Show dashboard panel"
      : "Hide dashboard panel";

    [topButton, floatingButton].forEach((button) => {
      if (!button) {
        return;
      }

      button.setAttribute("aria-label", label);
      button.setAttribute("title", label);
      button.textContent = "☰";
    });
  };

  // Toggle the dashboard sidebar.
  const toggleSidebar = () => {
    shell.classList.toggle("sidebar-collapsed");

    document.body.classList.toggle(
      "sidebar-collapsed",
      shell.classList.contains("sidebar-collapsed")
    );

    // Save the current state for future page loads.
    localStorage.setItem(
      "codeassess-sidebar-collapsed",
      shell.classList.contains("sidebar-collapsed")
        ? "true"
        : "false"
    );

    updateLabels();
  };

  // Attach click events to both sidebar buttons.
  topButton?.addEventListener("click", toggleSidebar);
  floatingButton?.addEventListener("click", toggleSidebar);

  // Set the initial button state.
  updateLabels();
})();