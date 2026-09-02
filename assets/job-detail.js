(function () {
  "use strict";

  var title = new URLSearchParams(window.location.search).get("job") || "Senior Operations Manager";
  var lastFocus = null;
  var toastTimer = null;
  var matchCompleted = false;
  var selectedResumeName = "Not attached";
  var pathwayEvidence = {
    conventionalFitGrade: "C",
    fitScore: 88,
    careerPathwayFit: "HIGH",
    sourceOccupation: "Operations Program Lead",
    targetOccupation: title,
    transitionCount: 1240,
    paWorkersWithoutFourYearDegree: 18400,
    degreeUsedInScoring: false
  };

  document.querySelectorAll("[data-job-title]").forEach(function (el) {
    el.textContent = title;
  });
  document.title = title + " | Careers";
  var activeCrumb = document.querySelector(".cmp-breadcrumb__item--active [itemprop='name']");
  if (activeCrumb) activeCrumb.textContent = title;

  function showToast(message) {
    var toast = document.getElementById("pa-jd-toast");
    if (!toast) return;
    toast.querySelector("span").textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () { toast.classList.remove("is-visible"); }, 2400);
  }

  document.querySelectorAll("[data-jd-tab]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var target = tab.getAttribute("data-jd-tab");
      document.querySelectorAll("[data-jd-tab]").forEach(function (item) {
        var selected = item === tab;
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-selected", selected ? "true" : "false");
      });
      document.querySelectorAll("[data-jd-panel]").forEach(function (panel) {
        var selected = panel.getAttribute("data-jd-panel") === target;
        panel.hidden = !selected;
        panel.classList.toggle("is-active", selected);
      });
    });
  });

  var readMore = document.getElementById("pa-jd-read-more");
  var description = document.getElementById("pa-jd-description-body");
  if (readMore && description) {
    readMore.addEventListener("click", function () {
      var expanded = readMore.getAttribute("aria-expanded") === "true";
      readMore.setAttribute("aria-expanded", expanded ? "false" : "true");
      description.classList.toggle("is-collapsed", expanded);
      readMore.querySelector("span").textContent = expanded ? "Read full job description" : "Show less";
      readMore.querySelector(".ri-arrow-down-s-line, .ri-arrow-up-s-line").className = expanded ? "ri-arrow-down-s-line" : "ri-arrow-up-s-line";
    });
  }

  var share = document.getElementById("pa-jd-share");
  var shareMenu = document.getElementById("pa-jd-share-menu");
  if (share && shareMenu) {
    share.addEventListener("click", function () {
      var open = shareMenu.hidden;
      shareMenu.hidden = !open;
      share.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  document.querySelector("[data-copy-job-link]").addEventListener("click", function () {
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(window.location.href);
    shareMenu.hidden = true;
    share.setAttribute("aria-expanded", "false");
    showToast("Job link copied");
  });
  document.querySelector("[data-share-email]").addEventListener("click", function () {
    window.location.href = "mailto:?subject=" + encodeURIComponent(title + " at the Commonwealth of Pennsylvania") + "&body=" + encodeURIComponent(window.location.href);
  });

  var save = document.getElementById("pa-jd-save");
  save.addEventListener("click", function () {
    var saved = save.getAttribute("aria-pressed") === "true";
    save.setAttribute("aria-pressed", saved ? "false" : "true");
    save.querySelector("i").className = saved ? "ri-heart-line" : "ri-heart-fill";
    save.querySelector("span").textContent = saved ? "Save job" : "Saved";
    showToast(saved ? "Job removed from saved jobs" : "Job saved");
  });

  var modal = document.getElementById("pa-jd-apply-modal");
  var applicationResume = modal.querySelector("[data-application-resume]");
  var applicationFit = modal.querySelector("[data-application-fit]");
  var applicationPathway = modal.querySelector("[data-application-pathway]");
  var applicationPathwayNote = modal.querySelector("[data-apply-pathway-note]");

  function updateApplicationSummary() {
    applicationResume.textContent = matchCompleted ? selectedResumeName : "Not attached";
    applicationFit.textContent = matchCompleted ? pathwayEvidence.fitScore + "% · Strong match" : "Not calculated";
    applicationPathway.textContent = matchCompleted ? pathwayEvidence.careerPathwayFit + " fit" : "Available after resume match";
    applicationPathwayNote.hidden = !matchCompleted;
  }

  function openApply() {
    lastFocus = document.activeElement;
    updateApplicationSummary();
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    modal.querySelector(".pa-jd-modal__close").focus();
  }
  function closeApply() {
    modal.hidden = true;
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  document.querySelectorAll("[data-open-apply]").forEach(function (button) { button.addEventListener("click", openApply); });
  modal.querySelector(".pa-jd-modal__close").addEventListener("click", closeApply);
  modal.addEventListener("click", function (event) { if (event.target === modal) closeApply(); });
  modal.querySelector("[data-confirm-apply]").addEventListener("click", function () {
    var payload = {
      type: "prototype-application-submitted",
      candidate: "Alex Jordan",
      job: title,
      conventionalFitGrade: pathwayEvidence.conventionalFitGrade,
      fitScore: pathwayEvidence.fitScore,
      careerPathwayFit: pathwayEvidence.careerPathwayFit,
      sourceOccupation: pathwayEvidence.sourceOccupation,
      targetOccupation: pathwayEvidence.targetOccupation,
      transitionCount: pathwayEvidence.transitionCount,
      paWorkersWithoutFourYearDegree: pathwayEvidence.paWorkersWithoutFourYearDegree,
      degreeUsedInScoring: pathwayEvidence.degreeUsedInScoring,
      matchCompleted: matchCompleted,
      resumeName: matchCompleted ? selectedResumeName : null
    };
    closeApply();
    showToast("Application submitted. A confirmation email is on its way.");
    try { window.localStorage.setItem("prototype-application-submitted", JSON.stringify({ timestamp: Date.now(), payload: payload })); } catch (error) {}
    if ("BroadcastChannel" in window) {
      var channel = new BroadcastChannel("opportunity-prototype");
      channel.postMessage(payload);
      channel.close();
    }
    if (window.opener && !window.opener.closed) {
      window.opener.postMessage(payload, window.location.origin);
      window.opener.focus();
    }
    window.setTimeout(function () {
      window.close();
      window.setTimeout(function () { window.location.href = "/?candidate=alex-jordan"; }, 150);
    }, 850);
  });

  var matchModal = document.getElementById("pa-jd-match-modal");
  var matchUploadView = matchModal.querySelector("[data-match-upload-view]");
  var matchResultView = matchModal.querySelector("[data-match-result-view]");
  var resumeInput = document.getElementById("pa-jd-resume-file");
  var resumeDrop = matchModal.querySelector(".pa-jd-resume-drop");
  var resumeFileName = matchModal.querySelector("[data-resume-file-name]");
  var matchStatus = matchModal.querySelector("[data-match-status]");
  var analyzeButton = matchModal.querySelector("[data-run-match]");
  var matchTimer = null;
  var lastMatchFocus = null;

  function openMatch() {
    lastMatchFocus = document.activeElement;
    matchModal.hidden = false;
    document.body.style.overflow = "hidden";
    matchModal.querySelector("[data-close-match]").focus();
  }

  function closeMatch() {
    matchModal.hidden = true;
    document.body.style.overflow = "";
    if (lastMatchFocus) lastMatchFocus.focus();
  }

  function setResume(file) {
    var allowed = /\.(pdf|doc|docx)$/i.test(file.name);
    if (!allowed || file.size > 5 * 1024 * 1024) {
      resumeFileName.textContent = "Choose a resume";
      matchStatus.textContent = allowed ? "That file is larger than 5 MB." : "Choose a PDF, DOC, or DOCX file.";
      analyzeButton.disabled = true;
      return;
    }
    selectedResumeName = file.name;
    resumeFileName.textContent = file.name;
    matchStatus.textContent = "Resume ready to analyze.";
    analyzeButton.disabled = false;
  }

  document.querySelector("[data-open-match]").addEventListener("click", openMatch);
  matchModal.querySelectorAll("[data-close-match]").forEach(function (button) { button.addEventListener("click", closeMatch); });
  matchModal.addEventListener("click", function (event) { if (event.target === matchModal) closeMatch(); });
  resumeInput.addEventListener("change", function () { if (resumeInput.files[0]) setResume(resumeInput.files[0]); });
  matchModal.querySelector("[data-use-sample-resume]").addEventListener("click", function () {
    setResume({ name: "alex-jordan-resume.pdf", size: 184000 });
  });
  ["dragenter", "dragover"].forEach(function (name) {
    resumeDrop.addEventListener(name, function (event) { event.preventDefault(); resumeDrop.classList.add("is-dragging"); });
  });
  ["dragleave", "drop"].forEach(function (name) {
    resumeDrop.addEventListener(name, function (event) { event.preventDefault(); resumeDrop.classList.remove("is-dragging"); });
  });
  resumeDrop.addEventListener("drop", function (event) {
    var file = event.dataTransfer.files[0];
    if (file) setResume(file);
  });
  analyzeButton.addEventListener("click", function () {
    analyzeButton.disabled = true;
    analyzeButton.classList.add("is-loading");
    analyzeButton.querySelector("i").className = "ri-loader-4-line";
    analyzeButton.querySelector("span").textContent = "Analyzing resume…";
    matchStatus.textContent = "Comparing your experience with the job requirements.";
    window.clearTimeout(matchTimer);
    matchTimer = window.setTimeout(function () {
      matchCompleted = true;
      matchUploadView.hidden = true;
      matchResultView.hidden = false;
      matchResultView.querySelector("[data-match-result-title]").focus();
    }, 1100);
  });
  matchModal.querySelector("[data-match-apply]").addEventListener("click", function () {
    closeMatch();
    openApply();
  });
  modal.querySelector("[data-apply-check-match]").addEventListener("click", function () {
    closeApply();
    openMatch();
  });

  document.querySelectorAll(".pa-jd-recommendation-grid article button").forEach(function (button) {
    button.addEventListener("click", function () {
      var icon = button.querySelector("i");
      var saved = icon.classList.contains("ri-heart-fill");
      icon.className = saved ? "ri-heart-line" : "ri-heart-fill";
      showToast(saved ? "Job removed from saved jobs" : "Similar job saved");
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      if (!matchModal.hidden) closeMatch();
      else if (!modal.hidden) closeApply();
      if (!shareMenu.hidden) {
        shareMenu.hidden = true;
        share.setAttribute("aria-expanded", "false");
      }
    }
  });
})();
