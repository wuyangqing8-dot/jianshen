# Project status — 2026-09-28

## Completed in code

- Real YOLOv8n-pose ONNX model included; no MediaPipe. COCO17 keypoints, NMS, confidence filtering, letterbox inverse mapping.
- Python OpenCV camera/video and Tk dashboard with separate camera/inference/UI threads, explicit camera stop, local voice worker, goal display, camera scan, JSON/CSV session export.
- Browser camera/video, local ONNX Runtime Web using WASM, skeleton and nine-action controls; local model/runtime and no remote inference API. Camera permission is requested before model loading; stop/restart releases camera tracks, failed inference closes the input, and the same video can be reselected.
- Geometry, five-sample moving average or EMA, per-action FSM with configurable hysteresis and duration, rejection of incomplete reps, scores, error priorities, batch/per-rep voice feedback.
- Nine exercise rule implementations, front-leg fallback for lunges, signed hip offset for valid side-view plank/pushup, plank quality duration, bridge top hold and jumping jack reps/min.
- Conservative temporal auto mode on desktop and web: a single unambiguous candidate is needed; otherwise abstain. The first full motion used for identification can be replayed and counted. Idealized trajectories for all nine actions now select their intended labels in both runtimes.
- One-click local Windows browser launcher uses built-in PowerShell and needs no Python; physical Windows verification remains open.
- Browser camera selector, per-set count/hold goal, explicit new-workout control, in-memory multi-exercise history, JSON and Excel-friendly CSV summaries. Plank end-set stores scored hold duration and quality duration; desktop includes matching goal/export controls.
- Labeled-data evaluation programs for reps, phases, errors, action classification, and expert-score comparison; optional Random Forest trainer and predictor interface only after real labels exist.
- 38 previously run Python tests, 27 JavaScript tests, authentic image inference in Python and Chromium WASM, H.264 browser-video integration, headless Chromium virtual webcam camera switching and workout/export smoke tests. Browser integration confirmed two manual squat counts and first-cycle automatic recognition/count with idealized keypoints at about 8 pose FPS.
- Static site is published privately at https://form-fitness-coach-2026.ruanwuzhi123.chatgpt.site; optional GitHub Pages workflow, references and report documents are included but no GitHub connection is used.

## Requires the user's equipment or research data

- Camera, audio, CPU/memory/GPU, and sustained FPS acceptance on actual Apple M2 and Windows devices.
- Native Tk visual/interaction acceptance on those devices; tested here with static Python checks because no desktop display server exists.
- Optional WebGPU acceleration after the stable WASM path is verified on physical M2/Windows devices.
- Volunteer exercise clips and expert ground truth to compute real nine-exercise recognition, counting, phase and error detection accuracy and score correlations.
- Real physical-camera acceptance on the user's laptop remains unverified; the hosted Site is already available without GitHub.

## Known limitations

- Auto recognition is heuristic with abstention; similar poses can remain unidentified. Manually selecting an exercise gives more predictable counting.
- The lunge front-leg fallback uses the more bent knee when the face or foot separation is unclear; it may select the wrong leg.
- Single RGB camera gives 2D projections only. Hip sag/pike label is an image-plane hint when projected line geometry is valid, not a 3D or medical finding.
- The web UI now shows the tracked angle, four-step detection state and current thresholds, with three preset sensitivities plus per-session personal calibration and diagnostic JSON export. Scoring thresholds remain provisional. The 2019/2026 historical user-provided count rates are not results of this model.
- CPU Python backend does not use CoreML; JS preprocessing remains on the browser main thread and can lower video/UI responsiveness on slow devices.
- No claims of ≥90% keypoint accuracy, r>0.85 expert correlation, injury risk prediction, or 30 FPS on M2.
