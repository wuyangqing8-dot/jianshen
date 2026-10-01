# Architecture

Desktop: Camera worker → latest-frame slot → ONNX worker → PoseResult → TemporalFilter → feature extractor → selected-exercise engine or conservative temporal recognizer → FSM / continuous hold → scoring → training session. Tk main thread draws the latest camera frame, and only overlays a pose less than 0.5 s old. Voice is queued on a separate daemon worker. UI changes are handed to inference via a command queue.

Browser: getUserMedia or local File URL → video → letterbox canvas → ONNX Runtime Web WASM → same COCO17 contract → JS exercise engine → overlay + dashboard. No video backend, telemetry, remote API, or external CDN. Static HTTP is needed for JS/WASM/model assets. Camera permission precedes model initialization so the browser can display a clear permission error. JS preprocessing still runs on the main thread; a Worker migration is a future optimization.

Public backend contract: load_model, preprocess, infer, postprocess, get_keypoints. PoseResult contains original-frame xyxy bbox, 17 × (x,y,confidence), person confidence, post-NMS person count. Business logic is independent of ONNX tensor layout.

Single-user behavior: estimator returns highest-confidence person after NMS. If multiple people are present, drawing is allowed but scoring pauses to avoid mixed identities. A large bbox-center displacement resets partial cycles; this is not a robust tracking algorithm.

No default persistence of camera/video/keypoints. Exercise summaries stay in memory while the app is open, including after switching actions. Explicit JSON export saves derived rep/session data; explicit CSV export saves a per-set summary without keypoints. A new-workout action deliberately clears in-memory history. Explicit pose-camera --output saves annotated video. The web app only issues static-resource GETs.

Auto mode: a separate buffered action recognizer consumes keypoints; it only instantiates the chosen exercise engine after exactly one stable candidate appears. Unknown stays unscored. A single detection motion may be consumed by recognition; the user returns to the initial state for the first counted repetition. Manual selection remains the reliable path when motion categories overlap in 2D.
