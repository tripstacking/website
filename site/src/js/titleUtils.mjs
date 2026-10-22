export const SITE_TITLE_PREFIX = "Trip Stacking - ";

/**
 * Formats any page title so that all pages consistently start with "Trip Stacking - ".
 *
 * @param {string | undefined | null} rawTitle
 * @returns {string}
 */
export function formatPageTitle(rawTitle) {
  const trimmed = typeof rawTitle === "string" ? rawTitle.trim() : "";
  if (!trimmed) {
    return `${SITE_TITLE_PREFIX}STACK YOUR STOPS. OWN YOUR WEEK.`;
  }
  if (trimmed.startsWith(SITE_TITLE_PREFIX)) {
    return trimmed;
  }
  const stripped = trimmed.replace(/^Trip Stacking\s*[-—–:]\s*/i, "").trim();
  if (!stripped || /^Trip Stacking$/i.test(stripped)) {
    return `${SITE_TITLE_PREFIX}STACK YOUR STOPS. OWN YOUR WEEK.`;
  }
  return `${SITE_TITLE_PREFIX}${stripped}`;
}
