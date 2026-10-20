function getAnimationDurationMs(dialogElement) {
  var animationDurationString = dialogElement.style.animationDuration || "";
  if (animationDurationString.endsWith("ms")) {
    return parseFloat(animationDurationString);
  }
  if (animationDurationString.endsWith("s")) {
    return parseFloat(animationDurationString) * 1000;
  }
  return 200;
}

function closeDialog(dialogElement, backdropElement, animationDuration) {
  document.body.classList.remove("overflow-hidden");
  dialogElement.dataset.state = "closed";
  backdropElement.dataset.state = "closed";

  setTimeout(function () {
    backdropElement.classList.add("hidden");
    dialogElement.close();
  }, animationDuration - 10);
}

function openDialog(dialogElement, backdropElement) {
  dialogElement.showModal();
  document.body.classList.add("overflow-hidden");
  backdropElement.classList.remove("hidden");
  backdropElement.dataset.state = "open";
  dialogElement.dataset.state = "open";
}

function setupSearchDialog() {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  var searchDialog = document.querySelector("#docs-search-dialog");
  if (!searchDialog) return;

  var dialogElement = searchDialog.querySelector("dialog");
  var backdropElement = searchDialog.querySelector(".starwind-dialog-backdrop");
  var triggerElement = searchDialog.querySelector(".starwind-dialog-trigger");
  if (!dialogElement || !backdropElement || !triggerElement) return;

  if (triggerElement.hasAttribute("data-search-dialog-ready")) return;
  triggerElement.setAttribute("data-search-dialog-ready", "true");

  var animationDuration = getAnimationDurationMs(dialogElement);
  var actualTrigger = triggerElement;
  if (triggerElement.hasAttribute("data-as-child") && triggerElement.firstElementChild) {
    actualTrigger = triggerElement.firstElementChild;
  }

  var firstHeading = dialogElement.querySelector("h1, h2, h3, h4, h5, h6");
  if (firstHeading) {
    firstHeading.id = "starwind-dialog0-heading";
    dialogElement.setAttribute("aria-labelledby", firstHeading.id);
  }

  var tempCloseButtons = searchDialog.querySelectorAll(".starwind-dialog-close");
  tempCloseButtons.forEach(function (button) {
    if (button.hasAttribute("data-as-child") && button.firstElementChild) {
      var childElement = button.firstElementChild;
      childElement.classList.add("starwind-dialog-close");
      if (button.parentNode) {
        button.parentNode.replaceChild(childElement, button);
      }
    }
  });

  var closeButtons = searchDialog.querySelectorAll(".starwind-dialog-close");

  actualTrigger.addEventListener("click", function () {
    openDialog(dialogElement, backdropElement);
  });

  closeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      closeDialog(dialogElement, backdropElement, animationDuration);
    });
  });

  dialogElement.addEventListener("click", function (event) {
    var dialogDimensions = dialogElement.getBoundingClientRect();
    var clickedInDialog =
      event.clientX >= dialogDimensions.left &&
      event.clientX <= dialogDimensions.right &&
      event.clientY >= dialogDimensions.top &&
      event.clientY <= dialogDimensions.bottom;

    if (!clickedInDialog) {
      closeDialog(dialogElement, backdropElement, animationDuration);
    }
  });

  dialogElement.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeDialog(dialogElement, backdropElement, animationDuration);
    }
  });

  window.addEventListener("keydown", function (event) {
    var activeElement = document.activeElement;
    var isInput =
      activeElement instanceof HTMLElement &&
      (["input", "select", "textarea"].includes(activeElement.tagName.toLowerCase()) ||
        activeElement.isContentEditable);

    if ((event.metaKey === true || event.ctrlKey === true) && event.key === "k") {
      if (dialogElement.dataset.state === "open") {
        closeDialog(dialogElement, backdropElement, animationDuration);
      } else {
        openDialog(dialogElement, backdropElement);
      }
      event.preventDefault();
    } else if (event.key === "/" && dialogElement.dataset.state !== "open" && !isInput) {
      openDialog(dialogElement, backdropElement);
      event.preventDefault();
    }
  });

  var forms = dialogElement.querySelectorAll("form");
  forms.forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (form.method === "dialog") {
        event.preventDefault();
        closeDialog(dialogElement, backdropElement, animationDuration);
      }
    });
  });
}

function setupPagefindSearch() {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  var searchElement = document.querySelector("#search");
  if (!searchElement || searchElement.hasChildNodes()) return;

  var onIdle = window.requestIdleCallback || function (callback) {
    return setTimeout(callback, 1);
  };

  onIdle(function () {
    import("/pagefind/pagefind-ui.js").then(function (module) {
      var PagefindUI = module.PagefindUI;
      new PagefindUI({
        element: "#search",
        showImages: false,
        showSubResults: true,
      });
    });
  });
}

function setupGalaxySearch() {
  setupSearchDialog();
  setupPagefindSearch();
}

if (typeof window !== "undefined" && typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupGalaxySearch, { once: true });
  } else {
    setupGalaxySearch();
  }

  document.addEventListener("astro:after-swap", setupGalaxySearch);
}
