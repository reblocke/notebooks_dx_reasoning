# Atlas mathematics and validation appendix

## Purpose and scope

The four finalized synthetic reference vignettes show convergence, reopening, substitution, and persistent ambiguity. These are descriptive patterns in deliberately constructed probability paths, not validated case classifications or estimates of learners' beliefs. The different initial priors are intentional: this is not a controlled comparison of methods.

Every vignette uses the same fixed, mutually exclusive, exhaustive categories **A, B, C**, four binary findings, and five recorded probability states. All state probabilities, event likelihoods, and complementary-event likelihoods are strictly positive. No endpoint needs certainty.

The complete numerical reference fixtures are stored in [manim_fixtures.json](../data/manim_fixtures.json), under key `goal_04`. The fixed likelihood vectors, reference posteriors, entropy values, complementary branches, and geometry define the synthetic models used by this specification. These are finalized mathematical reference fixtures, not empirical estimates or an implementation.

## 1. Exact target paths

Each vector is ordered `(A, B, C)`. Step 0 is the initial prior; step t is the posterior after observing the first t events. Entropies use base 2 and are shown to six decimals.

| Vignette | Step 0 | Step 1 | Step 2 | Step 3 | Step 4 |
|---|---|---|---|---|---|
| **Convergence** | `(1/3, 1/3, 1/3)` | `(.55, .28, .17)` | `(.72, .18, .10)` | `(.86, .09, .05)` | `(.94, .04, .02)` |
| H, bits | 1.584963 | 1.423180 | 1.118731 | 0.715879 | 0.382543 |
| **Reopening** | `(.90, .05, .05)` | `(.78, .12, .10)` | `(.65, .20, .15)` | `(.50, .25, .25)` | `(.38, .34, .28)` |
| H, bits | 0.568996 | 0.978854 | 1.278898 | 1.500000 | 1.573847 |
| **Substitution** | `(.80, .10, .10)` | `(.65, .25, .10)` | `(.40, .50, .10)` | `(.20, .70, .10)` | `(.10, .80, .10)` |
| H, bits | 0.921928 | 1.236160 | 1.360964 | 1.156780 | 0.921928 |
| **Persistent ambiguity** | `(.40, .35, .25)` | `(.35, .30, .35)` | `(.28, .40, .32)` | `(.36, .29, .35)` | `(.33, .36, .31)` |
| H, bits | 1.558872 | 1.581291 | 1.569026 | 1.578620 | 1.582232 |

The intended distinctions are exact at the recorded states:

- **Convergence:** entropy falls after every finding; A's probability increases from one third to .94.
- **Reopening:** entropy rises after every finding, while the initially dominant A becomes less dominant. This is a valid sequence of Bayes updates, not an error or failure of inference.
- **Substitution:** support moves from A to B through two moderately ambiguous states. Initial and final entropy are exactly equal because the endpoint permutes the initial probabilities. The endpoint-to-initial KL divergence is nevertheless 2.1 bits.
- **Persistent ambiguity:** entropy stays above 1.55 bits and no diagnosis exceeds .40 at the recorded states. Small movements in the leading label do not imply a confident commitment. This high-entropy range is a fixture property, not a proposed clinical cutoff.

Net signed entropy reductions `H(step 0) - H(step 4)` are respectively `+1.202419832`, `-1.004851397`, `0`, and `-0.023360425` bits.

## 2. Construct once; update with fixed likelihoods thereafter

For design only, let p be the preceding target state and q the next target state. Set

\[
r_j=\frac{q_j}{p_j},\qquad
c=\frac{4/5}{\max_j r_j},\qquad
L_j=P(E=1\mid D=j)=c\,r_j.
\]

Then `0 < L_j <= .8 < 1`, and

\[
P(E=1\mid\text{observed prefix})=\sum_j p_jL_j=c,
\qquad
P(D=j\mid E=1,\text{prefix})=\frac{p_jL_j}{c}=q_j.
\]

Define the other binary outcome by `P(E=0 | D=j)=1-L_j`. It also has strictly positive support. This produces an ordinary, complete binary observation model for every step.

**Important runtime contract:** perform this construction once, store the L vectors, and freeze them. A renderer/calculator should use the initial prior and the stored likelihoods to recompute each posterior, then compare against the stored reference target. It must not reconstruct or refit the likelihoods from the current animated beliefs during playback. The targets are deliberately designed fixtures, not inferred or empirically estimated probabilities.

### Fixed event likelihoods, exact fractions

Each entry is `(P(E_t=1|A), P(E_t=1|B), P(E_t=1|C))`. Entries across a row need not sum to one: they condition on different diagnoses.

| Vignette | Event 1 | Event 2 | Event 3 | Event 4 |
|---|---|---|---|---|
| Convergence | `(4/5,112/275,68/275)` | `(4/5,11/28,55/153)` | `(4/5,72/215,72/215)` | `(4/5,688/2115,344/1175)` |
| Reopening | `(13/45,4/5,2/3)` | `(2/5,4/5,18/25)` | `(24/65,3/5,4/5)` | `(38/85,4/5,56/85)` |
| Substitution | `(13/50,4/5,8/25)` | `(16/65,4/5,2/5)` | `(2/7,4/5,4/7)` | `(7/20,4/5,7/10)` |
| Persistent ambiguity | `(1/2,24/49,4/5)` | `(12/25,4/5,96/175)` | `(4/5,203/450,49/72)` | `(319/540,4/5,899/1575)` |

The displayed path observes outcome 1 for all four events. The conditional probabilities of these observed branches are:

| Vignette | Event 1 | Event 2 | Event 3 | Event 4 | Probability of the entire displayed branch |
|---|---:|---:|---:|---:|---:|
| Convergence | .484848485 | .611111111 | .669767442 | .731914894 | .145248227 |
| Reopening | .333333333 | .480000000 | .480000000 | .588235294 | .045176471 |
| Substitution | .320000000 | .400000000 | .571428571 | .700000000 | .051200000 |
| Persistent ambiguity | .571428571 | .600000000 | .622222222 | .644444444 | .137481481 |

These are `P(E_t=1 | E_1=...=E_(t-1)=1)`, not unconditional event probabilities. Their product is the probability of the displayed branch. This branch was selected by construction; its probability should not be presented as an empirical frequency. The choice of the factor .8 sets a permissible likelihood scale. Other admissible common scales would preserve the posteriors while changing branch probabilities.

### One coherent joint model per vignette

Treat the four fixed binary findings as conditionally independent given D:

\[
P(D=j,e_1,e_2,e_3,e_4)
=p_{0j}\prod_{t=1}^{4}L_{tj}^{e_t}(1-L_{tj})^{1-e_t}.
\]

This defines all 16 outcome sequences and sums to one. The displayed posteriors follow

\[
p_{tj}=\frac{p_{0j}\prod_{u=1}^{t}L_{uj}}
{\sum_k p_{0k}\prod_{u=1}^{t}L_{uk}}.
\]

Do not multiply fixed OVR LRs. If OVR values are shown for explanation, recompute them from the fixed likelihoods and the current prior-weighted complement mixture. Under this declared product model, changing finding order can change intermediate states and their entropy, but not the final posterior after the same four findings.

## 3. Barycentric geometry and entropy heatmap

Use a unit equilateral triangle with

\[
v_A=(0,\sqrt3/2),\quad v_B=(-1/2,0),\quad v_C=(1/2,0).
\]

Map a probability vector to the point

\[
v(p)=p_Av_A+p_Bv_B+p_Cv_C
=\left(\frac{p_C-p_B}{2},\frac{\sqrt3}{2}p_A\right).
\]

The inverse is

\[
p_A=2y/\sqrt3,\quad
p_B=(1-p_A)/2-x,\quad
p_C=(1-p_A)/2+x.
\]

Translate and uniformly scale this triangle for layout as needed; retain the same labels and orientation in every panel. A dot's Cartesian position is a mixture of fixed category vertices, not a probability pair plotted on unrelated axes. Euclidean path length is not information gain or KL divergence.

The heatmap quantity is

\[
H(p)=-\sum_j p_j\log_2p_j,\qquad
0\leq H(p)\leq\log_2 3=1.5849625007\text{ bits}.
\]

Use `0 log2 0 = 0` at the boundary. Heatmap vertices are zero entropy, and the centroid is the maximum. The heatmap may include zero-probability boundary points even though every trajectory state has strictly positive support. Use one fixed color scale from 0 to log2 3 across all panels and encounter windows; do not autoscale separately. Entropy contours show uncertainty, not diagnostic truth, correctness, utility, or quality of reasoning.

## 4. Within-step motion: a coherent illustrative bridge

The five recorded markers represent belief states: state 0 is the initial prior, and states 1–4 follow the four observed findings. Intermediate motion adds no observation. For smooth motion between p_(t-1) and p_t, use

\[
\widetilde p_{tj}(\alpha)=
\frac{p_{t-1,j}L_{tj}^{\alpha}}
{\sum_k p_{t-1,k}L_{tk}^{\alpha}},\qquad 0\leq\alpha\leq1.
\]

Equivalently, this is normalized geometric interpolation:

\[
\widetilde p_t(\alpha)
\propto p_{t-1}^{1-\alpha}p_t^{\alpha}.
\]

The common likelihood scale cancels, endpoints are exact, all intermediate distributions are positive and normalized, and pairwise log probability ratios change linearly in alpha. The Cartesian path need not be a straight segment.

Label this **“0: prior. 1–4: after findings. Motion illustrates transitions.”** Fractional powers are a visual convention for scaling the evidence, not a measured sequence of partial clinical observations. If easing is used, the eased alpha must drive both the probability point and any simultaneous entropy display.

For this film, display the entropy trace only at the five recorded belief-state markers, with the horizontal axis labeled “Observed finding index”; connecting marks are a guide to the eye. State 0 shows prior entropy, and states 1–4 show entropy after the corresponding findings. A separate live entropy badge may display `H(tilde p_t(alpha))` during the explicitly illustrative motion. Do not add interpolated points to the recorded entropy trace.

Do not linearly interpolate H independently of the probability state while implying they describe the same distribution. Do not infer within-step monotonic entropy from the endpoints alone.

## 5. Encounter-window cropping

A window `[a,b]` displays the existing states `p_a,...,p_b`, and the updates `E_(a+1),...,E_b`. It changes the visible observation span only. Preserve the triangle, category inventory, coordinate scale, entropy color limits, and all original probabilities. Do not drop a category or renormalize over the visible path. Do not restart the cropped sequence from p_0: p_a already includes the hidden earlier evidence.

Substitution is the clearest demonstration:

- States 0–2 show entropy rising from .921928 to 1.360964 bits: the visible segment looks like reopening.
- States 2–4 show entropy falling by the same .439036 bits: the segment looks like convergence toward B.
- States 0–4 show substitution from A to B with zero net entropy reduction.

Label the window using original state/finding indices and explicitly state any hidden prefix incorporated into the starting posterior. For the states 2–4 window, label state 2 **Starting beliefs already include E1 and E2**; E3 and E4 are the visible findings. A path pattern can depend on the observation window. No window is required to end at certainty, and no crop establishes a clinically correct final diagnosis.

## 6. Validation specification

The following are bounded correctness checks for the fixture and eventual animation, not a new analysis pipeline.

### Fixture and Bayes arithmetic

- Four vignettes, exactly five reference states and four fixed likelihood rows each; all arrays use A/B/C order.
- Every state sums to one and is strictly positive. Every L is positive and at most .8; every complement equals `1-L` and is positive.
- Starting from p_0, ordinary Bayes with the frozen L rows reproduces every target state. Exact rational arithmetic establishes the identities; floating-point validation can use the shared absolute tolerance `1e-10` for probabilities and H values in these moderate fixtures.
- The sequential endpoint equals normalization of `p_0 * product(L_rows)`; the evidence probability equals the product of the recorded conditional branch probabilities. A reverse-order endpoint check provides an additional consistency check for this product model; it is not sufficient by itself to validate a general OVR implementation.
- For each binary finding, the complementary posterior is computed from `p*(1-L)` and the two branch probabilities sum to one. Expected posterior entropy, averaged across the two branches, does not exceed current entropy within numerical tolerance. A realized reopening step is still permitted to increase entropy.
- Sum of signed realized entropy reductions telescopes to `H(p_0)-H(p_4)`. Do not replace signed changes with absolute values or their positive parts under the same label.

### Intended narrative constraints

- Convergence H strictly decreases at each of the four recorded updates.
- Reopening H strictly increases at each recorded update.
- Substitution starts with A=.8, ends with B=.8, has equal initial/final H, and includes the prescribed intermediate states. Do not claim H was constant throughout.
- Persistent ambiguity has H above 1.55 bits and maximum class probability at most .40 at all recorded states.

### Geometry, bridge, and display

- Each category vertex and the uniform centroid map correctly; the inverse map recovers the original probability vector.
- Heatmap H agrees with the same entropy function used by markers. Endpoints, interior points, and boundary convention are checked; the color range is identical across panels.
- At alpha=0 and 1 the bridge reproduces the exact adjacent reference states. At representative interior alpha values, probabilities are positive, normalized, and lie inside the simplex; the entropy display is computed from that same state.
- Persistent category labels and colors do not reorder when the leading diagnosis changes. A change in leading label must not silently relabel the vertices.
- Window cropping preserves the stored state vectors and axes; its first state retains the hidden evidence prefix. Cropped labels identify the included updates correctly.
- Numerical fixtures are deterministic. No random noise, adaptive LR fitting, or numerical OVR projection is needed for this atlas.

## Principal interpretation limits

The target paths are designed illustrations, not case data; case-specific priors are intentional. Coherent updating does not certify the likelihoods as clinically accurate. The independence assumption defines a valid synthetic model here and is not a claim about real findings. The chosen branches demonstrate possible realized paths; expected information gain concerns all outcomes of the complete tests. The geometry and interpolation must not be read as elapsed time, clinical distance, or evidence of diagnostic correctness.
