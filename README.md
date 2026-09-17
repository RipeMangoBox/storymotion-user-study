# Paired Motion–Camera Study

Bilingual, anonymous A/B video questionnaire: 20 given-human camera trials, a transition page, then 20 joint human–camera trials. No ground-truth videos are included. English experimental prompts are preserved in both interface languages.

## Design

- Given-human: camera–text alignment, camera movement coherence/plausibility, and camera-view framing.
- Joint: the same camera criteria plus human–text alignment and human motion naturalness/physical plausibility.
- Five comparative choices (A much/slightly better, equal, B slightly/much better), plus cannot judge.
- StoryMotion versus one baseline per sample. Baselines are cyclically counterbalanced by sample and session; within each task A/B has ten StoryMotion-left and ten StoryMotion-right trials. Trial order is randomized within each task, never across task boundaries. Abandonment can unbalance completed-response counts, which should be inspected before analysis.
- Camera-only supplied human motion is not rated. Both synchronized replay and independent inspection are supported; the browser requires full playback before advancing.
- Responses are saved after each trial, with local draft recovery. Final submission is complete-only and idempotent. Test and incomplete sessions are excluded from the reporting CLI.

## Running

Install `requirements.txt`. `prepare.py` freezes the current selected gallery into a private `runtime/catalog.json`; videos remain in their original location. Run `python launch.py` for the server, or set `STUDY_SHARE=1` to start a **temporary Gradio share tunnel (one-week lifetime)**. Runtime files and response databases must not be published.

For GitHub Pages, publish `web/` and set `web/config.js` to the API origin. Pages hosts only the frontend; it does not store answers. A temporary tunnel supports pilot testing, not unattended long-term recruitment. Use a stable HTTPS backend for longer collection.

## Private statistics

`python report.py` exports completed real responses and per-task/per-baseline/per-criterion descriptive preferences to `runtime/exports/`. It does not expose an unauthenticated results API. Do not treat repeated judgments as independent observations for significance testing. The videos form a manually selected cohort, not a random sample of the full test set. Existing render processing is retained, including any method-specific visualization smoothing; this questionnaire does not establish an unprocessed-motion comparison.

The service stores no names, emails, or IP addresses in its database. Session credentials are stored hashed server-side. The hosting/network provider may separately maintain network logs. Public video stimuli should be treated as downloadable, not confidential. Formal recruitment remains subject to the research team's applicable ethics and consent requirements.
