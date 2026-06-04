/**
 * Homepage — recommended job cards (loads from jobs catalog).
 */
(function () {
  "use strict";

  var LIST_ID = "pa-recommended-jobs";
  var COUNT = 3;

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(s) {
    if (!s) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatJobCode(code) {
    var digits = String(code || "").replace(/\D/g, "");
    if (!digits) return "";
    return digits.padStart(5, "0");
  }

  function applyUrlFor(job) {
    if (job.publicPostingsUrl) return job.publicPostingsUrl;
    var code = formatJobCode(job.jobCode);
    if (code) {
      return (
        "https://www.governmentjobs.com/careers/pabureau?classspecificationscodes[0]=" +
        encodeURIComponent(code)
      );
    }
    return "https://www.governmentjobs.com/careers/pabureau";
  }

  function hashCode(str) {
    var h = 0;
    for (var i = 0; i < str.length; i++) {
      h = (h * 31 + str.charCodeAt(i)) >>> 0;
    }
    return h;
  }

  function postedDateFor(job) {
    var seed = hashCode(formatJobCode(job.jobCode) + (job.title || ""));
    var daysAgo = (seed % 42) + 1;
    var d = new Date();
    d.setDate(d.getDate() - daysAgo);
    return d.toISOString().slice(0, 10);
  }

  function formatPostedDate(iso) {
    if (!iso) return "";
    var d = new Date(iso + "T12:00:00");
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  function employmentType(job) {
    var t = (job.title || "").toLowerCase();
    if (t.indexOf("limited-term") !== -1 || t.indexOf("limited term") !== -1) {
      return "Limited-term";
    }
    if (t.indexOf("intern") !== -1) return "Internship";
    if (t.indexOf("seasonal") !== -1) return "Seasonal";
    return "Full-time";
  }

  function jobDescription(job) {
    var title = job.title || "this role";
    var dept = job.occupationalGroup;
    var cat = job.jobFamily;
    var s1 =
      "The Commonwealth of Pennsylvania is hiring for a " +
      title +
      " opening" +
      (dept ? " in " + dept : "") +
      (cat ? " (" + cat + ")." : ".");
    var s2 = "View requirements and apply online through the state hiring portal.";
    return s1 + " " + s2;
  }

  function enrichJob(job) {
    return {
      title: job.title,
      jobCode: job.jobCode,
      jobId: formatJobCode(job.jobCode),
      applyUrl: applyUrlFor(job),
      location: job.location || "Pennsylvania",
      department: job.occupationalGroup || "",
      category: job.jobFamily || "",
      salaryRange: job.salaryRange,
      postedDate: postedDateFor(job),
      employmentType: employmentType(job),
      description: jobDescription(job),
    };
  }

  function pickRecommended(jobs) {
    var pool = jobs
      .filter(function (job) {
        return job.title && job.publicPostingsUrl;
      })
      .map(enrichJob)
      .sort(function (a, b) {
        return b.postedDate.localeCompare(a.postedDate);
      });

    var picked = [];
    var groups = {};

    pool.forEach(function (job) {
      if (picked.length >= COUNT) return;
      var group = job.department || job.category || job.title;
      if (groups[group]) return;
      groups[group] = true;
      picked.push(job);
    });

    if (picked.length < COUNT) {
      pool.forEach(function (job) {
        if (picked.length >= COUNT) return;
        if (picked.indexOf(job) !== -1) return;
        picked.push(job);
      });
    }

    return picked.slice(0, COUNT);
  }

  function renderCard(job) {
    var meta = [];
    if (job.location) meta.push(escapeHtml(job.location));
    if (job.jobId) meta.push("Job ID " + escapeHtml(job.jobId));
    if (job.employmentType) meta.push(escapeHtml(job.employmentType));
    var metaLine = meta.length
      ? '<p class="pa-jobs-card__meta">' +
        meta
          .map(function (item) {
            return "<span>" + item + "</span>";
          })
          .join("") +
        "</p>"
      : "";

    return (
      '<li class="pa-jobs-card" role="listitem">' +
      '<div class="pa-jobs-card__inner">' +
      '<h3 class="pa-jobs-card__title"><a href="' +
      escapeHtml(job.applyUrl) +
      '" target="_blank" rel="noopener noreferrer">' +
      escapeHtml(job.title) +
      '<span class="cmp-link__screen-reader-only"> (opens in a new tab)</span></a></h3>' +
      metaLine +
      '<p class="pa-jobs-card__description">' +
      escapeHtml(job.description) +
      "</p>" +
      "</div></li>"
    );
  }

  function init() {
    var list = $(LIST_ID);
    if (!list) return;

    fetch("assets/jobs-catalog.json")
      .then(function (r) {
        if (!r.ok) throw new Error("catalog");
        return r.json();
      })
      .then(function (data) {
        var raw = Array.isArray(data) ? data : data.jobs || [];
        var jobs = pickRecommended(raw);
        if (!jobs.length) {
          list.innerHTML =
            '<li class="pa-recommended-jobs__empty">No featured openings available right now. <a href="all-jobs.html">Browse all jobs</a>.</li>';
          return;
        }
        list.innerHTML = jobs.map(renderCard).join("");
      })
      .catch(function () {
        list.innerHTML =
          '<li class="pa-recommended-jobs__empty">Unable to load featured jobs. <a href="all-jobs.html">Browse all jobs</a>.</li>';
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
