const CDN_BASE = "/";
const CDN_FALLBACK = "https://cdn.jsdelivr.net/gh/hasaneyldrm/exercises-dataset@main/";
const PARTS = { chest: "胸部", back: "背部", shoulders: "肩部", "upper arms": "上臂", "lower arms": "前臂", "upper legs": "大腿", "lower legs": "小腿", waist: "核心", cardio: "有氧", neck: "颈部" };
const EQUIPMENT = { "body weight": "自重", dumbbell: "哑铃", barbell: "杠铃", cable: "绳索", band: "弹力带", kettlebell: "壶铃", "smith machine": "史密斯机", "leverage machine": "固定器械", rope: "绳索", "stability ball": "瑜伽球", "wheel roller": "健腹轮" };
const TARGET = { pectorals: "胸大肌", lats: "背阔肌", "upper back": "上背", delts: "三角肌", biceps: "二头肌", triceps: "三头肌", glutes: "臀大肌", quads: "股四头肌", hamstrings: "腘绳肌", calves: "小腿", abs: "腹肌", "cardiovascular system": "心肺", spine: "脊柱", traps: "斜方肌", adductors: "内收肌", "levator scapulae": "提肩胛肌" };
let exercises = [], enhanced = {}, selectedPart = "", selectedEquipment = "", query = "";
let favorites = new Set(JSON.parse(localStorage.getItem("motionfit-favorites") || "[]"));
let installPrompt = null;

function parseCSV(text) { const rows = []; let row = [], cell = "", quoted = false; for (let i = 0; i < text.length; i += 1) { const c = text[i], n = text[i + 1]; if (c === '"' && quoted && n === '"') { cell += '"'; i += 1; continue; } if (c === '"') { quoted = !quoted; continue; } if (c === ',' && !quoted) { row.push(cell); cell = ''; continue; } if ((c === '\n' || c === '\r') && !quoted) { if (c === '\r' && n === '\n') i += 1; row.push(cell); if (row.some(Boolean)) rows.push(row); row = []; cell = ''; continue; } cell += c; } if (cell || row.length) { row.push(cell); rows.push(row); } const head = rows.shift() || []; return rows.map(r => Object.fromEntries(head.map((h, i) => [h, r[i] || ""]))); }
function imageUrl(path) { return CDN_BASE + path; }
function imgFallback(el) {
  const path = el.getAttribute("data-path") || "";
  if (path && el.src.indexOf(CDN_FALLBACK) === -1) { el.src = CDN_FALLBACK + path; return; }
  el.outerHTML = '<div class="media-fallback">◌</div>';
}
function label(map, key) { return map[key] || key; }
function esc(value) { return String(value ?? "").replace(/[&<>\"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c])); }
function saveFavorites() { localStorage.setItem("motionfit-favorites", JSON.stringify([...favorites])); document.querySelector("#favoriteCount").textContent = favorites.size; }
function showToast(msg) { const t = document.querySelector("#toast"); t.textContent = msg; t.classList.add("show"); setTimeout(() => t.classList.remove("show"), 1800); }
function card(ex) { const saved = favorites.has(ex.英文名); return `<article class="exercise-card"><button class="favorite-button ${saved ? 'saved' : ''}" data-fav="${encodeURIComponent(ex.英文名)}" aria-label="${saved ? '取消收藏' : '收藏'} ${esc(ex.标准中文名)}">${saved ? '♥' : '♡'}</button><a class="media-button" href="#exercise/${encodeURIComponent(ex.英文名)}"><img loading="lazy" data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="${esc(ex.标准中文名)}" onerror="imgFallback(this)"></a><div class="card-content"><h3>${esc(ex.标准中文名)}</h3><div class="card-meta"><span class="tag">${esc(label(PARTS, ex.身体部位))}</span><span class="tag">${esc(label(EQUIPMENT, ex.器械))}</span></div></div></article>`; }
function filtered() { return exercises.filter(e => (!query || `${e.标准中文名} ${e.英文名} ${label(TARGET, e.目标肌群)}`.toLowerCase().includes(query.toLowerCase())) && (!selectedPart || e.身体部位 === selectedPart) && (!selectedEquipment || e.器械 === selectedEquipment) && (!document.querySelector("#bodyweightOnly")?.checked || e.器械 === "body weight")); }
function renderFilters() { const parts = [...new Set(exercises.map(e => e.身体部位))], eq = [...new Set(exercises.map(e => e.器械))]; document.querySelector("#partFilters").innerHTML = `<button class="chip ${!selectedPart ? 'selected' : ''}" data-part="">全部</button>` + parts.map(x => `<button class="chip ${selectedPart === x ? 'selected' : ''}" data-part="${esc(x)}">${esc(label(PARTS, x))}</button>`).join(""); document.querySelector("#equipmentFilters").innerHTML = `<button class="chip ${!selectedEquipment ? 'selected' : ''}" data-equipment="">全部</button>` + eq.map(x => `<button class="chip ${selectedEquipment === x ? 'selected' : ''}" data-equipment="${esc(x)}">${esc(label(EQUIPMENT, x))}</button>`).join(""); }
function renderLibrary() { const list = filtered(); document.querySelector("#exerciseGrid").innerHTML = list.map(card).join(""); document.querySelector("#resultCount").textContent = `${list.length} 个动作`; document.querySelector("#resultTitle").textContent = selectedPart ? label(PARTS, selectedPart) : query ? `搜索“${query}”` : "全部动作"; document.querySelector("#emptyState").hidden = list.length > 0; renderFilters(); bindCards(); }
function bindCards() { document.querySelectorAll("[data-fav]").forEach(b => b.onclick = e => { e.preventDefault(); const id = decodeURIComponent(b.dataset.fav); favorites.has(id) ? (favorites.delete(id), showToast("已取消收藏")) : (favorites.add(id), showToast("已收藏")); saveFavorites(); renderLibrary(); }); }
function renderFavorites() { const list = exercises.filter(e => favorites.has(e.英文名)); document.querySelector("#favoriteGrid").innerHTML = list.map(card).join(""); document.querySelector("#favoriteEmpty").hidden = list.length > 0; bindCards(); }
function listItems(items, className = "") { return `<ul class="${className}">${(items || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>`; }
function detail(name) {
  const ex = exercises.find(e => e.英文名 === String(name).replace(/^\/+/, "").trim());
  if (!ex) return;
  const d = enhanced.exercises?.[ex.英文名];
  const primaryGoal = d?.primary_goal || "原始数据标签，未作为训练目标使用";
  const steps = d?.steps || ["当前只有开源动作元数据，分阶段步骤正在复核。", "在完成复核前，不要仅凭动图尝试高负重或高难度变式。", "优先选择已复核的退阶动作，或请持证教练现场指导。"];
  const primary = d?.primary_muscles || [label(TARGET, ex.目标肌群)];
  const secondary = d?.secondary_muscles || [];
  const status = d ? d.review_status : "基础资料，动作要点待教练复核";
  const sources = d?.sources?.map(id => enhanced.references?.find(r => r.id === id)?.citation || id) || [];
  const cues = d?.cues || ["暂无动作专属提示，待教练复核"];
  const errors = d?.common_errors || ["暂无动作专属错误清单，待教练复核"];
  const breathing = d?.breathing || "暂无动作专属呼吸提示，待教练复核。";
  const programming = d?.programming || "暂无动作专属训练建议，待教练复核；不要根据原始 target 标签自行安排负重。";
  const safety = d?.safety || "详细安全边界尚未复核；出现疼痛、麻木、眩晕或放射症状请立即停止。";
  const rel = related(ex);
  const paramSection = `<section class="detail-section"><h2>训练参数速查</h2>${paramBlock(d?.params)}</section>`;
  const relSection = `<section class="detail-section"><h2>同类动作</h2><div class="related-grid">${relatedBlock("退阶 · 更简单", rel.down, "这个部位没有更简单的同类动作，可以先降重量或减小幅度。")}${relatedBlock("进阶 · 更难", rel.up, "这个部位暂时没有更高阶的同类动作。")}${relatedBlock("替代 · 换器械", rel.alt, "同目标肌群暂无其他器械版本。")}</div></section>`;
  document.querySelector("#detail").innerHTML = `<a href="#library" class="back-link">← 返回动作库</a><div class="detail-head"><div class="detail-media"><img data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="${esc(ex.标准中文名)}" onerror="imgFallback(this)"></div><div class="detail-copy"><p class="eyebrow">${esc(label(PARTS, ex.身体部位))} · ${esc(label(EQUIPMENT, ex.器械))}</p><h1>${esc(ex.标准中文名)}</h1><p class="english">${esc(ex.英文名)}</p><div class="detail-tags"><span class="tag">主要目标：${esc(primaryGoal)}</span><span class="tag">动作模式：${esc(d?.movement_pattern || "待复核")}</span><span class="tag tag-diff">难度：${esc(d?.difficulty || "待定")}</span><span class="tag">证据等级 ${esc(d?.evidence_level || "—")}</span></div><div class="detail-actions"><button class="primary" data-fav="${encodeURIComponent(ex.英文名)}">${favorites.has(ex.英文名) ? '♥ 已收藏' : '♡ 收藏动作'}</button><button class="secondary" data-solo="${encodeURIComponent(ex.英文名)}">跟练这个动作</button><a class="secondary" href="#library">继续浏览</a></div></div></div><section class="detail-section"><h2>动作拆解</h2><div class="step-list">${steps.map((s, i) => `<div class="step"><span class="step-num">0${i + 1}</span><span>${esc(s)}</span></div>`).join("")}</div></section><section class="detail-section"><h2>训练重点</h2><div class="detail-columns"><div class="info-panel"><h3>主要参与肌群</h3>${listItems(primary)}${secondary.length ? `<h3 class="subheading">辅助与稳定</h3>${listItems(secondary)}` : ""}</div><div class="info-panel"><h3>可执行提示</h3>${listItems(cues, "cue-list")}${d?.not_the_goal ? `<p class="not-goal"><strong>不要误解：</strong>${esc(d.not_the_goal)}</p>` : ""}</div></div></section><section class="detail-section"><h2>呼吸、错误与训练建议</h2><div class="detail-columns"><div class="info-panel"><h3>呼吸</h3><p>${esc(breathing)}</p><h3 class="subheading">常见错误</h3>${listItems(errors)}</div><div class="info-panel">${d?.params ? "" : `<h3>训练建议</h3><p>${esc(programming)}</p>`}<h3 class="${d?.params ? "" : "subheading"}">安全边界</h3><p>${esc(safety)}</p></div></div>${paramSection}${relSection}</section><section class="detail-section research-note"><h2>资料状态</h2><p><strong>${esc(status)}</strong></p>${sources.length ? `<details><summary>查看参考依据</summary>${listItems(sources)}</details>` : "<p>当前只有开源元数据，详细动作资料正在逐条复核。</p>"}<p class="attribution-line">素材署名：© Gym visual — https://gymvisual.com/</p></section>`;
  document.querySelector("#detail [data-fav]").onclick = () => { favorites.has(ex.英文名) ? favorites.delete(ex.英文名) : favorites.add(ex.英文名); saveFavorites(); detail(ex.英文名); showToast(favorites.has(ex.英文名) ? "已收藏" : "已取消收藏"); };
}

// ---- 难度与同类动作（A2） ----
const DIFF_RANK = { "基础": 1, "中级": 2, "高级": 3 };
function rankOf(name) { const t = enhanced.exercises?.[name]?.difficulty || "中级"; return DIFF_RANK[t] || 2; }
function related(ex) {
  const self = rankOf(ex.英文名);
  const pool = exercises.filter(x => x.英文名 !== ex.英文名 && x.身体部位 !== "neck" && !/拉伸|stretch|dog/i.test(x.标准中文名 + " " + x.英文名));
  const samePart = pool.filter(x => x.身体部位 === ex.身体部位);
  const sameTarget = pool.filter(x => x.目标肌群 === ex.目标肌群);
  const used = new Set([ex.英文名]);
  const take = (arr, n) => { const out = []; for (const x of arr) { if (out.length >= n) break; if (used.has(x.英文名)) continue; used.add(x.英文名); out.push(x); } return out; };
  const patKey = name => enhanced.exercises?.[name]?.family || (enhanced.exercises?.[name]?.movement_pattern || "").split(/[（(、+]/)[0].trim().slice(0, 3);
  const selfPat = patKey(ex.英文名);
  const down = take(samePart.filter(x => rankOf(x.英文名) < self).sort((a, b) => (patKey(b.英文名) === selfPat ? 1 : 0) - (patKey(a.英文名) === selfPat ? 1 : 0) || rankOf(b.英文名) - rankOf(a.英文名)), 3);
  const up = take(samePart.filter(x => rankOf(x.英文名) > self).sort((a, b) => (patKey(b.英文名) === selfPat ? 1 : 0) - (patKey(a.英文名) === selfPat ? 1 : 0) || rankOf(a.英文名) - rankOf(b.英文名)), 3);
  const alt = take(sameTarget.filter(x => x.器械 !== ex.器械).sort((a, b) => (patKey(b.英文名) === selfPat ? 1 : 0) - (patKey(a.英文名) === selfPat ? 1 : 0)), 3);
  return { down, up, alt };
}
function relatedItem(ex) {
  return `<a class="related-item" href="#exercise/${encodeURIComponent(ex.英文名)}"><img loading="lazy" data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="${esc(ex.标准中文名)}" onerror="imgFallback(this)"><span><strong>${esc(ex.标准中文名)}</strong><em>${esc(label(EQUIPMENT, ex.器械))} · ${esc(enhanced.exercises?.[ex.英文名]?.difficulty || "难度待定")}</em></span></a>`;
}
function relatedBlock(title, list, hint) {
  return `<div class="related-col"><h3>${title}</h3>${list.length ? list.map(relatedItem).join("") : `<p class="related-empty">${hint}</p>`}</div>`;
}
function paramBlock(params) {
  if (!params) return '<p class="related-empty">该动作暂无处方数据，先用轻重量熟悉动作，或参考同类已复核动作。</p>';
  const rows = Object.entries(params).map(([goal, v]) => `<div class="param-row"><span class="param-goal">${esc(goal)}</span><span>${esc(v.sets)} 组</span><span>× ${esc(v.reps)}</span><span>休息 ${esc(v.rest)}</span></div>`).join("");
  return `<div class="param-table">${rows}</div><p class="param-note">组数 × 次数为起始建议，按恢复情况和动作质量调整；动作变形就结束该组。</p>`;
}

// ---- 今日一练 / 部位快捷入口（A4） ----
const STEP_EXCLUDE = /拉伸|stretch|dog|颈部/i;
function pickToday() {
  const pool = exercises.filter(x => !STEP_EXCLUDE.test(x.标准中文名 + " " + x.英文名));
  if (!pool.length) return null;
  const now = new Date();
  const seed = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
  let h = 7;
  for (let i = 0; i < seed.length; i += 1) h = (h * 31 + seed.charCodeAt(i)) % 1000003;
  return pool[h % pool.length];
}
function renderToday() {
  const el = document.querySelector("#today"); if (!el) return;
  const ex = pickToday(); if (!ex) return;
  const d = enhanced.exercises?.[ex.英文名];
  const now = new Date();
  el.hidden = false;
  el.innerHTML = `<a class="today-card" href="#exercise/${encodeURIComponent(ex.英文名)}"><div class="today-media"><img data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="${esc(ex.标准中文名)}" onerror="imgFallback(this)"></div><div class="today-copy"><p class="eyebrow">今日一练 · ${now.getMonth() + 1} 月 ${now.getDate()} 日</p><h2>${esc(ex.标准中文名)}</h2><p class="today-meta">${esc(label(PARTS, ex.身体部位))} · ${esc(label(EQUIPMENT, ex.器械))} · ${esc(d?.difficulty || "难度待定")}</p><p class="today-aim">${esc(d?.primary_goal || "")}</p><span class="today-cta">看动作拆解 →</span></div></a>`;
}
const QUICK_PARTS = ["chest", "back", "shoulders", "upper arms", "upper legs", "waist", "cardio", "neck"];
function renderQuickParts() {
  const el = document.querySelector("#quickParts"); if (!el) return;
  const items = QUICK_PARTS.filter(p => exercises.some(e => e.身体部位 === p));
  el.innerHTML = `<span class="quick-label">按部位练</span>` + items.map(p => `<button class="quick-chip" data-quick="${esc(p)}">${esc(label(PARTS, p))}<em>${exercises.filter(e => e.身体部位 === p).length}</em></button>`).join("");
}


// ============================================================ 训练计划（B6）
let plans = [], records = JSON.parse(localStorage.getItem("dongdui-records") || "[]");

function planById(id) { return plans.find(p => p.id === id); }
function fmtMin(m) { return m < 60 ? `${m} 分钟` : `${Math.floor(m / 60)} 小时 ${m % 60} 分`; }
function itemLabel(it) { return it.duration ? `${it.sets} 组 × ${it.duration} 秒` : `${it.sets} 组 × ${it.reps}`; }

function renderPlans() {
  const el = document.querySelector("#planList"); if (!el) return;
  el.hidden = false;
  document.querySelector("#plansHead") && (document.querySelector("#plansHead").hidden = false);
  const detail = document.querySelector("#planDetail"); if (detail) { detail.hidden = true; detail.innerHTML = ""; }
  const rec = document.querySelector("#recordPanel"); if (rec) rec.hidden = false;
  if (!plans.length) { el.innerHTML = '<p class="related-empty">训练计划数据未加载。</p>'; return; }
  el.innerHTML = plans.map(p => {
    const cover = exercises.find(e => e.英文名 === p.items[0]?.en);
    return `<article class="plan-card"><a class="plan-cover" href="#plan/${encodeURIComponent(p.id)}">${cover ? `<img loading="lazy" data-path="${esc(cover.gif)}" src="${imageUrl(cover.gif)}" alt="${esc(cover.标准中文名)}" onerror="imgFallback(this)">` : ""}</a><div class="plan-body"><p class="eyebrow">${esc(p.focus)} · ${esc(p.level)}</p><h2><a href="#plan/${encodeURIComponent(p.id)}">${esc(p.name)}</a></h2><p class="plan-goal">${esc(p.goal)}</p><div class="plan-meta"><span>${esc(fmtMin(p.minutes))}</span><span>${p.items.length} 个动作</span><span>${p.items.reduce((n, i) => n + i.sets, 0)} 组</span></div><button class="primary plan-start" data-plan="${esc(p.id)}">开始跟练</button></div></article>`;
  }).join("");
  renderRecords();
}

function renderPlan(id) {
  const p = planById(id); const detail = document.querySelector("#planDetail"); if (!p || !detail) return;
  document.querySelector("#plansHead").hidden = true;
  document.querySelector("#planList").hidden = true;
  document.querySelector("#recordPanel").hidden = true;
  detail.hidden = false;
  detail.innerHTML = `<a href="#plans" class="back-link">← 返回计划列表</a><div class="page-heading"><p class="eyebrow">${esc(p.focus)} · ${esc(p.level)} · ${esc(fmtMin(p.minutes))}</p><h1>${esc(p.name)}</h1><p>${esc(p.goal)}</p></div><div class="plan-note">${esc(p.note)}</div><ol class="plan-items">${p.items.map((it, i) => { const ex = exercises.find(e => e.英文名 === it.en); return `<li class="plan-item"><span class="plan-item-num">${String(i + 1).padStart(2, "0")}</span><div class="plan-item-copy"><a class="plan-item-name" href="#exercise/${encodeURIComponent(it.en)}">${esc(ex?.标准中文名 || it.en)}</a><span class="plan-item-meta">${esc(itemLabel(it))} · 休息 ${it.rest} 秒</span></div>${ex ? `<img class="plan-item-thumb" loading="lazy" data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="" onerror="imgFallback(this)">` : ""}</li>`; }).join("")}</ol><div class="plan-actions"><button class="primary" data-plan="${esc(p.id)}">开始跟练（${p.items.reduce((n, i) => n + i.sets, 0)} 组）</button><a class="secondary" href="#plans">换一套</a></div><div class="plan-tip">跟练时每组结束自动进入休息倒计时；组间休息时长可在跟练页切换 30 / 60 / 90 秒。</div>`;
}

function getRecords() { try { return JSON.parse(localStorage.getItem("dongdui-records") || "[]"); } catch (e) { return []; } }
function saveRecord(rec) { const all = getRecords(); all.unshift(rec); localStorage.setItem("dongdui-records", JSON.stringify(all.slice(0, 60))); records = getRecords(); }
function streakDays(recs) {
  const days = new Set(recs.map(r => new Date(r.ts).toDateString()));
  let n = 0; const d = new Date();
  while (days.has(d.toDateString())) { n += 1; d.setDate(d.getDate() - 1); }
  return n;
}
function renderRecords() {
  const el = document.querySelector("#recordPanel"); if (!el) return;
  const recs = getRecords();
  if (!recs.length) { el.innerHTML = '<div class="record-empty"><strong>还没有训练记录</strong><p>跟着上面的计划练一次，这里会自动出现你的记录。</p></div>'; return; }
  const totalMin = recs.reduce((n, r) => n + (r.minutes || 0), 0);
  el.innerHTML = `<div class="record-head"><div><p class="eyebrow">训练记录</p><h2>已经练了 ${recs.length} 次</h2></div><div class="record-stats"><span><strong>${totalMin}</strong>累计分钟</span><span><strong>${streakDays(recs)}</strong>连续天数</span></div></div><ul class="record-list">${recs.slice(0, 6).map(r => `<li><span class="record-date">${new Date(r.ts).toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" })}</span><span class="record-name">${esc(r.title)}</span><span class="record-detail">${r.sets} 组 · ${r.minutes} 分钟</span></li>`).join("")}</ul>`;
}

// ============================================================ 跟练引擎（B5）
let wo = null, woTick = null, audioCtx = null;

function beep(freq = 880, dur = 0.12, count = 1) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    for (let i = 0; i < count; i += 1) {
      const t = audioCtx.currentTime + i * 0.18;
      const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
      o.frequency.value = freq; o.type = "sine";
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.22, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.connect(g); g.connect(audioCtx.destination); o.start(t); o.stop(t + dur + 0.02);
    }
  } catch (e) { /* 静音环境忽略 */ }
}
function buzz(pattern) { try { navigator.vibrate && navigator.vibrate(pattern); } catch (e) {} }

function startWorkout(opts) {
  wo = {
    title: opts.title, planId: opts.planId || null, restDefault: opts.restDefault || 60,
    items: opts.items.map(it => ({ ...it, restDefault: it.rest || 60 })),
    i: 0, set: 1, phase: "ready", left: 5, doneSets: 0, startedAt: Date.now(), totalSets: opts.items.reduce((n, i) => n + i.sets, 0),
  };
  if (location.hash === "#workout") renderWorkout(); else location.hash = "#workout";
  tickStart();
}
function curItem() { return wo ? wo.items[wo.i] : null; }
function clearTick() { if (woTick) { clearInterval(woTick); woTick = null; } }
function tickStart() {
  clearTick();
  woTick = setInterval(() => {
    if (!wo) return;
    if (wo.phase === "work" && !curItem().duration) return;   // 次数类动作不计时
    wo.left -= 1;
    if (wo.left <= 0) { advance(); } else { updateWorkoutTimer(); }
  }, 1000);
}
function advance(skipped) {
  const it = curItem();
  if (wo.phase === "ready") {
    wo.phase = it.duration ? "work" : "work";
    wo.left = it.duration || 0;
    beep(880, 0.12, 2); buzz([120, 60, 120]);
  } else if (wo.phase === "work") {
    if (!skipped) wo.doneSets += 1;
    if (wo.set < it.sets) { wo.phase = "rest"; wo.left = wo.restLen || it.restDefault; beep(660, 0.1, 1); }
    else { nextItem(); return; }
  } else if (wo.phase === "rest") {
    wo.set += 1; wo.phase = "work"; wo.left = it.duration || 0; beep(880, 0.12, 2); buzz([120, 60, 120]);
  }
  renderWorkout();
}
function nextItem() {
  if (wo.i < wo.items.length - 1) {
    wo.i += 1; wo.set = 1; wo.phase = "ready"; wo.left = 5;
    beep(520, 0.16, 1); buzz([200]);
    renderWorkout();
  } else { finishWorkout(); }
}
function finishWorkout() {
  clearTick();
  const mins = Math.max(1, Math.round((Date.now() - wo.startedAt) / 60000));
  if (wo.doneSets > 0) {
    saveRecord({ ts: Date.now(), title: wo.title, planId: wo.planId, minutes: mins, sets: wo.doneSets, exercises: wo.items.length });
  }
  const summary = { title: wo.title, sets: wo.doneSets, total: wo.totalSets, minutes: mins };
  wo.phase = "done"; wo.summary = summary;
  beep(880, 0.14, 3); buzz([120, 80, 120, 80, 200]);
  renderWorkout();
}
function quitWorkout() {
  if (!wo) return;
  if (wo.phase !== "done" && wo.doneSets > 0) {
    const mins = Math.max(1, Math.round((Date.now() - wo.startedAt) / 60000));
    saveRecord({ ts: Date.now(), title: wo.title + "（提前结束）", planId: wo.planId, minutes: mins, sets: wo.doneSets, exercises: wo.i + 1 });
  }
  clearTick(); wo = null; location.hash = "#plans";
}

function renderWorkout() {
  const el = document.querySelector("#workout"); if (!el) return;
  if (!wo) { location.hash = "#plans"; return; }
  const it = curItem();
  const ex = exercises.find(e => e.英文名 === it.en);

  if (wo.phase === "done") {
    const s = wo.summary;
    el.innerHTML = `<div class="wo-done"><p class="eyebrow">完成</p><h1>练完了。</h1><p class="wo-done-line">${esc(s.title)} · 完成 ${s.sets}/${s.total} 组 · 用时 ${s.minutes} 分钟</p><p class="wo-done-tip">记录已保存到本机。今天的状态如果不好，少做几组也没关系——明天继续。</p><div class="wo-done-actions"><a class="primary" href="#plans">回到计划</a><a class="secondary" href="#library">看动作库</a></div></div>`;
    return;
  }

  el.innerHTML = `<div class="wo"><header class="wo-top"><button class="wo-exit" id="woExit">退出</button><span class="wo-title">${esc(wo.title)}</span><span class="wo-progress">${wo.i + 1} / ${wo.items.length} 个动作</span></header><div class="wo-main"><div class="wo-media">${ex ? `<img id="woImg" data-path="${esc(ex.gif)}" src="${imageUrl(ex.gif)}" alt="${esc(ex.标准中文名)}" onerror="imgFallback(this)">` : ""}</div><div class="wo-info"><p class="eyebrow" id="woPhase">${wo.phase === "ready" ? "准备" : wo.phase === "rest" ? "组间休息" : "开始做"}</p><h1 id="woName">${esc(ex?.标准中文名 || it.en)}</h1><p class="wo-target" id="woTarget">${esc(itemLabel(it))}${it.duration ? "" : ` · 第 ${wo.set}/${it.sets} 组`}</p><div class="wo-timer" id="woTimer"></div><div class="wo-set" id="woSet">${it.duration ? `第 ${wo.set}/${it.sets} 组` : ""}</div></div></div><div class="wo-controls" id="woControls"></div><div class="wo-rest-pick"><span>组间休息</span>${[30, 60, 90, 120].map(n => `<button class="wo-rest-btn ${ (wo.restLen || it.restDefault) === n ? "on" : ""}" data-rest="${n}">${n} 秒</button>`).join("")}</div></div>`;
  updateWorkoutControls();
  updateWorkoutTimer();
}

function updateWorkoutControls() {
  const box = document.querySelector("#woControls"); if (!box || !wo) return;
  const it = curItem();
  const mmss = s => `${Math.floor(s / 60)}:${String(Math.max(0, s % 60)).padStart(2, "0")}`;
  if (wo.phase === "ready") {
    box.innerHTML = `<button class="primary wo-main-btn" id="woGo">开始（${wo.left}）</button><button class="secondary" id="woSkip">跳过准备</button>`;
  } else if (wo.phase === "work" && it.duration) {
    box.innerHTML = `<button class="primary wo-main-btn" id="woFinishSet">这组做完了</button><button class="secondary" id="woSkip">跳过本组</button>`;
  } else if (wo.phase === "work") {
    box.innerHTML = `<button class="primary wo-main-btn" id="woFinishSet">完成第 ${wo.set} 组</button><button class="secondary" id="woSkip">跳过本组</button>`;
  } else if (wo.phase === "rest") {
    box.innerHTML = `<button class="primary wo-main-btn" id="woEndRest">休息结束，继续</button><button class="secondary" id="woSkip">跳过休息</button>`;
  }
  document.querySelector("#woExit").onclick = quitWorkout;
  document.querySelector("#woGo")?.addEventListener("click", () => advance());
  document.querySelector("#woFinishSet")?.addEventListener("click", () => advance());
  document.querySelector("#woEndRest")?.addEventListener("click", () => advance());
  document.querySelector("#woSkip")?.addEventListener("click", () => advance(true));
  document.querySelectorAll("[data-rest]").forEach(b => b.onclick = () => { wo.restLen = Number(b.dataset.rest); renderWorkout(); });
}

function updateWorkoutTimer() {
  const t = document.querySelector("#woTimer"); if (!t || !wo) return;
  const it = curItem();
  const mmss = s => `${Math.floor(s / 60)}:${String(Math.max(0, s % 60)).padStart(2, "0")}`;
  if (wo.phase === "rest") { t.textContent = mmss(wo.left); t.className = "wo-timer rest"; }
  else if (wo.phase === "ready") { t.textContent = wo.left + ""; t.className = "wo-timer ready"; }
  else if (it.duration) { t.textContent = mmss(wo.left); t.className = "wo-timer work"; }
  else { t.innerHTML = `${esc(it.reps || "8–12")}<small class="wo-unit">次</small>`; t.className = "wo-timer work"; }
  const go = document.querySelector("#woGo"); if (go && wo.phase === "ready") go.textContent = `开始（${wo.left}）`;
  document.querySelectorAll("[data-rest]").forEach(b => b.classList.toggle("on", Number(b.dataset.rest) === (wo.restLen || it.restDefault)));
}

function startPlan(id) {
  const p = planById(id); if (!p) return;
  startWorkout({ title: p.name, planId: p.id, items: p.items.map(it => ({ ...it })) });
}
function startSolo(en) {
  const ex = exercises.find(e => e.英文名 === en); if (!ex) return;
  const d = enhanced.exercises?.[en];
  const row = d?.params ? Object.values(d.params)[0] : null;
  const sets = row ? Number(String(row.sets).replace(/[^0-9]/g, "").slice(0, 1)) || 3 : 3;
  const isHold = /拉伸|plank|dead bug/i.test(en) || ex.身体部位 === "cardio";
  startWorkout({ title: ex.标准中文名 + " · 单项跟练", items: [{ en, sets: Math.max(2, sets), reps: isHold ? undefined : (row?.reps || "8–12"), duration: isHold ? 30 : undefined, rest: 60 }] });
}

function route() { document.querySelectorAll(".view").forEach(v => { v.hidden = true; v.classList.remove("active-view"); }); document.querySelectorAll(".top-nav a").forEach(a => a.classList.remove("active")); const hash = location.hash || "#library"; if (hash.startsWith("#exercise/")) { document.querySelector("#detail").hidden = false; detail(decodeURIComponent(hash.slice("#exercise/".length))); } else { const id = hash.slice(1).split("/")[0]; const viewId = id === "plan" ? "plans" : id; const view = document.querySelector(`#${viewId}`) || document.querySelector("#library"); view.hidden = false; view.classList.add("active-view"); document.querySelector(`.top-nav a[href='#${view.id}']`)?.classList.add("active"); document.querySelectorAll('.top-nav a').forEach(a => { if (a.getAttribute('href') === '#plans' && view.id === 'plans') a.classList.add('active'); }); if (id === "favorites") renderFavorites(); if (id === "plans") renderPlans(); if (id === "plan") renderPlan(decodeURIComponent(hash.split("/")[1] || "")); if (id === "workout") renderWorkout(); } }
async function init() { try { const [csvRes, enhancementRes, planRes] = await Promise.all([fetch("精选100动作.csv?v=7", { cache: "no-store" }), fetch("动作增强数据.json?v=8", { cache: "no-store" }), fetch("训练计划.json?v=1", { cache: "no-store" })]); exercises = parseCSV(await csvRes.text()); enhanced = await enhancementRes.json();
    try { plans = (await planRes.json()).plans || []; } catch (e) { plans = []; } document.querySelector("#totalCount").textContent = exercises.length; renderToday(); renderQuickParts(); renderFilters(); renderLibrary(); saveFavorites(); } catch (e) { document.querySelector("#exerciseGrid").innerHTML = `<div class="empty-state"><h3>动作数据加载失败</h3><p>请通过本地开发服务器打开此页面。</p></div>`; } document.querySelector("#searchInput").oninput = e => { query = e.target.value.trim(); renderLibrary(); }; document.querySelector("#filterToggle").onclick = e => { const f = document.querySelector("#filters"); f.hidden = !f.hidden; e.currentTarget.setAttribute("aria-expanded", String(!f.hidden)); }; document.querySelector("#bodyweightOnly").onchange = renderLibrary; document.querySelector("#clearFilters").onclick = () => { query = ""; selectedPart = ""; selectedEquipment = ""; document.querySelector("#searchInput").value = ""; document.querySelector("#bodyweightOnly").checked = false; renderLibrary(); }; document.addEventListener("click", e => {
  const startBtn = e.target.closest("[data-plan]");
  if (startBtn) { e.preventDefault(); startPlan(startBtn.dataset.plan); return; }
  const soloBtn = e.target.closest("[data-solo]");
  if (soloBtn) { e.preventDefault(); startSolo(soloBtn.dataset.solo); return; } if (e.target.closest("[data-quick]")) { selectedPart = e.target.closest("[data-quick]").dataset.quick; const f = document.querySelector("#filters"); if (f.hidden) { f.hidden = false; document.querySelector("#filterToggle").setAttribute("aria-expanded", "true"); } renderLibrary(); document.querySelector("#exerciseGrid").scrollIntoView({ behavior: "smooth", block: "start" }); } if (e.target.matches("[data-part]")) { selectedPart = e.target.dataset.part; renderLibrary(); } if (e.target.matches("[data-equipment]")) { selectedEquipment = e.target.dataset.equipment; renderLibrary(); } }); document.querySelector("#aboutButton").onclick = () => location.hash = "#about"; window.addEventListener("hashchange", route); route(); }
window.addEventListener("beforeinstallprompt", event => { event.preventDefault(); installPrompt = event; const button = document.querySelector("#installButton"); button.hidden = false; });
document.querySelector("#installButton").onclick = async () => { if (!installPrompt) return; installPrompt.prompt(); await installPrompt.userChoice; installPrompt = null; document.querySelector("#installButton").hidden = true; };
init();
