# Do calculus — referee audit record

## Scope and workflow

First audit of "Markov categories, causal theories, and the do-calculus" (Yin and
Zhang; `docalculus.tex`, published as Studies in Logic 14 (2021)), November 20.
It follows the free Markov workflow (`../free markov/REVIEW.md`), step 1. The
statements and proofs were read independently, in paper order, and every picture was
checked in a compiled copy. Each finding is classified as **Error**, **Gap** (omitted
justification), **Clarification** or **Typo**. The report has the format of the free
Markov second audit: purple remarks R001–R018 inside the retained original text, with
an overview page.

- Annotated audit: `Do calculus - audit.tex` and `Do calculus - audit.pdf` (22 pages).
- Untouched original: `docalculus.tex` (sha256 `a25eb61e…`).
- Build: `python3 review/make-audit.py`. It checks the hash and the 18 insertion lines,
  writes the audit, and compiles it in `.scratch/audit/`. It uses Tectonic from
  ChatGPT.app, offline, with the free Markov cache. Two font substitutions apply to
  the offline build only: `cmss12` is replaced by Latin Modern Sans for `\cau`, and
  `cmsy7` by scaled `cmsy6` in the footnote. No git here.

Checked against:
- the revised free Markov paper (`../free markov/Free Markov - revised.tex`,
  November 20): Theorem 4.1, Lemmas 4.3–4.5, Remarks 5.2–5.3, Definitions 5.4, 6.2,
  6.4, Proposition 5.6;
- Fong, arXiv:1301.6201v1: Section 4 (causal conditionals, pp. 43–44) and
  Proposition 4.2. Fong's statement is about *inferential* maps, i.e. maps that do not
  factor through the unit, not about "connected" maps;
- Fritz, arXiv:1908.07021v8: Remark 2.3, Definition 10.14, Theorem 10.17,
  Definition 11.5, Example 11.6, Definition 12.12;
- Huang and Valtorta, UAI 2006: Lemma 4 ("Rule 1 follows from rule 2 and rule 3").

All of these citations are correct. Not read: Pearl 1995, Mac Lane, SGS, Tian–Pearl,
Jacobs–Kissinger–Zanasi.

## Findings

| Item | Class | Place | Finding |
| --- | --- | --- | --- |
| R001 | Typo | ll. 533, 633, 688, 758 | `\delta_n`, `\sigma_{BA}`, unnamed category, missing parentheses |
| R002 | Typo | l. 890 | pa(v) "contains all the parents" must be exactly the parents; "a exogenous", "an categorical" |
| R003 | Clarification | ll. 893–904 | state the strict universal property of Cau(G); models in Set, Rel via Fritz 10.17 |
| R004 | Clarification | l. 914 | multiplier uniqueness: cite free Markov Remark 5.3, not "(2.5)" |
| R005 | Clarification | l. 960 | `vw`, `uv`, `vu` are not sub-variables of V̇; `[w‖uv]` versus `[w‖vu]` |
| R006 | Clarification | l. 977 | independence of choices; each κ_i occurs once and is live |
| R007 | Error | Lemma 4.2 | items 2, 3 false (balanced tree versus comb: 12/13 paths, 8/10 splitter paths); replacement from free Markov Lemma 4.3 |
| R008 | Clarification | Lemma 4.3 | `f = g ⊗ ε_{v'}` lacks the symmetry; free Markov Lemma 4.5 |
| R009 | Clarification | proof of Lemma 4.5 | case v ∈ u; identification of the remaining components |
| R010 | Error | Proposition 4.6 | false with "connected" (the left side of (4.2) is a counterexample); restate with Fong's "inferential"; proof given |
| R011 | Clarification | l. 1322 | unproved general claim; slip "conditional of [w‖uv]" |
| R012 | Clarification | proofs of Thms 4.8, 4.10 "if" | shortening to proper treks; children decomposition; slips l. 1403, l. 1404 |
| R013 | Gap | Thm 4.8 "only if" | argument relies on false items; corrected item 3 does not suffice (k→a, k→b, a→b); counting proof given |
| R014 | Gap | Thm 4.11 "only if" | same; counting proof given |
| R015 | Clarification | Cor 4.12 | (4.11), (4.12) labelled `[w‖uv]` but wired as `[w‖vu]`; strong versus strict F |
| R016 | Gap | Section 5 footnote | `v_G` undefined; `\mathbf(V)`; F([v‖u]) = v-marginal of (3.2) needs a proof (given) |
| R017 | Gap | ll. 1908–1913 | invariance P(V \| pa(V), do(T)) = P(V \| pa(V)) missing; derived from Rules 2, 3 |
| R018 | Clarification | bibliography | new pointers into the free Markov paper; Fong is a master's thesis |

Correct and checked: Example 3.7, Lemma 4.5 (statement), the "if" directions of
Theorems 4.8, 4.10, 4.11, Corollary 4.12, the example (4.2) against Fong, the example
x → y after Proposition 4.6, the remark that (4.11) holds in Set, the equivalence of
Rules 1–3 with Pearl's rules for empty W (in the mutilated graphs no collider can be
opened, and the collider-free paths from Z are exactly the treks of the matching kind),
and the derivation of the local Markov condition.

## Relation to the free Markov audit of this paper

`../free markov/review/docalculus-audit.md` (same day) audited this paper for its
uses of the free Markov paper. This audit agrees with it on Lemma 4.2, Lemma 4.3,
Proposition 4.6 and the slips. It adds:

- the counterexample to Proposition 4.6 is already in the paper, at (4.2);
- Fong's Proposition 4.2 concerns inferential maps;
- the necessity proofs of Theorems 4.8 and 4.11 fail as written, even with the corrected
  lemma, and need the counting argument;
- (4.11) and (4.12) are ill-typed as labelled;
- `v_G` is undefined;
- the Section 5 footnote and the post-intervention step need proofs (R016, R017);
- the case v ∈ u in the proof of Lemma 4.5 is not handled.

## Next step

If the paper is to be revised, use the free Markov procedure. R001 and R002 are
routine edits. Everything else goes in batches of at most two items, with orange
review copies and approval before applying.
