/* Cross-page guided tour using driver.js.
 *
 * Stops list a `route` (path) and a `selector`. When a Next click crosses
 * routes, the in-flight state is persisted to localStorage and the page
 * navigates; tour.js picks back up on DOMContentLoaded.
 *
 * Triggers: persistent "?" button in the nav (#help-btn) and first-visit
 * auto-start chained off the welcome modal's dismissal.
 */
(function () {
  if (!window.driver || !window.driver.js) return;
  const driver = window.driver.js.driver;

  const STATE_KEY = 'claudio-tour';
  const SEEN_KEY  = 'claudio-tour-seen';

  const STEPS = [
    {
      route: '/',
      element: '.nav-brand',
      popover: {
        title: 'Welcome to claudio',
        description: 'A local browser for your Claude Code sessions stored in ~/.claude/. This quick tour shows the main surfaces.',
      },
    },
    {
      route: '/',
      element: '#search',
      popover: {
        title: 'Search',
        description: 'Filter sessions by title or project path. Matches highlight inline.',
      },
    },
    {
      route: '/',
      element: '.session-card',
      popover: {
        title: 'A session',
        description: 'Each card is one Claude Code conversation. Click to open its transcript, todos, and memory.',
      },
    },
    {
      route: '/',
      element: '.badge-mem',
      popover: {
        title: 'Project memory',
        description: 'Projects with memory files show this badge. Click it to browse them.',
      },
    },
    {
      route: '/',
      element: '.stats-btn',
      popover: {
        title: 'Stats',
        description: 'Cost, activity, and per-project breakdowns. Heading there next.',
      },
    },
    {
      route: '/stats',
      element: '#filterToggle',
      popover: {
        title: 'Date filter',
        description: 'Narrow the stats to a window: last 7, 30, 90 days, or a custom range.',
      },
    },
    {
      route: '/stats',
      element: '.heatmap-card',
      popover: {
        title: 'Activity heatmap',
        description: 'Your work over time. Toggle between cost, session count, or both.',
      },
    },
    {
      route: '/stats',
      element: '.cumulative-card',
      popover: {
        title: 'Cumulative cost',
        description: 'Total spend marching forward over time. Flat stretches are quiet weeks; steep climbs are heavy ones.',
      },
    },
    {
      route: '/stats',
      element: '.cost-grid-wrap',
      popover: {
        title: 'Cost breakdowns',
        description: 'Spend grouped by project on the left, and your most expensive individual sessions on the right.',
      },
    },
    {
      route: '/stats',
      element: 'a.theme-btn[download]',
      popover: {
        title: 'Export',
        description: 'Download every session as portable JSON. Useful for backups or sharing.',
      },
    },
    {
      route: '/stats',
      element: '#help-btn',
      popover: {
        title: 'Replay anytime',
        description: 'Click this question mark whenever you want to run the tour again.',
      },
    },
  ];

  function loadState() {
    try {
      const raw = localStorage.getItem(STATE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveState(s) {
    localStorage.setItem(STATE_KEY, JSON.stringify(s));
  }

  function finishTour() {
    localStorage.removeItem(STATE_KEY);
    localStorage.setItem(SEEN_KEY, 'true');
  }

  function visibleStepsOnPage(path) {
    // Filter out any step whose anchor isn't in the DOM. Some anchors are
    // conditionally rendered (memory badge, session card, heatmap card),
    // and the rest are belt-and-braces against future template churn.
    return STEPS
      .map((step, i) => ({ step, originalIndex: i }))
      .filter(({ step }) => step.route === path)
      .filter(({ step }) => document.querySelector(step.element));
  }

  function startFromGlobal(globalIdx) {
    if (globalIdx >= STEPS.length) {
      finishTour();
      return;
    }
    const path = window.location.pathname;
    const target = STEPS[globalIdx];
    if (target.route !== path) {
      saveState({ index: globalIdx });
      window.location.href = target.route;
      return;
    }

    const pageSteps = visibleStepsOnPage(path);
    let activeIdx = pageSteps.findIndex(s => s.originalIndex === globalIdx);
    if (activeIdx === -1) {
      // Requested step is on this page but its anchor is missing (optional+absent).
      // Advance to the next global step.
      startFromGlobal(globalIdx + 1);
      return;
    }

    const dSteps = pageSteps.map(({ step, originalIndex }) => ({
      element: step.element,
      popover: step.popover,
      _orig: originalIndex,
    }));

    const d = driver({
      showProgress: true,
      allowClose: true,
      animate: true,
      smoothScroll: true,
      overlayOpacity: 0.55,
      stagePadding: 6,
      nextBtnText: 'Next',
      prevBtnText: 'Back',
      doneBtnText: 'Done',
      progressText: '{{current}} of {{total}}',
      onCloseClick: () => {
        finishTour();
        d.destroy();
      },
      onNextClick: () => {
        const cur = d.getActiveIndex();
        const curOrig = dSteps[cur]._orig;
        // Next stop on this page: let driver handle it.
        if (cur + 1 < dSteps.length) {
          saveState({ index: dSteps[cur + 1]._orig });
          d.moveNext();
          return;
        }
        // Done with this page; either navigate or finish.
        const nextGlobal = curOrig + 1;
        if (nextGlobal >= STEPS.length) {
          finishTour();
          d.destroy();
          return;
        }
        const nextTarget = STEPS[nextGlobal];
        saveState({ index: nextGlobal });
        d.destroy();
        if (nextTarget.route !== path) {
          window.location.href = nextTarget.route;
        } else {
          startFromGlobal(nextGlobal);
        }
      },
      onPrevClick: () => {
        const cur = d.getActiveIndex();
        if (cur > 0) {
          saveState({ index: dSteps[cur - 1]._orig });
          d.movePrevious();
          return;
        }
        const curOrig = dSteps[cur]._orig;
        const prevGlobal = curOrig - 1;
        if (prevGlobal < 0) return;
        const prevTarget = STEPS[prevGlobal];
        saveState({ index: prevGlobal });
        d.destroy();
        if (prevTarget.route !== path) {
          window.location.href = prevTarget.route;
        } else {
          startFromGlobal(prevGlobal);
        }
      },
      steps: dSteps,
    });

    saveState({ index: globalIdx });
    d.drive(activeIdx);
  }

  window.startClaudioTour = function () {
    saveState({ index: 0 });
    if (window.location.pathname !== '/') {
      window.location.href = '/';
      return;
    }
    startFromGlobal(0);
  };

  document.addEventListener('DOMContentLoaded', function () {
    const helpBtn = document.getElementById('help-btn');
    if (helpBtn) {
      helpBtn.addEventListener('click', function (e) {
        e.preventDefault();
        window.startClaudioTour();
      });
    }

    const state = loadState();
    if (state && typeof state.index === 'number') {
      startFromGlobal(state.index);
      return;
    }

    // First-visit auto-start: wait for the welcome modal to be acknowledged,
    // then run the tour. The welcome modal exposes window.dismissModal; we
    // wrap it so the tour fires immediately after the user clicks "I Understand".
    if (localStorage.getItem(SEEN_KEY)) return;

    if (localStorage.getItem('claudio-first-launch-acknowledged')) {
      // Modal already acknowledged on a previous visit; start shortly.
      setTimeout(window.startClaudioTour, 400);
      return;
    }

    const orig = window.dismissModal;
    if (typeof orig === 'function') {
      window.dismissModal = function () {
        orig();
        if (!localStorage.getItem(SEEN_KEY)) {
          setTimeout(window.startClaudioTour, 300);
        }
      };
    }
  });
})();
