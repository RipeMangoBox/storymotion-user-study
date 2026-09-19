# User-study scoring

Given-Human compares AESOP with CCD, DanceCamera3D-Text and DIRECTOR-C. Joint compares AESOP with PulpMotion DiT and MAR. Neither GenDoP nor ground-truth videos are included.

## Randomization

New participants are randomly assigned among the least occupied slots of a balanced 48-slot template. Each participant sees AESOP on the left ten times and on the right ten times in each task. Trial order is shuffled within each task. Opponent, presentation side and task order are counterbalanced across the template. Assignments are saved with the session, so refresh/resume does not change a comparison. Actual completed coverage is reported separately; incomplete participation need not preserve perfect balance.

## Judgments and preference scores

Each participant completes 20 given-Human and 20 joint comparisons. Given-Human has three criteria: camera–text alignment, camera motion quality, and framing quality. Joint adds human–text alignment and human motion quality, yielding 160 judgments per participant.

The five preference options are A much better, A slightly better, about equal, B slightly better and B much better; unable to judge is separate. Stored display-side answers are mapped back to method identity before scoring. For AESOP relative to each opponent:

| Outcome | Meaning | Primary preference credit |
|---|---|---:|
| W | AESOP preferred, slightly or much | 1 |
| T | About equal | 0.5 |
| L | Opponent preferred, slightly or much | 0 |
| NA | Unable to judge | Excluded from preference denominator |

**Primary preference = (W + 0.5 T) / (W + T + L).** Multiply by 100 to display a percentage. A value of 50% indicates equal aggregate preference; values above 50% favor AESOP. Slight and strong preferences have equal weight in this primary score, but their original counts are retained and reported.

For example, 60 wins, 20 ties, 20 losses and 10 NA responses give 70% primary preference, 75% conditional win rate excluding ties, and 9.091% NA. The secondary conditional win rate is W/(W+L). NA rate is NA/(W+T+L+NA). Empty denominators are missing values, not zero.

Results are reported separately for each task, opponent and criterion. Camera and human criteria are not averaged into an overall score. The design compares AESOP with each baseline; it does not directly rank baselines against each other.

## Eligibility and uncertainty

Only complete, consenting, reviewed-valid human responses enter the results. Automated tests, author/maintenance pilots, incomplete responses and documented duplicates or invalidating technical failures do not enter formal statistics. Repeated saving and submission do not create extra votes. Original responses remain stored; stimulus/protocol versions are analyzed separately. Do not exclude a response because it prefers a baseline, is fast, or contains many NA judgments alone.

Preference intervals use 2,000 crossed bootstrap draws over participants and source-video clusters, multiplying their sampled observation counts. Report the 2.5th and 97.5th percentiles as a 95% interval when both cluster dimensions contain multiple units. This interval addresses repeated observations, not the selection bias of the manually chosen 20 clips per task. No significance test or composite score is implemented.

Both videos must reach 90% client-reported playback coverage before a trial can be saved. This is a playback check, not proof of participant attention. Data remain private on the backend; GitHub Pages serves the questionnaire interface only.
