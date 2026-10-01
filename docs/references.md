# References and evidence scope

访问核对：2026-09-28。以下资料支持模型接口、部署路径和动作评价边界，不为本项目的具体阈值或准确率背书。

1. Ultralytics YOLOv8 model documentation. https://docs.ultralytics.com/models/yolov8/ — YOLOv8 pose family, supported tasks and exports.
2. Ultralytics Pose estimation. https://docs.ultralytics.com/tasks/pose/ — COCO-style keypoint task and usage. Current documentation also covers newer generations; this project intentionally fixes YOLOv8 raw output.
3. Ultralytics ONNX export. https://docs.ultralytics.com/integrations/onnx/ — ONNX export integration. Do not confuse export success with task validation.
4. Microsoft ONNX Runtime Web. https://onnxruntime.ai/docs/tutorials/web/ — browser-local inference providers.
5. Microsoft Using WebGPU. https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html — WebGPU import/runtime route and WASM alternative.
6. Microsoft env flags and session options. https://onnxruntime.ai/docs/tutorials/web/env-flags-and-session-options.html — WASM assets, threading, execution providers.
7. NSCA. Anthropometrical Considerations for Customizing the Squat Pattern. https://dxpprod.nsca.com/education/articles/ptq/anthropometrical-considerations-for-customizing-the-squat-pattern/ — individual anatomy influences stance/setup/depth; supports avoiding a universal depth rule.
8. NSCA. Considerations for Squat Depth. https://www.nsca.com/education/articles/nsca-coach/considerations-for-squat-depth/ — discussion of squat-depth considerations, not a validation of our 100° threshold.
9. NASM exercise library: Plank. https://www.nasm.org/resource-center/exercise-library/plank — head-to-heel alignment and avoiding hip drop support using body-line features.

Research extension: conduct a systematic literature review on monocular exercise assessment, phase recognition, and expert score reliability before claiming scientific novelty or validated biomechanics. This delivery contains an engineering baseline, not a completed systematic review.
