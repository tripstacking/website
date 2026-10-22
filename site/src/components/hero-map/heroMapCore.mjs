/**
 * Shared core logic for the Trip Stacking Apple Maps Hero Background.
 * Provides Web Mercator tile math, Apple MapKit tile URL construction,
 * geolocation fallback (Portland, OR), and screen-bounds random route generation (3-8 stops).
 */

export const DEFAULT_LOCATION = Object.freeze({
  lat: 45.5152,
  lng: -122.6784,
  label: "Portland, OR",
});

export const DEFAULT_ZOOM = 12;
export const TILE_SIZE = 256;
export const MIN_STOPS = 3;
export const MAX_STOPS = 8;

export const BRAND_COLORS = Object.freeze({
  horizonTeal: "#44C0C5",
  flowGreen: "#77C57F",
  beaconYellow: "#FFDE59",
  harborSlate: "#1A2E35",
  alabasterMint: "#F7FBF9",
  harborNight: "#0F1D22",
});

const STOP_PALETTE = Object.freeze([
  BRAND_COLORS.beaconYellow,
  BRAND_COLORS.flowGreen,
  BRAND_COLORS.horizonTeal,
]);

const INTERMEDIATE_ERRANDS = Object.freeze([
  { name: "First Federal Bank", detail: "15m • Before Hardware" },
  { name: "Pacific Hardware", detail: "20m • 0 Left Turns" },
  { name: "Pearl Dry Cleaners", detail: "10m • Low-Crowd Window" },
  { name: "Rose City Pharmacy", detail: "12m • Drive-Thru Ready" },
  { name: "Neighborhood Post", detail: "10m • Right-Turn Loop" },
  { name: "Powell's Pickup", detail: "15m • Curbside Window" },
  { name: "Roastery & Bakery", detail: "10m • Morning Window" },
]);

const FINAL_ERRAND = Object.freeze({
  name: "Harbor Market Groceries",
  detail: "25m • Pinned Last (Cold)",
});

/**
 * Convert latitude and longitude to fractional Web Mercator tile coordinates.
 */
export function latLngToTileXY(lat, lng, zoom = DEFAULT_ZOOM) {
  const scale = 2 ** zoom;
  const clampedLat = Math.max(-85.0511, Math.min(85.0511, lat));
  const latRad = (clampedLat * Math.PI) / 180;
  const x = ((lng + 180) / 360) * scale;
  const y =
    ((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) *
    scale;
  return { x, y };
}

/**
 * Compute all 256x256 map tiles required to cover a viewport of (width x height)
 * centered at (lat, lng) at the given zoom level.
 */
export function computeViewportTiles(
  lat,
  lng,
  zoom = DEFAULT_ZOOM,
  width = 1440,
  height = 800,
) {
  const safeWidth = Math.max(320, width);
  const safeHeight = Math.max(320, height);
  const center = latLngToTileXY(lat, lng, zoom);
  const centerPixelX = center.x * TILE_SIZE;
  const centerPixelY = center.y * TILE_SIZE;

  const topLeftPixelX = centerPixelX - safeWidth / 2;
  const topLeftPixelY = centerPixelY - safeHeight / 2;

  const minTileX = Math.floor(topLeftPixelX / TILE_SIZE);
  const maxTileX = Math.floor((topLeftPixelX + safeWidth) / TILE_SIZE);
  const minTileY = Math.floor(topLeftPixelY / TILE_SIZE);
  const maxTileY = Math.floor((topLeftPixelY + safeHeight) / TILE_SIZE);
  const maxIndex = 2 ** zoom;

  const tiles = [];
  for (let ty = minTileY; ty <= maxTileY; ty++) {
    if (ty < 0 || ty >= maxIndex) continue;
    for (let tx = minTileX; tx <= maxTileX; tx++) {
      const wrappedX = ((tx % maxIndex) + maxIndex) % maxIndex;
      tiles.push({
        x: wrappedX,
        y: ty,
        z: zoom,
        left: Math.round(tx * TILE_SIZE - topLeftPixelX),
        top: Math.round(ty * TILE_SIZE - topLeftPixelY),
      });
    }
  }
  return tiles;
}

/**
 * Build an Apple MapKit raster tile URL (`cdn.apple-mapkit.com/ti/tile`),
 * or fallback tile URL when accessKey is empty.
 */
export function buildAppleMapsTileUrl({
  x,
  y,
  z = DEFAULT_ZOOM,
  accessKey = "",
  version = "2610193",
  dark = true,
  lang = "en",
}) {
  if (!accessKey) {
    return buildFallbackTileUrl({ x, y, z, dark });
  }
  const tintParam = dark ? "&tint=dark" : "";
  return (
    `https://cdn.apple-mapkit.com/ti/tile?style=0&size=1` +
    `&x=${x}&y=${y}&z=${z}&scale=2&lang=${encodeURIComponent(lang)}` +
    `&v=${encodeURIComponent(version)}&poi=1${tintParam}` +
    `&accessKey=${encodeURIComponent(accessKey)}`
  );
}

/**
 * Fallback high-DPI tile URL if Apple MapKit accessKey is expired or offline.
 */
export function buildFallbackTileUrl({ x, y, z = DEFAULT_ZOOM, dark = true }) {
  const subdomains = ["a", "b", "c", "d"];
  const sub = subdomains[Math.abs(x + y) % subdomains.length];
  const style = dark ? "dark_all" : "voyager";
  return `https://${sub}.basemaps.cartocdn.com/rastertiles/${style}/${z}/${x}/${y}@2x.png`;
}

/**
 * Determine whether an existing loaded tile `<img>` can be reused as-is without
 * updating its `src`. Returns false if the element is currently showing a fallback
 * tile while a distinct Apple Maps `primaryUrl` is available and has not failed.
 */
export function shouldReuseLoadedTile({
  currentSrc = "",
  primaryUrl = "",
  complete = false,
  naturalWidth = 0,
  failedPrimarySrc = "",
} = {}) {
  if (!complete || naturalWidth <= 0 || !currentSrc) {
    return false;
  }
  if (currentSrc === primaryUrl) {
    return true;
  }
  return Boolean(failedPrimarySrc && failedPrimarySrc === primaryUrl);
}

/**
 * Resolve the target `src` for a tile `<img>` element, upgrading fallback tiles
 * to `primaryUrl` unless `primaryUrl` already failed to load.
 */
export function resolveTileImageSrc({
  currentSrc = "",
  primaryUrl = "",
  fallbackUrl = "",
  failedPrimarySrc = "",
} = {}) {
  if (primaryUrl && failedPrimarySrc !== primaryUrl) {
    return primaryUrl;
  }
  return fallbackUrl || currentSrc;
}

function distanceBetween(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function segmentsIntersect(p1, p2, p3, p4) {
  const ccw = (a, b, c) => (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x);
  return (
    ccw(p1, p3, p4) !== ccw(p2, p3, p4) && ccw(p1, p2, p3) !== ccw(p1, p2, p4)
  );
}

/**
 * Order random points into a clean, non-crossing Trip Stacking route.
 */
function orderPointsSmoothly(points) {
  if (points.length <= 2) return [...points];

  const remaining = [...points].sort((a, b) => a.x - b.x);
  const ordered = [remaining.shift()];

  while (remaining.length > 0) {
    const current = ordered[ordered.length - 1];
    let bestIdx = 0;
    let bestDist = Infinity;
    for (let i = 0; i < remaining.length; i++) {
      const d = distanceBetween(current, remaining[i]);
      if (d < bestDist) {
        bestDist = d;
        bestIdx = i;
      }
    }
    ordered.push(remaining.splice(bestIdx, 1)[0]);
  }

  // 2-opt uncrossing pass so the route never crosses itself
  for (let pass = 0; pass < 6; pass++) {
    let improved = false;
    for (let i = 0; i < ordered.length - 2; i++) {
      for (let j = i + 2; j < ordered.length - 1; j++) {
        if (
          segmentsIntersect(ordered[i], ordered[i + 1], ordered[j], ordered[j + 1])
        ) {
          const reversed = ordered.slice(i + 1, j + 1).reverse();
          ordered.splice(i + 1, j - i, ...reversed);
          improved = true;
        }
      }
    }
    if (!improved) break;
  }

  return ordered;
}

/**
 * Convert an ordered array of {x, y} points into a smooth cubic Bezier SVG path.
 */
export function buildSmoothRouteSvgPath(points) {
  if (points.length === 0) return "";
  if (points.length === 1) return `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)}`;

  let d = `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)}`;
  const tension = 0.28;

  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[Math.max(0, i - 1)];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[Math.min(points.length - 1, i + 2)];

    const cp1x = p1.x + (p2.x - p0.x) * tension;
    const cp1y = p1.y + (p2.y - p0.y) * tension;
    const cp2x = p2.x - (p3.x - p1.x) * tension;
    const cp2y = p2.y - (p3.y - p1.y) * tension;

    d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }

  return d;
}

/**
 * Build a smooth curved SVG path from the final stop back to the first stop (origin/home),
 * bowing gently outward from the intermediate stops' centroid so the return-to-home leg
 * reads as a clean loop without slicing across the primary route.
 */
export function buildReturnHomeSvgPath(
  lastStop,
  firstStop,
  stops = [],
  width = 1440,
  height = 800,
) {
  if (!lastStop || !firstStop) return "";

  const midX = (lastStop.x + firstStop.x) / 2;
  const midY = (lastStop.y + firstStop.y) / 2;
  const dx = firstStop.x - lastStop.x;
  const dy = firstStop.y - lastStop.y;
  const span = Math.hypot(dx, dy) || 1;

  // Unit normal perpendicular to the chord (lastStop -> firstStop)
  let nx = -dy / span;
  let ny = dx / span;

  // Choose the normal direction that bows away from the average of intermediate stops
  if (stops.length > 2) {
    let sumX = 0;
    let sumY = 0;
    for (let i = 1; i < stops.length - 1; i++) {
      sumX += stops[i].x;
      sumY += stops[i].y;
    }
    const centroidX = sumX / (stops.length - 2);
    const centroidY = sumY / (stops.length - 2);
    const toCentroidDot = (centroidX - midX) * nx + (centroidY - midY) * ny;
    if (toCentroidDot > 0) {
      nx = -nx;
      ny = -ny;
    }
  } else if (ny < 0) {
    nx = -nx;
    ny = -ny;
  }

  const arcOffset = Math.min(Math.max(span * 0.24, 65), Math.min(width, height) * 0.26);
  const pad = 42;
  const cpX = Math.max(pad, Math.min(width - pad, midX + nx * arcOffset));
  const cpY = Math.max(pad, Math.min(height - pad, midY + ny * arcOffset));

  return (
    `M ${lastStop.x.toFixed(1)} ${lastStop.y.toFixed(1)} ` +
    `Q ${cpX.toFixed(1)} ${cpY.toFixed(1)}, ${firstStop.x.toFixed(1)} ${firstStop.y.toFixed(1)}`
  );
}

function computeRouteBoundsBox(width = 1440, height = 800) {
  const safeW = Math.max(360, Math.round(width));
  const safeH = Math.max(360, Math.round(height));
  const padX = Math.min(safeW * 0.18, Math.max(64, safeW * 0.08));
  const padTop = Math.min(safeH * 0.24, Math.max(88, safeH * 0.14));
  const padBottom = Math.min(safeH * 0.22, Math.max(76, safeH * 0.12));
  const usableW = Math.max(160, safeW - padX * 2);
  const usableH = Math.max(140, safeH - padTop - padBottom);
  return { safeW, safeH, padX, padTop, padBottom, usableW, usableH };
}

/**
 * Randomly place 3 to 8 stops within the bounds of the screen and build
 * a branded Trip Stacking route, optional return-to-home loop, and marker descriptors.
 */
export function generateRandomRouteForBounds(
  width = 1440,
  height = 800,
  rng = Math.random,
  options = {},
) {
  const { returnToHome = true } = options ?? {};
  const { safeW, safeH, padX, padTop, usableW, usableH } =
    computeRouteBoundsBox(width, height);

  const stopCount =
    MIN_STOPS + Math.floor(rng() * (MAX_STOPS - MIN_STOPS + 1));

  const minSeparation = Math.min(usableW, usableH) / (stopCount + 1.5);

  const rawPoints = [];
  for (let i = 0; i < stopCount; i++) {
    // Stratified horizontal bands with random jitter so stops span nicely across screen bounds
    const bandStart = i / stopCount;
    const bandEnd = (i + 1) / stopCount;
    let candidate = null;

    for (let attempt = 0; attempt < 20; attempt++) {
      const rx = bandStart + (bandEnd - bandStart) * (0.15 + 0.7 * rng());
      const ry = 0.08 + 0.84 * rng();
      const pt = {
        x: Math.round(padX + rx * usableW),
        y: Math.round(padTop + ry * usableH),
      };
      const tooClose = rawPoints.some(
        (existing) => distanceBetween(existing, pt) < minSeparation,
      );
      candidate = pt;
      if (!tooClose) break;
    }
    rawPoints.push(candidate);
  }

  const orderedPoints = orderPointsSmoothly(rawPoints);

  const stops = orderedPoints.map((pt, idx) => {
    const isFirst = idx === 0;
    const isLast = idx === orderedPoints.length - 1;
    const color = isFirst
      ? BRAND_COLORS.beaconYellow
      : isLast
        ? BRAND_COLORS.horizonTeal
        : STOP_PALETTE[idx % STOP_PALETTE.length];

    const errand = isLast
      ? FINAL_ERRAND
      : INTERMEDIATE_ERRANDS[idx % INTERMEDIATE_ERRANDS.length];

    return {
      number: idx + 1,
      x: pt.x,
      y: pt.y,
      color,
      name: errand.name,
      detail: errand.detail,
    };
  });

  const svgPath = buildSmoothRouteSvgPath(stops);
  const enabledReturnToHome = Boolean(returnToHome);
  const returnHomeSvgPath =
    enabledReturnToHome && stops.length >= 2
      ? buildReturnHomeSvgPath(
          stops[stops.length - 1],
          stops[0],
          stops,
          safeW,
          safeH,
        )
      : "";

  return {
    stopCount: stops.length,
    stops,
    svgPath,
    returnToHome: enabledReturnToHome,
    returnHomeSvgPath,
    width: safeW,
    height: safeH,
  };
}

/**
 * Proportionally rescale an existing route's stops and SVG paths to fit updated
 * viewport dimensions (e.g. when expanding window width or zooming out).
 */
export function resizeRouteToBounds(
  route,
  width = 1440,
  height = 800,
  options = {},
) {
  if (!route || !Array.isArray(route.stops) || route.stops.length === 0) {
    return generateRandomRouteForBounds(width, height, Math.random, options);
  }

  const enabledReturnToHome = Boolean(
    options.returnToHome ?? route.returnToHome ?? true,
  );
  const prevBox = computeRouteBoundsBox(
    route.width || width,
    route.height || height,
  );
  const nextBox = computeRouteBoundsBox(width, height);

  const stops = route.stops.map((stop) => {
    const normX = Math.max(
      0,
      Math.min(1, (stop.x - prevBox.padX) / prevBox.usableW),
    );
    const normY = Math.max(
      0,
      Math.min(1, (stop.y - prevBox.padTop) / prevBox.usableH),
    );
    return {
      ...stop,
      x: Math.round(nextBox.padX + normX * nextBox.usableW),
      y: Math.round(nextBox.padTop + normY * nextBox.usableH),
    };
  });

  const svgPath = buildSmoothRouteSvgPath(stops);
  const returnHomeSvgPath =
    enabledReturnToHome && stops.length >= 2
      ? buildReturnHomeSvgPath(
          stops[stops.length - 1],
          stops[0],
          stops,
          nextBox.safeW,
          nextBox.safeH,
        )
      : "";

  return {
    stopCount: stops.length,
    stops,
    svgPath,
    returnToHome: enabledReturnToHome,
    returnHomeSvgPath,
    width: nextBox.safeW,
    height: nextBox.safeH,
  };
}
