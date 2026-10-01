# Pose estimation

Chosen baseline: YOLOv8n-pose, 3.29 million parameters, exported as float32 ONNX opset 17 at 320 × 320. Choice prioritizes a small established model and one backend shared by Python/web. A comparative RTMPose/MoveNet benchmark has not been performed; this is a baseline selection, not a proven optimum.

Image is resized with preserved aspect ratio, padded with RGB 114, converted BGR→RGB in Python, divided by 255 and packed NCHW. Rounded resize dimensions have separate x/y scales. Decode raw [1,56,N] outputs, filter person confidence ≥0.4, run box IoU NMS at 0.45, undo padding and scale. Points outside original frame receive zero confidence; unavailable points do not become valid zero coordinates. Engine threshold: 0.45.

COCO17 ordering matches the specification. Only indices 5–16 are drawn in normal mode. Ear points can support an optional side-view head-line feature; nose helps resolve projected front-leg direction when confidence and foot separation suffice. Eyes are never scored. Facial landmarks are not a face recognition system.

Python currently uses ONNX Runtime CPUExecutionProvider with 2 inference threads. CoreML acceleration is not implemented or benchmarked. Browser uses WASM for predictable runtime loading across devices. Runtime and model are bundled, so no first-use remote model download is required.

Schema mismatches fail explicitly. When changing architectures implement a new adapter; the current adapter cannot decode RTMPose heatmaps or newer end-to-end NMS output formats.
