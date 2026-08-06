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

## 2. Uniform typography and spacing

Anything that is the same *kind* of thing is set the same way. Font size, weight, and style are
determined by what an element **is**, never by how important a particular instance feels. Two
constructs that look structurally alike must render alike — a reader reads inconsistency as
carelessness long before they can name what is wrong.

### Type scale

| Element | Setting |
|---|---|
| Name | `\LARGE\bfseries` |
| Contact line | `\small` |
| Section heading | `\normalsize\bfseries\uppercase` + rule |
| Entry — employer or institution | `\normalsize\bfseries` |
| Entry — location | `\small\textit` |
| Entry — role or qualification | `\normalsize\textit` |
| Entry — dates | `\small` |
| Bullet text | `\normalsize` |
| Standalone supplementary block | `\small`, bold lead-in, `---` separator |

"Standalone supplementary block" means the credential and affiliation paragraphs that close a
section — currently the A.CRE line and the memberships list. They are the same construct and take
the same treatment.

### Spacing scale

Every vertical gap comes from this list. Do not introduce new values.

| Gap | Value | Source |
|---|---|---|
| Before a section heading | 6pt | `\titlespacing` |
| After a section heading | 2pt | `\titlespacing` |
| Between entries | `\vspace{4pt}` | explicit |
| Between the two lines of an entry | `\\[-2pt]` | `\entry` macro |
| After an entry block | `\vspace{1pt}` | `\entry` macro |
| Between bullets | 1pt | `itemsep` |
| Above and below a bullet list | 1pt | `topsep` |

The first entry after a section heading takes no `\vspace{4pt}` — the heading's 2pt trailing space
covers it. This is deliberate, not an omission.

### How to keep it uniform

Entries go through the `\entry` macro, which is why they are consistent by construction. Anything
set by hand is where drift appears, so prefer the macro. When adding a construct that has no macro,
match an existing one exactly rather than inventing a variant.

Never adjust spacing or type size to solve a length problem — that is rule 1's territory, and the
answer there is always to cut a bullet.
