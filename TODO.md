# Remaining acceptance work

- [x] Inspect source; establish project configuration, model and camera/video input
- [x] Genuine ONNX COCO17 inference, Python renderer, Python + browser runs on real test photograph
- [x] Geometry, confidence policy, filters, normalized motion features
- [x] Squat full pipeline and partial-cycle suppression
- [x] Nine exercise rules and per-action prototypes for counting/scoring/feedback
- [x] Conservative nine-action auto recognition mode with explicit abstention
- [x] Chinese/English text/voice controls, set reports, performance metrics, debug values
- [x] Synthetic keypoint cycle coverage across nine exercises and both runtimes
- [x] Browser H.264 video plus browser virtual-camera inference smoke test
- [x] Windows built-in PowerShell local browser launcher (no Python install); pending device acceptance
- [x] Nine-class conservative auto mode checked with idealized trajectories on both runtimes
- [x] Transient webcam read retry, visible primary-angle overlay, and browser camera stop/restart cleanup
- [x] Camera selection, per-set goals, explicit new workout, multi-exercise session summaries, CSV/JSON export, scored plank set endings
- [x] Offline browser runtime/model and GitHub Pages workflow
- [x] Report, methodology, limitation and validation documents
- [ ] Test Mac M2 and Windows real RGB cameras at 640×480, 480×360 and 320×240, record camera/pose/UI FPS, latency, CPU/memory
- [ ] Verify macOS Tk window, Windows PowerShell launcher and voice output, Chrome/Edge access to a physical camera; assess optional WebGPU acceleration later
- [ ] Record consenting volunteers and manually annotate complete/partial reps, errors and state-transition times
- [ ] Tune per-user/per-view thresholds, measure nine-class auto recognition including abstention, score agreement and false alarms
- [ ] Publish Pages after a destination GitHub repository becomes available

Do not turn synthetic sequence or virtual-camera smoke results into real exercise accuracy statistics. First physical milestone: verify shoulder/elbow/wrist/hip/knee/ankle overlay from local camera; then measure ten deliberate squats against manual annotations.
