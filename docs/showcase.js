(() => {
  "use strict";
  const labels = {
    overview: "Overview", evidence: "Evidence graph", pipeline: "Analysis pipeline",
    models: "Models & MLOps", cases: "Case review", deployment: "Deployment"
  };
  const buttons = [...document.querySelectorAll("[data-view]")];
  function show(view) {
    if (!Object.prototype.hasOwnProperty.call(labels, view)) return;
    for (const b of buttons) {
      const active = b.dataset.view === view;
      b.classList.toggle("active", active);
      b.setAttribute("aria-current", active ? "page" : "false");
    }
    for (const section of document.querySelectorAll(".view")) {
      section.classList.toggle("active", section.id === "view-" + view);
    }
    document.getElementById("breadcrumb").textContent = labels[view];
    if (window.location.hash !== "#" + view) history.replaceState(null, "", "#" + view);
    window.scrollTo({top: 0, behavior: "instant"});
  }
  for (const button of buttons) button.addEventListener("click", () => show(button.dataset.view));
  const modelCheck = document.getElementById("model-check");
  modelCheck.addEventListener("click", () => {
    document.getElementById("model-state").textContent =
      "MODEL_NOT_CONNECTED — GitHub Pages cannot access local trained weights. " +
      "Run the CLARION local API and pass a verified artifact; never substitute an invented .pkl or .h5.";
  });
  show(location.hash.slice(1) || "overview");
  window.addEventListener("hashchange", () => show(location.hash.slice(1) || "overview"));
})();