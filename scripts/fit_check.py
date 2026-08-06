#!/usr/bin/env python3
"""Estimate whether a tailored CV still fits on one page.

This is a heuristic, not a renderer. There is no LaTeX engine in the working
environment, so the real confirmation is always the Overleaf compile. What this
gives you is a fast answer to "did that rewrite push me over?" without a
round trip, plus a per-section breakdown showing where the space went.

The model walks the .tex source and accumulates vertical height in points,
handling the specific constructs this CV uses: \\section, the \\entry macro,
itemize lists, multicols, explicit \\vspace, and the centred header block. Text
is stripped of markup and wrapped against the geometry text width to count
rendered lines.

Usage:
    python3 scripts/fit_check.py applications/<company>-<role>/resume.tex
    python3 scripts/fit_check.py <tailored.tex> --baseline resume.tex
"""

import argparse
import math
import os
import re
import sys

PT_PER_CM = 28.4527

# From \usepackage[top=0.9cm, bottom=0.9cm, left=1.35cm, right=1.35cm]{geometry}
# on a4paper (21.0cm x 29.7cm), with \pagestyle{empty} so no header/footer.
TEXT_WIDTH_PT = (21.0 - 1.35 - 1.35) * PT_PER_CM
TEXT_HEIGHT_PT = (29.7 - 0.9 - 0.9) * PT_PER_CM

# 10pt Latin Modern Roman. Average advance width across typical English prose,
# calibrated so the known-good baseline resume.tex lands just inside the page.
# The baseline is essentially full, so it reports only a few points of slack --
# that is accurate, not a calibration error. The CV has no room to grow.
CHAR_WIDTH_PT = 4.30
LINE_HEIGHT_PT = 12.0

# Line counts are integers, so a single bullet flipping between two and three
# rendered lines moves the total by a whole LINE_HEIGHT_PT. Across ~15 bullets
# the accumulated rounding is worth roughly this much either way.
UNCERTAINTY_PT = 2 * LINE_HEIGHT_PT

# \small is roughly 9pt at a 10pt base.
SMALL_SCALE = 0.9

BULLET_INDENT_PT = 13.0  # leftmargin=1.3em at 10pt


def strip_comments(tex: str) -> str:
    out = []
    for line in tex.split("\n"):
        stripped, escaped = [], False
        for ch in line:
            if escaped:
                stripped.append(ch)
                escaped = False
                continue
            if ch == "\\":
                stripped.append(ch)
                escaped = True
                continue
            if ch == "%":
                break
            stripped.append(ch)
        out.append("".join(stripped))
    return "\n".join(out)


def visible_text(tex: str) -> str:
    """Reduce LaTeX markup to the characters that actually get set."""
    s = tex
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:textbf|textit|emph|underline)\{([^{}]*)\}", r"\1", s)
    s = s.replace(r"\pounds", "£")
    s = re.sub(r"\\([$&%_#])", r"\1", s)  # escaped specials set one glyph each
    s = s.replace("---", "—").replace("--", "–")
    s = s.replace(r"\enspace", " ").replace("~", " ")
    s = re.sub(r"\\\\\[[^\]]*\]", " ", s)
    s = s.replace(r"\\", " ")
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)  # remaining control sequences
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def wrapped_lines(text: str, width_pt: float, small: bool = False) -> int:
    """How many rendered lines this text occupies at the given width."""
    if not text:
        return 0
    char_w = CHAR_WIDTH_PT * (SMALL_SCALE if small else 1.0)
    chars_per_line = max(1, int(width_pt / char_w))
    return max(1, math.ceil(len(text) / chars_per_line))


def line_height(small: bool = False) -> float:
    return LINE_HEIGHT_PT * (SMALL_SCALE if small else 1.0)


def measure(tex: str):
    """Return (total_pt, [(label, pt), ...]) for the document body."""
    body = tex
    if r"\begin{document}" in body:
        body = body.split(r"\begin{document}", 1)[1]
    if r"\end{document}" in body:
        body = body.split(r"\end{document}", 1)[0]

    sections = []           # (label, points)
    current = "Header"
    accumulated = 0.0

    in_itemize = False
    in_multicols = False
    multicol_cols = 1
    multicol_lines = 0
    pending = ""            # buffer for multi-line constructs

    def flush(label, pts):
        nonlocal accumulated
        accumulated += pts

    def close_section():
        nonlocal accumulated, current
        sections.append((current, accumulated))
        accumulated = 0.0

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1

        if not line:
            continue

        # ---- centred header block -------------------------------------
        if line.startswith(r"\begin{center}"):
            block = []
            while i < len(lines) and not lines[i].strip().startswith(r"\end{center}"):
                block.append(lines[i])
                i += 1
            i += 1
            joined = " ".join(block)
            # \LARGE name line, then a \small contact line that may wrap.
            name_pt = 17.28 * 1.2
            contact = visible_text(joined.split(r"\\[4pt]")[-1] if r"\\[4pt]" in joined else joined)
            contact_pt = wrapped_lines(contact, TEXT_WIDTH_PT, small=True) * line_height(True)
            flush(current, name_pt + 4.0 + contact_pt)
            continue

        # ---- section headings -----------------------------------------
        m = re.match(r"\\section\{(.+?)\}", line)
        if m:
            close_section()
            current = visible_text(m.group(1))
            # titlespacing 6pt before + heading line + rule (vspace -5pt) + 2pt after
            flush(current, 6.0 + LINE_HEIGHT_PT - 5.0 + 0.5 + 2.0)
            continue

        # ---- explicit vertical space ----------------------------------
        m = re.match(r"\\vspace\{(-?[\d.]+)pt\}", line)
        if m:
            flush(current, float(m.group(1)))
            continue

        # ---- \entry macro (may span several source lines) -------------
        if line.startswith(r"\entry{"):
            block = line
            while block.count("{") > block.count("}") and i < len(lines):
                block += " " + lines[i].strip()
                i += 1
            # Two tabularx rows, \\[-2pt] between, \vspace{1pt} after.
            flush(current, 2 * LINE_HEIGHT_PT - 2.0 + 1.0)
            continue

        if line.startswith(r"\subentry{"):
            flush(current, LINE_HEIGHT_PT + 1.0)
            continue

        # ---- multicols ------------------------------------------------
        m = re.match(r"\\begin\{multicols\}\{(\d+)\}", line)
        if m:
            in_multicols = True
            multicol_cols = int(m.group(1))
            multicol_lines = 0
            continue

        if line.startswith(r"\end{multicols}"):
            rows = math.ceil(multicol_lines / multicol_cols) if multicol_cols else multicol_lines
            flush(current, rows * LINE_HEIGHT_PT)
            in_multicols = False
            multicol_cols = 1
            continue

        # ---- itemize --------------------------------------------------
        if line.startswith(r"\begin{itemize}"):
            in_itemize = True
            if not in_multicols:
                flush(current, 1.0)  # topsep
            continue

        if line.startswith(r"\end{itemize}"):
            in_itemize = False
            if not in_multicols:
                flush(current, 1.0)
            continue

        if line.startswith(r"\item"):
            block = line[len(r"\item"):].strip()
            # absorb continuation lines
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or nxt.startswith("\\item") or nxt.startswith(r"\end{"):
                    break
                block += " " + nxt
                i += 1
            text = visible_text(block)
            if in_multicols:
                col_w = (TEXT_WIDTH_PT / multicol_cols) - 10.0 - BULLET_INDENT_PT
                multicol_lines += wrapped_lines(text, col_w)
            else:
                n = wrapped_lines(text, TEXT_WIDTH_PT - BULLET_INDENT_PT)
                flush(current, n * LINE_HEIGHT_PT + 1.0)  # itemsep
            continue

        # ---- ordinary paragraph text ----------------------------------
        if line.startswith("\\") and not line.startswith(r"\noindent") and not line.startswith(r"\textbf"):
            continue  # a command we don't model; assume negligible height

        small = r"\small" in line
        block = line
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith("\\section") or nxt.startswith(r"\vspace") \
                    or nxt.startswith(r"\entry") or nxt.startswith(r"\begin"):
                break
            block += " " + nxt
            i += 1
        text = visible_text(block)
        if text:
            flush(current, wrapped_lines(text, TEXT_WIDTH_PT, small) * line_height(small))

    close_section()
    total = sum(p for _, p in sections)
    return total, sections


def report(path, baseline_path=None):
    with open(path) as f:
        total, sections = measure(strip_comments(f.read()))

    print(f"\n  {path}")
    print(f"  {'-' * 56}")
    for label, pts in sections:
        if pts <= 0:
            continue
        print(f"    {label[:40]:<42} {pts:6.0f} pt  ({pts / LINE_HEIGHT_PT:4.1f} lines)")
    print(f"  {'-' * 56}")
    print(f"    {'TOTAL':<42} {total:6.0f} pt")
    print(f"    {'PAGE BUDGET':<42} {TEXT_HEIGHT_PT:6.0f} pt")

    slack = TEXT_HEIGHT_PT - total
    is_baseline = (baseline_path and os.path.exists(baseline_path)
                   and os.path.abspath(baseline_path) != os.path.abspath(path))

    # The delta against the baseline is the trustworthy signal: both documents
    # go through the same model, so systematic bias cancels. The absolute
    # verdict is coarser and carries the full rounding uncertainty.
    if is_baseline:
        with open(baseline_path) as f:
            base_total, _ = measure(strip_comments(f.read()))
        delta = total - base_total
        print(f"\n  vs baseline ({baseline_path}, known to fit on one page):")
        if delta > LINE_HEIGHT_PT / 2:
            print(f"    ~{delta / LINE_HEIGHT_PT:.1f} lines LONGER  ->  likely spills. Cut a bullet.")
        elif delta < -LINE_HEIGHT_PT / 2:
            print(f"    ~{abs(delta) / LINE_HEIGHT_PT:.1f} lines shorter  ->  comfortable.")
        else:
            print("    same length  ->  fits as well as the baseline does.")

    verdict = "FITS" if slack >= 0 else "OVER"
    print(f"\n  Absolute estimate: {verdict} by {abs(slack):.0f} pt "
          f"(~{abs(slack) / LINE_HEIGHT_PT:.1f} lines), ±{UNCERTAINTY_PT / LINE_HEIGHT_PT:.0f} lines")
    if abs(slack) < UNCERTAINTY_PT:
        print("  Within the model's margin of error — trust the baseline delta above.")

    print("\n  Estimate only — no LaTeX engine here. Confirm on Overleaf.\n")
    return 0 if slack >= 0 else 1


def main():
    ap = argparse.ArgumentParser(description="Estimate one-page fit for a CV .tex file.")
    ap.add_argument("tex", nargs="?", default="resume.tex", help="the .tex file to measure")
    ap.add_argument("--baseline", default="resume.tex", help="baseline to compare against")
    args = ap.parse_args()

    if not os.path.exists(args.tex):
        print(f"error: no such file: {args.tex}", file=sys.stderr)
        return 2
    return report(args.tex, args.baseline)


if __name__ == "__main__":
    sys.exit(main())
