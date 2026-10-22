/**
 * User avatar resolution for Clerk authentication (social login avatar vs. Gravatar fallback for email-only users).
 */

const MD5_S = [
  7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
];

const MD5_K = Array.from({ length: 64 }, (_, i) =>
  Math.floor(Math.abs(Math.sin(i + 1)) * 0x100000000) >>> 0,
);

function rotateLeft32(value, shift) {
  return ((value << shift) | (value >>> (32 - shift))) >>> 0;
}

function wordToHexLittleEndian(word) {
  let out = "";
  for (let i = 0; i < 4; i++) {
    const byte = (word >>> (i * 8)) & 0xff;
    out += byte.toString(16).padStart(2, "0");
  }
  return out;
}

/**
 * Compute RFC 1321 MD5 hex digest for UTF-8 input string.
 * @param {string} input
 * @returns {string}
 */
export function md5Hex(input) {
  const utf8Bytes = new TextEncoder().encode(String(input ?? ""));
  const bitLenLow = (utf8Bytes.length * 8) >>> 0;
  const bitLenHigh = Math.floor((utf8Bytes.length * 8) / 0x100000000) >>> 0;

  const paddedLen = (((utf8Bytes.length + 8) >>> 6) + 1) << 6;
  const buffer = new Uint8Array(paddedLen);
  buffer.set(utf8Bytes);
  buffer[utf8Bytes.length] = 0x80;

  const view = new DataView(buffer.buffer);
  view.setUint32(paddedLen - 8, bitLenLow, true);
  view.setUint32(paddedLen - 4, bitLenHigh, true);

  let a0 = 0x67452301;
  let b0 = 0xefcdab89;
  let c0 = 0x98badcfe;
  let d0 = 0x10325476;

  const words = new Uint32Array(16);

  for (let offset = 0; offset < paddedLen; offset += 64) {
    for (let j = 0; j < 16; j++) {
      words[j] = view.getUint32(offset + j * 4, true);
    }

    let a = a0;
    let b = b0;
    let c = c0;
    let d = d0;

    for (let i = 0; i < 64; i++) {
      let f = 0;
      let g = 0;
      if (i < 16) {
        f = (b & c) | (~b & d);
        g = i;
      } else if (i < 32) {
        f = (d & b) | (~d & c);
        g = (5 * i + 1) % 16;
      } else if (i < 48) {
        f = b ^ c ^ d;
        g = (3 * i + 5) % 16;
      } else {
        f = c ^ (b | ~d);
        g = (7 * i) % 16;
      }

      const temp = d;
      d = c;
      c = b;
      const sum = (a + f + MD5_K[i] + words[g]) >>> 0;
      b = (b + rotateLeft32(sum, MD5_S[i])) >>> 0;
      a = temp;
    }

    a0 = (a0 + a) >>> 0;
    b0 = (b0 + b) >>> 0;
    c0 = (c0 + c) >>> 0;
    d0 = (d0 + d) >>> 0;
  }

  return (
    wordToHexLittleEndian(a0) +
    wordToHexLittleEndian(b0) +
    wordToHexLittleEndian(c0) +
    wordToHexLittleEndian(d0)
  );
}

/**
 * Build a Gravatar avatar URL for an email address.
 * @param {string} email
 * @param {{ size?: number, defaultImage?: string }} [options]
 * @returns {string}
 */
export function computeGravatarUrl(email, options = {}) {
  const { size = 80, defaultImage = "mp" } = options;
  const normalized = String(email ?? "")
    .trim()
    .toLowerCase();
  const hash = md5Hex(normalized);
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encodeURIComponent(defaultImage)}`;
}

/**
 * Extract primary email address from a Clerk user resource.
 * @param {any} user
 * @returns {string}
 */
export function extractPrimaryEmail(user) {
  if (!user) return "";
  if (typeof user.primaryEmailAddress?.emailAddress === "string") {
    return user.primaryEmailAddress.emailAddress.trim();
  }
  if (Array.isArray(user.emailAddresses) && user.emailAddresses.length > 0) {
    const first = user.emailAddresses[0]?.emailAddress;
    if (typeof first === "string") return first.trim();
  }
  if (typeof user.email === "string") {
    return user.email.trim();
  }
  return "";
}

/**
 * Extract a social provider or custom uploaded avatar URL from a Clerk user resource.
 * Returns null when the user only has an email account without a custom/social image.
 * @param {any} user
 * @returns {string | null}
 */
export function extractSocialAvatarUrl(user) {
  if (!user) return null;

  if (Array.isArray(user.externalAccounts)) {
    for (const account of user.externalAccounts) {
      const candidate = account?.imageUrl || account?.avatarUrl;
      if (typeof candidate === "string" && candidate.trim().length > 0) {
        return candidate.trim();
      }
    }
  }

  if (user.hasImage === true && typeof user.imageUrl === "string" && user.imageUrl.trim().length > 0) {
    return user.imageUrl.trim();
  }

  return null;
}

/**
 * Resolve the avatar URL and metadata for a signed-in Clerk user:
 * - Prefers social login avatar (or custom image) when available
 * - Falls back to Gravatar derived from the user's primary email when email-only
 * @param {any} user
 * @param {{ size?: number, defaultImage?: string }} [options]
 * @returns {{ url: string, source: "social" | "gravatar" | "fallback", email: string, displayName: string }}
 */
export function resolveUserAvatar(user, options = {}) {
  const email = extractPrimaryEmail(user);
  const displayName =
    user?.fullName ||
    user?.firstName ||
    user?.username ||
    (email ? email.split("@")[0] : "Waitlist Member");

  const socialUrl = extractSocialAvatarUrl(user);
  if (socialUrl) {
    return {
      url: socialUrl,
      source: "social",
      email,
      displayName,
    };
  }

  if (email) {
    return {
      url: computeGravatarUrl(email, options),
      source: "gravatar",
      email,
      displayName,
    };
  }

  return {
    url: user?.imageUrl || computeGravatarUrl("", options),
    source: "fallback",
    email: "",
    displayName,
  };
}
