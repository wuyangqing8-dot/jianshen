# Executed validation

2026-09-28, Linux server; Python 3.12, ONNX Runtime CPU; headless Chromium with WebAssembly. This environment has neither an Apple M2 nor a real attached RGB webcam nor a desktop display server.

| Check | Observed | Scope |
|---|---|---|
| Python test suite | 38 passed | Geometry, NMS/inverse mapping, confidence loss, webcam transient failure, phase timeouts, incomplete reps, nine idealized auto labels, goal and multi-exercise export, plank end-set |
| JavaScript test suite | 27 passed | Shared rule behavior; idealized 17-point full cycles for eight repeated actions and continuous plank; nine idealized auto labels, 4/8 pose FPS cycles, single missing pose, moderate ankle confidence, multi-person modest squat, missing-joint diagnosis, personal-range calibration, first-cycle auto replay/count, goal/CSV, scored plank end-set |
| Genuine ONNX on upstream public photograph | 3 detected people, 17 keypoints selected; primary person entered STAND with a 176° knee angle | Browser WASM model and updated engine, using a static photograph; no real exercise cycle | Network-free Python pose runtime after setup |
| Python smoke video, 40 processed frames | 40 detected; mean inference 20.44 ms; ~29.97 processed FPS | Video/pose integration on this host; repeated static frames, no exercise accuracy |
| Chromium WASM | 3 people, 17 keypoints, no JS errors | Browser model/session/postprocessing actually run |
| Chromium H.264 input, pause, plank switch, reset, reselect same video, stop | All exercised without page errors | Browser video flow and UI controls |
| Chromium virtual webcam | Local ONNX inference and webcam/UI counters updated; stop freed tracks, restart passed; one run 8.2 camera FPS, 7.8 pose FPS | **Synthetic webcam on constrained headless server**, not Apple M2 or real camera performance |
| Browser goal/camera/export workflow | Goal editing, virtual camera selection, synthetic plank hold end-set, prior exercise retention, CSV/JSON download, new workout all passed with no page errors | UI integration test; plank pose was an **injected idealized fixture**, not human accuracy data |
| Hosted asset regression, local served copy | The published asset set initialized WASM, inferred a canvas frame, acquired a virtual camera, reported camera/pose FPS, released tracks and restarted; denied permission displayed a specific error before requesting the model | Tested the exact static file layout locally, using a synthetic camera; physical webcam authorization remains device/browser dependent |
| Browser guided calibration, local served copy | Captured a 151° start and 136° squat endpoint, then repeated the range and counted one; displayed all four detection checks and exported a non-video diagnostic JSON; no page errors | Virtual webcam plus injected idealized 17-point pose, not an actual user camera |
| Browser counting flow, local served copy | Default manual squat counted two cycles; live knee-angle guidance displayed; changing sensitivity retained the count; opt-in automatic mode identified squat and counted its first full cycle at about 8 pose FPS; no page errors | Synthetic keypoints supplied to the browser at inference time with a virtual camera. Verifies UI and state flow, not accuracy on real exercise footage |
| Repeat-image CPU benchmark, 50 measurements per size | 640×480:21.77 ms; 480×360:18.07 ms; 320×240:18.33 ms | Fixed 320×320 model; details in benchmark.json |

The benchmark process could not access process CPU and memory metrics in this environment; nulls are recorded. Its camera/UI FPS are null because no camera/UI participated. The separate virtual-webcam smoke results are not comparable with a physical camera or interactive browser.

## Not established

- Real human fitness action classification accuracy, count/event precision and recall, true movement quality, or expert score correlation.
- Apple M2, Windows physical camera permissions, sustained 30 FPS, native Tk dashboard window, audible local voice or real WebGPU GPU acceleration. The current browser build intentionally uses WASM.
- One-click Windows PowerShell launcher behavior on a real Windows installation; source reviewed and packaged, but this Linux host has no PowerShell executable.
- Actual physical-camera exercise count and phase recognition on the user's device; the Site is hosted without GitHub.

Use README commands to reproduce. `tests/assets/motion_sequences.json` is synthetic 2D pose data created for deterministic software behavior tests, not participant data. Bus-image video clips are smoke assets only.
