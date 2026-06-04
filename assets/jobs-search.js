(function () {
  "use strict";

  var PAGE_SIZE = 10;
  var FACET_LIMIT = 12;

  var state = {
    jobs: [],
    filtered: [],
    keyword: "",
    profileMatch: false,
    facets: {
      occupationalGroup: new Set(),
      jobFamily: new Set(),
      payScaleType: new Set(),
      bargainingUnit: new Set(),
    },
    sort: "relevance",
    page: 1,
  };

  var els = {};

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

  function norm(s) {
    return (s || "").toLowerCase().trim();
  }

  function formatJobCode(code) {
    var digits = String(code || "").replace(/\D/g, "");
    if (!digits) return "";
    return digits.padStart(5, "0");
  }

  function applyUrlFor(job) {
    if (job.applyUrl) return job.applyUrl;
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

  function profileScore(job) {
    var seed = "profile";
    try {
      var stored = JSON.parse(sessionStorage.getItem("pa-resume-match") || "{}");
      if (stored.name) seed = stored.name;
    } catch (err) {
      /* ignore */
    }
    return hashCode(seed + (job.jobId || "") + (job.title || ""));
  }

  function postedDateFor(job) {
    if (job.postedDate) return job.postedDate;
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
    if (job.description) return job.description;
    var title = job.title || "this role";
    var dept = job.department || job.occupationalGroup;
    var cat = job.category || job.jobFamily;
    var s1 =
      "The Commonwealth of Pennsylvania is hiring for a " +
      title +
      " opening" +
      (dept ? " in " + dept : "") +
      (cat ? " (" + cat + ")." : ".");
    var s2 =
      "This position is open to job seekers through the state hiring portal";
    if (job.salaryRange && job.salaryRange !== "N/A") {
      s2 += " with a salary range of " + job.salaryRange;
    }
    s2 += ". Click the job title to view requirements and apply online.";
    return s1 + " " + s2;
  }

  function enrichJobs(jobs) {
    return jobs.map(function (job) {
      job.jobId = formatJobCode(job.jobCode);
      job.applyUrl = applyUrlFor(job);
      job.location = job.location || "Pennsylvania";
      job.department = job.occupationalGroup || "";
      job.category = job.jobFamily || "";
      job.postedDate = postedDateFor(job);
      job.employmentType = employmentType(job);
      job.description = jobDescription(job);
      return job;
    });
  }

  function matchesKeyword(job, q) {
    if (!q) return true;
    var hay = [
      job.title,
      job.jobCode,
      job.jobId,
      job.location,
      job.department,
      job.category,
      job.occupationalGroup,
      job.jobFamily,
      job.payScaleType,
      job.bargainingUnit,
      job.salaryRange,
      job.employmentType,
      job.description,
    ]
      .join(" ")
      .toLowerCase();
    return hay.indexOf(q) !== -1;
  }

  function relevanceScore(job, q) {
    if (!q) return 0;
    var title = norm(job.title);
    var code = norm(job.jobCode);
    var desc = norm(job.description);
    var score = 0;
    if (title === q) score += 120;
    else if (title.indexOf(q) === 0) score += 90;
    else if (title.indexOf(q) !== -1) score += 70;
    if (code === q) score += 80;
    else if (code.indexOf(q) !== -1) score += 45;
    if (desc.indexOf(q) !== -1) score += 25;
    var words = q.split(/\s+/).filter(Boolean);
    words.forEach(function (w) {
      if (w.length < 2) return;
      if (title.indexOf(w) !== -1) score += 18;
      if (norm(job.occupationalGroup).indexOf(w) !== -1) score += 10;
      if (norm(job.jobFamily).indexOf(w) !== -1) score += 10;
      if (code.indexOf(w) !== -1) score += 12;
    });
    return score;
  }

  function matchesFacets(job) {
    var f = state.facets;
    if (f.occupationalGroup.size && !f.occupationalGroup.has(job.occupationalGroup))
      return false;
    if (f.jobFamily.size && !f.jobFamily.has(job.jobFamily)) return false;
    if (f.payScaleType.size && !f.payScaleType.has(job.payScaleType)) return false;
    if (f.bargainingUnit.size && !f.bargainingUnit.has(job.bargainingUnit))
      return false;
    return true;
  }

  function applyFilters() {
    var q = norm(state.keyword);
    state.filtered = state.jobs.filter(function (job) {
      return matchesKeyword(job, q) && matchesFacets(job);
    });
    sortJobs();
    state.page = 1;
    renderAll();
  }

  function sortJobs() {
    var list = state.filtered.slice();
    var sort = state.sort;
    var q = norm(state.keyword);

    list.sort(function (a, b) {
      if (state.profileMatch) {
        var profileDiff = profileScore(b) - profileScore(a);
        if (profileDiff !== 0) return profileDiff;
      }
      if (sort === "relevance") {
        if (q) {
          var diff = relevanceScore(b, q) - relevanceScore(a, q);
          if (diff !== 0) return diff;
        }
        return (b.postedDate || "").localeCompare(a.postedDate || "");
      }
      if (sort === "posted-desc") {
        return (b.postedDate || "").localeCompare(a.postedDate || "");
      }
      if (sort === "title-desc")
        return (b.title || "").localeCompare(a.title || "");
      if (sort === "code-asc")
        return (a.jobId || "").localeCompare(b.jobId || "");
      if (sort === "salary-desc") {
        var sa = parseSalaryTop(a.salaryRange);
        var sb = parseSalaryTop(b.salaryRange);
        return sb - sa || (a.title || "").localeCompare(b.title || "");
      }
      return (a.title || "").localeCompare(b.title || "");
    });
    state.filtered = list;
  }

  function parseSalaryTop(range) {
    if (!range) return 0;
    var m = String(range).match(/\$?([\d,]+)/g);
    if (!m || !m.length) return 0;
    var last = m[m.length - 1].replace(/[$,]/g, "");
    return parseInt(last, 10) || 0;
  }

  function facetCounts(field, subset) {
    var counts = {};
    subset.forEach(function (job) {
      var v = job[field];
      if (!v) return;
      counts[v] = (counts[v] || 0) + 1;
    });
    return Object.keys(counts)
      .sort(function (a, b) {
        return counts[b] - counts[a] || a.localeCompare(b);
      })
      .map(function (key) {
        return { value: key, count: counts[key] };
      });
  }

  function jobsForFacetExcept(exceptField) {
    var q = norm(state.keyword);
    return state.jobs.filter(function (job) {
      if (!matchesKeyword(job, q)) return false;
      var f = state.facets;
      if (exceptField !== "occupationalGroup" && f.occupationalGroup.size) {
        if (!f.occupationalGroup.has(job.occupationalGroup)) return false;
      }
      if (exceptField !== "jobFamily" && f.jobFamily.size) {
        if (!f.jobFamily.has(job.jobFamily)) return false;
      }
      if (exceptField !== "payScaleType" && f.payScaleType.size) {
        if (!f.payScaleType.has(job.payScaleType)) return false;
      }
      if (exceptField !== "bargainingUnit" && f.bargainingUnit.size) {
        if (!f.bargainingUnit.has(job.bargainingUnit)) return false;
      }
      return true;
    });
  }

  function renderFacetList(containerId, field, label) {
    var ul = $(containerId);
    if (!ul) return;
    var subset = jobsForFacetExcept(field);
    var items = facetCounts(field, subset).slice(0, FACET_LIMIT);
    var selected = state.facets[field];

    if (!items.length) {
      ul.innerHTML =
        '<li class="pa-jobs-facet__empty">No options for current filters</li>';
      return;
    }

    ul.innerHTML = items
      .map(function (item) {
        var id = "facet-" + field + "-" + hashVal(item.value);
        var checked = selected.has(item.value) ? " checked" : "";
        return (
          '<li class="pa-jobs-facet__item">' +
          '<label class="pa-jobs-facet__label" for="' +
          id +
          '">' +
          '<input type="checkbox" id="' +
          id +
          '" data-facet="' +
          field +
          '" data-value="' +
          escapeHtml(item.value) +
          '"' +
          checked +
          ">" +
          "<span>" +
          escapeHtml(item.value) +
          ' <span class="pa-jobs-facet__count">(' +
          item.count +
          ")</span></span>" +
          "</label></li>"
        );
      })
      .join("");

    ul.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
      cb.addEventListener("change", onFacetChange);
    });
  }

  function hashVal(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return h.toString(36);
  }

  function renderFacets() {
    renderFacetList("facet-occupational-group", "occupationalGroup", "Occupational Group");
    renderFacetList("facet-job-family", "jobFamily", "Job Family");
    renderFacetList("facet-pay-scale", "payScaleType", "Pay Scale Type");
    renderFacetList("facet-bargaining", "bargainingUnit", "Bargaining Unit");
  }

  function renderCount() {
    var total = state.filtered.length;
    var start = total ? (state.page - 1) * PAGE_SIZE + 1 : 0;
    var end = Math.min(state.page * PAGE_SIZE, total);
    var el = $("pa-jobs-count");
    if (!el) return;
    if (!total) {
      el.innerHTML = "Showing <strong>0</strong> jobs";
      return;
    }
    el.innerHTML =
      "Showing <strong>" +
      start +
      " – " +
      end +
      "</strong> of <strong>" +
      total +
      "</strong> jobs";
  }

  function renderTags() {
    var ul = $("pa-jobs-tags");
    if (!ul) return;
    var tags = [];
    var labels = {
      occupationalGroup: "Department",
      jobFamily: "Category",
      payScaleType: "Pay scale",
      bargainingUnit: "Bargaining unit",
    };

    Object.keys(state.facets).forEach(function (field) {
      state.facets[field].forEach(function (val) {
        tags.push({
          field: field,
          value: val,
          label: labels[field] + ": " + val,
        });
      });
    });

    if (state.profileMatch) {
      tags.unshift({
        field: "profileMatch",
        value: "1",
        label: "Resume based",
      });
    }

    if (state.keyword) {
      tags.unshift({
        field: "keyword",
        value: state.keyword,
        label: 'Keyword: "' + state.keyword + '"',
      });
    }

    if (!tags.length) {
      ul.innerHTML = "";
      return;
    }

    var html = tags
      .map(function (t) {
        return (
          '<li class="pa-jobs-tag">' +
          "<span>" +
          escapeHtml(t.label) +
          "</span>" +
          '<button type="button" aria-label="Remove filter" data-remove="' +
          escapeHtml(t.field) +
          '" data-val="' +
          escapeHtml(t.value) +
          '"><i class="ri-close-line" aria-hidden="true"></i></button>' +
          "</li>"
        );
      })
      .join("");

    html +=
      '<li class="pa-jobs-tag pa-jobs-tag--clear">' +
      '<button type="button" id="pa-jobs-clear-all">Clear all</button></li>';

    ul.innerHTML = html;


  }

  function initTagDelegation() {
    var ul = $("pa-jobs-tags");
    if (!ul) return;
    ul.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-remove], #pa-jobs-clear-all");
      if (!btn) return;
      if (btn.id === "pa-jobs-clear-all") {
        clearAllFilters();
        return;
      }
      var field = btn.getAttribute("data-remove");
      var val = btn.getAttribute("data-val");
      if (field === "keyword") {
        state.keyword = "";
        if (els.keyword) els.keyword.value = "";
        if (els.clearKw) els.clearKw.hidden = true;
      } else if (field === "profileMatch") {
        state.profileMatch = false;
        var profileCb = $("pa-jobs-profile-match");
        if (profileCb) profileCb.checked = false;
      } else if (field) {
        state.facets[field].delete(val);
      }
      applyFilters();
    });
  }

  function clearAllFilters() {
    state.keyword = "";
    state.profileMatch = false;
    state.facets.occupationalGroup.clear();
    state.facets.jobFamily.clear();
    state.facets.payScaleType.clear();
    state.facets.bargainingUnit.clear();
    if (els.keyword) els.keyword.value = "";
    if (els.clearKw) els.clearKw.hidden = true;
    var profileCb = $("pa-jobs-profile-match");
    if (profileCb) profileCb.checked = false;
    applyFilters();
  }

  function renderJobs() {
    var list = $("pa-jobs-list");
    var empty = $("pa-jobs-empty");
    if (!list) return;

    var total = state.filtered.length;
    var start = (state.page - 1) * PAGE_SIZE;
    var pageJobs = state.filtered.slice(start, start + PAGE_SIZE);

    if (!total) {
      list.innerHTML = "";
      if (empty) empty.hidden = false;
      return;
    }
    if (empty) empty.hidden = true;

    list.innerHTML = pageJobs
      .map(function (job) {
        var link = job.applyUrl || applyUrlFor(job);
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

        var desc = job.description
          ? '<p class="pa-jobs-card__description">' +
            escapeHtml(job.description) +
            "</p>"
          : "";

        return (
          '<li class="pa-jobs-card" role="listitem">' +
          '<div class="pa-jobs-card__inner">' +
          '<h3 class="pa-jobs-card__title"><a href="' +
          escapeHtml(link) +
          '" target="_blank" rel="noopener noreferrer">' +
          escapeHtml(job.title || "Untitled") +
          "</a></h3>" +
          metaLine +
          desc +
          "</div></li>"
        );
      })
      .join("");
  }

  function renderPagination() {
    var nav = $("pa-jobs-pagination");
    if (!nav) return;
    var total = state.filtered.length;
    var pages = Math.ceil(total / PAGE_SIZE) || 1;

    if (pages <= 1) {
      nav.innerHTML = "";
      return;
    }

    var html = "";
    html +=
      '<li><button type="button" data-page="prev"' +
      (state.page <= 1 ? " disabled" : "") +
      ' aria-label="Previous page"><i class="ri-arrow-left-s-line"></i></button></li>';

    var windowStart = Math.max(1, state.page - 2);
    var windowEnd = Math.min(pages, state.page + 2);

    for (var p = windowStart; p <= windowEnd; p++) {
      html +=
        '<li><button type="button" data-page="' +
        p +
        '"' +
        (p === state.page ? ' class="is-active" aria-current="page"' : "") +
        ">" +
        p +
        "</button></li>";
    }

    html +=
      '<li><button type="button" data-page="next"' +
      (state.page >= pages ? " disabled" : "") +
      ' aria-label="Next page"><i class="ri-arrow-right-s-line"></i></button></li>';

    nav.innerHTML = html;

    nav.querySelectorAll("button[data-page]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var v = btn.getAttribute("data-page");
        if (v === "prev") state.page = Math.max(1, state.page - 1);
        else if (v === "next") state.page = Math.min(pages, state.page + 1);
        else state.page = parseInt(v, 10);
        renderCount();
        renderJobs();
        renderPagination();
        var list = $("pa-jobs-list");
        if (list) list.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function renderAll() {
    renderFacets();
    renderCount();
    renderTags();
    renderJobs();
    renderPagination();
  }

  function onFacetChange(e) {
    var cb = e.target;
    var field = cb.getAttribute("data-facet");
    var val = cb.getAttribute("data-value");
    if (!field || !val) return;
    if (cb.checked) state.facets[field].add(val);
    else state.facets[field].delete(val);
    applyFilters();
  }

  function onKeywordSubmit(e) {
    if (e) e.preventDefault();
    state.keyword = (els.keyword && els.keyword.value) || "";
    if (els.clearKw) els.clearKw.hidden = !state.keyword;
    applyFilters();
  }

  function initFacetToggles() {
    document.querySelectorAll(".pa-jobs-facet").forEach(function (facet) {
      var btn = facet.querySelector(".pa-jobs-facet__toggle");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var open = facet.classList.toggle("is-open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
  }

  function initMobileFilter() {
    var openBtn = $("pa-jobs-filter-open");
    var closeBtn = $("pa-jobs-refine-close");
    var refine = $("pa-jobs-refine");
    var backdrop = $("pa-jobs-refine-backdrop");

    function open() {
      if (refine) refine.classList.add("is-mobile-open");
      if (backdrop) backdrop.classList.add("is-visible");
      document.body.style.overflow = "hidden";
    }
    function close() {
      if (refine) refine.classList.remove("is-mobile-open");
      if (backdrop) backdrop.classList.remove("is-visible");
      document.body.style.overflow = "";
    }

    if (openBtn) openBtn.addEventListener("click", open);
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (backdrop) backdrop.addEventListener("click", close);
  }

  function initFacetSearch() {
    document.querySelectorAll("[data-facet-filter]").forEach(function (input) {
      input.addEventListener("input", function () {
        var q = norm(input.value);
        var listId = input.getAttribute("data-facet-filter");
        var ul = $(listId);
        if (!ul) return;
        ul.querySelectorAll(".pa-jobs-facet__item").forEach(function (li) {
          var text = norm(li.textContent);
          li.style.display = !q || text.indexOf(q) !== -1 ? "" : "none";
        });
      });
    });
  }

  function loadCatalog() {
    return fetch("assets/jobs-catalog.json")
      .then(function (r) {
        if (!r.ok) throw new Error("catalog");
        return r.json();
      })
      .then(function (data) {
        var raw = Array.isArray(data) ? data : data.jobs || [];
        state.jobs = enrichJobs(raw);
        applyFilters();
      })
      .catch(function () {
        var list = $("pa-jobs-list");
        var empty = $("pa-jobs-empty");
        if (list) list.innerHTML = "";
        if (empty) {
          empty.hidden = false;
          empty.innerHTML =
            "Unable to load job openings. Please try again later or visit " +
            '<a href="https://www.governmentjobs.com/careers/pabureau">the Commonwealth hiring portal</a>.';
        }
      });
  }

  function initProfileMatch() {
    var cb = $("pa-jobs-profile-match");
    if (!cb) return;

    var params = new URLSearchParams(window.location.search);
    if (params.get("resumeMatch") === "1" || sessionStorage.getItem("pa-resume-match")) {
      cb.checked = true;
      state.profileMatch = true;
    }

    cb.addEventListener("change", function () {
      state.profileMatch = cb.checked;
      if (cb.checked && !sessionStorage.getItem("pa-resume-match")) {
        var trigger = $("pa-resume-open");
        if (trigger) trigger.click();
      }
      applyFilters();
    });
  }

  function init() {
    els.keyword = $("pa-jobs-keyword");
    els.clearKw = $("pa-jobs-keyword-clear");
    els.form = $("pa-jobs-search-form");

    if (els.form) els.form.addEventListener("submit", onKeywordSubmit);
    if (els.clearKw) {
      els.clearKw.addEventListener("click", function () {
        if (els.keyword) els.keyword.value = "";
        els.clearKw.hidden = true;
        state.keyword = "";
        applyFilters();
      });
    }
    if (els.keyword) {
      els.keyword.addEventListener("input", function () {
        if (els.clearKw) els.clearKw.hidden = !els.keyword.value;
      });
    }

    var sort = $("pa-jobs-sort");
    if (sort) {
      sort.value = state.sort;
      sort.addEventListener("change", function () {
        state.sort = sort.value;
        sortJobs();
        renderJobs();
        renderPagination();
        renderCount();
      });
    }

    var params = new URLSearchParams(window.location.search);
    var q = params.get("q") || params.get("keyword") || params.get("keyWord") || "";
    if (q && els.keyword) {
      els.keyword.value = q;
      state.keyword = q;
      if (els.clearKw) els.clearKw.hidden = false;
    }

    initProfileMatch();
    initFacetToggles();
    initMobileFilter();
    initFacetSearch();
    initTagDelegation();
    loadCatalog();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
