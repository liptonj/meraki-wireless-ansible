"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { Canvas, loadImage } = require("skia-canvas");
const {
  svgToDataUri,
  imageSizingContain,
  autoFontSize,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
  safeOuterShadow,
} = require("./pptxgenjs_helpers");

const FONT_HEAD = "CiscoSansTT Medium";
const FONT_BODY = "CiscoSansTT";
const FONT_MONO = "Courier New";

const C = {
  bg: "07182D",
  panel: "122743",
  panelAlt: "1B3455",
  panelSoft: "214062",
  accent: "02C8FF",
  accent2: "0A60FF",
  accent3: "FF007F",
  text: "FFFFFF",
  muted: "B4B9C0",
  line: "525E6C",
  ok: "23C16B",
  warn: "F59E0B",
  danger: "EF4444",
};

const W = 13.333;
const H = 7.5;

const JOURNEY_STEPS = ["Request", "Plan", "Change", "Verify", "Prove"];

const ciscoLogoSvg = fs.readFileSync(path.resolve(__dirname, "cisco_logo_white.svg"), "utf8");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.defineLayout({ name: "LAYOUT_WIDE", width: W, height: H });
pptx.author = "Meraki Wireless Automation";
pptx.company = "Cisco";
pptx.subject = "Sales Demo Narrative";
pptx.title = "Meraki Wireless Automation Demo";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: FONT_HEAD,
  bodyFontFace: FONT_BODY,
  lang: "en-US",
};

const rasterCache = new Map();

async function svgToPngDataUri(svg) {
  if (rasterCache.has(svg)) return rasterCache.get(svg);
  const source = svgToDataUri(svg);
  const img = await loadImage(source);
  const cw = Math.max(2, Math.round(img.width || 128));
  const ch = Math.max(2, Math.round(img.height || 128));
  const canvas = new Canvas(cw, ch);
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0, cw, ch);
  const png = `data:image/png;base64,${(await canvas.toBuffer("png")).toString("base64")}`;
  rasterCache.set(svg, png);
  return png;
}

async function addSvg(slide, svg, x, y, w, h) {
  const data = await svgToPngDataUri(svg);
  slide.addImage({ data, ...imageSizingContain(data, x, y, w, h) });
}

function icon(type, fg = C.accent, bg = C.panelAlt) {
  const shell = `<rect x="0" y="0" width="128" height="128" rx="22" fill="#${bg}"/><rect x="2" y="2" width="124" height="124" rx="20" fill="none" stroke="#${C.line}" stroke-width="2"/>`;
  const glyphs = {
    request: `<rect x="24" y="28" width="80" height="58" rx="8" fill="none" stroke="#${fg}" stroke-width="6"/><line x1="24" y1="48" x2="104" y2="48" stroke="#${fg}" stroke-width="6"/><line x1="54" y1="48" x2="54" y2="86" stroke="#${fg}" stroke-width="6"/><circle cx="40" cy="40" r="4" fill="#${fg}"/><circle cx="50" cy="40" r="4" fill="#${fg}"/><circle cx="60" cy="40" r="4" fill="#${fg}"/>`,
    plan: `<circle cx="64" cy="64" r="34" fill="none" stroke="#${fg}" stroke-width="7"/><line x1="64" y1="64" x2="96" y2="42" stroke="#${fg}" stroke-width="6"/><circle cx="64" cy="64" r="4" fill="#${fg}"/><circle cx="96" cy="42" r="7" fill="#${fg}"/>`,
    change: `<path d="M34 64h60" stroke="#${fg}" stroke-width="7"/><path d="M64 32v64" stroke="#${fg}" stroke-width="7"/><polygon points="64,20 50,38 78,38" fill="#${fg}"/><path d="M44 86 q20 16 40 0" fill="none" stroke="#${fg}" stroke-width="6"/>`,
    verify: `<path d="M64 24l30 12v24c0 20-14 33-30 44-16-11-30-24-30-44V36z" fill="none" stroke="#${fg}" stroke-width="6"/><path d="M49 62l12 12 20-24" fill="none" stroke="#${fg}" stroke-width="7"/>`,
    prove: `<rect x="34" y="22" width="60" height="84" rx="8" fill="none" stroke="#${fg}" stroke-width="6"/><line x1="44" y1="46" x2="84" y2="46" stroke="#${fg}" stroke-width="5"/><line x1="44" y1="62" x2="84" y2="62" stroke="#${fg}" stroke-width="5"/><line x1="44" y1="78" x2="74" y2="78" stroke="#${fg}" stroke-width="5"/>`,
    risk: `<triangle points="64,22 104,96 24,96" fill="none" stroke="#${fg}" stroke-width="7"/><line x1="64" y1="46" x2="64" y2="72" stroke="#${fg}" stroke-width="7"/><circle cx="64" cy="84" r="4" fill="#${fg}"/>`,
    speed: `<circle cx="64" cy="64" r="34" fill="none" stroke="#${fg}" stroke-width="7"/><path d="M64 64 L90 50" stroke="#${fg}" stroke-width="7"/><circle cx="64" cy="64" r="5" fill="#${fg}"/>`,
    audit: `<ellipse cx="64" cy="34" rx="28" ry="12" fill="none" stroke="#${fg}" stroke-width="6"/><path d="M36 34v44c0 7 13 12 28 12s28-5 28-12V34" fill="none" stroke="#${fg}" stroke-width="6"/><ellipse cx="64" cy="78" rx="28" ry="12" fill="none" stroke="#${fg}" stroke-width="6"/>`,
    github: `<circle cx="34" cy="36" r="8" fill="#${fg}"/><circle cx="94" cy="28" r="8" fill="#${fg}"/><circle cx="94" cy="72" r="8" fill="#${fg}"/><line x1="42" y1="36" x2="86" y2="28" stroke="#${fg}" stroke-width="6"/><line x1="42" y1="36" x2="86" y2="72" stroke="#${fg}" stroke-width="6"/><rect x="48" y="84" width="34" height="12" rx="6" fill="#${fg}"/>`,
    ansible: `<circle cx="64" cy="64" r="34" fill="none" stroke="#${fg}" stroke-width="7"/><polygon points="50,84 70,54 82,84" fill="#${fg}"/><circle cx="76" cy="46" r="6" fill="#${fg}"/>`,
    cloud: `<circle cx="52" cy="62" r="20" fill="none" stroke="#${fg}" stroke-width="7"/><circle cx="73" cy="56" r="24" fill="none" stroke="#${fg}" stroke-width="7"/><circle cx="90" cy="66" r="16" fill="none" stroke="#${fg}" stroke-width="7"/><line x1="34" y1="81" x2="102" y2="81" stroke="#${fg}" stroke-width="7"/>`,
    exec: `<rect x="26" y="76" width="16" height="24" fill="#${fg}"/><rect x="52" y="58" width="16" height="42" fill="#${fg}"/><rect x="78" y="40" width="16" height="60" fill="#${fg}"/>`,
    security: `<path d="M64 22l32 12v26c0 24-18 37-32 46C50 97 32 84 32 60V34z" fill="none" stroke="#${fg}" stroke-width="6"/><line x1="64" y1="41" x2="64" y2="83" stroke="#${fg}" stroke-width="6"/><line x1="45" y1="62" x2="83" y2="62" stroke="#${fg}" stroke-width="6"/>`,
    ops: `<path d="M34 64h60" stroke="#${fg}" stroke-width="7"/><path d="M64 34v60" stroke="#${fg}" stroke-width="7"/><circle cx="64" cy="64" r="6" fill="#${fg}"/>`,
  };
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">${shell}${glyphs[type] || glyphs.request}</svg>`;
}

function dashboardSvg(title, accent = C.accent2) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1A2D4A"/>
        <stop offset="100%" stop-color="#101B2D"/>
      </linearGradient>
    </defs>
    <rect x="0" y="0" width="1280" height="720" rx="28" fill="url(#g)"/>
    <rect x="24" y="20" width="1232" height="64" rx="16" fill="#0B1322"/>
    <text x="154" y="62" fill="#E5F4FF" font-family="${FONT_BODY}" font-size="30" font-weight="700">${title}</text>
    <rect x="40" y="106" width="1200" height="250" rx="18" fill="#13243D"/>
    <polyline points="72,312 138,248 208,276 276,214 348,246 424,196 528,228" fill="none" stroke="#${accent}" stroke-width="8"/>
    <rect x="40" y="386" width="280" height="290" rx="14" fill="#0B1322"/>
    <rect x="340" y="386" width="280" height="290" rx="14" fill="#0B1322"/>
    <rect x="640" y="386" width="280" height="290" rx="14" fill="#0B1322"/>
    <rect x="940" y="386" width="300" height="290" rx="14" fill="#0B1322"/>
  </svg>`;
}

function addBase(slide) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: W,
    h: H,
    fill: { color: C.bg },
    line: { color: C.bg },
  });
}

function addCard(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: opts.radius || 0.07,
    fill: { color: opts.fill || C.panel },
    line: { color: opts.line || C.line, pt: opts.linePt || 1 },
    shadow: safeOuterShadow("000000", 0.14, 45, 2, 1),
  });
}

async function addHeaderFooter(slide, title, subtitle) {
  slide.addText(title, {
    ...autoFontSize(title, FONT_HEAD, {
      x: 0.36,
      y: 0.28,
      w: 11.8,
      h: 0.52,
      minFontSize: 20,
      maxFontSize: 30,
      fontSize: 27,
      mode: "shrink",
      bold: true,
      color: C.text,
      valign: "mid",
    }),
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.36,
      y: 0.84,
      w: 11.0,
      h: 0.26,
      fontFace: FONT_BODY,
      fontSize: 12,
      color: C.muted,
    });
  }

  await addSvg(slide, ciscoLogoSvg, 12.60, 6.95, 0.38, 0.20);
  slide.addText("Cisco Confidential", {
    x: 11.35,
    y: 7.20,
    w: 1.45,
    h: 0.14,
    fontFace: FONT_BODY,
    fontSize: 7,
    color: C.muted,
    align: "right",
    valign: "mid",
  });
}

function addFlowArrow(slide, x, y, w, h, color = C.accent2) {
  slide.addShape(pptx.ShapeType.line, {
    x,
    y,
    w,
    h,
    line: { color, pt: 2, beginArrowType: "none", endArrowType: "triangle" },
  });
}

function addJourneyRibbon(slide, activeIndex) {
  const x0 = 0.68;
  const y = 1.20;
  const w = 2.34;
  const h = 0.46;
  const gap = 0.22;

  for (let i = 0; i < JOURNEY_STEPS.length; i += 1) {
    const x = x0 + i * (w + gap);
    addCard(slide, x, y, w, h, {
      fill: i <= activeIndex ? C.panelAlt : C.panel,
      line: i === activeIndex ? C.accent : C.line,
      linePt: i === activeIndex ? 1.4 : 1,
      radius: 0.12,
    });
    slide.addText(JOURNEY_STEPS[i], {
      x,
      y: y + 0.14,
      w,
      h: 0.18,
      fontFace: FONT_BODY,
      fontSize: 10,
      color: i <= activeIndex ? C.accent : C.muted,
      align: "center",
      bold: i === activeIndex,
    });
    if (i < JOURNEY_STEPS.length - 1) {
      addFlowArrow(slide, x + w, y + 0.23, gap, 0, C.line);
    }
  }
}

function addMetricCard(slide, x, y, w, h, title, sub, value, color) {
  addCard(slide, x, y, w, h, { fill: C.panelSoft, line: C.line, linePt: 1.2 });
  slide.addText(value, {
    x: x + 0.16,
    y: y + 0.18,
    w: w - 0.32,
    h: 0.36,
    fontFace: FONT_HEAD,
    fontSize: 24,
    color,
    bold: true,
    align: "center",
  });
  slide.addText(title, {
    x: x + 0.16,
    y: y + 0.62,
    w: w - 0.32,
    h: 0.2,
    fontFace: FONT_HEAD,
    fontSize: 12,
    color: C.text,
    bold: true,
    align: "center",
  });
  slide.addText(sub, {
    x: x + 0.16,
    y: y + 0.86,
    w: w - 0.32,
    h: 0.26,
    fontFace: FONT_BODY,
    fontSize: 9,
    color: C.muted,
    align: "center",
  });
}

function addChip(slide, x, y, w, text, color = "0B1322") {
  addCard(slide, x, y, w, 0.42, { fill: color, line: C.line, radius: 0.1 });
  slide.addText(text, {
    x,
    y: y + 0.13,
    w,
    h: 0.16,
    fontFace: FONT_MONO,
    fontSize: 8.5,
    color: C.text,
    align: "center",
  });
}

function validateSlide(slide) {
  if (process.env.SLIDE_LAYOUT_DEBUG === "1") {
    warnIfSlideHasOverlaps(slide, pptx, {
      muteContainment: true,
      ignoreLines: true,
      ignoreDecorativeShapes: true,
    });
    warnIfSlideElementsOutOfBounds(slide, pptx);
  }
}

async function slide1() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Meraki Wireless Automation: Sales Demo Storyline",
    "Business value first, then a connected live demo flow"
  );
  addJourneyRibbon(s, 0);

  addCard(s, 0.55, 1.95, 8.45, 4.95, { fill: C.panelSoft });

  const steps = [
    { x: 1.0, y: 2.45, t: "Request", i: "request" },
    { x: 3.05, y: 2.45, t: "Plan", i: "plan" },
    { x: 5.10, y: 2.45, t: "Change", i: "change" },
    { x: 7.15, y: 2.45, t: "Verify", i: "verify" },
    { x: 4.08, y: 4.55, t: "Prove", i: "prove" },
  ];

  for (const st of steps) {
    addCard(s, st.x, st.y, 1.7, 1.25, { fill: C.panelAlt });
    await addSvg(s, icon(st.i), st.x + 0.13, st.y + 0.16, 0.52, 0.52);
    s.addText(st.t, {
      x: st.x + 0.72,
      y: st.y + 0.43,
      w: 0.82,
      h: 0.2,
      fontFace: FONT_HEAD,
      fontSize: 12,
      color: C.text,
      bold: true,
      align: "center",
    });
  }

  addFlowArrow(s, 2.70, 3.04, 0.35, 0);
  addFlowArrow(s, 4.75, 3.04, 0.35, 0);
  addFlowArrow(s, 6.80, 3.04, 0.35, 0);
  addFlowArrow(s, 7.95, 3.70, -2.2, 0.9);
  addFlowArrow(s, 4.08, 4.52, -1.8, -0.85);

  addCard(s, 9.25, 1.95, 3.55, 1.45, { fill: C.panel });
  addCard(s, 9.25, 3.68, 3.55, 1.45, { fill: C.panel });
  addCard(s, 9.25, 5.40, 3.55, 1.45, { fill: C.panel });

  await addSvg(s, icon("speed"), 9.47, 2.18, 0.58, 0.58);
  await addSvg(s, icon("security"), 9.47, 3.91, 0.58, 0.58);
  await addSvg(s, icon("audit"), 9.47, 5.63, 0.58, 0.58);

  s.addText("Faster change delivery", { x: 10.18, y: 2.34, w: 2.45, h: 0.2, fontFace: FONT_HEAD, fontSize: 12, color: C.text, bold: true });
  s.addText("Lower risk at rollout", { x: 10.18, y: 4.07, w: 2.45, h: 0.2, fontFace: FONT_HEAD, fontSize: 12, color: C.text, bold: true });
  s.addText("Proof for every run", { x: 10.18, y: 5.79, w: 2.45, h: 0.2, fontFace: FONT_HEAD, fontSize: 12, color: C.text, bold: true });

  validateSlide(s);
}

async function slide2() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Business Pain -> Buyer Value",
    "Replace manual wireless changes with controlled, measurable delivery"
  );
  addJourneyRibbon(s, 0);

  addCard(s, 0.60, 1.95, 6.20, 4.95, { fill: C.panelSoft });
  addCard(s, 6.95, 1.95, 5.80, 4.95, { fill: C.panelSoft });

  s.addText("Without automation", {
    x: 0.9,
    y: 2.24,
    w: 5.6,
    h: 0.2,
    fontFace: FONT_HEAD,
    fontSize: 14,
    color: C.warn,
    bold: true,
    align: "center",
  });
  s.addText("With this playbook flow", {
    x: 7.15,
    y: 2.24,
    w: 5.4,
    h: 0.2,
    fontFace: FONT_HEAD,
    fontSize: 14,
    color: C.ok,
    bold: true,
    align: "center",
  });

  const left = [
    { y: 2.75, t: "Manual dashboard edits", i: "risk" },
    { y: 3.65, t: "Unpredictable rollout impact", i: "risk" },
    { y: 4.55, t: "No consistent drift view", i: "risk" },
    { y: 5.45, t: "Weak audit evidence", i: "risk" },
  ];
  for (const row of left) {
    addCard(s, 0.95, row.y, 5.5, 0.72, { fill: C.panelAlt });
    await addSvg(s, icon(row.i, C.warn), 1.12, row.y + 0.11, 0.42, 0.42);
    s.addText(row.t, {
      x: 1.72,
      y: row.y + 0.24,
      w: 4.5,
      h: 0.2,
      fontFace: FONT_BODY,
      fontSize: 11,
      color: C.muted,
    });
  }

  const right = [
    { y: 2.75, t: "Policy-driven requests", i: "request" },
    { y: 3.65, t: "Serial, limited rollout", i: "change" },
    { y: 4.55, t: "Auto compliance + security", i: "verify" },
    { y: 5.45, t: "Snapshot + report evidence", i: "prove" },
  ];
  for (const row of right) {
    addCard(s, 7.25, row.y, 5.2, 0.72, { fill: C.panelAlt });
    await addSvg(s, icon(row.i, C.ok), 7.42, row.y + 0.11, 0.42, 0.42);
    s.addText(row.t, {
      x: 8.02,
      y: row.y + 0.24,
      w: 4.2,
      h: 0.2,
      fontFace: FONT_BODY,
      fontSize: 11,
      color: C.muted,
    });
  }

  validateSlide(s);
}

async function slide3() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Value Slide For Buyers",
    "Use this in-demo to anchor ROI and risk reduction"
  );
  addJourneyRibbon(s, 1);

  addMetricCard(s, 0.70, 2.00, 3.95, 2.00, "Faster Delivery", "from request to execution", "2-4x", C.accent);
  addMetricCard(s, 4.95, 2.00, 3.95, 2.00, "Lower Change Risk", "scoped + check-first workflow", "~50%", C.ok);
  addMetricCard(s, 9.20, 2.00, 3.40, 2.00, "Audit Coverage", "evidence artifact per run", "100%", C.accent2);

  addCard(s, 0.70, 4.35, 12.00, 2.35, { fill: C.panelSoft });
  await addSvg(s, icon("exec"), 1.05, 4.75, 0.7, 0.7);
  await addSvg(s, icon("security"), 4.10, 4.75, 0.7, 0.7);
  await addSvg(s, icon("ops"), 7.15, 4.75, 0.7, 0.7);
  await addSvg(s, icon("prove"), 10.20, 4.75, 0.7, 0.7);

  s.addText("Leadership: measurable delivery velocity", { x: 1.9, y: 4.97, w: 2.0, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("Security: baseline + policy enforcement", { x: 4.95, y: 4.97, w: 2.0, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("NetOps: repeatable rollout mechanics", { x: 8.0, y: 4.97, w: 2.0, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("Audit: report and snapshot evidence", { x: 11.05, y: 4.97, w: 1.6, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted, align: "right" });

  validateSlide(s);
}

async function slide4() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Live Demo Flow Part 1: Request -> Change",
    "Show intent trigger, guarded run, and scoped deployment"
  );
  addJourneyRibbon(s, 2);

  addCard(s, 0.60, 1.95, 4.10, 4.95, { fill: C.panelSoft });
  addCard(s, 4.90, 1.95, 4.10, 4.95, { fill: C.panelSoft });
  addCard(s, 9.20, 1.95, 3.55, 4.95, { fill: C.panelSoft });

  s.addText("Trigger", { x: 0.9, y: 2.22, w: 3.5, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });
  s.addText("Execution", { x: 5.2, y: 2.22, w: 3.5, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });
  s.addText("Guardrails", { x: 9.45, y: 2.22, w: 3.05, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });

  await addSvg(s, icon("request"), 1.05, 2.65, 0.62, 0.62);
  await addSvg(s, icon("github"), 1.05, 3.65, 0.62, 0.62);
  await addSvg(s, icon("ansible"), 5.35, 2.65, 0.62, 0.62);
  await addSvg(s, icon("cloud"), 5.35, 3.65, 0.62, 0.62);

  s.addText("Meraki workflow intent", { x: 1.82, y: 2.86, w: 2.6, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("repository_dispatch event", { x: 1.82, y: 3.86, w: 2.6, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("playbook execution", { x: 6.12, y: 2.86, w: 2.6, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });
  s.addText("Meraki API apply", { x: 6.12, y: 3.86, w: 2.6, h: 0.2, fontFace: FONT_BODY, fontSize: 10, color: C.muted });

  addFlowArrow(s, 4.70, 3.20, 0.2, 0);
  addFlowArrow(s, 9.00, 3.20, 0.2, 0);

  addChip(s, 9.45, 2.70, 2.95, '"dry_run": true');
  addChip(s, 9.45, 3.30, 2.95, '"target_networks": "Site-A"');
  addChip(s, 9.45, 3.90, 2.95, '"scope_ssid": "Corp-Secure"');

  addCard(s, 0.90, 5.05, 8.0, 1.55, { fill: "0B1322" });
  s.addText("Demo talk track: start with dry-run output, then run limited live on one site", {
    x: 1.15,
    y: 5.53,
    w: 7.5,
    h: 0.2,
    fontFace: FONT_BODY,
    fontSize: 11,
    color: C.accent,
  });

  validateSlide(s);
}

async function slide5() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Live Demo Flow Part 2: Verify -> Prove",
    "Compliance verdict and evidence artifacts shown right after change"
  );
  addJourneyRibbon(s, 4);

  addCard(s, 0.60, 1.95, 6.30, 4.95, { fill: C.panelSoft });
  addCard(s, 7.05, 1.95, 5.70, 4.95, { fill: C.panelSoft });

  s.addText("Compliance view", {
    x: 0.9,
    y: 2.22,
    w: 5.7,
    h: 0.2,
    fontFace: FONT_HEAD,
    fontSize: 13,
    color: C.text,
    bold: true,
    align: "center",
  });
  s.addText("Evidence generated", {
    x: 7.35,
    y: 2.22,
    w: 5.1,
    h: 0.2,
    fontFace: FONT_HEAD,
    fontSize: 13,
    color: C.text,
    bold: true,
    align: "center",
  });

  await addSvg(s, dashboardSvg("Compliance Dashboard", C.ok), 0.92, 2.55, 5.75, 2.75);

  addChip(s, 0.95, 5.45, 1.70, "Compliant", "163A2B");
  addChip(s, 2.85, 5.45, 1.55, "Drift", "3A2C16");
  addChip(s, 4.60, 5.45, 2.20, "Security Critical", "3A1616");

  addCard(s, 7.35, 2.70, 5.10, 1.30, { fill: "0B1322" });
  addCard(s, 7.35, 4.15, 5.10, 1.30, { fill: "0B1322" });
  addCard(s, 7.35, 5.60, 5.10, 0.95, { fill: "0B1322" });

  s.addText("reports/compliance_report_<timestamp>.md", {
    x: 7.58,
    y: 3.15,
    w: 4.65,
    h: 0.2,
    fontFace: FONT_MONO,
    fontSize: 10,
    color: C.accent,
  });
  s.addText("baselines/<network_id>/ssids.yml", {
    x: 7.58,
    y: 4.60,
    w: 4.65,
    h: 0.2,
    fontFace: FONT_MONO,
    fontSize: 10,
    color: C.accent,
  });
  s.addText("Optional GitHub issue when violations exist", {
    x: 7.58,
    y: 5.95,
    w: 4.65,
    h: 0.2,
    fontFace: FONT_BODY,
    fontSize: 10,
    color: C.muted,
  });

  validateSlide(s);
}

async function slide6() {
  const s = pptx.addSlide();
  addBase(s);
  await addHeaderFooter(
    s,
    "Demo Close: What The Customer Buys",
    "A repeatable wireless change platform, not just a playbook run"
  );
  addJourneyRibbon(s, 4);

  addCard(s, 0.60, 1.95, 12.15, 1.65, { fill: C.panelSoft });
  s.addText("Request intent -> controlled change -> automatic verification -> evidence package", {
    x: 0.95,
    y: 2.58,
    w: 11.5,
    h: 0.22,
    fontFace: FONT_HEAD,
    fontSize: 15,
    color: C.text,
    bold: true,
    align: "center",
  });

  addCard(s, 0.60, 3.85, 3.80, 2.85, { fill: C.panelSoft });
  addCard(s, 4.75, 3.85, 3.80, 2.85, { fill: C.panelSoft });
  addCard(s, 8.90, 3.85, 3.85, 2.85, { fill: C.panelSoft });

  await addSvg(s, icon("exec", C.accent), 0.95, 4.20, 0.62, 0.62);
  await addSvg(s, icon("security", C.ok), 5.10, 4.20, 0.62, 0.62);
  await addSvg(s, icon("ops", C.accent2), 9.25, 4.20, 0.62, 0.62);

  s.addText("Executive Value", { x: 1.72, y: 4.36, w: 2.4, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });
  s.addText("Security Value", { x: 5.87, y: 4.36, w: 2.4, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });
  s.addText("Operations Value", { x: 10.02, y: 4.36, w: 2.4, h: 0.2, fontFace: FONT_HEAD, fontSize: 13, color: C.text, bold: true, align: "center" });

  s.addText("Faster delivery\nLower incident exposure\nMeasurable outcomes", {
    x: 1.05,
    y: 4.90,
    w: 2.9,
    h: 0.9,
    fontFace: FONT_BODY,
    fontSize: 11,
    color: C.muted,
    align: "center",
  });
  s.addText("Enforced baseline\nContinuous compliance\nEvidence on every run", {
    x: 5.20,
    y: 4.90,
    w: 2.9,
    h: 0.9,
    fontFace: FONT_BODY,
    fontSize: 11,
    color: C.muted,
    align: "center",
  });
  s.addText("Repeatable rollouts\nPredictable rollback path\nSimple runbook adoption", {
    x: 9.35,
    y: 4.90,
    w: 3.0,
    h: 0.9,
    fontFace: FONT_BODY,
    fontSize: 11,
    color: C.muted,
    align: "center",
  });

  validateSlide(s);
}

async function buildDeck() {
  await slide1();
  await slide2();
  await slide3();
  await slide4();
  await slide5();
  await slide6();

  const out = path.resolve(__dirname, "meraki-wireless-playbook-cisco-dark.pptx");
  await pptx.writeFile({ fileName: out });
  // eslint-disable-next-line no-console
  console.log(`Wrote ${out}`);
}

buildDeck().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exitCode = 1;
});
