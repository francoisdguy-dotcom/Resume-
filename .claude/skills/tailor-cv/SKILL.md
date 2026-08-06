---
name: tailor-cv
description: Tailor Francois's CV to a specific job description. Use when a job posting, job description, job ad, or role spec is pasted in and a matching version of the CV is wanted, or when asked to "tailor my CV", "customise my resume for this role", or "apply to this job". Produces a tailored .tex plus an evidence map and honest gap report.
---

# Tailor CV

Turn a pasted job description into a version of the CV that reads as genuinely well suited to the
role — never as manufactured for it, and never claiming anything untrue.

## The governing idea

Do not write lines *toward* the posting. Everything true about Francois lives in
`profile/master.md`, which deliberately holds several times more material than fits on one page.
Tailoring is **selection and re-angling from that bank** — choosing what surfaces, what gets cut,
and which of his own existing phrasings leads.

This is what makes the result seamless: the language was always his. The posting only decides the
emphasis.

It also makes honesty structural rather than aspirational. A requirement with no backing fact has
nothing in the bank to draw on, so it cannot be written — it gets reported as a gap instead. **If
the match isn't there, don't force it.**

## Inputs

- `profile/master.md` — the fact bank. The only permitted source of claims.
- `resume.tex` — the baseline. Read-only; tailoring never edits it.
- `references/naturalness-rules.md` — anti-detectability constraints. Binding.
- `references/immutables.md` — never-change list. Binding.

If `profile/master.md` does not exist or is thin, say so before tailoring. Tailoring against an
empty bank degrades into keyword-matching, which is the thing this system exists to avoid.

## Procedure

### 1. Parse the job description

Read it twice — once for requirements, once for language. Extract:

- **Hard requirements** — the "you have" / "essential" list.
- **Preferred** — "nice to have", "bonus".
- **Responsibilities** — what the job actually does day to day. Often more revealing than the
  requirements list, which is frequently boilerplate.
- **Implicit profile** — seniority, autonomy expected, client-facing or not, team size, pace,
  whether it's a build-it-yourself shop or a process shop.
- **Employer vocabulary** — their specific term for each concept. This is the single most useful
  extraction. Note where their word differs from Francois's word for the same thing:
  *underwriting* vs *loan analysis*; *originations* vs *new lending*; *sponsor* vs *borrower*;
  *asset management* vs *portfolio work*; *investment committee* vs *credit committee*.
- **Register** — a clearing bank and a four-person fund write differently. Tone-match within the
  bounds of the voice fingerprint.

### 2. Build the evidence map

Every requirement lands in exactly one bucket:

| Bucket | Meaning | Use |
|---|---|---|
| **A** | Strong, direct evidence in the fact bank | Lead with it |
| **B** | Partial or adjacent — real, but not a bullseye | Use honestly, don't oversell |
| **C** | No evidence | **Never appears in the CV** |

Bucket C is the load-bearing rule. It goes to `notes.md` so Francois knows exactly where he's
short and can decide whether to apply, address it, or prepare for the question. It never gets
papered over with adjacent-sounding language.

Be strict about the A/B boundary. "I did something similar in a different asset class" is B. "I
have used this exact system" is A. Inflating B to A is how a CV survives the screen and dies in the
interview.

### 3. Select and order

- Choose which fact-bank bullets survive for each role, within the one-page budget.
- Lead each role with its strongest A-evidence bullet.
- Reorder the Technical Skills list so what the posting cares about comes first. Nothing is added.
- Section order and layout do not change.

### 4. Language pass

Apply `references/naturalness-rules.md` in full. The short form:

- Substitute the employer's vocabulary, never insert it.
- Alter at most ~60% of bullets; leave at least one bullet in the lead role untouched.
- Work down the lever priority — reorder before rewriting.
- Preserve the voice fingerprint: verb-first, British spellings, tense by recency, one figure per
  bullet on average.
- Add no sections, no keyword blocks, no skills that weren't already there.

### 5. Fit check — one page, always

```bash
python3 scripts/fit_check.py applications/<company>-<role>/resume.tex
```

**One page is a hard constraint.** A two-page output is a failed output. See `CLAUDE.md` for the
full rule and the list of prohibited workarounds — in short, fit is bought by **cutting a bullet**,
never by shrinking font, margins, or spacing.

The baseline has no headroom left, so anything promoted from the fact bank must be paid for by
something removed. That trade is the mechanism working: a fixed page forces selection, and selection
is what prevents keyword accumulation.

The estimator is a heuristic, not a renderer. Treat "roughly the same length as the baseline" as the
pass condition; real confirmation is the Overleaf compile.

### 6. Verify before writing

Run all four checks. Report the results; do not silently self-certify.

1. **Fabrication check.** Walk the diff line by line. For every changed phrase, name the specific
   `profile/master.md` entry it came from. Anything that can't be traced gets reverted.
2. **Immutables check.** Diff against `references/immutables.md`. Zero changes to names, titles,
   dates, IDs, classifications, contact details.
3. **Saturation check.** Count altered bullets as a percentage of total. Confirm the untouched
   bullet in the lead role.
4. **Cold-read test.** Read the whole thing as a stranger, without the posting in mind. Would it
   still work as an application to a different firm in the same sector? If not, it's over-fitted.

### 7. Write outputs

```
applications/<company>-<role>/
├─ jd.md         # the posting as pasted, for future reference
├─ resume.tex    # the tailored CV
└─ notes.md      # evidence map, gaps, change log, interview prep
```

Directory name: lowercase, hyphenated, e.g. `applications/blackstone-credit-analyst/`.

`notes.md` contains:

- **Evidence map** — each requirement, its bucket, and the backing fact.
- **Gaps (bucket C)** — stated plainly. This is the most useful section; do not soften it.
- **Change log** — every alteration with its justification and source fact.
- **Interview prep** — which claims Francois should expect to be asked to defend, given what was
  emphasised.

Then tell Francois: what was emphasised and why, where the real gaps are, and an honest read on
fit. If the role is a stretch, say so — a tailored CV cannot fix a genuine mismatch, and pretending
otherwise wastes his applications.

## When to refuse to tailor

Stop and say so if:

- The posting requires a qualification, licence, or right-to-work status not in the fact bank. No
  amount of emphasis substitutes for a hard credential.
- Matching would need bucket-C claims to do the work.
- The role is far enough from the evidence that an honest CV won't be competitive. Say that
  plainly, with what's missing — that is more valuable than a polished document that fails at
  first contact.

Declining to force a match is a correct outcome of this skill, not a failure of it.
