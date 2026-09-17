# Paired comparison protocol v2 (pilot)

## Cohort and judgments

The fixed manually selected cohort contains 20 given-human and 20 joint sources.
Given compares StoryMotion against CCD, CCD-H, DanceCamera3D, DIRECTOR,
GenDoP and GenDoP-H. Joint compares it against PulpMotion DiT and MAR.
Each participant sees one opponent per source: 40 comparisons and 160 judgments.
No ground truth is shown. Conclusions apply to these selected stimuli, not a
randomly sampled full test population or intensity-control evaluation.

The current Python-rendered stimuli remain a pilot. Blender replacements and
two neutral, unscored video exercises are pending. Textual orientation concepts
are supplied now, but are not a substitute for testing those practice videos.
Existing joint StoryMotion previews declare display smoothing. The new renderer
must establish consistent processing, readable human views and a common spatial
view per source before the new stimulus version is frozen. Do not overwrite
videos used by an existing session.

## Assignment

The 48-slot template crosses task order, source, opponent and presentation side.
Each participant sees StoryMotion on the left and right ten times per task.
Across 48 complete slots, task order is split 24/24. Each given
source/opponent/side/order cell has two observations, each joint cell six.
This is an assignment template, not a fixed recruitment or power requirement.

New sessions select randomly among least occupied slots. Completed responses
awaiting review reserve their slots, as do active sessions for 24 hours.
Excluded responses release capacity. Expired sessions can still complete;
legitimate responses are not deleted to force equal counts. Inspect actual
reviewed completion coverage and replenish deficits. Test sessions use separate
allocation counts and never enter human statistics.

## Eligibility and exclusion

Every submission initially awaits eligibility review. Include consenting,
complete, unique human responses. Exclude documented automated tests, author or
maintenance pilots, known duplicate submissions and documented protocol or
technical failures that invalidate comparison. Do not exclude based on which
method wins, a high NA rate alone, speed alone, or an isolated inconsistent
preference. Do not infer human identity from IP addresses. Record reasons with
the private review CLI; retain original responses. Changes to these rules after
formal collection begins require a new protocol, not retrospective optimization.

Watch coverage is client-reported accumulated played ranges, required to reach
90% on each side. It is a playback check, not proof of attention. Missing props,
scene geometry and clothing are not rated. Human quality uses the Spatial view;
framing uses the Camera view. Camera movement quality combines coherence and
visible spatial plausibility; its score does not identify independent effects.

## Scoring

Retain all five preference levels and separate unable-to-judge responses.
Report W/T/L with denominator W+T+L and NA with denominator W+T+L+NA.
Primary descriptive preference is (W+0.5T)/(W+T+L). W/(W+L) is secondary and
explicitly excludes ties. Empty denominators yield null, not zero.

Report each task/opponent/criterion separately. The 95% preference interval
uses 2,000 crossed bootstrap draws: independently resample participant and
source-video clusters and multiply their observation multiplicities. This does
not remove selection bias, supply independent training seeds, or establish a
ranking among baselines that were not directly compared. No significance tests
or cross-dimension composite score are planned.

## Versioning and operations

Protocol and stimulus versions are stored per session. Version-1 participants
retain their original text, order and media. Catalog snapshots are immutable;
new render assets require a new stimulus version and new media identifiers.
Start requests and final submission are idempotent; repeated saves update one
trial rather than creating additional votes. The browser preserves its resume
credential and draft across refreshes. Do not clear browser storage to resume.

The public test entry is `?test=1`; a private test credential must be supplied
through its password field. Test credentials are not included in public source,
URLs or exports. Test local storage is separate from ordinary sessions.

The frontend is GitHub Pages; the current backend is a temporary share tunnel.
Formal recruitment needs a stable HTTPS backend and persistent hosting, plus
a small human pilot of completion time, dropout, NA and stimulus readability.
Neither the current automated checks nor 48-slot balance replace that pilot.

## Private export

Run `python report.py`. JSON exports contain raw anonymous observations,
reviewed coverage (including zero cells), session progress and summary measures.
RESULTS.md contains three-decimal presentation tables. No identity, IP,
contact information or credentials are exported. Results are split by protocol
and stimulus version; no pooled total is substituted for per-opponent results.

Run `python review_session.py --session ID --status valid|excluded|pending_review
--reason TEXT` after eligibility review. Test and incomplete sessions cannot be
marked valid. No automatic preference-based exclusions are performed.
