"""
Drop-in replacement for the `full_html` string inside the Timeline View tab
of your Streamlit app (tab_timeline).
"""


def build_animated_gantt_html(
    *,
    t_min,
    t_max,
    span_hrs,
    machines,
    machine_bars,
    prod_color,
    bar_pos_map,
    machine_idx,
    batch_grps,
    kpi_items,
    util_rows,
    tick_items,
    n_slots,
    hdr_cells,
    table_rows_html,
    total_ops,
    LABEL_W,
    ROW_H,
    TRACK_PAD,
    BAR_H,
    CANVAS_W,
    PX_PER_HR,
    gantt_scroll_h,
    total_iframe_h,
    _parse_iso,
) -> str:
    """Build and return the animated Gantt HTML string."""

    # ── grid lines ──────────────────────────────────────────────────────────
    grid_lines_html = "".join(
        f"<div class='grid-v' style='left:{px:.1f}px;'></div>"
        for px, _ in tick_items
    )

    # ── tick header ─────────────────────────────────────────────────────────
    tick_header_html = "".join(
        f"<div class='tick-lbl' style='left:{px:.1f}px;'>{lbl}</div>"
        for px, lbl in tick_items
    )

    # ── KPI cards ────────────────────────────────────────────────────────────
    kpi_cards_html = ""
    for lbl, val in kpi_items:
        kpi_cards_html += f"""
        <div class='kpi-card'>
          <div class='kpi-lbl'>{lbl}</div>
          <div class='kpi-val'>{val}</div>
        </div>"""

    # ── utilization bars ─────────────────────────────────────────────────────
    util_bars_html = ""
    for m in machines:
        util_pct = next((u["utilization"] for u in util_rows if u["machine"] == m), 0)
        if util_pct >= 85:
            bar_col  = "#ef4444"
            text_col = "#fca5a5"
        elif util_pct >= 65:
            bar_col  = "#f59e0b"
            text_col = "#fcd34d"
        else:
            bar_col  = "#10b981"
            text_col = "#6ee7b7"
        safe_m = m.replace("'", "&#39;").replace('"', "&quot;")
        util_bars_html += f"""
        <div class='util-row'>
          <div class='util-name' title='{safe_m}'>{safe_m[:22]}</div>
          <div class='util-track'>
            <div class='util-fill' style='--tw:{min(util_pct,100):.1f}%;background:{bar_col};'></div>
          </div>
          <div class='util-pct' style='color:{text_col};'>{util_pct:.0f}%</div>
        </div>"""

    # ── gantt rows + bar position map ────────────────────────────────────────
    rows_html = ""
    for ri, machine in enumerate(machines):
        mbars  = machine_bars.get(machine, [])
        safe_m = machine.replace("'", "&#39;").replace('"', "&quot;")
        util_pct = next((u["utilization"] for u in util_rows if u["machine"] == machine), 0)
        util_w   = f"{min(util_pct, 100):.1f}%"
        if util_pct >= 85:
            util_col = "#ef4444"
        elif util_pct >= 65:
            util_col = "#f59e0b"
        else:
            util_col = "#10b981"
        row_bg = "#0a0d1c" if ri % 2 == 0 else "#080b16"

        bar_blocks = grid_lines_html
        if not mbars:
            bar_blocks += (
                "<div style='position:absolute;left:50%;top:50%;"
                "transform:translate(-50%,-50%);color:#1e2a3a;font-size:12px;"
                "font-style:italic;'>— idle —</div>"
            )
        else:
            for bi, b in enumerate(sorted(mbars, key=lambda x: x["start"])):
                bs_dt    = _parse_iso(b["start"])
                be_dt    = _parse_iso(b["end"])
                offset   = (bs_dt - t_min).total_seconds() / 3600
                dur_b    = b["duration_h"]
                left_px  = max(0.0, offset * PX_PER_HR)
                width_px = max(4.0, dur_b * PX_PER_HR)

                bar_pos_map[(b["product"], b["batch_id"], b["step"])] = {
                    "x_start": left_px,
                    "x_end":   left_px + width_px,
                    "machine": b["machine"],
                }

                color    = prod_color.get(b["product"], "#4facfe")
                step_no  = b["step"]
                step_nm  = b.get("step_name", "")
                batch_id = b.get("batch_id", "")
                tip = (
                    f"Step {step_no}: {step_nm} | "
                    f"Product {b['product']} | Batch {batch_id} | "
                    f"{bs_dt.strftime('%H:%M')} – "
                    f"{be_dt.strftime('%H:%M')} ({dur_b:.2f} h)"
                ).replace("'", "&#39;")

                if width_px > 80:
                    inner = (
                        f"<div class='bar-step'>Step {step_no}</div>"
                        f"<div class='bar-name'>{step_nm[:20]}</div>"
                    )
                elif width_px > 36:
                    inner = f"<div class='bar-step'>S{step_no}</div>"
                else:
                    inner = f"<div class='bar-step-mini'>{step_no}</div>"

                delay = bi * 45 + ri * 20
                bar_blocks += f"""
                <div class='bar' title='{tip}'
                     style='left:{left_px:.1f}px;width:{width_px:.1f}px;
                            background:linear-gradient(135deg,{color} 0%,{color}cc 100%);
                            top:{TRACK_PAD}px;height:{BAR_H}px;
                            border-left:3px solid {color};
                            box-shadow:0 2px 8px {color}44,inset 0 1px 0 rgba(255,255,255,0.2);
                            opacity:0;
                            animation:barIn 0.4s cubic-bezier(.22,1,.36,1) {delay}ms forwards;'>
                  <div class='bar-gloss'></div>
                  <div class='bar-shimmer'></div>
                  {inner}
                </div>"""

        rows_html += f"""
        <div class='gantt-row' style='background:{row_bg};'>
          <div class='row-label' title='{safe_m}'>
            <div class='row-name'>{safe_m}</div>
            <div class='row-util-bar' style='width:{util_w};background:{util_col};'></div>
          </div>
          <div class='row-track' style='width:{CANVAS_W}px;height:{ROW_H}px;
                                        position:relative;overflow:visible;'>
            {bar_blocks}
          </div>
        </div>"""

    # ── dependency connection arrows ──────────────────────────────────────────
    svg_paths = []
    conn_count = 0
    for (_prod, _bid), _steps in batch_grps.items():
        sorted_steps = sorted(set(_steps))
        for si in range(len(sorted_steps) - 1):
            if conn_count >= 500:
                break
            s1 = sorted_steps[si]
            s2 = sorted_steps[si + 1]
            p1 = bar_pos_map.get((_prod, _bid, s1))
            p2 = bar_pos_map.get((_prod, _bid, s2))
            if not p1 or not p2:
                continue
            i1 = machine_idx.get(p1["machine"])
            i2 = machine_idx.get(p2["machine"])
            if i1 is None or i2 is None:
                continue

            ax1 = LABEL_W + p1["x_end"]
            ay1 = i1 * ROW_H + ROW_H / 2
            ax2 = LABEL_W + p2["x_start"]
            ay2 = i2 * ROW_H + ROW_H / 2

            if i1 == i2:
                # Same-machine sequential steps → arc above the row
                mid_x = (ax1 + ax2) / 2
                arc_y = ay1 - ROW_H * 0.55
                d = f"M {ax1:.1f},{ay1:.1f} Q {mid_x:.1f},{arc_y:.1f} {ax2:.1f},{ay2:.1f}"
            else:
                # Cross-machine → wide cubic S-curve
                span_x    = abs(ax2 - ax1)
                cp_offset = max(span_x * 0.45, 40)
                d = (
                    f"M {ax1:.1f},{ay1:.1f} "
                    f"C {ax1+cp_offset:.1f},{ay1:.1f} "
                    f"{ax2-cp_offset:.1f},{ay2:.1f} "
                    f"{ax2:.1f},{ay2:.1f}"
                )

            stagger = conn_count * 55
            svg_paths.append(f"""
            <path d="{d}"
                  class="conn-path"
                  style="animation:
                    connAppear 0.5s ease-out {stagger}ms forwards,
                    dashFlow 2.8s linear {stagger+500}ms infinite;"
                  filter="url(#conn-glow)"
                  marker-end="url(#arrow-tip)"/>
            <circle cx="{ax1:.1f}" cy="{ay1:.1f}" r="3.8"
                    class="conn-dot"
                    style="animation:dotPop 0.35s ease-out {stagger}ms forwards;"/>
            """)
            conn_count += 1
        if conn_count >= 500:
            break

    svg_w = LABEL_W + CANVAS_W
    svg_h  = max(len(machines) * ROW_H, 50)

    connections_svg = f"""
    <svg style="position:absolute;top:0;left:0;pointer-events:none;z-index:20;overflow:visible;"
         width="{svg_w}" height="{svg_h}">
      <defs>
        <marker id="arrow-tip" markerWidth="0" markerHeight="7"
                refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="rgba(251,191,36,0.9)"/>
        </marker>
        <filter id="conn-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2.5" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      {''.join(svg_paths)}
    </svg>"""

    # ── product legend ────────────────────────────────────────────────────────
    legend_html = "".join(
        f"<div class='leg-item' style='animation-delay:{i*40}ms;'>"
        f"<div class='leg-dot' style='background:{col};box-shadow:0 0 5px {col}88;'></div>"
        f"<span>P{prod}</span></div>"
        for i, (prod, col) in enumerate(list(prod_color.items())[:24])
    )

    t_start_str = t_min.strftime("%d %b %Y %H:%M")
    t_end_str   = t_max.strftime("%H:%M")
    table_block = ""
    # if table_rows_html:
        # table_block = f"""
        # <div class="tbl-section">
        #   <div class="tbl-title">&#9658; Operations Detail</div>
        #   <div class="tbl-scroll">
        #     <table>
        #       <thead><tr>{hdr_cells}</tr></thead>
        #       <tbody>{table_rows_html}</tbody>
        #     </table>
        #   </div>
        # </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
/* ── KEYFRAMES ──────────────────────────────────────────────────────── */
@keyframes barIn {{
  from {{ opacity:0; transform:scaleX(0.15) translateX(-12px); }}
  to   {{ opacity:1; transform:scaleX(1)    translateX(0); }}
}}
@keyframes connAppear {{
  from {{ stroke:rgba(251,191,36,0);   stroke-dashoffset:600; }}
  to   {{ stroke:rgba(251,191,36,.82); stroke-dashoffset:0; }}
}}
@keyframes dashFlow {{
  to {{ stroke-dashoffset:-28; }}
}}
@keyframes dotPop {{
  0%   {{ r:0;   fill:rgba(251,191,36,0); }}
  55%  {{ r:5.5; fill:rgba(251,191,36,1); }}
  100% {{ r:3.8; fill:rgba(251,191,36,.8); }}
}}
@keyframes utilGrow {{
  from {{ width:0%; }}
  to   {{ width:var(--tw); }}
}}
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(10px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes shimmer {{
  0%   {{ transform:translateX(-100%); opacity:0; }}
  30%  {{ opacity:1; }}
  100% {{ transform:translateX(280%);  opacity:0; }}
}}
@media(prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation-duration:.01ms!important;animation-iteration-count:1!important;}}
}}

/* ── RESET / BASE ───────────────────────────────────────────────────── */
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{
  background:#060811;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Inter',sans-serif;
  color:#e2e8f0;font-size:12px;
}}

/* ── PAGE HEADER ────────────────────────────────────────────────────── */
.ph{{
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:10px 14px;
  background:linear-gradient(135deg,#0d0f22 0%,#060811 100%);
  border-bottom:1px solid rgba(99,102,241,.2);
}}
.ph-left{{display:flex;align-items:center;gap:9px;}}
.ph-icon{{
  width:28px;height:28px;border-radius:7px;flex-shrink:0;
  background:linear-gradient(135deg,#6366f1,#3b82f6);
  display:flex;align-items:center;justify-content:center;
  font-size:14px;box-shadow:0 0 14px rgba(99,102,241,.45);
}}
.ph-title{{font-size:15px;font-weight:800;color:#f1f5f9;letter-spacing:-.3px;}}
.ph-sub{{font-size:10px;color:#334155;margin-top:1px;}}
.badges{{display:flex;flex-wrap:wrap;gap:5px;}}
.badge{{display:inline-flex;align-items:center;gap:4px;
        border-radius:20px;padding:3px 9px;font-size:10px;font-weight:600;}}
.b-time{{background:rgba(6,182,212,.1);border:1px solid rgba(6,182,212,.25);color:#67e8f9;}}
.b-span{{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.25);color:#fcd34d;}}
.b-mach{{background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.25);color:#a5b4fc;}}
.b-ops {{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);color:#6ee7b7;}}

/* ── OUTER LAYOUT ───────────────────────────────────────────────────── */
.outer{{display:flex;gap:10px;padding:10px 12px;align-items:flex-start;}}
.left{{flex:1;min-width:0;}}

/* ── KPI SIDEBAR ────────────────────────────────────────────────────── */
.kpi-panel{{
  width:192px;min-width:192px;flex-shrink:0;
  background:linear-gradient(160deg,#0e1020 0%,#0a0c18 100%);
  border:1px solid rgba(99,102,241,.18);border-radius:10px;padding:12px;
  animation:fadeUp .55s ease-out 250ms both;
}}
.kp-sec{{
  font-size:9px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;
  color:#6366f1;margin-bottom:7px;padding-bottom:5px;
  border-bottom:1px solid rgba(99,102,241,.15);
}}
.kpi-card{{
  display:flex;justify-content:space-between;align-items:baseline;
  padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);
}}
.kpi-lbl{{color:#475569;font-size:10px;}}
.kpi-val{{color:#f8fafc;font-weight:700;font-size:11px;}}
.util-row{{margin:5px 0;}}
.util-name{{color:#94a3b8;font-size:9px;margin-bottom:3px;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.util-track{{background:rgba(255,255,255,.06);border-radius:3px;height:5px;overflow:hidden;}}
.util-fill{{height:100%;border-radius:3px;width:0%;
            animation:utilGrow .9s cubic-bezier(.22,1,.36,1) 600ms forwards;}}
.util-pct{{font-size:9px;text-align:right;margin-top:2px;}}

/* ── GANTT WRAPPER ──────────────────────────────────────────────────── */
.gw{{border:1px solid rgba(99,102,241,.15);border-radius:10px;overflow:hidden;background:#080b16;}}

/* ── GANTT HEADER ───────────────────────────────────────────────────── */
.ghdr{{
  display:flex;
  background:linear-gradient(90deg,#0d0f22 0%,#080b16 100%);
  border-bottom:1px solid rgba(99,102,241,.2);
  position:sticky;top:0;z-index:10;
}}
.hdr-label{{
  width:{LABEL_W}px;min-width:{LABEL_W}px;flex-shrink:0;
  padding:6px 10px;font-size:9px;color:#334155;font-weight:700;
  text-transform:uppercase;letter-spacing:1px;
  border-right:1px solid rgba(99,102,241,.15);
  display:flex;align-items:center;
}}
.hdr-ticks{{flex:1;overflow:hidden;}}
.hdr-ticks-inner{{position:relative;height:26px;width:{CANVAS_W}px;}}
.tick-lbl{{
  position:absolute;transform:translateX(-50%);
  color:#334155;font-size:10px;white-space:nowrap;top:6px;
  font-variant-numeric:tabular-nums;
}}

/* ── SCROLL + ROWS ──────────────────────────────────────────────────── */
.gscroll{{overflow:auto;max-height:{gantt_scroll_h}px;}}
.gantt-row{{
  display:flex;align-items:stretch;
  border-bottom:1px solid rgba(99,102,241,.07);
  transition:background .15s;
}}
.gantt-row:hover{{filter:brightness(1.12);}}
.row-label{{
  width:{LABEL_W}px;min-width:{LABEL_W}px;flex-shrink:0;
  padding:0 8px;
  display:flex;flex-direction:column;justify-content:center;
  border-right:1px solid rgba(99,102,241,.12);cursor:default;
}}
.row-name{{
  font-size:11px;font-weight:600;color:#cbd5e1;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.row-util-bar{{
  height:3px;border-radius:2px;margin-top:4px;
  transition:width 1.2s ease;
  box-shadow:0 0 6px currentColor;
}}
.row-track{{flex:1;overflow:visible;position:relative;}}

/* ── BARS ───────────────────────────────────────────────────────────── */
.bar{{
  position:absolute;border-radius:6px;
  display:flex;flex-direction:column;align-items:flex-start;justify-content:center;
  overflow:hidden;cursor:default;
  transform-origin:left center;
  transition:filter .2s,transform .2s;
  padding:0 8px 0 7px;
}}
.bar:hover{{filter:brightness(1.4) saturate(1.25);transform:scaleY(1.08);z-index:30;}}
.bar-gloss{{
  position:absolute;top:0;left:0;right:0;height:50%;
  background:linear-gradient(180deg,rgba(255,255,255,.18) 0%,rgba(255,255,255,0) 100%);
  border-radius:6px 6px 0 0;pointer-events:none;
}}
.bar-shimmer{{
  position:absolute;top:0;left:0;width:45%;height:100%;
  background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,.18) 50%,transparent 100%);
  transform:translateX(-100%);
  animation:shimmer 4.5s ease-in-out 2s infinite;
  pointer-events:none;
}}
.bar-step{{font-size:10px;font-weight:800;color:#fff;
           text-shadow:0 1px 4px rgba(0,0,0,.95);line-height:1.2;white-space:nowrap;}}
.bar-step-mini{{font-size:9px;font-weight:800;color:rgba(255,255,255,.9);
                text-shadow:0 1px 3px rgba(0,0,0,.95);}}
.bar-name{{font-size:9px;color:rgba(255,255,255,.76);
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
           max-width:100%;line-height:1.2;text-shadow:0 1px 3px rgba(0,0,0,.8);}}

/* ── GRID LINES ─────────────────────────────────────────────────────── */
.grid-v{{position:absolute;top:0;bottom:0;width:1px;
         background:rgba(99,102,241,.08);pointer-events:none;}}

/* ── CONNECTION SVG ─────────────────────────────────────────────────── */
.conn-path{{
  fill:none;
  stroke:rgba(251,191,36,0);
  stroke-width:2px;
  stroke-dasharray:7,4;
  stroke-linecap:round;
}}
.conn-dot{{fill:rgba(251,191,36,0);}}

/* ── LEGEND ─────────────────────────────────────────────────────────── */
.legend{{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;padding-top:8px;
         border-top:1px solid rgba(99,102,241,.1);}}
.leg-item{{display:flex;align-items:center;gap:4px;font-size:10px;color:#475569;
           animation:fadeUp .4s ease-out both;}}
.leg-dot{{width:9px;height:9px;border-radius:3px;flex-shrink:0;}}

/* ── DETAIL TABLE ────────────────────────────────────────────────────── */
.tbl-section{{margin-top:14px;}}
.tbl-title{{color:#6366f1;font-size:10px;font-weight:700;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:6px;}}
.tbl-scroll{{overflow-x:auto;border:1px solid rgba(99,102,241,.12);border-radius:8px;}}
table{{border-collapse:collapse;min-width:500px;}}
th{{padding:6px 10px;background:#0d0f1e;color:#6366f1;font-size:10px;font-weight:700;
    border:1px solid rgba(99,102,241,.12);white-space:nowrap;text-align:left;
    position:sticky;top:0;letter-spacing:.5px;}}
td{{padding:4px 10px;border:1px solid rgba(99,102,241,.07);font-size:10px;
    color:#cbd5e1;vertical-align:top;line-height:1.4;}}
.td-machine{{font-weight:700;color:#94a3b8;white-space:nowrap;background:#080b16;
             position:sticky;left:0;border-right:1px solid rgba(99,102,241,.15);}}
.tr-even td{{background:#090c18;}}
.tr-odd  td{{background:#080b16;}}
tr:hover td{{background:#0f1228!important;}}
</style>
</head>
<body>

<!-- PAGE HEADER -->
<div class="ph">
  <div class="ph-left">
    <div class="ph-icon">&#128202;</div>
    <div>
      <div class="ph-title">Production Schedule Dashboard</div>
      <div class="ph-sub">Live operations timeline</div>
    </div>
  </div>
  <div class="badges">
    <span class="badge b-time">&#128336; {t_start_str} &#8594; {t_end_str}</span>
    <span class="badge b-span">&#9201; {span_hrs:.1f}&nbsp;h&nbsp;span</span>
    <span class="badge b-mach">&#9881; {len(machines)}&nbsp;machines</span>
    <span class="badge b-ops">&#128203; {total_ops:,}&nbsp;ops</span>
  </div>
</div>

<!-- MAIN AREA: GANTT + KPI SIDEBAR -->
<div class="outer">

  <!-- LEFT: GANTT CHART -->
  <div class="left">
    <div class="gw">
      <!-- sticky time header -->
      <div class="ghdr">
        <div class="hdr-label">Machine</div>
        <div class="hdr-ticks" id="hdr-ticks" style="overflow:hidden;">
          <div class="hdr-ticks-inner">{tick_header_html}</div>
        </div>
      </div>
      <!-- scrollable body -->
      <div class="gscroll" id="gscroll">
        <div style="position:relative;width:{LABEL_W + CANVAS_W}px;min-height:{len(machines)*ROW_H}px;">
          {connections_svg}
          {rows_html}
        </div>
      </div>
    </div>

    <!-- product color legend -->
    <div class="legend">{legend_html}</div>

    <!-- operations detail table -->
    {table_block}
  </div>

  <!-- RIGHT: KPI SIDEBAR -->

</div>

<script>
(function() {{
  // sync horizontal scroll between gantt body and time header
  var scroll = document.getElementById('gscroll');
  var hticks = document.getElementById('hdr-ticks');
  if (scroll && hticks) {{
    scroll.addEventListener('scroll', function() {{
      hticks.scrollLeft = scroll.scrollLeft;
    }});
  }}

  // custom tooltip on bar hover
  document.querySelectorAll('.bar').forEach(function(bar) {{
    bar.addEventListener('mouseenter', function(e) {{
      var tip = bar.getAttribute('title');
      if (!tip) return;
      var el = document.createElement('div');
      el.id = 'rt-tip';
      el.style.cssText = [
        'position:fixed',
        'background:linear-gradient(135deg,#1a1d2e,#141828)',
        'border:1px solid rgba(99,102,241,.4)',
        'border-radius:9px',
        'padding:10px 14px',
        'font-size:11px',
        'color:#c7d2fe',
        'pointer-events:none',
        'z-index:9999',
        'line-height:1.7',
        'max-width:300px',
        'box-shadow:0 8px 32px rgba(0,0,0,.75),0 0 0 1px rgba(99,102,241,.12)'
      ].join(';');
      el.innerHTML = tip.replace(/\\|/g, '<br><span style="color:#1e2a3a;">&#8212;</span> ');
      document.body.appendChild(el);
    }});
    bar.addEventListener('mousemove', function(e) {{
      var el = document.getElementById('rt-tip');
      if (el) {{
        el.style.left = (e.clientX + 16) + 'px';
        el.style.top  = (e.clientY - 10) + 'px';
      }}
    }});
    bar.addEventListener('mouseleave', function() {{
      var el = document.getElementById('rt-tip');
      if (el) el.remove();
    }});
  }});
}})();
</script>
</body>
</html>"""
