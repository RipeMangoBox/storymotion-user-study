# Paired Motion–Camera Study

Bilingual, blinded A/B questionnaire with 20 given-human camera and 20 joint human–camera comparisons. Each source pairs StoryMotion with one baseline; no ground truth is shown. See [PROTOCOL.md](PROTOCOL.md) for frozen questions, allocation and analysis rules.

## Pilot v2

- Task order is counterbalanced independently of opponent allocation through a 48-slot template, with ten StoryMotion-left and ten StoryMotion-right trials per task.
- Five preference levels plus a separate unable-to-judge option; camera text alignment, movement quality and framing in both tasks, plus human text alignment and quality in joint.
- Shared buffering, synchronized replay/pause, drift correction, 90% played-coverage gates, draft recovery, idempotent start and final submission.
- Test sessions use a separate allocation pool and browser storage. Open `?test=1` and supply a private test credential; none is published.
- Existing version-1 sessions retain their original questionnaire and stimulus snapshot. New video renders require new stimulus identifiers.
- Current rendered outputs are a manually selected pilot cohort. Blender replacements and neutral practice videos are pending; do not describe these results as a random full-test evaluation.

## Deployment

Install `requirements.txt`; keep `runtime/` private. `prepare.py` freezes gallery inputs. `python launch.py` serves the API; `STUDY_SHARE=1` enables a temporary share tunnel. GitHub Pages hosts `web/`; `web/config.js` selects the API.

A temporary tunnel is not permanent study hosting. Provision a stable HTTPS backend before extended recruitment. Preserve the response database, archived catalogs, media and resume credentials across updates.

## Private analysis

Submissions remain pending eligibility review. Use `review_session.py` to mark documented eligible human responses; retain all original answers. Do not exclude based on preferences or to force balanced cells.

`python report.py` writes anonymous observations, coverage including missing cells, progress, and per-task/opponent/criterion statistics to private `runtime/exports/`. It reports W/T/L, NA, tie-inclusive preference and crossed participant/source-video bootstrap intervals. Protocol and stimulus versions remain separate.

The database contains no names, emails or IP addresses. Hosting providers may maintain their own network logs. Formal recruitment requires the research team's applicable consent and ethics process. Public stimuli are downloadable, not confidential.

## Checks

`python test_v2.py` uses an isolated synthetic database to verify allocation, idempotency, gates and scoring. `node test_browser_v2.cjs` exercises both task orders and actual video playback with explicitly marked test sessions.
