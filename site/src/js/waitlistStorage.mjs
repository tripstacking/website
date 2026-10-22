export const WAITLIST_STORAGE_KEY = "tripstacking_waitlist_status";

/**
 * Reads persisted waitlist membership status from storage.
 *
 * @param {Pick<Storage, 'getItem'> | undefined} [storage]
 * @returns {{ joined: boolean, email: string, tier: string, joinedAt: string } | null}
 */
export function readWaitlistStatus(storage = globalThis?.localStorage) {
  if (!storage || typeof storage.getItem !== "function") {
    return null;
  }
  try {
    const raw = storage.getItem(WAITLIST_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || parsed.joined !== true) return null;
    return {
      joined: true,
      email: typeof parsed.email === "string" ? parsed.email : "",
      tier: "free",
      joinedAt: typeof parsed.joinedAt === "string" ? parsed.joinedAt : "",
    };
  } catch {
    return null;
  }
}

/**
 * Persists waitlist membership status to storage.
 * All waitlist entries default to the "free" tier.
 *
 * @param {{ email?: string, tier?: string }} [details]
 * @param {Pick<Storage, 'setItem' | 'getItem'> | undefined} [storage]
 */
export function saveWaitlistStatus(details = {}, storage = globalThis?.localStorage) {
  const existing = readWaitlistStatus(storage);
  const record = {
    joined: true,
    email:
      typeof details.email === "string" && details.email.trim()
        ? details.email.trim().toLowerCase()
        : existing?.email || "",
    tier: "free",
    joinedAt: existing?.joinedAt || new Date().toISOString(),
  };

  if (storage && typeof storage.setItem === "function") {
    try {
      storage.setItem(WAITLIST_STORAGE_KEY, JSON.stringify(record));
    } catch {
      // Ignore storage quota/privacy errors
    }
  }

  return record;
}

/**
 * Clears persisted waitlist status from storage.
 *
 * @param {Pick<Storage, 'removeItem'> | undefined} [storage]
 */
export function clearWaitlistStatus(storage = globalThis?.localStorage) {
  if (!storage || typeof storage.removeItem !== "function") {
    return;
  }
  try {
    storage.removeItem(WAITLIST_STORAGE_KEY);
  } catch {
    // Ignore storage errors
  }
}
