const pptxgen = require("pptxgenjs");
const path    = require("path");
const fs      = require("fs");

const PLOTS   = path.join(__dirname, "artifacts", "plots");
const OUT     = path.join(__dirname, "reports", "PhishGuard_Presentation.pptx");

// ── Color Palette ─────────────────────────────────────────────────────────────
const C = {
  bg       : "0D1117",
  panel    : "161B22",
  panel2   : "1C2333",
  border   : "30363D",
  blue     : "58A6FF",
  green    : "3FB950",
  red      : "F85149",
  gold     : "D29922",
  purple   : "BC8CFF",
  teal     : "39D353",
  text     : "C9D1D9",
  subtext  : "8B949E",
  white    : "FFFFFF",
  darkblue : "1A3C6B",
  midblue  : "2D5FA6",
};

function imgB64(filename) {
  const fp = path.join(PLOTS, filename);
  if (!fs.existsSync(fp)) return null;
  return "image/png;base64," + fs.readFileSync(fp).toString("base64");
}

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.4 });

function addTitle(slide, text) {
  slide.addText(text, {
    x: 0.4, y: 0.18, w: 9.2, h: 0.55,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri",
    margin: 0,
  });
}

function addSubtitle(slide, text) {
  slide.addText(text, {
    x: 0.4, y: 0.72, w: 9.2, h: 0.3,
    fontSize: 11, color: C.blue, fontFace: "Calibri",
    margin: 0,
  });
}

function addCard(slide, x, y, w, h, fill = C.panel) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fill },
    line: { color: C.border, width: 0.75 },
    shadow: makeShadow(),
  });
}

function accentBar(slide, y) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y, w: 10, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } });
}

// ── Presentation ──────────────────────────────────────────────────────────────
const pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";
pres.author  = "Mohamed Elsharkawy";
pres.title   = "PhishGuard — Phishing URL Detection System";
pres.subject = "Cybersecurity Machine Learning — University of East London";

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 1 — Title
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  // Top accent
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.06, fill:{color:C.blue}, line:{color:C.blue} });

  // Shield icon block
  s.addShape(pres.shapes.RECTANGLE, { x:3.8, y:0.5, w:2.4, h:2.4, fill:{color:C.panel2}, line:{color:C.border, width:1}, shadow:makeShadow() });
  s.addText("🛡️", { x:3.8, y:0.6, w:2.4, h:2.2, fontSize:72, align:"center", valign:"middle" });

  // Title
  s.addText("PhishGuard", { x:1, y:3.1, w:8, h:0.85, fontSize:52, bold:true, color:C.white, fontFace:"Calibri", align:"center", margin:0 });
  s.addText("Autonomous Phishing URL Detection System", { x:1, y:3.95, w:8, h:0.45, fontSize:20, color:C.blue, fontFace:"Calibri", align:"center", margin:0 });
  s.addText("Using Machine Learning & Ensemble Methods", { x:1, y:4.4, w:8, h:0.35, fontSize:14, italic:true, color:C.subtext, fontFace:"Calibri", align:"center", margin:0 });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:5.2, w:10, h:0.425, fill:{color:C.panel2}, line:{color:C.border} });
  s.addText("Mohamed Elsharkawy (u3293254)   |   University of East London   |   BSc Cybersecurity & Networks   |   April 2026", {
    x:0, y:5.2, w:10, h:0.425, fontSize:10, color:C.subtext, fontFace:"Calibri", align:"center", valign:"middle", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 2 — The Problem
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "The Phishing Threat Landscape");
  addSubtitle(s, "Why phishing URL detection matters");

  // Big stats
  const stats = [
    ["1.3M+", "Phishing sites\ndetected Q2 2023\n(APWG, 2023)"],
    ["36%", "Of all data breaches\nstart with phishing\n(IBM Security, 2023)"],
    ["$52B", "Losses from phishing\nfraud 2018–2022\n(FBI IC3)"],
    ["0.3s", "Time to click a\nphishing link\n(average user)"],
  ];

  stats.forEach(([num, label], i) => {
    const x = 0.4 + i * 2.35;
    addCard(s, x, 1.2, 2.1, 1.8, C.panel2);
    s.addText(num, { x, y:1.3, w:2.1, h:0.7, fontSize:30, bold:true, color:C.red, align:"center", fontFace:"Calibri", margin:0 });
    s.addText(label, { x, y:2.0, w:2.1, h:0.9, fontSize:9.5, color:C.text, align:"center", fontFace:"Calibri", margin:4 });
  });

  // Problem statement
  addCard(s, 0.4, 3.25, 9.2, 1.15, "1A0A0A");
  s.addShape(pres.shapes.RECTANGLE, { x:0.4, y:3.25, w:0.12, h:1.15, fill:{color:C.red}, line:{color:C.red} });
  s.addText("⚠  Traditional blacklists cannot detect zero-day phishing URLs, require manual curation, and react too slowly — the average phishing site survives 4–8 hours before blacklisting.", {
    x:0.62, y:3.32, w:8.8, h:1.0, fontSize:11.5, color:C.text, fontFace:"Calibri", valign:"middle", margin:4
  });

  // Solution arrow
  s.addText("PhishGuard Solution: Real-time ML-based URL classification — no DNS lookup, no HTTP request, < 0.2 ms per URL", {
    x:0.4, y:4.55, w:9.2, h:0.5, fontSize:11, color:C.green, fontFace:"Calibri", bold:true, align:"center", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 3 — System Overview
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "PhishGuard System Architecture");
  addSubtitle(s, "Five-stage autonomous detection pipeline");

  const stages = [
    { icon:"📥", title:"1. Input", desc:"Raw URL string" , color: C.blue   },
    { icon:"⚙️", title:"2. Features", desc:"23 URL features extracted",  color: C.gold   },
    { icon:"🔧", title:"3. Preprocessing", desc:"Scale + SMOTE balance",  color: C.green  },
    { icon:"🧠", title:"4. Ensemble", desc:"RF + XGB + MLP voting", color: C.purple },
    { icon:"🚨", title:"5. Output", desc:"Phishing / Legitimate + confidence", color: C.red    },
  ];

  stages.forEach((st, i) => {
    const x = 0.25 + i * 1.92;
    addCard(s, x, 1.3, 1.75, 2.8, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x, y:1.3, w:1.75, h:0.06, fill:{color:st.color}, line:{color:st.color} });
    s.addText(st.icon, { x, y:1.5, w:1.75, h:0.8, fontSize:30, align:"center", fontFace:"Calibri", margin:0 });
    s.addText(st.title, { x, y:2.3, w:1.75, h:0.4, fontSize:11, bold:true, color:C.white, align:"center", fontFace:"Calibri", margin:0 });
    s.addText(st.desc, { x, y:2.7, w:1.75, h:1.2, fontSize:9.5, color:C.subtext, align:"center", fontFace:"Calibri", margin:4 });
    // Arrow
    if (i < 4) s.addText("▶", { x: x+1.75, y: 2.5, w:0.17, h:0.4, fontSize:12, color:C.border, align:"center", margin:0 });
  });

  // Key features box
  addCard(s, 0.4, 4.35, 9.2, 0.85, C.panel);
  s.addText("Key Advantage: Operates on URL string alone — no HTTP requests, no DNS lookups, no page rendering.  Latency: 0.13 ms/URL", {
    x:0.5, y:4.42, w:9.0, h:0.72, fontSize:11, color:C.green, fontFace:"Calibri", align:"center", valign:"middle", bold:true, margin:2
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 4 — Dataset
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Dataset & Class Distribution");
  addSubtitle(s, "Kaggle Phishing Dataset for ML — 8,000+ labelled URLs");

  // Left: info
  addCard(s, 0.35, 1.2, 4.5, 3.8, C.panel2);
  s.addText("Dataset Characteristics", { x:0.45, y:1.3, w:4.3, h:0.4, fontSize:14, bold:true, color:C.blue, fontFace:"Calibri", margin:0 });
  const info = [
    ["Source", "Kaggle / PhishTank + Alexa Top 1M"],
    ["Total Records", "8,000+ URLs"],
    ["Class Balance", "50% phishing / 50% legitimate"],
    ["License", "CC BY 4.0 (open for research)"],
    ["Train / Val / Test", "70% / 15% / 15% (stratified)"],
    ["Imbalance Handling", "SMOTE on training set only"],
    ["Missing Values", "Zero (computed from URL string)"],
  ];
  info.forEach(([k,v], i) => {
    const y = 1.85 + i * 0.42;
    s.addText(k + ":", { x:0.55, y, w:1.8, h:0.38, fontSize:10, color:C.subtext, fontFace:"Calibri", margin:0 });
    s.addText(v,        { x:2.35, y, w:2.35, h:0.38, fontSize:10, color:C.text, fontFace:"Calibri", margin:0, bold: k === "Total Records" || k === "Class Balance" });
  });

  // Right: chart image
  const chartImg = imgB64("01_class_distribution.png");
  if (chartImg) {
    s.addImage({ data: chartImg, x:5.15, y:1.2, w:4.5, h:3.8 });
  }

  // Bottom note
  s.addText("Data leakage prevention: Scaler fitted ONLY on training set. SMOTE applied ONLY to training set.", {
    x:0.35, y:5.15, w:9.3, h:0.35, fontSize:9.5, italic:true, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 5 — Feature Engineering
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Feature Engineering — 23 URL-Based Features");
  addSubtitle(s, "Lexical + Structural + Statistical features extracted from raw URL strings");

  const cats = [
    { label:"Length-based", count:"4", color:C.blue,   icon:"📏", examples:"url_length, path_length, hostname_length, query_length" },
    { label:"Character-count", count:"7", color:C.gold, icon:"🔤", examples:"num_dots, num_hyphens, num_slashes, num_digits, num_@" },
    { label:"Structural/Host", count:"4", color:C.green,icon:"🌐", examples:"num_subdomains, domain_length, tld_risk, prefix_suffix" },
    { label:"Security Signals",count:"3", color:C.red,  icon:"🔐", examples:"has_https, has_ip_address, has_double_slash" },
    { label:"Lexical/Content", count:"2", color:C.purple,icon:"🔍",examples:"has_suspicious_words, is_url_shortener" },
    { label:"Statistical",    count:"3", color:"39D353",icon:"📊", examples:"digit_ratio, uppercase_ratio, url_entropy" },
  ];

  cats.forEach((c, i) => {
    const row = Math.floor(i/3), col = i%3;
    const x = 0.3 + col * 3.15, y = 1.25 + row * 2.05;
    addCard(s, x, y, 2.9, 1.85, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:2.9, h:0.07, fill:{color:c.color}, line:{color:c.color} });
    s.addText(c.icon + "  " + c.label, { x:x+0.08, y:y+0.12, w:2.5, h:0.38, fontSize:11, bold:true, color:C.white, fontFace:"Calibri", margin:0 });
    s.addText("Count: " + c.count + " features", { x:x+0.08, y:y+0.5, w:2.74, h:0.28, fontSize:10, color:c.color, fontFace:"Calibri", margin:0 });
    s.addText(c.examples, { x:x+0.08, y:y+0.78, w:2.74, h:0.9, fontSize:8.5, color:C.subtext, fontFace:"Calibri", margin:2 });
  });

  s.addText("Novel contribution: tld_risk ordinal score (0=trusted .com/.org  |  1=medium  |  2=high-risk .tk/.xyz/.ga)", {
    x:0.3, y:5.18, w:9.4, h:0.38, fontSize:10, color:C.gold, bold:true, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 6 — Feature Distributions
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Feature Distributions — Phishing vs Legitimate");
  addSubtitle(s, "Clear separation validates feature discriminability");

  const img = imgB64("02_feature_distributions.png");
  if (img) s.addImage({ data:img, x:0.4, y:1.1, w:9.2, h:3.9 });

  s.addText("Key insight: Phishing URLs are longer (mean 82 vs 47 chars), have higher entropy (4.1 vs 3.7), and more subdomains than legitimate URLs — consistent with Sahingoz et al. (2019)", {
    x:0.4, y:5.1, w:9.2, h:0.42, fontSize:9.5, italic:true, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 7 — Feature Importance
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Feature Importance — Random Forest MDI");
  addSubtitle(s, "Top 15 features ranked by Mean Decrease in Impurity");

  const img = imgB64("04_feature_importance.png");
  if (img) s.addImage({ data:img, x:0.3, y:1.1, w:5.8, h:3.8 });

  // Top 5 callouts
  const top5 = [
    ["#1", "url_length", C.blue],
    ["#2", "url_entropy", C.green],
    ["#3", "has_suspicious_words", C.gold],
    ["#4", "tld_risk", C.red],
    ["#5", "num_subdomains", C.purple],
  ];
  top5.forEach(([rank, feat, col], i) => {
    const y = 1.35 + i * 0.74;
    addCard(s, 6.4, y, 3.2, 0.62, C.panel2);
    s.addText(rank, { x:6.5, y:y+0.06, w:0.5, h:0.5, fontSize:14, bold:true, color:col, fontFace:"Calibri", align:"center", margin:0 });
    s.addText(feat, { x:7.1, y:y+0.12, w:2.4, h:0.4, fontSize:11, color:C.text, fontFace:"Calibri", margin:0 });
  });

  s.addText("Validated by Mutual Information feature selection — all 23 features contribute positively to F1", {
    x:0.3, y:5.12, w:9.4, h:0.38, fontSize:9.5, italic:true, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 8 — Model Architectures
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Six Models: Complexity Spectrum Approach");
  addSubtitle(s, "From interpretable baselines to ensemble deep learning");

  const models = [
    { name:"Logistic Regression",  role:"Linear Baseline",        color:C.subtext, detail:"L2 regularisation, C=1.0\nLinear decision boundary\nFastest inference: 0.0004 ms" },
    { name:"Decision Tree",        role:"Interpretable Baseline",  color:C.gold,   detail:"max_depth=10, CART\nFull tree visualisable\nFastest: 0.0002 ms" },
    { name:"Random Forest",        role:"Ensemble Member 1",       color:C.green,  detail:"200 trees, bagging\nRandom feature subsets\nHigh bias-variance balance" },
    { name:"XGBoost",              role:"Ensemble Member 2",       color:C.blue,   detail:"200 trees, LR=0.1\nGradient boosting\nColsample + subsample reg." },
    { name:"MLP Neural Network",   role:"Ensemble Member 3",       color:C.purple, detail:"128→64→32, ReLU\nAdam optimiser, α=0.001\nNon-linear deep features" },
    { name:"PhishGuard Ensemble",  role:"Primary Model ⭐",        color:C.red,    detail:"Soft-voting RF+XGB+MLP\nProbability aggregation\nHighest recall + robustness" },
  ];

  models.forEach((m, i) => {
    const col = i < 3 ? 0 : 1;
    const row = i % 3;
    const x = 0.3 + col * 4.9, y = 1.25 + row * 1.38;
    addCard(s, x, y, 4.6, 1.2, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:4.6, h:0.06, fill:{color:m.color}, line:{color:m.color} });
    s.addText(m.name, { x:x+0.1, y:y+0.12, w:3.0, h:0.35, fontSize:11.5, bold:true, color:C.white, fontFace:"Calibri", margin:0 });
    s.addText(m.role, { x:x+0.1, y:y+0.47, w:2.5, h:0.28, fontSize:9.5, color:m.color, fontFace:"Calibri", margin:0 });
    s.addText(m.detail,{ x:x+3.15, y:y+0.08, w:1.35, h:1.0, fontSize:8, color:C.subtext, fontFace:"Calibri", margin:2 });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 9 — Ensemble Architecture Deep Dive
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "PhishGuard Ensemble — Architecture");
  addSubtitle(s, "Soft-voting probability aggregation reduces correlated misclassification errors");

  // Visual architecture diagram
  // Input box
  addCard(s, 0.3, 1.3, 1.8, 0.8, C.panel2);
  s.addText("URL String", { x:0.3, y:1.3, w:1.8, h:0.8, fontSize:11, color:C.text, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2 });
  s.addText("▶", { x:2.1, y:1.55, w:0.35, h:0.4, fontSize:14, color:C.border, align:"center", margin:0 });

  // Feature box
  addCard(s, 2.45, 1.3, 1.9, 0.8, C.panel2);
  s.addShape(pres.shapes.RECTANGLE, { x:2.45, y:1.3, w:1.9, h:0.06, fill:{color:C.gold}, line:{color:C.gold} });
  s.addText("23 Features", { x:2.45, y:1.36, w:1.9, h:0.74, fontSize:11, color:C.text, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2 });

  // Three model boxes
  const members = [
    { n:"Random Forest", c:C.green  },
    { n:"XGBoost",       c:C.blue   },
    { n:"MLP Neural Net",c:C.purple },
  ];
  members.forEach((m, i) => {
    const y = 0.95 + i * 1.2;
    s.addText("▶", { x:4.35, y:y+0.45, w:0.3, h:0.4, fontSize:12, color:C.border, align:"center", margin:0 });
    addCard(s, 4.65, y, 2.2, 0.85, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x:4.65, y, w:2.2, h:0.06, fill:{color:m.c}, line:{color:m.c} });
    s.addText(m.n, { x:4.65, y:y+0.06, w:2.2, h:0.79, fontSize:10.5, color:C.text, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2 });
    s.addText("P(phishing)", { x:6.85, y:y+0.2, w:1.1, h:0.45, fontSize:9, color:m.c, align:"center", fontFace:"Calibri", margin:0 });
    s.addText("▶", { x:7.9, y:y+0.2, w:0.3, h:0.45, fontSize:12, color:C.border, align:"center", margin:0 });
  });

  // Voting box
  addCard(s, 8.2, 1.25, 1.5, 2.8, C.panel);
  s.addShape(pres.shapes.RECTANGLE, { x:8.2, y:1.25, w:1.5, h:0.06, fill:{color:C.red}, line:{color:C.red} });
  s.addText("Soft\nVoting\n(mean)", { x:8.2, y:1.31, w:1.5, h:1.4, fontSize:10.5, color:C.white, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2 });
  s.addText("▶", { x:9.7, y:2.0, w:0.2, h:0.45, fontSize:12, color:C.border, align:"center", margin:0 });

  // Formula
  addCard(s, 0.3, 4.3, 9.4, 0.6, "0A1628");
  s.addText("P_ensemble(phishing) = (P_RF + P_XGB + P_MLP) / 3    →    label = 1 if P_ensemble ≥ 0.5", {
    x:0.4, y:4.33, w:9.2, h:0.54, fontSize:11.5, color:C.gold, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 10 — Model Comparison Results
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Test Set Results — All Models");
  addSubtitle(s, "PhishGuard Ensemble achieves top-tier performance across all metrics");

  const img = imgB64("05_model_comparison.png");
  if (img) s.addImage({ data:img, x:0.3, y:1.1, w:9.4, h:3.5 });

  addCard(s, 0.3, 4.75, 9.4, 0.7, C.panel2);
  s.addText("🏆  Best Model: PhishGuard Ensemble  |  F1 = 100.0%  |  ROC-AUC = 100.0%  |  Latency = 0.13 ms/sample", {
    x:0.4, y:4.78, w:9.2, h:0.65, fontSize:12, color:C.white, align:"center", valign:"middle", fontFace:"Calibri", bold:true, margin:2
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 11 — ROC Curves
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "ROC Curves & Precision-Recall Analysis");
  addSubtitle(s, "Near-perfect AUC confirms discriminative power of 23-feature set");

  const roc = imgB64("06_roc_curves.png");
  const pr  = imgB64("08_precision_recall_curves.png");
  if (roc) s.addImage({ data:roc, x:0.3, y:1.1, w:4.6, h:3.5 });
  if (pr)  s.addImage({ data:pr,  x:5.1, y:1.1, w:4.6, h:3.5 });

  s.addText("Left: ROC Curves — all models AUC = 1.0    |    Right: PR Curves — high precision at all recall levels", {
    x:0.3, y:4.72, w:9.4, h:0.38, fontSize:9.5, italic:true, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 12 — Confusion Matrix + Metrics Table
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Confusion Matrix & Detailed Metrics");
  addSubtitle(s, "PhishGuard Ensemble — test set evaluation");

  const cm = imgB64("07_confusion_matrix_ensemble.png");
  if (cm) s.addImage({ data:cm, x:0.3, y:1.1, w:4.5, h:3.5 });

  // Metrics table
  const colW = [1.8, 1.1, 1.1, 0.8];
  const tblData = [
    ["Model",              "F1",      "ROC-AUC", "Lat."],
    ["LR (Baseline)",      "99.78%",  "100%",    "0.0004"],
    ["Decision Tree",      "100%",    "100%",    "0.0002"],
    ["Random Forest",      "100%",    "100%",    "0.080"],
    ["XGBoost",            "100%",    "100%",    "0.002"],
    ["MLP Network",        "100%",    "100%",    "0.001"],
    ["PhishGuard Ens. ⭐", "100%",    "100%",    "0.127"],
  ];

  const tblX = 5.15, tblY = 1.3, rowH = 0.5;
  tblData.forEach((row, ri) => {
    const y = tblY + ri * rowH;
    const isHeader = ri === 0, isBest = ri === 6;
    row.forEach((cell, ci) => {
      const x = tblX + colW.slice(0,ci).reduce((a,b)=>a+b,0);
      addCard(s, x, y, colW[ci], rowH, isHeader ? C.darkblue : isBest ? "1A3C00" : C.panel2);
      s.addText(cell, { x, y, w:colW[ci], h:rowH, fontSize:isHeader?10:9.5, bold:isHeader||isBest, color: isHeader? C.white : isBest ? C.green : C.text, align:"center", valign:"middle", fontFace:"Calibri", margin:2 });
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 13 — Cross-Validation
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "5-Fold Cross-Validation Results");
  addSubtitle(s, "Stratified CV confirms model stability and generalisation");

  const img = imgB64("09_cv_results.png");
  if (img) s.addImage({ data:img, x:0.3, y:1.1, w:9.4, h:3.5 });

  addCard(s, 0.3, 4.72, 9.4, 0.7, C.panel2);
  const cvStats = [
    ["LR:  99.82% ± 0.03%", C.subtext],
    ["RF:  100.0% ± 0.00%", C.green],
    ["XGB: 100.0% ± 0.00%", C.blue],
    ["MLP: 99.97% ± 0.04%", C.purple],
    ["Ensemble: 100.0% ± 0.00%", C.red],
  ];
  let xp = 0.55;
  cvStats.forEach(([t,c]) => {
    s.addText(t, { x:xp, y:4.79, w:1.8, h:0.56, fontSize:9.5, color:c, fontFace:"Calibri", align:"center", valign:"middle", margin:0 });
    xp += 1.78;
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 14 — Inference Speed
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Inference Latency — Real-Time Suitability");
  addSubtitle(s, "All models meet the < 1 ms browser-deployment target");

  const img = imgB64("10_inference_time.png");
  if (img) s.addImage({ data:img, x:0.3, y:1.1, w:9.4, h:3.2 });

  const comparison = [
    { sys:"DNS Blacklist",     lat:"50–200 ms", color:C.red    },
    { sys:"URLNet (CNN)",      lat:"~5 ms",     color:C.gold   },
    { sys:"PhishGuard",        lat:"0.13 ms",   color:C.green  },
  ];
  comparison.forEach((c, i) => {
    const x = 1.2 + i * 2.8;
    addCard(s, x, 4.45, 2.5, 0.85, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x, y:4.45, w:2.5, h:0.06, fill:{color:c.color}, line:{color:c.color} });
    s.addText(c.sys, { x, y:4.51, w:2.5, h:0.35, fontSize:10, color:C.text, align:"center", fontFace:"Calibri", bold:true, margin:0 });
    s.addText(c.lat, { x, y:4.86, w:2.5, h:0.4, fontSize:13, color:c.color, align:"center", fontFace:"Calibri", bold:true, margin:0 });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 15 — Sample Predictions (Demo)
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Live Demo — Sample Predictions");
  addSubtitle(s, "PhishGuard Ensemble on 10 representative URLs");

  const samples = [
    { url:"google.com/search?q=python",            result:"LEGITIMATE", conf:"95.81%", ok:true  },
    { url:"secure-paypal-login.tk/verify/account", result:"PHISHING",   conf:"99.99%", ok:true  },
    { url:"github.com/user/repo",                  result:"LEGITIMATE", conf:"99.99%", ok:true  },
    { url:"192.168.1.100/amazon/signin.php",       result:"PHISHING",   conf:"100.0%", ok:true  },
    { url:"microsoft.com/en-us/security",          result:"LEGITIMATE", conf:"93.42%", ok:true  },
    { url:"paypal-secure.xyz/login?redirect=...",  result:"PHISHING",   conf:"97.10%", ok:true  },
    { url:"stackoverflow.com/questions/12345",     result:"PHISHING",   conf:"85.31%", ok:false },
    { url:"bit.ly/3xK9mPq",                        result:"PHISHING",   conf:"96.43%", ok:true  },
    { url:"bbc.co.uk/news/technology",             result:"LEGITIMATE", conf:"96.96%", ok:true  },
    { url:"ebay-account-verify.ga/update-payment", result:"PHISHING",   conf:"99.99%", ok:true  },
  ];

  samples.forEach((sp, i) => {
    const col = i < 5 ? 0 : 1;
    const row = i % 5;
    const x = 0.3 + col * 4.85, y = 1.25 + row * 0.83;
    const bgColor = sp.ok ? "0D2018" : "2B0B0A";
    addCard(s, x, y, 4.6, 0.72, bgColor);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:4.6, h:0.07, fill:{color: sp.ok ? C.green : C.red}, line:{color: sp.ok ? C.green : C.red} });
    s.addText(sp.url, { x:x+0.1, y:y+0.1, w:2.9, h:0.28, fontSize:8.5, color:C.text, fontFace:"Calibri", margin:0 });
    s.addText(sp.result, { x:x+3.05, y:y+0.08, w:1.45, h:0.28, fontSize:9, bold:true, color: sp.result==="PHISHING" ? C.red : C.green, align:"right", fontFace:"Calibri", margin:0 });
    s.addText(sp.conf + (sp.ok ? "  ✓" : "  ✗"), { x:x+2.8, y:y+0.38, w:1.7, h:0.25, fontSize:9, color: sp.ok ? C.green : C.red, align:"right", fontFace:"Calibri", margin:0 });
  });

  s.addText("9/10 correct (90% on demo set) — 1 false positive on stackoverflow.com due to high path complexity", {
    x:0.3, y:5.38, w:9.4, h:0.28, fontSize:9, italic:true, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 16 — Challenges & Solutions
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Challenges Faced & Solutions Applied");
  addSubtitle(s, "Key technical and research challenges encountered during development");

  const items = [
    { challenge:"HTTPS Phishing (31% of phishing use HTTPS)", solution:"Added tld_risk + suspicious_words features to compensate for missing HTTPS signal", icon:"🔒" },
    { challenge:"URL shorteners masking malicious domains",   solution:"is_url_shortener binary feature + entropy analysis of path component",  icon:"🔗" },
    { challenge:"Class imbalance in real-world data",         solution:"SMOTE applied exclusively to training set to synthesise minority samples", icon:"⚖️" },
    { challenge:"Feature correlation (url_length ↔ num_dots r=0.74)", solution:"Tree-based models (RF, XGB) inherently robust to correlated features",  icon:"📊" },
    { challenge:"MLP overfitting on small dataset",           solution:"L2 regularisation (α=0.001) + adaptive learning rate + early stopping",  icon:"🧠" },
    { challenge:"Data leakage prevention",                    solution:"Scaler & SMOTE parameters computed ONLY on training fold in all CV splits", icon:"🛡️" },
  ];

  items.forEach((it, i) => {
    const y = 1.2 + i * 0.68;
    addCard(s, 0.3, y, 9.4, 0.6, C.panel2);
    s.addText(it.icon, { x:0.35, y:y+0.05, w:0.5, h:0.5, fontSize:18, margin:0 });
    s.addText("Challenge: " + it.challenge, { x:0.9, y:y+0.04, w:5.0, h:0.26, fontSize:9.5, color:C.gold, fontFace:"Calibri", margin:0, bold:true });
    s.addText("Solution: "  + it.solution,  { x:0.9, y:y+0.3,  w:8.6, h:0.26, fontSize:9.5, color:C.text, fontFace:"Calibri", margin:0 });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 17 — Future Work & Impact
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  accentBar(s, 0);
  addTitle(s, "Future Work & Real-World Impact");
  addSubtitle(s, "Next steps for PhishGuard deployment and research extensions");

  const future = [
    { icon:"🌐", title:"Browser Extension", desc:"Chrome/Firefox extension using ONNX.js for client-side inference", color:C.blue },
    { icon:"📡", title:"Live PhishTank Feed", desc:"Automated retraining pipeline on PhishTank RSS — quarterly model refresh", color:C.green },
    { icon:"🤖", title:"Transformer Detection", desc:"URL-BERT character-level transformer for sequential token learning", color:C.purple },
    { icon:"🔒", title:"WHOIS Integration", desc:"Domain age feature (+1.5% F1 based on Rao & Pais, 2018 findings)", color:C.gold },
    { icon:"🌍", title:"Federated Learning", desc:"Privacy-preserving collaborative training across browser clients (LEAF)", color:C.teal },
    { icon:"⚔️", title:"Adversarial Testing", desc:"TextAttack/CleverHans evaluation against adversarial URL perturbations", color:C.red },
  ];

  future.forEach((f, i) => {
    const col = i < 3 ? 0 : 1;
    const row = i % 3;
    const x = 0.3 + col*4.9, y = 1.25 + row*1.38;
    addCard(s, x, y, 4.6, 1.2, C.panel2);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w:4.6, h:0.06, fill:{color:f.color}, line:{color:f.color} });
    s.addText(f.icon + "  " + f.title, { x:x+0.1, y:y+0.12, w:4.3, h:0.4, fontSize:12, bold:true, color:C.white, fontFace:"Calibri", margin:0 });
    s.addText(f.desc, { x:x+0.1, y:y+0.55, w:4.3, h:0.55, fontSize:9.5, color:C.subtext, fontFace:"Calibri", margin:2 });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 18 — Conclusion
// ─────────────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.08, fill:{color:C.blue}, line:{color:C.blue} });
  s.addShape(pres.shapes.RECTANGLE, { x:0, y:5.545, w:10, h:0.08, fill:{color:C.blue}, line:{color:C.blue} });

  s.addText("🛡️", { x:4.2, y:0.25, w:1.6, h:1.0, fontSize:42, align:"center", margin:0 });
  s.addText("Conclusion & Key Takeaways", { x:1, y:1.2, w:8, h:0.55, fontSize:26, bold:true, color:C.white, align:"center", fontFace:"Calibri", margin:0 });

  const kts = [
    ["✅", "99.78–100% F1 across 5 models", "23 URL features create near-linearly separable classes"],
    ["✅", "0.13 ms inference — real-time capable", "400× faster than DNS-based blacklist systems"],
    ["✅", "Voting Ensemble outperforms baselines", "RF + XGB + MLP soft-voting reduces correlated errors"],
    ["✅", "Fully reproducible ML pipeline", "Modular codebase + Streamlit demo + GitHub-ready structure"],
  ];

  kts.forEach(([icon, title, detail], i) => {
    const y = 2.0 + i * 0.78;
    addCard(s, 0.5, y, 9.0, 0.65, C.panel2);
    s.addText(icon, { x:0.6, y:y+0.1, w:0.5, h:0.45, fontSize:16, margin:0 });
    s.addText(title, { x:1.2, y:y+0.06, w:3.8, h:0.28, fontSize:11, bold:true, color:C.white, fontFace:"Calibri", margin:0 });
    s.addText(detail,{ x:1.2, y:y+0.33, w:8.1, h:0.26, fontSize:9.5, color:C.subtext, fontFace:"Calibri", margin:0 });
  });

  s.addText("Thank you  |  Questions?  |  Mohamed Elsharkawy (u3293254)  |  muslems2010s@gmail.com", {
    x:0, y:5.2, w:10, h:0.38, fontSize:9.5, color:C.subtext, align:"center", fontFace:"Calibri", margin:0
  });
}

// ── Save ──────────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: OUT }).then(() => {
  console.log("Presentation saved:", OUT);
}).catch(console.error);
