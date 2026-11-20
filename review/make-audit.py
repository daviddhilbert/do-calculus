#!/usr/bin/env python3
"""Build the annotated audit of the do-calculus paper.

    python3 review/make-audit.py

Reads the untouched manuscript `docalculus.tex`, inserts the referee preamble,
the overview and the purple referee remarks R001-R018 (format of the free Markov
second audit), writes `Do calculus - audit.tex`, compiles it offline with the
Tectonic bundled with ChatGPT.app and copies the PDF to `Do calculus - audit.pdf`.
Each remark is inserted after a fixed line of the original; the script checks
that line before inserting.
"""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = root / 'docalculus.tex'
target = root / 'Do calculus - audit.tex'
pdf_target = root / 'Do calculus - audit.pdf'
build = root / '.scratch' / 'audit'
TECTONIC = '/Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic'
CACHE = root.parent / 'free markov' / '.scratch' / 'tectonic-cache'
SHA256 = 'a25eb61ec4760a9696e68b7c0d364f0ccd512561aa3ad92eb2edc30722dc4a79'

PREAMBLE_OLD = '\\usepackage{tikzit}\n\\input{cause.tikzstyles}\n'
PREAMBLE_NEW = r'''% BEGIN REFEREE INSERTION FIGURE SUPPORT
\IfFileExists{cause.tikzstyles}{\IfFileExists{tikzit.sty}{\def\ReviewOriginalTikz{1}}{}}{}
\ifdefined\ReviewOriginalTikz
\usepackage{tikzit}
\input{cause.tikzstyles}
\else
\pgfdeclarelayer{edgelayer}
\pgfdeclarelayer{nodelayer}
\pgfsetlayers{edgelayer,nodelayer,main}
\tikzset{none/.style={inner sep=0pt,minimum size=0pt},
 wire/.style={draw=black,line width=0.6pt},
 small box/.style={draw,fill=white,minimum width=0.6cm,minimum height=0.45cm,inner sep=2pt,font=\small},
 wide small box/.style={draw,fill=white,minimum width=1.1cm,minimum height=0.45cm,inner sep=2pt,font=\small}}
\fi
% END REFEREE INSERTION FIGURE SUPPORT
% BEGIN REFEREE INSERTION FONT SUPPORT
% Offline build only: cmss12 and cmsy7.pfb are not in the Tectonic cache.
\DeclareMathAlphabet{\mathsf}{TU}{lmss}{m}{n}
\DeclareFontShape{OMS}{cmsy}{m}{n}{<-7.5>cmsy6 <7.5-9>cmsy8 <9->cmsy10}{}
% END REFEREE INSERTION FONT SUPPORT
'''

COLOR_OLD = '\\usepackage{environ}\n'
COLOR_NEW = r'''\usepackage{environ}
% BEGIN REFEREE INSERTION LINK DISPLAY
\hypersetup{hidelinks}
% END REFEREE INSERTION LINK DISPLAY
% BEGIN REFEREE INSERTION PREAMBLE
% Purple referee remarks; all original color commands are unchanged.
\definecolor{RefereePurple}{RGB}{103,34,147}
\newcommand{\RefereeRemark}[4]{%
  \par\medskip\begingroup\normalfont\small\color{RefereePurple}%
  \emergencystretch=1.5em\noindent\textbf{Referee R#1 [#2] -- #3.}\par\nobreak\noindent #4\par
  \endgroup\medskip
}
% END REFEREE INSERTION PREAMBLE
'''

OVERVIEW = r'''% BEGIN REFEREE INSERTION OVERVIEW
{\normalfont\small\color{RefereePurple}
\noindent\textbf{Technical referee report. First audit.}\par\nobreak
\noindent\textbf{Recommendation. Minor revision.}
The three characterizations, Theorems~\ref{thm: main1}, \ref{thm:main2} and~\ref{thm:main3}, and Corollary~\ref{cor:model:do} are correct. So is the recovery of Pearl's calculus from Rules~2 and~3 in Section~\ref{sec:cal}, once one step is added. Two statements need repair. Lemma~\ref{decor:mat}, quoted from the free Markov paper, is false in its second and third items. The corrected form proved there is enough for every use (\hyperlink{review-007}{R007}). Proposition~\ref{connect:ancestral} is false with \emph{connected} in the sense of Definition~\ref{defn:inferen}, and the left side of (\ref{fong:counter}) is a counterexample. Fong's own formulation, about maps that do not factor through the unit, is true and follows from Lemma~\ref{infe:ances} (\hyperlink{review-010}{R010}).
\par\smallskip
The ``only if'' proofs of Theorems~\ref{thm: main1} and~\ref{thm:main3} rest on the false items and do not go through as written (\hyperlink{review-013}{R013}, \hyperlink{review-014}{R014}). Both follow from the first item alone. Every mechanism occurs once in a diagram of a causal effect and is not quasi-terminal (\hyperlink{review-006}{R006}). So a trek that avoids $u$ produces a second such copy of one mechanism on the right side. Section~\ref{sec:cal} obtains a factorization of $P(\mathbf{V} | do(\mathbf{T}))$ with post-intervention factors. Their equality with the pre-intervention factors still has to be derived from Rules~2 and~3, and it can be (\hyperlink{review-017}{R017}).
\par\smallskip
I read the supplied source independently, in paper order, and checked every picture in a compiled copy. The results cited as \cite{YinZhangModularity} were checked against the revised free Markov paper of November~20; \hyperlink{review-018}{R018} lists the new pointers. I read Fong's thesis (arXiv v1, Section~4 and Proposition~4.2), Fritz (arXiv v8, Remark~2.3, Definitions~10.14, 11.5 and~12.12, Theorem~10.17, Example~11.6) and Huang--Valtorta (Lemma~4). These citations are correct. Also checked and correct: Example~\ref{exa:cau:con}, Lemma~\ref{three:cau:mar}, the ``if'' directions, the example (\ref{fong:counter}) against Fong, the example after Proposition~\ref{connect:ancestral}, the claim that (\ref{do-cal2}) holds in every model in \cat{Set}, the equivalence of Rules~1--3 with Pearl's rules for empty $\mathbf{W}$, and the derivation of the local Markov condition. There are 18 remarks: 2 \textbf{Error}, 4 \textbf{Gap}, 10 \textbf{Clarification} and 2 \textbf{Typo}. Each purple insertion gives the original source line. The original text is retained, so each proposal can be read against its claim.
\par}
% END REFEREE INSERTION OVERVIEW

% BEGIN REFEREE INSERTION CONTENTS BREAK
\clearpage
% END REFEREE INSERTION CONTENTS BREAK
'''

# (insert after this line of the original, expected start of that line, number, class, title, text)
REMARKS = [
(799, r'\end{defn}', '001', 'Typo', 'Four local edits in Section 2', r'''\textit{Original source lines 533, 633, 688, 758.}\quad Line~688: the right-hand composite of counitality is $(\epsilon_A \otimes 1_A) \circ \delta_A$, so the subscript $n$ should be $A$. Line~758: line~602 fixes $\sigma_{AB} : A \otimes B \fun B \otimes A$. With that convention, the middle swap after $\delta_A \otimes \delta_B$ is $\sigma_{AB}$, not $\sigma_{BA}$. Line~633: name the category, ``a symmetric monoidal category $\cat C$''. Line~533: ``equation \ref{monoidal:def}'' should be ``equation (\ref{monoidal:def})''.'''),
(891, r'\end{itemize}', '002', 'Typo', 'Exactly the parents', r'''\textit{Original source line 890.}\quad ``Contains all the parents of $v$'' should read ``consists of the parents of $v$, in a chosen order''. If $\pa(v)$ contained a non-parent $j$, the count $o_j = p_j + 1$ in Definition~\ref{gen:condi} would fail, because the input $j$ of $\kappa_v$ is not counted among the copies of $j$. Remark~\ref{cau:mech:ind} and Fong's definition \cite[\S~4]{Fong:thesis} both take exactly the parents. On the same line, ``a exogenous'' should be ``an exogenous''. At line~904, ``an categorical'' should be ``a categorical''.'''),
(904, r'Following \cite{Fong:thesis}', '003', 'Clarification', 'The universal property of the causal theory', r'''\textit{Original source lines 893--904.}\quad \emph{Free} is explained only informally (``no junk no noise''). What the paper uses is strict freeness. Remark~\ref{cau:mech:ind} is the strict Markov functor that sends $\kappa_v$ to $\kappa'_v$ composed with a symmetry, and Terminology~\ref{what:dia} describes the free object. State the universal property. $\cau(G)$ is the strict Markov category that is free over the signature whose letters are the atomic variables and whose arrows are $\epsilon_v$, $\delta_v$, $\kappa_v$ \cite[Theorem~4.1, Definition~6.2]{YinZhangModularity}. So, for every strict Markov category $\cat D$, any assignment of objects to the atomic variables and of morphisms of the right types to the $\kappa_v$ extends to exactly one strict Markov functor $\cau(G) \fun \cat D$. \cat{Set} and \cat{Rel} are not strict, but every Markov category is comonoid equivalent to a strict one \cite[Theorem~10.17]{fritz2020synthetic}. Composing with that equivalence gives the strong Markov functors used as models at line~904.'''),
(949, r'\end{nota}', '004', 'Clarification', 'Uniqueness of multipliers', r'''\textit{Original source line 914.}\quad For several factors, uniqueness does not follow from (\ref{mon:law}) alone. It also uses (\ref{fins:frob}) and the coherence of the symmetries. A proof is now in \cite[Remark~5.3]{YinZhangModularity}. There, a multiplier on distinct letters is the image of a morphism of the free Markov category on those letters with no further generators. In that category a diagram has no live nodes, and the label of each output determines its origin. So all such diagrams have the same skeleton and represent one morphism \cite[Lemma~4.4]{YinZhangModularity}. Cite this instead of ``(\ref{mon:law}) or coherence''. Definition~\ref{gen:condi} needs only the one-letter multipliers $\iota_{i \rightarrow i^m}$, whose uniqueness is the usual comonoid coherence for (\ref{mon:law}) \cite[Remark~5.2]{YinZhangModularity}.'''),
(963, r'\end{nota}', '005', 'Clarification', 'Concatenations that are not sub-variables of the maximal one', r'''\textit{Original source line 960.}\quad After this convention the text uses concatenations such as $vw$, $uv$, $vu$. These are sub-variables of $\dot V$ only when their letters happen to be in order. The text also uses $[w \| vu]$ and $[w \| uv]$ interchangeably. (\ref{effect:decom}), Theorem~\ref{thm: main1}, (\ref{screenoff}) and Theorem~\ref{thm:main2} have $[w \| vu]$. The proof of Theorem~\ref{thm: main1}, line~1322 and Corollary~\ref{cor:model:do} have $[w \| uv]$. These are different morphisms: $[w \| uv] = [w \| vu] \circ \sigma_{uv}$. Definition~\ref{gen:condi} applies verbatim to any singular words $t$, $v$, because inputs and outputs carry distinct labels. Alternatively, define $[w \| v]$ for arbitrary singular variables as a twist of the effect between sub-variables of $\dot V$, as in \cite[Definition~6.4]{YinZhangModularity}. Then fix one order. A conditional over $v$ has domain $v \otimes u$ (Definition~\ref{defn:gen:cond}), so $[w \| vu]$ is the consistent choice throughout Section~\ref{sec:effect}. \hyperlink{review-015}{R015} names the displays where the mismatch matters.'''),
(978, r'\end{defn}', '006', 'Clarification', 'What the construction guarantees', r'''\textit{Original source line 977.}\quad Two facts make the definition precise, and every proof in Section~\ref{sec:effect} uses them tacitly. First, the morphism does not depend on the choices. Another matching of the wires composes some $\iota_{j \rightarrow j^m}$ with a symmetry, which gives a multiplier on the single letter $j$ again, hence the same morphism (Notation~\ref{uni:pro}). Second, each $\kappa_i$ with $i \in V(G_{t \rightarrow v}) \mi t$ occurs exactly once in $\stri_{[v \| t]}$ and is not quasi-terminal, since a directed path leads from it to the codomain. With the multipliers drawn as binary trees, no duplicate is quasi-terminal either. The only discards are those on the vertices $j \in t \mi v$ without children. Both facts are stated and proved in \cite[Definition~5.4]{YinZhangModularity}. The counting arguments in \hyperlink{review-013}{R013} and \hyperlink{review-014}{R014} need the second one. Say also that $t$ and $v$ may overlap (the case $i \in t \cap v$), since Lemma~\ref{three:cau:mar} allows it.'''),
(1104, r'\end{lem}', '007', 'Error', 'Path data are not invariant', r'''\textit{Original source line 1097.}\quad The first item is true. The second and third items are false. Take the fourfold copy $\iota_{v \rightarrow v^4}$ on an atomic variable, drawn once as a balanced binary tree of three duplicates and once as a comb. Coassociativity surgeries connect the two diagrams, and neither has a quasi-terminal node. The comb has a directed path that ends in the codomain and passes through all three duplicates; the balanced tree has none. So there is no bijection $\dot\pi$ compatible with $\pi$. The counts differ as well: 13 against 12 directed paths ending in the codomain, and 10 against 8 splitter paths between edges of the codomain. Path data change under coassociativity. Only the existence of a path between given ends is invariant.
\par\smallskip\emph{Replacement statement} \cite[Lemma~4.3]{YinZhangModularity}. Keep the first item. Call a node \emph{live} if it is in $\tilde \Delta_\Gamma$ and is not a duplicate. Second item: for live nodes $x$, $y$ of $\Gamma$ there is a directed path $x \rightsquigarrow y$ in $\Gamma$ if and only if there is a directed path $\pi(x) \rightsquigarrow \pi(y)$ in $\Upsilon$. The same holds with $x$ replaced by the $i$th edge of the domain, or $y$ by the $j$th edge of the codomain. Third item: the same holds for splitter paths between two ends, each of which is a live node or an edge of the codomain. $P_\Gamma$ and $S_\Gamma$ are then not needed.
\par\smallskip\emph{Uses.} The argument at line~1320 goes through verbatim with the first and third items. The proof of Theorem~\ref{thm:main2} (line~1542) goes through with the second item, for paths that begin with an edge of the domain. The proofs at lines~1408 and~1702 do not; see \hyperlink{review-013}{R013} and \hyperlink{review-014}{R014}.'''),
(1110, r'\end{lem}', '008', 'Clarification', 'A symmetry is missing', r'''\textit{Original source line 1109.}\quad $f = g \otimes \epsilon_{v'}$ is well typed only if $v'$ is a final segment of $v$. Otherwise $g \otimes \epsilon_{v'}$ has domain $(v/v')\,v' \neq v$, and symmetries are not identities here (Notation~3.5). Write $f = (g \otimes \epsilon_{v'}) \circ \tau$, where $\tau : v \fun (v/v')\,v'$ moves the letters of $v'$ to the end and otherwise keeps the order. This form is \cite[Lemma~4.5]{YinZhangModularity}, which also gives the uniqueness of $g$ and describes $v'$ as the inputs that are the origin of no consumer. Proposition~\ref{connect:ancestral} uses the lemma in this form (\hyperlink{review-010}{R010}).'''),
(1202, r'\end{proof}', '009', 'Clarification', 'Two cases of the reduction', r'''\textit{Original source line 1201.}\quad The lemma assumes only $v \cap w = \0$, so the atomic variable $v$ may lie in $u$. Then $\stri_v$ contains no $\kappa_v$, and ``reduced to $\bigotimes_{j \in \pa(v)} \epsilon_j$'' would delete the input wire. In this case $G_{u \rightarrow vw} = G_{u \rightarrow w}$, since every path that ends in $v$ ends in $u$. Composing with $\epsilon_v$ replaces $\iota_{v \rightarrow \bar v \otimes v}$ by $\iota_{v \rightarrow \bar v}$: by counitality if $\bar v \neq \0$, and trivially if $\bar v = \0$. For $v \notin u$, the last sentence needs one observation in each case. If $v$ has a child in $G_{u \rightarrow vw}$, then every path that ends in $v$ and avoids $u$ extends to one that ends in $w$, so again $G_{u \rightarrow vw} = G_{u \rightarrow w}$. If not, the successive discard surgeries remove exactly the vertices of $V(G_{u \rightarrow vw}) \mi u$ from which no directed path avoiding $u$ reaches $w$, that is, the vertices of $V(G_{u \rightarrow vw}) \mi V(G_{u \rightarrow w})$. Every remaining vertex keeps exactly its children in $G_{u \rightarrow w}$.'''),
(1267, r'\end{prop}', '010', 'Error', 'Connected versus inferential', r'''\textit{Original source line 1266; see also line 1262.}\quad Read ``connected'' as in Definition~\ref{defn:inferen} (any concatenation of directed paths, colliders included). Read ``a morphism in which $v$, $w$ are connected'' through Terminology~\ref{what:dia} (some diagram of it). Then the first claim is false, and the left side of (\ref{fong:counter}) is a counterexample. In the third graph of Example~\ref{exa:cau:con}, it is a diagram of $(1_x \otimes \epsilon_y) \circ [xy \| z] = \kappa_x \otimes \epsilon_z : z \fun x$. In it, $z$ and $x$ are connected through the collider $\kappa_y$, and $z$ is not an ancestor of $x$. Fong's Proposition~4.2 is about \emph{inferential} maps, those that do not factor through the monoidal unit \cite[p.~43]{Fong:thesis}. That version is true, and it is the one to state.
\par\smallskip\emph{Replacement statement.} If a morphism $f : v \fun w$ does not factor through $\0$, then $v$ is an ancestor of $w$. \emph{Proof.} Apply Lemma~\ref{infe:ances}, with the symmetry of \hyperlink{review-008}{R008}. Either $v' = v$, and $f = g \circ \epsilon_v$ factors through $\0$. Or $v' = \0$, and every diagram of $f$ contains a directed path from the input $v$ to the output $w$. Along a directed path in a diagram in $\cau(G)$, the label stays the same at a duplicate and passes from a parent to a child at a node $\kappa_i$. So $v$ is an ancestor of $w$. The hypothesis may equivalently be ``$v$ and $w$ are connected by a directed path in some diagram of $f$'' or ``connected in every diagram of $f$''. The second claim of the proposition is correct. The sentence at line~1262 (``this claim does hold'') is right for Fong's formulation. The sentence after the proposition should say ``inferential'' instead of ``connected''.'''),
(1375, r'Call the property expressed by', '011', 'Clarification', 'An unproved claim and a slip', r'''\textit{Original source line 1322.}\quad The general fact is asserted with its proof deferred, and nothing later depends on it. Label it as a claim without proof, or prove it; the completeness of the skeleton invariant \cite[Lemma~4.4]{YinZhangModularity} is the natural tool. A conditional over $v$ has domain $v \otimes u$ (Definition~\ref{defn:gen:cond}), so the candidate should read $[w \| vu]$ (\hyperlink{review-005}{R005}). Slip: ``when $[w \| uv]$ is a conditional of $[w \| uv]$'' should end ``of $[vw \| u]$''.'''),
(1406, r'This establishes (\ref{effect:decom}).', '012', 'Clarification', 'Graph-theoretic steps', r'''\textit{Original source lines 1402--1404 and 1540.}\quad Three steps are tacit. (a)~The first case produces a directed path from $i$ to $v$ that avoids $u$, and either $i \in w$ or a directed path from $i$ to $w$ that avoids $uv$. This is not yet a proper backward trek. Shorten as follows. Stop the first path at its first vertex $a \in v$. If it meets $w$, its segment from the last vertex of $w$ to $a$ is already a proper backward trek. Otherwise, stop the second path at its first vertex $b \in w$, and let $k$ be the last vertex of the first path that lies on the second. Then $a \leftarrow \cdots \leftarrow k \rightarrow \cdots \rightarrow b$ is proper and avoids $u$. (b)~For $i \in uv$, the children of $i$ in $G_{u \rightarrow vw}$ are the disjoint union of its children in $G_{u \rightarrow v}$ and in $G_{uv \rightarrow w}$. For $i \notin uv$, its children in $G_{u \rightarrow vw}$ are its children in the one subgraph that contains it. This is what makes the components agree. (c)~In Theorem~\ref{thm:main2}, forward-$t$-separation also excludes paths of $G_{u \rightarrow w}$ that start in or pass through $v$. This is needed for $G_{vu \rightarrow w}$ to be $G_{u \rightarrow w}$ together with the isolated vertices of $v$. Slips: at line~1403, ``joined by $\delta_u$'' should be ``by $\delta_u$ or $\delta_v$'' (the latter for $i \in v$); at line~1404, ``$G_{(uv \rightarrow w}$''.'''),
(1409, r'\end{proof}', '013', 'Gap', 'The necessity of backward separation', r'''\textit{Original source line 1408.}\quad The first alternative is already excluded by the preceding sentence. If $\pi$ is a directed path $b \rightsquigarrow a$ avoiding $u$, then $b \in V(G_{u \rightarrow v})$, so $\kappa_b$ occurs in $\stri_{[v \| u]}$. The second alternative uses the path matching of the second and third items of Lemma~\ref{decor:mat}, which are false (\hyperlink{review-007}{R007}). The corrected third item does not suffice either. Take $k \rightarrow a$, $k \rightarrow b$, $a \rightarrow b$, $u = \0$, $v = a$, $w = b$. On the right side of (\ref{effect:decom}) a splitter path between the outputs $a$ and $b$ starts at $\delta_a$, and on the left side one starts at $\kappa_k$.
\par\smallskip\emph{Replacement proof.} Use only the first item, as a count of mechanisms that are not quasi-terminal. Each $\kappa_i$ occurs once in $\stri_{[vw \| u]}$ (\hyperlink{review-006}{R006}). On the right side, every $\kappa_i$ of $\stri_{[v \| u]}$ and of $\stri_{[w \| vu]}$ stays non-quasi-terminal, since it still reaches the codomain. Suppose that $\pi$ avoids $u$. If $\pi$ is a directed path $b \rightsquigarrow a$, then $b \in V(G_{u \rightarrow v}) \mi u$ and $b \in w$, so $\kappa_b$ occurs in both factors. If $\pi$ is $a \leftarrow \cdots \leftarrow k \rightarrow \cdots \rightarrow b$, then $k \notin u \cup v \cup w$. Also $k \in V(G_{u \rightarrow v})$ and $k \in V(G_{vu \rightarrow w})$, because the branch to $b$ meets neither $u$ nor $v$. Either way, the right side has two non-quasi-terminal nodes with the same mechanism, and the left side has one. In the example, two copies of $\kappa_k$ face one.'''),
(1703, r'\end{proof}', '014', 'Gap', 'The necessity of t-separation', r'''\textit{Original source line 1702.}\quad The closing sentence relies on the second and third items of Lemma~\ref{decor:mat} (\hyperlink{review-007}{R007}). The preceding sentence already gives the contradiction, by the first item alone. A forward trek $a \rightsquigarrow b$ avoiding $u$ puts $a$ in $V(G_{u \rightarrow w}) \mi u$, so $\kappa_a$ would occur in $\stri_{[w \| u]}$. A directed path $b \rightsquigarrow a$ avoiding $u$ puts $b$ in $V(G_{u \rightarrow v}) \mi u$. For $a \leftarrow \cdots \leftarrow k \rightarrow \cdots \rightarrow b$, the mechanism $\kappa_k$ occurs in both $\stri_{[v \| u]}$ and $\stri_{[w \| u]}$: twice on the right side of (\ref{concau:indep:free}) and once on the left. Replace the last two sentences accordingly.'''),
(1846, r'\end{cor}', '015', 'Clarification', 'Typing in the corollary', r'''\textit{Original source lines 1707, 1758, 1811.}\quad ``Let $M$'' should be ``Let $\cat M$''. In items (2) and (3) and in (\ref{do-cal2}), (\ref{do-cal3}), the box is labelled $F([w \| uv])$ but wired with $v$ as its first input, as in (\ref{effect:decom}) and (\ref{screenoff}). Read with its label, (\ref{do-cal3}) discards $F(u)$ and feeds $F(v)$ into $F([w \| u])$, which is ill typed. Use $F([w \| vu])$ (\hyperlink{review-005}{R005}). If $F$ is strong but not strict, read the boxes with two outputs $F(v)$, $F(w)$ through the structure isomorphism $F(vw) \cong F(v) \otimes F(w)$. If $\cat M$ is strict, $F$ may be taken strict (\hyperlink{review-003}{R003}), and then the equations hold as drawn.'''),
(1852, r'Corollary \ref{cor:model:do} is particularly interesting', '016', 'Gap', 'From effects to truncated factorizations', r'''\textit{Original source lines 1852 (footnote) and 1878.}\quad ``$v_G$'' is not defined; presumably the maximal singular variable $\dot V$ of Notation~3.5 is meant. ``\texttt{\textbackslash mathbf(V)}'', typeset as a bold ``(V)'', should be $\mathbf{V}$. The sentence ``His argument can be generalized \ldots'' carries the whole translation in this section, so it should be a lemma with a proof. Statement: let $F : \cau(G) \fun \cat{FinStoch}$ be a strict Markov functor with $F(\kappa_i)$ the matrix of $P(i \mid \pa(i))$; then $F([v \| u])$ is the $v$-marginal of $P(\mathbf{V} \mid do(u))$ in (\ref{fac:post}). Proof: by \cite[Proposition~5.6]{YinZhangModularity}, $F([v \| u])$ is the diagram $\stri_{[v \| u]}$ evaluated in \cat{FinStoch}. This evaluation sums the product of the $P(i \mid \pa(i))$, $i \in V(G_{u \rightarrow v}) \mi u$, over the values of the vertices outside $u \cup v$. In (\ref{fac:post}), the remaining vertices $N = V \mi (u \cup V(G_{u \rightarrow v}))$ have all their children in $N \cup u$. Indeed, a child $c \notin u$ of $i$ with $c \in V(G_{u \rightarrow v})$ would put $i$ in $G_{u \rightarrow v}$. So their factors sum to $1$, working backward from the sinks of $N$. At line~1878, ``or regular'' is undefined; positivity is what the equivalences use.'''),
(1913, r'From this follows the factorization', '017', 'Gap', 'Post-intervention factors', r'''\textit{Original source lines 1908--1913.}\quad The equalities $P(V \mid \nd^*(V), do(\mathbf{T})) = P(V \mid \pa^*(V), do(\mathbf{T}))$ give a factorization of $P(\mathbf{V} \mid do(\mathbf{T}))$. Its factors are conditionals of the post-intervention distribution, $P(V \mid \pa(V), do(\mathbf{T}))$ for $V \notin \mathbf{T}$. The intervention principle (\ref{fac:post}) requires the pre-intervention factors $P(V \mid \pa(V))$. The missing step also follows from the specialized rules. For $V \notin \mathbf{T}$, apply Rule~2 with $(\mathbf X, \mathbf Z, \mathbf Y) = (\mathbf{T}, \pa(V) \mi \mathbf{T}, V)$, then Rule~3 with $(\pa(V), \mathbf{T} \mi \pa(V), V)$, then Rule~2 with $(\0, \pa(V), V)$. This gives $P(V \mid \pa(V) \mi \mathbf{T}, do(\mathbf{T})) = P(V \mid do(\pa(V))) = P(V \mid \pa(V))$, where the parents in $\mathbf{T}$ take their intervened values. The conditions hold for two reasons. A proper backward trek from a set of parents to $V$ must enter $V$ through a parent, which lies either in $\mathbf{T}$ or in that set. And every directed path into $V$ passes through a parent. State also the setting in which ``entailed'' is meant: a family of positive distributions $P(\cdot \mid do(\mathbf{T} = \mathbf{t}))$, under which $\mathbf{T} = \mathbf{t}$ holds with probability one.'''),
(1925, r'under the General Research Fund', '018', 'Clarification', 'The free Markov reference', r'''\textit{Original source line 1998.}\quad The manuscript cited as \cite{YinZhangModularity} is now Y.~Yin, ``A graphical construction of free Markov categories'' (revised November~20), and its numbering has settled. New pointers: Notation~\ref{uni:pro} $\to$ Remark~5.3; ``free'' and Terminology~\ref{what:dia} $\to$ the introduction, Theorem~4.1 and Definition~6.2; Definition~\ref{gen:condi} $\to$ Definitions~5.4 and~6.4 (the construction is the same); line~1093 $\to$ the four Markov templates of Section~4; Lemma~\ref{decor:mat} $\to$ Lemma~4.3, corrected (\hyperlink{review-007}{R007}); Lemma~\ref{infe:ances} $\to$ Lemma~4.5; the footnote in Section~\ref{sec:cal} $\to$ Proposition~5.6. Fong's entry should say ``Master's thesis, University of Oxford, 2012''. The other citations checked are correct: Fong, Section~4 and Proposition~4.2; Fritz, Remark~2.3, Definitions~10.14, 11.5 and~12.12, Example~11.6; Huang--Valtorta, Lemma~4.'''),
]


def remark_block(number, kind, title, text):
    return (f'% BEGIN REFEREE INSERTION R{number}\n'
            f'\\hypertarget{{review-{number}}}{{}}\\RefereeRemark{{{number}}}{{{kind}}}{{{title}}}{{%\n'
            f'{text}\n'
            f'}}\n'
            f'% END REFEREE INSERTION R{number}\n')


def main():
    raw = source.read_text()
    digest = hashlib.sha256(raw.encode()).hexdigest()
    if digest != SHA256:
        sys.exit(f'docalculus.tex changed (sha256 {digest}); line anchors must be rechecked')
    lines = raw.split('\n')
    for line, start, number, *_ in REMARKS:
        if not lines[line - 1].lstrip().startswith(start):
            sys.exit(f'R{number}: line {line} does not start with {start!r}: {lines[line - 1][:80]!r}')
    for line, start, number, kind, title, text in sorted(REMARKS, reverse=True):
        lines.insert(line, remark_block(number, kind, title, text).rstrip('\n'))
    text = '\n'.join(lines)
    for old, new in [(PREAMBLE_OLD, PREAMBLE_NEW), (COLOR_OLD, COLOR_NEW)]:
        if text.count(old) != 1:
            sys.exit(f'Preamble anchor not unique: {old!r}')
        text = text.replace(old, new, 1)
    marker = '\\maketitle\n'
    if text.count(marker) != 1:
        sys.exit('Cannot locate \\maketitle')
    text = text.replace(marker, marker + '\n' + OVERVIEW, 1)
    target.write_text(text)
    print('wrote', target.name, f'({len(REMARKS)} remarks)')

    build.mkdir(parents=True, exist_ok=True)
    (build / 'main.tex').write_text(text)
    env = dict(os.environ, TECTONIC_CACHE_DIR=str(CACHE))
    result = subprocess.run([TECTONIC, '--only-cached', '--keep-logs', 'main.tex'],
                            cwd=build, env=env, capture_output=True, text=True)
    (build / 'compile.out').write_text(result.stdout + result.stderr)
    if result.returncode != 0:
        sys.exit('Compilation failed; see .scratch/audit/compile.out')
    shutil.copyfile(build / 'main.pdf', pdf_target)
    log = (build / 'main.log').read_text(errors='replace')
    undefined = log.count('undefined')
    overfull = log.count('Overfull')
    print('wrote', pdf_target.name, f'(undefined: {undefined}, overfull boxes: {overfull})')


if __name__ == '__main__':
    main()
