(function () {
  "use strict";

  const mock = window.LUTHelperMock;
  if (!mock) {
    throw new Error("缺少 mock-data.js");
  }

  const ICONS = {
    chevron: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    plus: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    more: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>',
    play: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z"/></svg>',
    pause: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6v12M16 6v12"/></svg>',
    stop: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>',
    alert: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4 3.7 19h16.6L12 4Z"/><path d="M12 9v4M12 16.5v.1"/></svg>',
    check: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 12 4 4 8-9"/></svg>',
    clock: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    book: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5h16v13H4z"/><path d="M8 5.5v13M4 10h16"/></svg>',
    grip: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="7" r="1"/><circle cx="16" cy="7" r="1"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/><circle cx="8" cy="17" r="1"/><circle cx="16" cy="17" r="1"/></svg>',
    warning: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4 3.7 19h16.6L12 4Z"/><path d="M12 9v4M12 16.5v.1"/></svg>',
    chevronLeft: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg>',
    x: '<svg class="icon icon-sm" viewBox="0 0 24 24" aria-hidden="true"><path d="m7 7 10 10M17 7 7 17"/></svg>',
  };

  const state = {
    page: "courses",
    selectedCourseIds: new Set(),
    basket: [],
    allLoaded: false,
    filtersOpen: false,
    localFilters: {
      available: false,
      conflict: false,
    },
    schedule: null,
    countdownTimer: null,
    lastFocusedCourse: null,
    draggedTask: null,
    activeModalAction: null,
    pendingDuplicates: [],
    muted: false,
    logOpen: false,
    logUserScrolled: false,
    logs: mock.logs.map((entry) => ({ ...entry })),
    selectedWeek: "all",
    currentDetail: null,
    groups: structuredClone(mock.groups),
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const escapeHtml = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const courseById = new Map(mock.courses.map((course) => [course.id, course]));
  const allCourseById = new Map(mock.allCourses.map((course) => [course.id, course]));

  function capacityPercent(course) {
    if (!course.capacity) return 0;
    return clamp(Math.round((course.selected / course.capacity) * 100), 0, 100);
  }

  function capacityLabel(course) {
    return `${course.selected}/${course.capacity}`;
  }

  function statusMarkup(course) {
    if (course.selected >= course.capacity) {
      return '<span class="status-chip danger">已满</span>';
    }
    if (course.conflict) {
      return '<span class="status-chip warn">冲突</span>';
    }
    return '<span class="status-chip live">可选</span>';
  }

  function capMarkup(course) {
    const percent = capacityPercent(course);
    const mode = percent >= 100 ? "full" : percent >= 80 ? "warn" : "";
    return `
      <div class="capacity">
        <span class="capacity-bar ${mode}" aria-hidden="true"><span style="width:${percent}%"></span></span>
        <span class="capacity-text">${capacityLabel(course)}</span>
      </div>
    `;
  }

  function courseRowMarkup(course) {
    const selected = state.selectedCourseIds.has(course.id);
    const conflict = course.conflict ? `<span class="conflict-mark">${ICONS.alert}冲突</span>` : "";
    return `
      <tr data-course-id="${escapeHtml(course.id)}" class="${selected ? "is-selected" : ""}">
        <td><input class="checkbox" type="checkbox" aria-label="选择${escapeHtml(course.name)} ${escapeHtml(course.classNo)}班" ${selected ? "checked" : ""} data-course-check /></td>
        <td>
          <div class="course-name"><button class="course-name-button" type="button" data-detail-course="${escapeHtml(course.id)}" title="${escapeHtml(course.name)}">${escapeHtml(course.name)}</button></div>
          <div class="course-code">${escapeHtml(course.code)} · 课序号 ${escapeHtml(course.classNo)}</div>
        </td>
        <td data-column-body="capacity">${capMarkup(course)}</td>
        <td data-column-body="teacher"><span class="teacher">${escapeHtml(course.teacher)}</span></td>
        <td data-column-body="time"><span class="time-cell" title="${escapeHtml(course.time)}">${escapeHtml(course.time)}</span></td>
        <td data-column-body="status">${conflict || statusMarkup(course)}</td>
        <td><button class="more-button" type="button" data-course-menu="${escapeHtml(course.id)}" aria-label="更多课程操作">${ICONS.more}</button></td>
      </tr>
    `;
  }

  function renderCourses() {
    const tbody = $("[data-course-body]");
    if (!tbody) return;
    tbody.innerHTML = mock.courses.map(courseRowMarkup).join("");
    const count = state.selectedCourseIds.size;
    $("[data-selection-count]").textContent = count ? `已选择 ${count} 个教学班` : "未选择课程";
    $('[data-action="batch-add"]').disabled = count === 0;
    $("[data-course-summary]").textContent = `当前轮次 · ${mock.courses.length} 个教学班`;
    syncSelectAll();
  }

  function syncSelectAll() {
    const check = $("[data-select-all]");
    if (!check) return;
    check.checked = mock.courses.length > 0 && mock.courses.every((course) => state.selectedCourseIds.has(course.id));
    check.indeterminate = state.selectedCourseIds.size > 0 && !check.checked;
  }

  function renderAllCourses() {
    const tbody = $("[data-all-body]");
    if (!tbody) return;
    if (!state.allLoaded) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6">
            <div class="empty-state" style="min-height:360px">
              <div class="empty-inner">
                <div class="empty-mark">${ICONS.book}</div>
                <h3 class="empty-title">尚未加载全校课程</h3>
                <p class="empty-copy">点击“加载全校课程”后，将拉取完整课程列表，再在本地筛选。</p>
                <button class="button primary" type="button" data-action="load-all">${ICONS.book} 加载全校课程</button>
              </div>
            </div>
          </td>
        </tr>
      `;
      $("[data-all-count]").textContent = "等待加载";
      return;
    }
    const keyword = ($("[data-all-search]")?.value || "").trim().toLowerCase();
    const campus = $("[data-all-campus]")?.value || "";
    const visible = mock.allCourses.filter((course) => {
      const matchesKeyword =
        !keyword ||
        `${course.name} ${course.teacher} ${course.code} ${course.classNo}`.toLowerCase().includes(keyword);
      const matchesCampus = !campus || course.campus === campus;
      return matchesKeyword && matchesCampus;
    });
    tbody.innerHTML = visible.map((course) => allCourseRowMarkup(course)).join("");
    $("[data-all-count]").textContent =
      visible.length === mock.allCourses.length
        ? `已加载 ${mock.allCourses.length} 个教学班`
        : `显示 ${visible.length} / ${mock.allCourses.length} 个教学班`;
    syncAllSelect();
  }

  function allCourseRowMarkup(course) {
    const selected = state.basket.includes(course.id);
    return `
      <tr data-all-id="${escapeHtml(course.id)}" class="${selected ? "is-selected" : ""}">
        <td><input class="checkbox" type="checkbox" aria-label="选择${escapeHtml(course.name)} ${escapeHtml(course.classNo)}班" ${selected ? "checked" : ""} data-all-check /></td>
        <td>
          <div class="course-name"><button class="course-name-button" type="button" data-detail-all="${escapeHtml(course.id)}">${escapeHtml(course.name)}</button></div>
          <div class="course-code">${escapeHtml(course.code)} · 课序号 ${escapeHtml(course.classNo)}</div>
        </td>
        <td>${capMarkup(course)}</td>
        <td><span class="teacher">${escapeHtml(course.teacher)}</span></td>
        <td><span class="time-cell" title="${escapeHtml(course.time)}">${escapeHtml(course.time)}</span></td>
        <td>${statusMarkup(course)}</td>
      </tr>
    `;
  }

  function syncAllSelect() {
    const check = $("[data-all-select-all]");
    if (!check) return;
    check.checked = mock.allCourses.length > 0 && mock.allCourses.every((course) => state.basket.includes(course.id));
    check.indeterminate = state.basket.length > 0 && !check.checked;
  }

  function renderBasket() {
    const list = $("[data-basket-list]");
    if (!list) return;
    if (!state.basket.length) {
      list.innerHTML = `
        <div class="empty-state" style="min-height:190px">
          <div class="empty-inner">
            <div class="empty-mark">${ICONS.book}</div>
            <h3 class="empty-title">还没有选择教学班</h3>
            <p class="empty-copy">在左侧勾选后，点击下方按钮加入待选。</p>
          </div>
        </div>
      `;
    } else {
      list.innerHTML = state.basket
        .map((id) => {
          const course = allCourseById.get(id);
          if (!course) return "";
          return `
            <div class="basket-item">
              <span class="basket-code">${escapeHtml(course.classNo)}</span>
              <div class="basket-copy">
                <div class="basket-name">${escapeHtml(course.name)}</div>
                <div class="basket-meta">${escapeHtml(course.teacher)} · ${escapeHtml(course.campus)}</div>
              </div>
              <button class="more-button" type="button" data-basket-remove="${escapeHtml(course.id)}" aria-label="移出待加入列表">${ICONS.x}</button>
            </div>
          `;
        })
        .join("");
    }
    const groups = new Set(state.basket.map((id) => allCourseById.get(id)?.code).filter(Boolean));
    $("[data-basket-count]").textContent = state.basket.length;
    $("[data-basket-groups]").textContent = groups.size;
    $('[data-action="all-batch-add"]').disabled = state.basket.length === 0;
  }

  function groupStateLabel(group) {
    if (group.state === "success") return '<span class="status-chip live">已成功</span>';
    if (group.state === "running") return '<span class="status-chip live">运行中</span>';
    if (group.state === "paused") return '<span class="status-chip warn">已暂停</span>';
    return '<span class="status-chip neutral">待开始</span>';
  }

  function taskStateIcon(task) {
    if (task.state === "active") return ICONS.play;
    if (task.state === "paused") return ICONS.pause;
    if (task.state === "success") return ICONS.check;
    return ICONS.clock;
  }

  function taskClass(task) {
    if (task.state === "active") return "is-active";
    if (task.state === "paused") return "is-paused";
    if (task.selected >= task.capacity) return "is-full";
    return "";
  }

  function renderGroups() {
    const list = $("[data-group-list]");
    if (!list) return;
    list.innerHTML = state.groups.length
      ? state.groups.map(groupMarkup).join("")
      : `
        <div class="empty-state" style="min-height:300px">
          <div class="empty-inner">
            <div class="empty-mark">${ICONS.clock}</div>
            <h3 class="empty-title">抢课队列还是空的</h3>
            <p class="empty-copy">从左侧勾选教学班，加入后会按课程代码自动形成课程组。</p>
            <button class="button primary" type="button" data-action="focus-course-search">选择课程</button>
          </div>
        </div>
      `;
    $("[data-group-count]").textContent = state.groups.length;
    updateThreadLoad();
  }

  function groupMarkup(group) {
    const collapsed = group.state === "success" ? "is-collapsed" : "";
    const success = group.state === "success" ? "is-success" : "";
    const action = group.state === "running"
      ? `<button class="group-action" type="button" data-group-pause="${group.id}" aria-label="暂停整组">${ICONS.pause}</button>`
      : `<button class="group-action" type="button" data-group-start="${group.id}" aria-label="开始整组">${ICONS.play}</button>`;
    return `
      <article class="group-card ${collapsed} ${success}" data-group-id="${escapeHtml(group.id)}">
        <div class="group-head" data-group-toggle="${escapeHtml(group.id)}">
          <button class="group-expand" type="button" aria-label="展开或收起课程组">${ICONS.chevron}</button>
          <span class="group-symbol">${escapeHtml(group.code.slice(-2))}</span>
          <div class="group-copy">
            <div class="group-name">${escapeHtml(group.name)}</div>
            <div class="group-meta">${groupStateLabel(group)} <span>·</span> <span>${group.tasks.length} 个教学班</span></div>
          </div>
          <div class="group-actions">
            ${action}
            <button class="group-action" type="button" data-group-stop="${group.id}" aria-label="停止整组">${ICONS.stop}</button>
            <button class="group-action" type="button" data-group-menu="${group.id}" aria-label="课程组更多操作">${ICONS.more}</button>
          </div>
        </div>
        <div class="group-body">
          ${
            group.state === "success"
              ? `
                <div class="group-result">
                  <span class="result-check">${ICONS.check}</span>
                  <div class="result-copy">
                    <div class="result-title">已抢到 ${escapeHtml(group.successTask)}</div>
                    <div class="result-meta">${escapeHtml(group.successTime)} · 组内其他任务已停止</div>
                  </div>
                </div>
              `
              : `<div class="task-list">${group.tasks.map((task, index) => taskMarkup(group, task, index)).join("")}</div>`
          }
        </div>
      </article>
    `;
  }

  function taskMarkup(group, task, index) {
    const role = index === 0 ? "首选" : `备选 ${index}`;
    return `
      <div class="task ${taskClass(task)}" draggable="true" data-task-id="${escapeHtml(task.id)}" data-group-id="${escapeHtml(group.id)}">
        <span class="task-priority">${String(index + 1).padStart(2, "0")}</span>
        <span class="task-state-icon">${taskStateIcon(task)}</span>
        <div class="task-copy">
          <div class="task-name"><span>${escapeHtml(task.classNo)} 班 · ${escapeHtml(task.teacher)}</span><span class="role">${role}</span></div>
          <div class="task-meta">${escapeHtml(task.campus)} · ${escapeHtml(task.time)} · ${task.selected}/${task.capacity}</div>
        </div>
        <div class="task-info">
          <div class="task-attempt">${task.attempts} 次</div>
          <button class="task-menu" type="button" data-task-menu="${escapeHtml(task.id)}" aria-label="任务更多操作">${ICONS.more}</button>
        </div>
      </div>
    `;
  }

  function updateThreadLoad() {
    const threads = Number($('[data-param="threads"]')?.value || 3);
    const activeTasks = state.groups.reduce(
      (count, group) => count + group.tasks.filter((task) => task.state === "active").length,
      0,
    );
    const display = activeTasks || state.groups.filter((group) => group.state !== "success").length;
    const total = Math.max(display, 1) * threads;
    const el = $("[data-thread-load]");
    if (!el) return;
    el.textContent = `预计 ${total} 线程`;
    el.style.color = total > 50 ? "var(--red)" : total > 20 ? "var(--amber)" : "var(--teal)";
    el.style.background = total > 50 ? "var(--red-soft)" : total > 20 ? "var(--amber-soft)" : "var(--teal-pale)";
  }

  function renderSelected() {
    const body = $("[data-selected-body]");
    if (!body) return;
    body.innerHTML = mock.selectedCourses
      .map(
        (course) => `
        <tr data-selected-id="${escapeHtml(course.id)}">
          <td>
            <div class="course-name">
              <button class="course-name-button" type="button" data-selected-detail="${escapeHtml(course.id)}">${escapeHtml(course.name)}</button>
            </div>
            <div class="course-code">${escapeHtml(course.code)}</div>
          </td>
          <td>${escapeHtml(course.teacher)}</td>
          <td>
            <div style="font-size:9px;font-weight:700;color:var(--ink-soft)">${escapeHtml(course.weekdayLabel)}</div>
            <div style="font-size:8px;color:var(--muted)">第 ${course.start}–${course.end} 节 · ${escapeHtml(course.weeks)} 周</div>
          </td>
        </tr>
      `,
      )
      .join("");
    const dropBody = $("[data-drop-body]");
    if (dropBody) {
      dropBody.innerHTML = mock.dropHistory
        .map(
          (record) => `
            <div class="drop-record">
              <strong>${escapeHtml(record.name)}</strong>
              <span>${escapeHtml(record.time)}</span>
              <span style="margin-left:auto">${escapeHtml(record.reason)}</span>
            </div>
          `,
        )
        .join("");
    }
  }

  function renderTimetable() {
    const table = $("[data-timetable]");
    if (!table) return;
    const days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"];
    const timeLabels = {
      1: "08:00",
      2: "09:50",
      3: "10:00",
      4: "12:00",
      5: "14:30",
      6: "16:20",
      7: "16:40",
      8: "18:30",
      9: "19:30",
      10: "21:20",
      11: "21:30",
      12: "22:20",
    };
    const filterWeek = state.selectedWeek === "all" ? null : Number(state.selectedWeek);
    const visibleCourses = mock.selectedCourses.filter((course) => {
      if (filterWeek === null) return true;
      return course.weekMask[filterWeek - 1] === "1";
    });

    let html = '<div class="timetable-head timetable-corner">节次</div>';
    html += days.map((day) => `<div class="timetable-head">${day}</div>`).join("");
    for (let section = 1; section <= 12; section += 1) {
      html += `<div class="section-label"><span>${section}</span><span>${timeLabels[section]}</span></div>`;
      for (let day = 1; day <= 7; day += 1) {
        const occupying = visibleCourses.find(
          (course) => course.weekday === day && section >= course.start && section <= course.end,
        );
        if (occupying && occupying.start === section) {
          const span = occupying.end - occupying.start + 1;
          const conflict = mock.selectedCourses.some(
            (other) =>
              other.id !== occupying.id &&
              other.weekday === occupying.weekday &&
              !(other.end < occupying.start || other.start > occupying.end) &&
              (filterWeek === null || other.weekMask[filterWeek - 1] === "1"),
          );
          html += `
            <button
              class="course-block"
              type="button"
              style="grid-row: span ${span}; --block-bg:${blockColor(occupying.color).bg}; --block-line:${blockColor(occupying.color).border}; --block-accent:${blockColor(occupying.color).accent}"
              data-selected-detail="${escapeHtml(occupying.id)}"
              title="${escapeHtml(occupying.name)} · ${escapeHtml(occupying.teacher)} · ${escapeHtml(occupying.place)}"
            >
              <span class="course-block-name">${conflict ? ICONS.alert : ""}${escapeHtml(occupying.name)}</span>
              <span class="course-block-meta">${escapeHtml(occupying.teacher)}</span>
              <span class="course-block-meta">${escapeHtml(occupying.place)}</span>
            </button>
          `;
        } else if (!occupying) {
          html += '<div class="timetable-cell"></div>';
        }
      }
    }
    table.innerHTML = html;
    $("[data-week-pill]").textContent = filterWeek === null ? "全部周次" : `第 ${filterWeek} 周`;
    $("[data-week-summary]").textContent =
      filterWeek === null ? `全部周次 · ${visibleCourses.length} 门课程` : `第 ${filterWeek} 周 · ${visibleCourses.length} 门课程`;

    const unplaced = $("[data-unplaced]");
    if (unplaced) {
      unplaced.innerHTML = mock.unplacedCourses
        .map(
          (course) => `
            <button class="unplaced-item" type="button" title="${escapeHtml(course.time)}">
              ${ICONS.warning} ${escapeHtml(course.name)} · ${escapeHtml(course.teacher)}
            </button>
          `,
        )
        .join("");
    }
  }

  function blockColor(color) {
    const map = {
      teal: { bg: "#e7f2ed", border: "#c8ded5", accent: "#438b76" },
      amber: { bg: "#fbf1df", border: "#eeddbb", accent: "#bc8730" },
      blue: { bg: "#eaf2f8", border: "#cedfe9", accent: "#527f9f" },
      rose: { bg: "#f9eae7", border: "#ecd4cf", accent: "#b66b5c" },
      violet: { bg: "#f1edf6", border: "#ddd5e8", accent: "#7e6b99" },
      slate: { bg: "#edf0ef", border: "#d9dfdc", accent: "#687d73" },
    };
    return map[color] || map.teal;
  }

  function renderLogs() {
    const list = $("[data-log-list]");
    if (!list) return;
    const groupFilter = $("[data-log-group]")?.value || "all";
    const levelFilter = $("[data-log-level]")?.value || "all";
    const filtered = state.logs.filter(
      (entry) =>
        (levelFilter === "all" || entry.level === levelFilter) &&
        (groupFilter === "all" || entry.message.includes(groupFilter)),
    );
    list.innerHTML = filtered
      .map(
        (entry) => `
          <div class="log-row ${entry.level.toLowerCase()}">
            <span class="log-time">${escapeHtml(entry.time)}</span>
            <span class="log-level">${escapeHtml(entry.level)}</span>
            <span class="log-message">${escapeHtml(entry.message)}</span>
          </div>
        `,
      )
      .join("");
    const count = $("[data-log-count]");
    if (count) count.textContent = `${filtered.length} 条记录 · 2 个活跃任务`;
    const latest = $("[data-log-latest]");
    if (latest) latest.textContent = state.logs[0]?.message || "尚未收到新日志";
    if (!state.logUserScrolled) {
      requestAnimationFrame(() => {
        list.scrollTop = list.scrollHeight;
      });
    }
  }

  function renderBatchSelect() {
    const select = $("[data-batch-select]");
    if (!select) return;
    select.innerHTML = mock.batches.map((batch) => `<option>${escapeHtml(batch)}</option>`).join("");
    select.value = mock.session.batch;
  }

  function renderWeekSelect() {
    const select = $("[data-week-select]");
    if (!select) return;
    const options = ['<option value="all">全部周次</option>'];
    for (let week = 1; week <= 20; week += 1) {
      options.push(`<option value="${week}">第 ${week} 周</option>`);
    }
    select.innerHTML = options.join("");
  }

  function applySession() {
    $$("[data-session]").forEach((node) => {
      const key = node.dataset.session;
      if (mock.session[key]) node.textContent = mock.session[key];
    });
  }

  function switchPage(page) {
    if (!["courses", "all-courses", "selected"].includes(page)) return;
    state.page = page;
    $$("[data-page]").forEach((button) => {
      const active = button.dataset.page === page;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    $$("[data-page-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.pagePanel === page));
    const labels = { courses: "课程", "all-courses": "全校课程", selected: "已选课程" };
    $("[data-breadcrumb]").textContent = labels[page];
    if (page === "selected") renderTimetable();
    if (page === "all-courses") renderAllCourses();
  }

  function showInfo(message, title = "操作已完成", duration = 5000) {
    const bar = $("[data-info-bar]");
    if (!bar) return;
    $("[data-info-title]").textContent = title;
    $("[data-info-message]").textContent = message;
    bar.hidden = false;
    clearTimeout(showInfo.timer);
    showInfo.timer = window.setTimeout(() => {
      bar.hidden = true;
    }, duration);
  }

  function pushLog(message, level = "INFO") {
    const now = new Date();
    const time = now.toLocaleTimeString("zh-CN", { hour12: false });
    state.logs.unshift({ time, level, message });
    if (state.logs.length > 5000) state.logs.pop();
    if (state.logOpen) renderLogs();
    const latest = $("[data-log-latest]");
    if (latest) latest.textContent = message;
    if (level === "SUCCESS") {
      showInfo(message, "检测到抢课成功", 5000);
      playSuccessTone();
    }
  }

  function playSuccessTone() {
    if (state.muted) return;
    try {
      const audioContext = new AudioContext();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(660, audioContext.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(980, audioContext.currentTime + 0.16);
      gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.09, audioContext.currentTime + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.3);
      oscillator.connect(gain);
      gain.connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.32);
      oscillator.addEventListener("ended", () => audioContext.close());
    } catch {
      // 浏览器自动播放策略可能阻止提示音，不影响原型交互。
    }
  }

  function toggleFilters(force) {
    state.filtersOpen = typeof force === "boolean" ? force : !state.filtersOpen;
    const panel = $("[data-filter-panel]");
    const trigger = $('[data-action="toggle-filters"]');
    panel.hidden = !state.filtersOpen;
    trigger.setAttribute("aria-expanded", String(state.filtersOpen));
    trigger.classList.toggle("active", state.filtersOpen);
  }

  function openDetail(course, source) {
    state.currentDetail = { course, source };
    const classNo = course.classNo || "已选";
    const credits = course.credits || "—";
    const hours = course.hours || "—";
    const department = course.department || "—";
    const classId = course.classId || course.id;
    const capacity = course.capacity ? capacityLabel(course) : "—";
    $("[data-detail-title]").textContent = course.name;
    $("[data-detail-subtitle]").textContent = `${course.code || "已选课程"} · ${
      course.classNo ? `课序号 ${course.classNo}` : "已选课程详情"
    }`;
    const conflict = course.conflict
      ? `<div class="conflict-box">${ICONS.warning}<div><strong>检测到时间冲突</strong><br>请展开周课表核对与已选课程的重叠时段。</div></div>`
      : "";
    const schedule = course.weekday
      ? `
        <div class="mini-schedule">
          <div class="mini-schedule-row"><span class="day">${escapeHtml(course.weekdayLabel)}</span><span>第 ${course.start}–${course.end} 节 · ${escapeHtml(course.weeks)} 周 · ${escapeHtml(course.place)}</span></div>
        </div>
      `
      : `
        <div class="mini-schedule">
          <div class="mini-schedule-row"><span class="day">上课时间</span><span>${escapeHtml(course.time || "未提供")}</span></div>
        </div>
      `;
    $("[data-detail-body]").innerHTML = `
      <div class="drawer-status-row">
        ${statusMarkup(course)}
        <span class="status-chip neutral">${escapeHtml(course.campus || course.place || "校区未提供")}</span>
        ${course.nature ? `<span class="status-chip neutral">${escapeHtml(course.nature)}</span>` : ""}
      </div>
      ${conflict}
      <div class="detail-grid" style="margin-top:${conflict ? "16px" : "0"}">
        <div class="detail-field"><div class="detail-label">教师</div><div class="detail-value">${escapeHtml(course.teacher)}</div></div>
        <div class="detail-field"><div class="detail-label">教学班</div><div class="detail-value">${escapeHtml(classNo)}${course.classNo ? " 班" : ""}</div></div>
        <div class="detail-field"><div class="detail-label">学分 / 学时</div><div class="detail-value">${escapeHtml(credits)} / ${escapeHtml(hours)}</div></div>
        <div class="detail-field"><div class="detail-label">容量</div><div class="detail-value">${escapeHtml(capacity)}</div></div>
        <div class="detail-field wide"><div class="detail-label">开课单位</div><div class="detail-value">${escapeHtml(department)}</div></div>
        <div class="detail-field wide"><div class="detail-label">教学班 ID</div><div class="detail-value mono">${escapeHtml(classId)}</div></div>
      </div>
      <div class="detail-section">
        <h3 class="detail-section-title">上课安排</h3>
        ${schedule}
      </div>
      <div class="detail-section">
        <h3 class="detail-section-title">任务建议</h3>
        <div class="mini-schedule">
          <div class="mini-schedule-row"><span class="day">首选</span><span>${escapeHtml(classNo)}${course.classNo ? " 班" : ""} · ${escapeHtml(course.teacher)}</span></div>
          <div class="mini-schedule-row"><span class="day">备选</span><span>加入同课程的其他教学班后，会按加入顺序自动接替。</span></div>
        </div>
      </div>
    `;
    $("[data-detail-scrim]").hidden = false;
    const drawer = $("[data-detail-drawer]");
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
  }

  function closeDetail() {
    $("[data-detail-scrim]").hidden = true;
    const drawer = $("[data-detail-drawer]");
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    state.currentDetail = null;
  }

  function addSelectedCoursesToQueue() {
    if (!state.selectedCourseIds.size) return;
    const courses = mock.courses.filter((course) => state.selectedCourseIds.has(course.id));
    let added = 0;
    const duplicates = [];
    const groupMap = new Map(state.groups.map((group) => [group.code, group]));
    courses.forEach((course) => {
      let group = groupMap.get(course.code);
      if (!group) {
        group = {
          id: `group-${course.code.toLowerCase()}`,
          code: course.code,
          name: course.name,
          state: "waiting",
          tasks: [],
        };
        state.groups.push(group);
        groupMap.set(course.code, group);
      }
      if (!group.tasks.some((task) => task.classId === course.classId)) {
        group.tasks.push({
          id: `task-${course.classId}`,
          classId: course.classId,
          classNo: course.classNo,
          teacher: course.teacher,
          campus: course.campus,
          time: course.time,
          state: "standby",
          attempts: 0,
          selected: course.selected,
          capacity: course.capacity,
        });
        added += 1;
      } else {
        duplicates.push({ course, group });
      }
    });
    state.selectedCourseIds.clear();
    renderCourses();
    renderGroups();
    if (added) {
      showInfo(`已加入 ${added} 个教学班；未自动开始抢课。`, "已加入抢课队列");
      pushLog(`[课程页] 批量加入 ${added} 个教学班，课程组保持待开始状态`, "INFO");
      const newest = $("[data-group-list]").lastElementChild;
      newest?.classList.add("is-new");
      newest?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    if (duplicates.length) openDuplicateModal("course-duplicate", duplicates);
  }

  function addAllBasket() {
    if (!state.basket.length) return;
    const courses = state.basket.map((id) => allCourseById.get(id)).filter(Boolean);
    const groupMap = new Map(state.groups.map((group) => [group.code, group]));
    let added = 0;
    const duplicates = [];
    courses.forEach((course) => {
      let group = groupMap.get(course.code);
      if (!group) {
        group = {
          id: `group-${course.code.toLowerCase()}`,
          code: course.code,
          name: course.name,
          state: "waiting",
          tasks: [],
        };
        state.groups.push(group);
        groupMap.set(course.code, group);
      }
      if (!group.tasks.some((task) => task.classId === course.classId)) {
        group.tasks.push({
          id: `task-${course.classId}`,
          classId: course.classId,
          classNo: course.classNo,
          teacher: course.teacher,
          campus: course.campus,
          time: course.time,
          state: "standby",
          attempts: 0,
          selected: course.selected,
          capacity: course.capacity,
        });
        added += 1;
      } else {
        duplicates.push({ course, group });
      }
    });
    state.basket = [];
    renderBasket();
    renderAllCourses();
    renderGroups();
    showInfo(`已创建 ${groupMap.size} 个课程组，共 ${added} 个教学班。`, "已加入抢课队列");
    pushLog(`[全校课程] 批量加入 ${added} 个教学班`, "INFO");
    if (duplicates.length) openDuplicateModal("basket-duplicate", duplicates);
  }

  function openDuplicateModal(action, duplicates = null) {
    state.activeModalAction = action;
    state.pendingDuplicates = duplicates || [];
    if (duplicates?.length) {
      restoreDuplicateModalDefaults();
      const first = duplicates[0];
      $("[data-modal-title]").textContent = "该教学班已在课程组中";
      $("[data-modal-copy]").textContent =
        duplicates.length > 1
          ? `有 ${duplicates.length} 个教学班已在组内。可以全部忽略，或把已有实例移动到组内末尾。`
          : "课程组内每个教学班只保留一个实例，可以选择忽略，或把已有实例移到备选末尾。";
      $("[data-modal-note]").textContent = `${first.course.name} · ${first.course.classNo} 班 · ${first.course.teacher}`;
      $('[data-action="modal-ignore"]').textContent = "忽略重复";
      $('[data-action="modal-move"]').textContent = "移到末尾";
    }
    $("[data-modal-scrim]").hidden = false;
    $("[data-modal]").hidden = false;
    $('[data-action="modal-ignore"]').focus();
  }

  function closeModal() {
    $("[data-modal-scrim]").hidden = true;
    $("[data-modal]").hidden = true;
    state.activeModalAction = null;
    state.pendingDuplicates = [];
  }

  function setSchedule() {
    const input = $("[data-schedule-input]");
    if (!input?.value) {
      showInfo("请选择定时时间后再设置。", "时间未设置");
      return;
    }
    const target = new Date(input.value);
    if (Number.isNaN(target.getTime())) {
      showInfo("定时时间格式无效。", "无法设置定时");
      return;
    }
    if (target.getTime() < Date.now()) {
      showInfo("已错过设定时间，将按规则立即启动所有待开始课程组。", "定时已过期");
    }
    state.schedule = target;
    $("[data-schedule-expand]").hidden = true;
    startCountdown();
    pushLog(`[全局定时] 已设置为 ${target.toLocaleString("zh-CN", { hour12: false })}`, "INFO");
  }

  function startCountdown() {
    clearInterval(state.countdownTimer);
    const tick = () => {
      const label = $("[data-countdown]");
      if (!label) return;
      if (!state.schedule) {
        label.textContent = "未设置";
        clearInterval(state.countdownTimer);
        return;
      }
      const diff = state.schedule.getTime() - Date.now();
      if (diff <= 0) {
        label.textContent = "即将启动";
        triggerScheduledStart();
        return;
      }
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      label.textContent = `距开始 ${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    };
    tick();
    state.countdownTimer = window.setInterval(tick, 1000);
  }

  function triggerScheduledStart() {
    if (!state.schedule) return;
    clearInterval(state.countdownTimer);
    state.schedule = null;
    $("[data-countdown]").textContent = "定时已触发";
    state.groups.forEach((group) => {
      if (group.state === "success") return;
      group.state = "running";
      group.tasks.forEach((task, index) => {
        task.state = index === 0 ? "active" : "standby";
      });
    });
    renderGroups();
    showInfo("全局定时已到，已从首选重新启动所有未成功课程组。", "定时启动", 5000);
    pushLog("[全局定时] 定时触发，所有课程组已按首选重新启动", "INFO");
    playSuccessTone();
  }

  function openColumnMenu(anchor) {
    const menu = document.createElement("div");
    menu.className = "menu-popover column-menu";
    menu.innerHTML = `
      <div style="padding:4px 7px 7px;color:var(--faint);font-size:8px;font-weight:700;letter-spacing:.08em">显示列</div>
      ${["capacity", "teacher", "time", "status"].map((column) => `
        <label class="column-option">
          <input class="checkbox" type="checkbox" checked data-column-toggle="${column}" />
          ${{ capacity: "余量", teacher: "教师", time: "时间地点", status: "状态" }[column]}
        </label>
      `).join("")}
    `;
    positionMenu(menu, anchor);
    $$("[data-column-toggle]", menu).forEach((input) => {
      input.addEventListener("change", () => {
        const column = input.dataset.columnToggle;
        $$(`[data-column="${column}"], [data-column-body="${column}"]`).forEach((node) => {
          node.hidden = !input.checked;
        });
      });
    });
  }

  function openCourseMenu(anchor, course) {
    const menu = document.createElement("div");
    menu.className = "menu-popover";
    menu.innerHTML = `
      <button class="menu-item" type="button" data-menu-detail>${ICONS.book} 查看详情</button>
      <button class="menu-item" type="button" data-menu-add>${ICONS.plus} 加入抢课队列</button>
      <div class="menu-separator"></div>
      <button class="menu-item danger" type="button" data-menu-remove>${ICONS.x} 从当前选择移除</button>
    `;
    positionMenu(menu, anchor);
    $("[data-menu-detail]", menu).addEventListener("click", () => {
      closePopover();
      openDetail(course);
    });
    $("[data-menu-add]", menu).addEventListener("click", () => {
      state.selectedCourseIds.add(course.id);
      renderCourses();
      closePopover();
      showInfo(`“${course.name}” ${course.classNo} 班已选中，可继续选择后批量加入。`, "已选择课程");
    });
    $("[data-menu-remove]", menu).addEventListener("click", () => {
      state.selectedCourseIds.delete(course.id);
      renderCourses();
      closePopover();
    });
  }

  function openTaskMenu(anchor, group, task) {
    const menu = document.createElement("div");
    menu.className = "menu-popover";
    menu.innerHTML = `
      <button class="menu-item" type="button" data-menu-stop>${ICONS.stop} 停止此教学班</button>
      <button class="menu-item" type="button" data-menu-move ${group.state === "running" ? "disabled title=\"运行中不可调整顺序\"" : ""}>${ICONS.clock} 移到组内末尾</button>
      <div class="menu-separator"></div>
      <button class="menu-item danger" type="button" data-menu-delete>${ICONS.x} 移除任务</button>
    `;
    positionMenu(menu, anchor);
    $("[data-menu-stop]", menu).addEventListener("click", () => {
      task.state = "paused";
      renderGroups();
      closePopover();
    });
    $("[data-menu-move]", menu).addEventListener("click", () => {
      if (group.state === "running") {
        showInfo("整组运行中不能调整首选/备选顺序，请先停止该课程组。", "顺序已锁定");
        return;
      }
      group.tasks = group.tasks.filter((item) => item.id !== task.id).concat(task);
      renderGroups();
      closePopover();
      showInfo("已将该任务移到组内末尾。", "顺序已调整");
    });
    $("[data-menu-delete]", menu).addEventListener("click", () => {
      group.tasks = group.tasks.filter((item) => item.id !== task.id);
      if (!group.tasks.length) state.groups = state.groups.filter((item) => item.id !== group.id);
      renderGroups();
      closePopover();
    });
  }

  function openGroupMenu(anchor, group) {
    const menu = document.createElement("div");
    menu.className = "menu-popover";
    menu.innerHTML = `
      <button class="menu-item" type="button" data-menu-reset>${ICONS.clock} 重置为待开始</button>
      <button class="menu-item" type="button" data-menu-schedule>${ICONS.play} 设置全局定时</button>
      <div class="menu-separator"></div>
      <button class="menu-item danger" type="button" data-menu-delete>${ICONS.x} 移除课程组</button>
    `;
    positionMenu(menu, anchor);
    $("[data-menu-reset]", menu).addEventListener("click", () => {
      group.state = "waiting";
      group.tasks.forEach((task) => {
        task.state = "standby";
      });
      renderGroups();
      closePopover();
    });
    $("[data-menu-schedule]", menu).addEventListener("click", () => {
      closePopover();
      $("[data-schedule-expand]").hidden = false;
    });
    $("[data-menu-delete]", menu).addEventListener("click", () => {
      state.groups = state.groups.filter((item) => item.id !== group.id);
      renderGroups();
      closePopover();
    });
  }

  function positionMenu(menu, anchor) {
    closePopover();
    $("[data-menu-root]").appendChild(menu);
    const rect = anchor.getBoundingClientRect();
    const top = Math.min(window.innerHeight - menu.offsetHeight - 10, rect.bottom + 4);
    const left = Math.min(window.innerWidth - menu.offsetWidth - 10, rect.right - menu.offsetWidth);
    menu.style.top = `${Math.max(10, top)}px`;
    menu.style.left = `${Math.max(10, left)}px`;
    setTimeout(() => {
      document.addEventListener("click", closePopoverOnce);
    }, 0);
  }

  function closePopoverOnce(event) {
    if (!$("[data-menu-root]")?.contains(event.target)) closePopover();
  }

  function closePopover() {
    $("[data-menu-root]").innerHTML = "";
    document.removeEventListener("click", closePopoverOnce);
  }

  function toggleSchedule(force) {
    const panel = $("[data-schedule-expand]");
    const trigger = $('[data-action="toggle-schedule"]');
    panel.hidden = typeof force === "boolean" ? !force : !panel.hidden;
    trigger.setAttribute("aria-expanded", String(!panel.hidden));
  }

  function toggleLog(force) {
    state.logOpen = typeof force === "boolean" ? force : !state.logOpen;
    const dock = $("[data-log-dock]");
    dock.classList.toggle("is-open", state.logOpen);
    $("[data-log-toggle]").setAttribute("aria-expanded", String(state.logOpen));
    if (state.logOpen) renderLogs();
  }

  function setupEvents() {
    $$("[data-page]").forEach((button) => {
      button.addEventListener("click", () => switchPage(button.dataset.page));
    });
    $("[data-course-body]").addEventListener("change", (event) => {
      const row = event.target.closest("tr[data-course-id]");
      if (!row) return;
      const id = row.dataset.courseId;
      if (event.target.matches("[data-course-check]")) {
        if (event.target.checked) state.selectedCourseIds.add(id);
        else state.selectedCourseIds.delete(id);
        renderCourses();
      }
    });
    $("[data-course-body]").addEventListener("click", (event) => {
      const detailButton = event.target.closest("[data-detail-course]");
      if (detailButton) {
        openDetail(courseById.get(detailButton.dataset.detailCourse));
        return;
      }
      const menuButton = event.target.closest("[data-course-menu]");
      if (menuButton) {
        openCourseMenu(menuButton, courseById.get(menuButton.dataset.courseMenu));
        return;
      }
      if (event.target.closest(".course-name-button") || event.target.closest("[data-course-check]")) return;
      const row = event.target.closest("tr[data-course-id]");
      if (row) {
        const check = $("[data-course-check]", row);
        check.checked = !check.checked;
        if (check.checked) state.selectedCourseIds.add(row.dataset.courseId);
        else state.selectedCourseIds.delete(row.dataset.courseId);
        renderCourses();
      }
    });
    $("[data-select-all]").addEventListener("change", (event) => {
      if (event.target.checked) mock.courses.forEach((course) => state.selectedCourseIds.add(course.id));
      else state.selectedCourseIds.clear();
      renderCourses();
    });
    $("[data-course-search]").addEventListener("input", () => {
      updateSearchClear();
      applyCourseFilters();
    });
    $("[data-course-search]").addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        applyLocalSearch();
      }
    });
    $$("[data-filter], [data-param]").forEach((control) => {
      if (control.matches(".switch")) {
        control.addEventListener("click", () => {
          const checked = control.getAttribute("aria-checked") === "true";
          control.setAttribute("aria-checked", String(!checked));
          if (control.dataset.filter) {
            state.localFilters[control.dataset.filter] = !checked;
            applyCourseFilters();
          }
          if (control.dataset.param === "auto-stop") {
            showInfo(!checked ? "抢到后自动停止本组其他任务。" : "抢到后继续运行，直到手动停止。", "抢到即停已切换");
          }
        });
      }
    });
    $("[data-campus-filter]").addEventListener("change", applyCourseFilters);
    $('[data-param="threads"]').addEventListener("change", updateThreadLoad);
    $$(".type-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        $$(".type-tab").forEach((item) => {
          item.classList.toggle("active", item === tab);
          item.setAttribute("aria-selected", String(item === tab));
        });
        showInfo(`已切换到“${tab.textContent}”课程类型；课程表会重新查询。`, "课程类型已切换");
      });
    });
    $$("[data-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.action;
        if (action === "toggle-filters") toggleFilters();
        if (action === "clear-search") {
          $("[data-course-search]").value = "";
          updateSearchClear();
          applyLocalSearch();
        }
        if (action === "focus-course-search") {
          $("[data-course-search]").focus();
        }
        if (action === "refresh-courses") {
          animateTopProgress();
          showInfo("课程数据已刷新；任务队列保持不变。", "刷新完成");
          pushLog("[课程页] 手动刷新课程列表，任务队列保留", "INFO");
        }
        if (action === "column-menu") openColumnMenu(button);
        if (action === "batch-add") addSelectedCoursesToQueue();
        if (action === "all-batch-add") addAllBasket();
        if (action === "load-all") loadAllCourses();
        if (action === "select-visible") {
          if (!state.allLoaded) {
            showInfo("请先加载全校课程。", "暂无可选课程");
            return;
          }
          mock.allCourses.forEach((course) => {
            if (!state.basket.includes(course.id)) state.basket.push(course.id);
          });
          renderAllCourses();
          renderBasket();
        }
        if (action === "refresh-selected") {
          showInfo("已刷新已选课程和课表。", "刷新完成");
          pushLog("[已选课程] 手动刷新课程与课表", "INFO");
        }
        if (action === "toggle-schedule") toggleSchedule();
        if (action === "set-schedule") setSchedule();
        if (action === "open-schedule") {
          switchPage("courses");
          toggleSchedule(true);
          $("[data-schedule-input]")?.focus();
        }
        if (action === "start-all") {
          state.groups.forEach((group) => {
            if (group.state === "success") return;
            group.state = "running";
            group.tasks.forEach((task, index) => {
              task.state = index === 0 ? "active" : "standby";
            });
          });
          renderGroups();
          showInfo("所有未成功课程组已从首选开始。", "已开始");
          pushLog("[课程组] 全部开始", "INFO");
        }
        if (action === "stop-all") {
          state.groups.forEach((group) => {
            if (group.state === "success") return;
            group.state = "paused";
            group.tasks.forEach((task) => {
              task.state = "paused";
            });
          });
          renderGroups();
          showInfo("所有运行中课程组已暂停。", "已停止");
          pushLog("[课程组] 全部停止", "INFO");
        }
        if (action === "mute") {
          state.muted = !state.muted;
          button.classList.toggle("is-muted", state.muted);
          button.setAttribute("aria-pressed", String(state.muted));
          button.setAttribute("aria-label", state.muted ? "开启提示音" : "静音提示音");
          showInfo(state.muted ? "当前会话已静音提示音。" : "提示音已恢复。", state.muted ? "静音" : "提示音");
        }
        if (action === "help") {
          showInfo("原型阶段使用占位数据；正式版会提供登录、查课、抢课与课表操作。", "帮助");
        }
        if (action === "logout") openLogoutModal();
        if (action === "close-info") $("[data-info-bar]").hidden = true;
        if (action === "close-detail") closeDetail();
        if (action === "detail-add") {
          if (state.currentDetail) {
            const course = state.currentDetail.course;
            state.selectedCourseIds.add(course.id);
            closeDetail();
            switchPage("courses");
            renderCourses();
            showInfo(`“${course.name}” ${course.classNo} 班已选中。`, "已加入选择");
          }
        }
        if (action === "modal-ignore") {
          closeModal();
          showInfo("已忽略重复教学班。", "未创建新任务");
        }
        if (action === "modal-move") {
          if (state.activeModalAction === "logout") {
            closeModal();
            showInfo("已清理演示任务并准备返回登录页。", "已退出登录");
            setTimeout(() => {
              window.location.href = "login.html";
            }, 650);
            return;
          }
          (state.pendingDuplicates || []).forEach(({ course, group }) => {
            const task = group.tasks.find((item) => item.classId === course.classId);
            if (task) {
              group.tasks = group.tasks.filter((item) => item.id !== task.id).concat(task);
            }
          });
          closeModal();
          renderGroups();
          showInfo("已将已有实例移到组内末尾。", "顺序已调整");
        }
        if (action === "modal-cancel") {
          if (state.activeModalAction === "logout") {
            closeModal();
            showInfo("原型保持当前演示会话；正式版本会返回登录弹窗。", "已取消退出");
          } else {
            closeModal();
          }
        }
        if (action === "log-bottom") {
          const list = $("[data-log-list]");
          state.logUserScrolled = false;
          list.scrollTop = list.scrollHeight;
          $("[data-action='log-bottom']").hidden = true;
        }
        if (action === "export-log") {
          const blob = new Blob(
            [state.logs.map((entry) => `${entry.time}\t${entry.level}\t${entry.message}`).join("\n")],
            { type: "text/plain;charset=utf-8" },
          );
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = "抢课日志_原型.txt";
          link.click();
          URL.revokeObjectURL(link.href);
          showInfo("已导出当前筛选结果。", "日志导出");
        }
        if (action === "clear-log") {
          state.logs = [];
          state.logUserScrolled = false;
          renderLogs();
          showInfo("本次会话日志已清空。", "日志清空");
        }
      });
    });
    $$("[data-group-list]").forEach((list) => {
      list.addEventListener("click", (event) => {
        const groupToggle = event.target.closest("[data-group-toggle]");
        if (groupToggle) {
          const card = groupToggle.closest(".group-card");
          if (card) card.classList.toggle("is-collapsed");
          return;
        }
        const start = event.target.closest("[data-group-start]");
        if (start) {
          const group = state.groups.find((item) => item.id === start.dataset.groupStart);
          if (!group) return;
          group.state = "running";
          group.tasks.forEach((task, index) => {
            task.state = index === 0 ? "active" : "standby";
          });
          renderGroups();
          return;
        }
        const pause = event.target.closest("[data-group-pause]");
        if (pause) {
          const group = state.groups.find((item) => item.id === pause.dataset.groupPause);
          if (!group) return;
          group.state = "paused";
          group.tasks.forEach((task) => {
            task.state = "paused";
          });
          renderGroups();
          return;
        }
        const stop = event.target.closest("[data-group-stop]");
        if (stop) {
          const group = state.groups.find((item) => item.id === stop.dataset.groupStop);
          if (!group) return;
          group.state = "paused";
          group.tasks.forEach((task) => {
            task.state = "paused";
          });
          renderGroups();
          return;
        }
        const taskMenu = event.target.closest("[data-task-menu]");
        if (taskMenu) {
          const task = state.groups
            .flatMap((group) => group.tasks.map((task) => ({ group, task })))
            .find((item) => item.task.id === taskMenu.dataset.taskMenu);
          if (task) openTaskMenu(taskMenu, task.group, task.task);
          return;
        }
        const groupMenu = event.target.closest("[data-group-menu]");
        if (groupMenu) {
          const group = state.groups.find((item) => item.id === groupMenu.dataset.groupMenu);
          if (group) openGroupMenu(groupMenu, group);
        }
      });
    });
    $$("[data-all-body]").forEach((body) => {
      body.addEventListener("change", (event) => {
        if (!event.target.matches("[data-all-check]")) return;
        const row = event.target.closest("tr[data-all-id]");
        const id = row?.dataset.allId;
        if (!id) return;
        if (event.target.checked) {
          if (!state.basket.includes(id)) state.basket.push(id);
        } else {
          state.basket = state.basket.filter((item) => item !== id);
        }
        renderAllCourses();
        renderBasket();
      });
      body.addEventListener("click", (event) => {
        const detailButton = event.target.closest("[data-detail-all]");
        if (detailButton) openDetail(allCourseById.get(detailButton.dataset.detailAll), "all");
      });
    });
    $("[data-all-select-all]").addEventListener("change", (event) => {
      if (!state.allLoaded) {
        event.target.checked = false;
        showInfo("请先加载全校课程。", "暂无可选课程");
        return;
      }
      state.basket = event.target.checked ? mock.allCourses.map((course) => course.id) : [];
      renderAllCourses();
      renderBasket();
    });
    $("[data-all-search]").addEventListener("input", renderAllCourses);
    $("[data-all-campus]").addEventListener("change", renderAllCourses);
    $("[data-basket-list]").addEventListener("click", (event) => {
      const remove = event.target.closest("[data-basket-remove]");
      if (!remove) return;
      state.basket = state.basket.filter((id) => id !== remove.dataset.basketRemove);
      renderBasket();
      renderAllCourses();
    });
    $("[data-batch-select]").addEventListener("change", (event) => {
      showInfo(`已切换到“${event.target.value}”；原型不会重新加载真实课程。`, "批次切换");
    });
    $("[data-group-list]").addEventListener("dragstart", (event) => {
      const task = event.target.closest("[data-task-id]");
      if (!task) return;
      const group = state.groups.find((item) => item.id === task.dataset.groupId);
      if (group?.state === "running") {
        event.preventDefault();
        showInfo("整组运行中不能调整首选/备选顺序，请先停止该课程组。", "顺序已锁定");
        return;
      }
      state.draggedTask = task;
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", task.dataset.taskId);
      task.classList.add("is-dragging");
    });
    $("[data-group-list]").addEventListener("dragend", () => {
      state.draggedTask?.classList.remove("is-dragging");
      state.draggedTask = null;
    });
    $("[data-group-list]").addEventListener("dragover", (event) => {
      const target = event.target.closest("[data-task-id]");
      if (!target || target === state.draggedTask) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
      target.style.borderColor = "var(--teal)";
    });
    $("[data-group-list]").addEventListener("dragleave", (event) => {
      const target = event.target.closest("[data-task-id]");
      if (target) target.style.borderColor = "";
    });
    $("[data-group-list]").addEventListener("drop", (event) => {
      const target = event.target.closest("[data-task-id]");
      if (!target || !state.draggedTask) return;
      const groupId = target.dataset.groupId;
      if (groupId !== state.draggedTask.dataset.groupId) {
        showInfo("只允许在同一课程组内调整首选和备选顺序。", "未移动");
        target.style.borderColor = "";
        return;
      }
      event.preventDefault();
      target.style.borderColor = "";
      const group = state.groups.find((item) => item.id === groupId);
      if (!group) return;
      const draggedId = state.draggedTask.dataset.taskId;
      const targetId = target.dataset.taskId;
      const tasks = [...group.tasks];
      const draggedIndex = tasks.findIndex((task) => task.id === draggedId);
      const targetIndex = tasks.findIndex((task) => task.id === targetId);
      const [dragged] = tasks.splice(draggedIndex, 1);
      tasks.splice(targetIndex, 0, dragged);
      group.tasks = tasks;
      renderGroups();
      showInfo("组内顺序已调整，首选与备选会按新顺序生效。", "顺序已保存");
    });
    $("[data-log-toggle]").addEventListener("click", () => toggleLog());
    $("[data-log-toggle]").addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") toggleLog();
    });
    $("[data-log-level]").addEventListener("change", renderLogs);
    $("[data-log-group]").addEventListener("change", renderLogs);
    $("[data-log-list]").addEventListener("scroll", () => {
      const list = $("[data-log-list]");
      const atBottom = list.scrollHeight - list.scrollTop - list.clientHeight < 16;
      state.logUserScrolled = !atBottom;
      $("[data-action='log-bottom']").hidden = atBottom;
    });
    $("[data-detail-scrim]").addEventListener("click", closeDetail);
    $("[data-modal-scrim]").addEventListener("click", closeModal);
    $("[data-drop-history] .drop-history-head").addEventListener("click", () => {
      const history = $("[data-drop-history]");
      const body = $("[data-drop-body]");
      const open = history.classList.toggle("is-open");
      body.hidden = !open;
      $(".drop-history-head", history).setAttribute("aria-expanded", String(open));
    });
    $("[data-drop-history] .drop-history-head").addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        $("[data-drop-history] .drop-history-head").click();
      }
    });
    $("[data-week-select]").addEventListener("change", (event) => {
      state.selectedWeek = event.target.value;
      renderTimetable();
    });
    document.querySelectorAll("[data-selected-body]").forEach((body) => {
      body.addEventListener("click", (event) => {
        const target = event.target.closest("[data-selected-detail]");
        if (target) openDetail(mock.selectedCourses.find((course) => course.id === target.dataset.selectedDetail), "selected");
      });
    });
    $("[data-timetable]").addEventListener("click", (event) => {
      const block = event.target.closest("[data-selected-detail]");
      if (block) openDetail(mock.selectedCourses.find((course) => course.id === block.dataset.selectedDetail), "selected");
    });
    window.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (!state.muted && state.logOpen) toggleLog(false);
      else if ($("[data-detail-drawer]").getAttribute("aria-hidden") === "false") closeDetail();
      else if (!$("[data-modal]").hidden) closeModal();
    });
  }

  function updateSearchClear() {
    const input = $("[data-course-search]");
    const clear = $('[data-action="clear-search"]');
    if (input && clear) clear.hidden = !input.value;
  }

  function applyLocalSearch() {
    applyCourseFilters();
  }

  function applyCourseFilters() {
    const keyword = ($("[data-course-search]")?.value || "").trim().toLowerCase();
    const campus = $("[data-campus-filter]")?.value || "";
    $$("[data-course-body] tr").forEach((row) => {
      const id = row.dataset.courseId;
      const course = courseById.get(id);
      if (!course) return;
      const matchesKeyword =
        !keyword ||
        `${course.name} ${course.teacher} ${course.code} ${course.classNo}`.toLowerCase().includes(keyword);
      const matchesCampus = !campus || course.campus === campus;
      const matchesAvailable = !state.localFilters.available || course.selected < course.capacity;
      const matchesConflict = !state.localFilters.conflict || course.conflict;
      row.hidden = !(matchesKeyword && matchesCampus && matchesAvailable && matchesConflict);
    });
  }

  function loadAllCourses() {
    if (state.allLoaded) {
      showInfo("全校课程已在当前会话中加载，可继续本地筛选。", "无需重复加载");
      return;
    }
    const progress = $("[data-all-progress]");
    const bar = $(".load-progress-bar span", progress);
    progress.querySelector("span:last-child").textContent = "正在加载 0 / 4455";
    let value = 0;
    const timer = window.setInterval(() => {
      value += 20;
      bar.style.width = `${Math.min(100, value)}%`;
      progress.querySelector("span:last-child").textContent = `正在加载 ${Math.min(4455, Math.round(4455 * value / 100))} / 4455`;
      if (value >= 100) {
        clearInterval(timer);
        state.allLoaded = true;
        progress.querySelector("span:last-child").textContent = "已加载 4455 条 · 本地筛选";
        renderAllCourses();
        showInfo("全部课程已加载，之后输入关键词只在本地过滤。", "加载完成");
        pushLog("[全校课程] 已加载 4455 条记录，切换为本地筛选", "INFO");
      }
    }, 120);
  }

  function animateTopProgress() {
    const bar = $("[data-top-progress]");
    if (!bar) return;
    bar.style.width = "18%";
    setTimeout(() => (bar.style.width = "62%"), 80);
    setTimeout(() => (bar.style.width = "100%"), 240);
    setTimeout(() => {
      bar.style.width = "0";
    }, 560);
  }

  function openLogoutModal() {
    $("[data-modal-title]").textContent = "退出当前账号？";
    $("[data-modal-copy]").textContent = "运行中或已定时的任务会先停止，确认后将清空本会话的课程与任务。";
    $("[data-modal-note]").textContent = "正式版本会重新显示登录弹窗，不会保存登录 token。";
    $('[data-action="modal-cancel"]').textContent = "取消";
    $('[data-action="modal-ignore"]').hidden = true;
    $('[data-action="modal-move"]').textContent = "先停止并退出";
    openDuplicateModal("logout");
  }

  function restoreDuplicateModalDefaults() {
    $('[data-action="modal-ignore"]').hidden = false;
    $('[data-action="modal-cancel"]').textContent = "取消";
    $('[data-action="modal-ignore"]').textContent = "忽略重复";
    $('[data-action="modal-move"]').textContent = "移到末尾";
  }

  function populateLogGroupFilter() {
    const select = $("[data-log-group]");
    if (!select) return;
    const current = select.value;
    select.innerHTML = [
      '<option value="all">全部课程组</option>',
      ...mock.groups.map((group) => `<option value="${escapeHtml(group.name)}">${escapeHtml(group.name)}</option>`),
    ].join("");
    select.value = [...select.options].some((option) => option.value === current) ? current : "all";
  }

  function init() {
    applySession();
    renderBatchSelect();
    renderCourses();
    renderAllCourses();
    renderBasket();
    renderGroups();
    renderSelected();
    renderWeekSelect();
    renderTimetable();
    renderLogs();
    setupEvents();
    populateLogGroupFilter();
    const requestedPage = new URLSearchParams(window.location.search).get("page");
    switchPage(["courses", "all-courses", "selected"].includes(requestedPage) ? requestedPage : "courses");
    const scheduleInput = $("[data-schedule-input]");
    if (scheduleInput) {
      const next = new Date(Date.now() + 10 * 60 * 1000);
      next.setSeconds(0, 0);
      const local = new Date(next.getTime() - next.getTimezoneOffset() * 60000).toISOString().slice(0, 19);
      scheduleInput.value = local;
    }
  }

  init();
})();
