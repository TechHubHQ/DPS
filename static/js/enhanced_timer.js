// Enhanced Timer Functionality for Dinner Polling System

class PollTimer {
  constructor(endTime, elementId = "timerDisplay") {
    this.endTime = endTime;
    this.elementId = elementId;
    this.interval = null;
    this.isActive = true;
    this.callbacks = {
      onTick: null,
      onEnd: null,
      onWarning: null,
    };

    this.init();
  }

  init() {
    this.updateDisplay();
    this.startTimer();
  }

  startTimer() {
    this.interval = setInterval(() => {
      this.updateDisplay();
    }, 1000);
  }

  stopTimer() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.isActive = false;
  }

  updateDisplay() {
    const now = new Date();
    const timeRemaining = this.endTime - now;

    if (timeRemaining <= 0) {
      this.handleTimerEnd();
      return;
    }

    const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
    const minutes = Math.floor(
      (timeRemaining % (1000 * 60 * 60)) / (1000 * 60)
    );
    const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

    const formattedTime = `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

    const element = document.getElementById(this.elementId);
    if (element) {
      element.textContent = `Poll ends in ${formattedTime}`;

      // Add warning styling when less than 30 minutes remain
      if (timeRemaining <= 30 * 60 * 1000) {
        element.classList.add("timer-warning");
        if (this.callbacks.onWarning) {
          this.callbacks.onWarning(timeRemaining);
        }
      }

      // Add critical styling when less than 5 minutes remain
      if (timeRemaining <= 5 * 60 * 1000) {
        element.classList.add("timer-critical");
      }
    }

    if (this.callbacks.onTick) {
      this.callbacks.onTick(timeRemaining);
    }
  }

  handleTimerEnd() {
    this.stopTimer();

    const element = document.getElementById(this.elementId);
    if (element) {
      element.textContent = "Poll Ended";
      element.classList.add("timer-ended");
      element.classList.remove("timer-warning", "timer-critical");
    }

    if (this.callbacks.onEnd) {
      this.callbacks.onEnd();
    }

    // Show notification if supported
    this.showNotification(
      "Poll Ended",
      "The dinner poll has ended. Thank you for participating!"
    );
  }

  showNotification(title, message) {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, {
        body: message,
        icon: "/static/favicon.ico",
        badge: "/static/favicon.ico",
      });
    }
  }

  requestNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }

  // Callback setters
  onTick(callback) {
    this.callbacks.onTick = callback;
    return this;
  }

  onEnd(callback) {
    this.callbacks.onEnd = callback;
    return this;
  }

  onWarning(callback) {
    this.callbacks.onWarning = callback;
    return this;
  }
}

// Enhanced UI Interactions
class UIEnhancements {
  constructor() {
    this.init();
  }

  init() {
    this.addSmoothScrolling();
    this.addFormValidation();
    this.addLoadingStates();
    this.addKeyboardShortcuts();
    this.addAccessibilityFeatures();
  }

  addSmoothScrolling() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      });
    });
  }
  addFormValidation() {
    // Enhanced form validation with real-time feedback
    const employeeIdInput = document.querySelector(
      'input[placeholder*="Employee ID"]'
    );
    if (employeeIdInput) {
      employeeIdInput.addEventListener("input", (e) => {
        const value = e.target.value;
        const isValid = /^\d+$/.test(value) && value.length > 0;
        e.target.classList.toggle("valid", isValid);
        e.target.classList.toggle("invalid", !isValid && value.length > 0);
      });
    }
  }

  addLoadingStates() {
    document.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", function () {
        if (!this.disabled) {
          this.classList.add("loading");
          this.innerHTML =
            '<span class="loading-spinner"></span> ' + this.textContent;
          // Remove loading state after 3 seconds (fallback)
          setTimeout(() => {
            this.classList.remove("loading");
            // Remove spinner, restore original text
            this.innerHTML = this.textContent.replace(/^.*?\s/, "");
          }, 3000);
        }
      });
    });
  }

  addKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
      // Ctrl/Cmd + Enter to submit form
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        const submitButton = document.querySelector(
          'button[type="primary"], button:contains("Submit")'
        );
        if (submitButton && !submitButton.disabled) {
          submitButton.click();
        }
      }
      // Escape to clear form
      if (e.key === "Escape") {
        const inputs = document.querySelectorAll(
          'input[type="text"], input[type="number"]'
        );
        inputs.forEach((input) => (input.value = ""));
      }
    });
  }

  addAccessibilityFeatures() {
    // Add ARIA labels and roles
    document.querySelectorAll(".status-card").forEach((card, index) => {
      card.setAttribute("role", "region");
      card.setAttribute("aria-label", `Status card ${index + 1}`);
    });

    // Add focus indicators
    document.querySelectorAll("button, input, select").forEach((element) => {
      element.addEventListener("focus", function () {
        this.classList.add("focused");
      });
      element.addEventListener("blur", function () {
        this.classList.remove("focused");
      });
    });
  }
}

// Progress Animation

class ProgressAnimator {
  constructor() {
    this.animateProgressBars();
    this.animateCounters();
  }

  animateProgressBars() {
    document.querySelectorAll(".progress-bar").forEach((bar) => {
      const width = bar.style.width || bar.getAttribute("data-width");
      if (width) {
        bar.style.width = "0%";
        setTimeout(() => {
          bar.style.width = width;
        }, 100);
      }
    });
  }

  animateCounters() {
    document.querySelectorAll(".metric-value").forEach((counter) => {
      const target = parseInt(counter.textContent);
      if (!isNaN(target)) {
        this.animateCounter(counter, 0, target, 1000);
      }
    });
  }

  animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    const updateCounter = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.floor(
        start + (end - start) * this.easeOutCubic(progress)
      );
      element.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      }
    };

    requestAnimationFrame(updateCounter);
  }

  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }
}

// Theme Manager
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem("pollTheme") || "light";
    this.init();
  }
  init() {
    this.applyTheme(this.currentTheme);
    this.addThemeToggle();
  }

  applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("pollTheme", theme);
    this.currentTheme = theme;
  }

  toggleTheme() {
    const newTheme = this.currentTheme === "light" ? "dark" : "light";
    this.applyTheme(newTheme);
  }

  addThemeToggle() {
    // Add theme toggle button if it doesn't exist
    if (!document.querySelector(".theme-toggle")) {
      const toggle = document.createElement("button");
      toggle.className = "theme-toggle";
      toggle.innerHTML = this.currentTheme === "light" ? "🌙" : "☀️";
      toggle.title = "Toggle theme";
      toggle.addEventListener("click", () => {
        this.toggleTheme();
        toggle.innerHTML = this.currentTheme === "light" ? "🌙" : "☀️";
      });
      // Add to header if it exists
      const header = document.querySelector(".main-header");
      if (header) {
        header.appendChild(toggle);
      }
    }
  }
}

// Initialize all enhancements when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Initialize UI enhancements
  new UIEnhancements();
  // Initialize progress animations
  new ProgressAnimator();
  // Initialize theme manager
  new ThemeManager();
  // Add custom styles for enhanced features
  const style = document.createElement("style");
  style.textContent = `
    .timer-warning {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        animation: pulse 1s infinite !important;
    }
    .timer-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        animation: pulse 0.5s infinite !important; 
    }
    .loading {
        opacity: 0.7;
        pointer-events: none;
    }
    .focused {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    input.valid {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1) !important;
    }
    input.invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1) !important;
    }
    .theme-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: rgba(255, 255, 255, 0.2);
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(1.1);
    }
    [data-theme=\"dark\"] {
        --primary-color: #8b9dc3;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
    }
    [data-theme=\"dark\"] body {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffffff;
    }
    [data-theme=\"dark\"] .status-card,
    [data-theme=\"dark\"] .poll-form,
    [data-theme=\"dark\"] .admin-panel {
        background: #2d2d2d;
        border-color: #404040;
    }`;
  document.head.appendChild(style);
});

// Export for use in Streamlit
window.PollTimer = PollTimer;
window.UIEnhancements = UIEnhancements;
window.ProgressAnimator = ProgressAnimator;
window.ThemeManager = ThemeManager;
