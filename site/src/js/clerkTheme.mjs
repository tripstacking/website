/**
 * Trip Stacking 60-30-10 brand palette appearance definitions for Clerk UI
 * in both light and dark modes.
 */

export const CLERK_LIGHT_APPEARANCE = {
  variables: {
    colorPrimary: "#1F8388",
    colorPrimaryForeground: "#F7FBF9",
    colorBackground: "#FFFFFF",
    colorForeground: "#1A2E35",
    colorNeutral: "#1A2E35",
    colorMuted: "#EBF3F0",
    colorMutedForeground: "#4D6A64",
    colorInput: "#F7FBF9",
    colorInputForeground: "#1A2E35",
    colorBorder: "#B5CCC5",
    colorRing: "rgba(43, 163, 168, 0.35)",
    colorModalBackdrop: "rgba(15, 29, 34, 0.65)",
    colorSuccess: "#3B8A43",
    colorWarning: "#D88E07",
    colorDanger: "#DC2626",
    borderRadius: "0.75rem",
    fontFamily: "InterVariable, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  options: {
    logoPlacement: "none",
  },
  elements: {
    cardBox: {
      border: "1px solid #D6E4DF",
      boxShadow: "0 12px 32px -8px rgba(26, 46, 53, 0.08)",
    },
    card: {
      backgroundColor: "#FFFFFF",
    },
    header: {
      display: "none",
    },
    headerTitle: {
      display: "none",
    },
    headerSubtitle: {
      display: "none",
    },
    socialButtonsBlockButton: {
      backgroundColor: "#F7FBF9",
      borderColor: "#8AA9A1",
      color: "#1A2E35",
    },
    formFieldInput: {
      backgroundColor: "#F7FBF9",
      borderColor: "#8AA9A1",
      color: "#1A2E35",
    },
    formButtonPrimary: {
      backgroundColor: "#1F8388",
      color: "#F7FBF9",
      fontWeight: "600",
    },
    footerActionLink: {
      color: "#1D696E",
      fontWeight: "600",
    },
  },
};

export const CLERK_DARK_APPEARANCE = {
  variables: {
    colorPrimary: "#44C0C5",
    colorPrimaryForeground: "#0F1D22",
    colorBackground: "#1A2E35",
    colorForeground: "#F7FBF9",
    colorNeutral: "#EBF3F0",
    colorMuted: "#0F1D22",
    colorMutedForeground: "#B5CCC5",
    colorInput: "#0F1D22",
    colorInputForeground: "#F7FBF9",
    colorBorder: "#243E47",
    colorRing: "rgba(68, 192, 197, 0.4)",
    colorModalBackdrop: "rgba(15, 29, 34, 0.8)",
    colorSuccess: "#77C57F",
    colorWarning: "#FFDE59",
    colorDanger: "#F87171",
    borderRadius: "0.75rem",
    fontFamily: "InterVariable, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  options: {
    logoPlacement: "none",
  },
  elements: {
    cardBox: {
      border: "1px solid #3D5450",
      boxShadow: "0 16px 40px -8px rgba(0, 0, 0, 0.45)",
    },
    card: {
      backgroundColor: "#1A2E35",
    },
    header: {
      display: "none",
    },
    headerTitle: {
      display: "none",
    },
    headerSubtitle: {
      display: "none",
    },
    socialButtonsBlockButton: {
      backgroundColor: "#0F1D22",
      borderColor: "#3D5450",
      color: "#F7FBF9",
    },
    formFieldInput: {
      backgroundColor: "#0F1D22",
      borderColor: "#3D5450",
      color: "#F7FBF9",
    },
    formButtonPrimary: {
      backgroundColor: "#44C0C5",
      color: "#0F1D22",
      fontWeight: "600",
    },
    footerActionLink: {
      color: "#44C0C5",
      fontWeight: "600",
    },
  },
};

const APPEARANCE_BY_MODE = {
  light: CLERK_LIGHT_APPEARANCE,
  dark: CLERK_DARK_APPEARANCE,
};

/**
 * Returns the Clerk appearance object for the given color mode ('light' | 'dark').
 * When `hideHeader` is false (used by `<Waitlist />` so its post-submit confirmation
 * header remains visible), `headerTitle` and `headerSubtitle` are styled with the
 * Trip Stacking palette instead of `display: 'none'`.
 *
 * @param {'light' | 'dark'} [mode='light']
 * @param {{ hideHeader?: boolean }} [options]
 */
export function getClerkAppearance(mode = "light", options = {}) {
  const isDark = mode === "dark";
  const base = APPEARANCE_BY_MODE[isDark ? "dark" : "light"];
  const { hideHeader = true } = options;

  if (hideHeader) {
    return base;
  }

  return {
    ...base,
    elements: {
      ...base.elements,
      header: {
        textAlign: "center",
      },
      headerTitle: {
        color: isDark ? "#F7FBF9" : "#1A2E35",
        fontWeight: "700",
        fontSize: "1.25rem",
      },
      headerSubtitle: {
        color: isDark ? "#B5CCC5" : "#4D6A64",
        fontSize: "0.9375rem",
      },
    },
  };
}

/**
 * Detects whether dark mode is currently active on the document root or persisted in localStorage.
 */
export function detectCurrentThemeMode() {
  if (typeof document !== "undefined" && document.documentElement?.classList?.contains("dark")) {
    return "dark";
  }
  try {
    if (typeof localStorage !== "undefined" && localStorage.getItem("colorTheme") === "dark") {
      return "dark";
    }
  } catch {
    // Ignore storage access errors
  }
  return "light";
}

/**
 * Synchronizes Clerk's global appearance and any mounted SignIn/SignUp/Waitlist components
 * with the active site theme ('light' or 'dark').
 *
 * @param {(opts: { appearance: object }) => void} [updateClerkOptionsFn]
 */
export function syncClerkAppearanceWithTheme(updateClerkOptionsFn) {
  if (typeof window === "undefined") return;
  const mode = detectCurrentThemeMode();
  const defaultAppearance = getClerkAppearance(mode, { hideHeader: true });
  const waitlistAppearance = getClerkAppearance(mode, { hideHeader: false });

  const propMap = window.__astro_clerk_component_props;
  if (propMap && typeof propMap.get === "function") {
    for (const [category, mountFn, componentAppearance] of [
      ["sign-in", "mountSignIn", defaultAppearance],
      ["sign-up", "mountSignUp", defaultAppearance],
      ["waitlist", "mountWaitlist", waitlistAppearance],
    ]) {
      const categoryMap = propMap.get(category);
      if (categoryMap && typeof categoryMap.forEach === "function") {
        categoryMap.forEach((props, id) => {
          if (props && typeof props === "object") {
            props.appearance = componentAppearance;
          }
          const el = document.querySelector(`[data-clerk-id="${id}"]`);
          if (el && window.Clerk?.loaded && typeof window.Clerk[mountFn] === "function") {
            window.Clerk[mountFn](el, props);
          }
        });
      }
    }
  }

  if (typeof updateClerkOptionsFn === "function" && window.Clerk?.loaded) {
    try {
      const hasWaitlistOnPage = !!document.querySelector('[data-clerk-id^="clerk-waitlist"]');
      updateClerkOptionsFn({
        appearance: hasWaitlistOnPage ? waitlistAppearance : defaultAppearance,
      });
    } catch {
      // Ignore if Clerk instance is still initializing
    }
  }
}
