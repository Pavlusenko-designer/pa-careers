/**
 * Homepage resume match widget — modal, upload, and redirect to job search.
 */
(function () {
  "use strict";

  var MODAL_ID = "pa-resume-modal";
  var BACKDROP_ID = "pa-resume-modal-backdrop";
  var TRIGGER_ID = "pa-resume-open";
  var FOCUSABLE =
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  var modal;
  var trigger;
  var backdrop;
  var closeBtn;
  var form;
  var fileInput;
  var fileLabel;
  var consent;
  var submitBtn;
  var errorEl;
  var lastFocus;

  function $(id) {
    return document.getElementById(id);
  }

  function isOpen() {
    return modal && modal.classList.contains("is-open");
  }

  function openModal() {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    if (backdrop) backdrop.classList.add("is-open");
    document.body.classList.add("pa-resume-modal-open");
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    if (backdrop) backdrop.classList.remove("is-open");
    document.body.classList.remove("pa-resume-modal-open");
    if (errorEl) errorEl.hidden = true;
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    else if (trigger) trigger.focus();
  }

  function focusTrap(e) {
    if (!isOpen() || e.key !== "Tab") return;
    var nodes = modal.querySelectorAll(FOCUSABLE);
    if (!nodes.length) return;
    var first = nodes[0];
    var last = nodes[nodes.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function onKeyUp(e) {
    if (e.key === "Escape" && isOpen()) closeModal();
  }

  function showError(msg) {
    if (!errorEl) return;
    errorEl.textContent = msg;
    errorEl.hidden = false;
  }

  function updateFileLabel() {
    if (!fileInput || !fileLabel) return;
    var name = fileInput.files && fileInput.files[0] ? fileInput.files[0].name : "";
    fileLabel.textContent = name || "Choose a file or drag it here";
    fileLabel.classList.toggle("has-file", !!name);
  }

  function onSubmit(e) {
    e.preventDefault();
    if (!fileInput || !consent) return;
    if (!fileInput.files || !fileInput.files[0]) {
      showError("Please upload your resume to continue.");
      fileInput.focus();
      return;
    }
    if (fileInput.files[0].size > 5 * 1024 * 1024) {
      showError("Resume must be 5 MB or smaller.");
      fileInput.focus();
      return;
    }
    if (!consent.checked) {
      showError("Please accept the privacy policy and terms of use to continue.");
      consent.focus();
      return;
    }
    if (errorEl) errorEl.hidden = true;
    try {
      sessionStorage.setItem(
        "pa-resume-match",
        JSON.stringify({ name: fileInput.files[0].name, at: Date.now() })
      );
    } catch (err) {
      /* ignore storage errors */
    }
    window.location.href = "all-jobs.html?resumeMatch=1";
  }

  function init() {
    modal = $(MODAL_ID);
    trigger = $(TRIGGER_ID);
    if (!modal || !trigger) return;

    backdrop = $(BACKDROP_ID);
    closeBtn = $("pa-resume-modal-close");
    form = $("pa-resume-form");
    fileInput = $("pa-resume-file");
    fileLabel = $("pa-resume-file-label");
    consent = $("pa-resume-consent");
    submitBtn = $("pa-resume-submit");
    errorEl = $("pa-resume-error");

    closeModal();

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      openModal();
    });
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (backdrop) backdrop.addEventListener("click", closeModal);
    modal.addEventListener("keydown", focusTrap);
    document.addEventListener("keyup", onKeyUp);
    if (fileInput) fileInput.addEventListener("change", updateFileLabel);
    if (form) form.addEventListener("submit", onSubmit);
    if (submitBtn && consent) {
      consent.addEventListener("change", function () {
        submitBtn.disabled = !consent.checked;
      });
      submitBtn.disabled = !consent.checked;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
