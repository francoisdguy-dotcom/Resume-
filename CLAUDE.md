# Working rules

Standing rules for this repository. These apply to every CV produced here — the baseline and every
tailored version — and override any conflicting guidance elsewhere, including in the skill.

## 1. Always one page

Every CV is exactly one page. This is not a target or a preference; it is a hard constraint, and a
two-page output is a failed output.

**Fit is bought by cutting, never by compressing.** When a draft runs over, remove the
weakest-evidence bullet and re-check. The following are prohibited as ways to make something fit:

- Reducing the font size below 10pt
- Widening the page by shrinking the `geometry` margins
- Tightening `\titlespacing`, `itemsep`, `topsep`, `parsep`, or any list spacing
- Removing the `\vspace` separators between entries
- Reducing `\baselineskip` or otherwise condensing line spacing

The layout parameters in `resume.tex` are settled. A CV that only fits because the margins were
squeezed reads as cramped, and a reader registers that before reading a word of it.

The constraint is also load-bearing for quality: a fixed page forces selection, and selection is
what stops a tailored CV from accumulating keywords. When something has to be cut to make room, that
pressure is the system working, not a problem to engineer around.

**Check before delivering:**

```bash
python3 scripts/fit_check.py <file.tex>
```

The estimator is a heuristic — there is no LaTeX engine in this environment — so it reports a
baseline delta and a margin of error rather than a verdict. Treat "roughly the same length as the
baseline" as the pass condition. Final confirmation is always the Overleaf compile.

**Current headroom: none.** The baseline measures ~5pt inside a ~794pt page. Anything added must be
paid for by something removed.
