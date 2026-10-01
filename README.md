# FORM — 基于实时姿态评估的多动作智能健身指导系统

可运行研究原型。已附真实 YOLOv8n-pose ONNX 模型及浏览器本地运行库，**没有使用 MediaPipe**。
真实模型 → COCO17 → 摄像头/视频 → 九动作几何规则表均已接通，并有保守自动识别模式。规则表是可检查的初始判定依据，**不是经真人标注训练的标准姿势数据库**。没有真人动作数据时不能声称九动作分类和评分已达到准确率指标。

## 最快启动：浏览器版

`localhost` 只指向**你正在使用的那台电脑**，不能从聊天窗口直接访问这里的开发环境。已发布测试页面：<https://form-fitness-coach-2026.ruanwuzhi123.chatgpt.site>。如需不依赖线上页面的本地版本，下载并解压项目，再在自己的电脑上运行下面的启动命令。

**Windows 10/11：**解压后双击 `start_web.bat`，系统会调用自带的 Windows PowerShell 在本机启动网页并打开浏览器。保持弹出的命令行窗口开启；关闭窗口即停止服务。浏览器请使用 Chrome 或 Edge。不需要为网页安装 Python、Node 或模型依赖。

**macOS / 已有 Python 的电脑：**在解压后的 `fitness_pose_system` 目录打开终端：

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Windows 也可用 `py -m http.server 8000 --bind 127.0.0.1`。
打开 **http://localhost:8000/web/**，点击“开启摄像头”。推荐使用最新版 Chrome / Edge；浏览器在本机用 WASM 运行姿态模型。不要双击 HTML 以 file:// 打开。
Mac 可运行 `bash start_web.command`。Windows 启动器只监听本机回环地址；若 8000 端口占用会尝试 8001–8010，并显示实际网址。
完整压缩包已经包含模型和 vendor 文件，正常使用无需 npm、PyTorch 或在线模型 API。首次运行库编译可能需要数秒。

1. 首次点击“开启摄像头”并授权；若电脑有多个摄像头，在顶部下拉框选择所需设备，或点“刷新设备”。切换摄像头会保留当前训练记录。
2. 页面默认选择“Squat / 深蹲”：按侧面或 45°摆放摄像头，让肩、髋、膝、脚踝尽量进入画面；做其他动作要先在右侧选择，页面展开“查看当前动作的判定依据”可看到起点、另一端、关键关节和完整计数条件。也可主动切换“自动识别 / Auto（实验）”。设置“本组目标”，动态动作按次数、平板支撑按秒数显示进度。
3. 先站直，观察右侧“实时检测”的膝角，再下蹲、起身。默认“宽松”深蹲计数约需先伸膝至 145°、下蹲至 125°、再伸膝至 145°；可以切换“更灵敏”（可能多计）或“标准”，切换时已完成次数保留。若摄像头测得的角度无法达到默认阈值，保持起始姿势约 1 秒后点“记录起始姿势”，再保持另一端约 1 秒点“记录动作另一端”；这会根据当前机位和你的动作幅度建立本次训练的计数阈值，无法看到关键节点或两姿势太接近时会提示具体原因。校准只保存当前网页会话，改变机位后应重新记录。页面还显示“摄像头／人体／关键关节／起始姿势”四步状态、阶段提示和当前关节角度；识别不到人体与看不清关节有不同提示。画面里有其他人时继续跟踪主目标，但建议尽量保持单人画面。短暂遮挡不立即清空未完成动作。
4. “结束本组”保存当前组统计。平板支撑会记录时长、质量时长与姿态分数，并开始下一组；切换动作或“重置当前动作”时，整次训练的已完成摘要仍会保留。
5. “下载检测诊断”可将最近约 900 次姿态推理的角度、检测置信度、动作阶段与拒绝原因保存为本地 JSON（不含视频画面或原始关键点），便于排查无法计数的问题；“导出 JSON”保存详细次数和整次训练摘要；“导出 CSV”保存各组摘要，可直接用 Excel 打开。训练记录仅在当前页面内存中，关闭页面前请主动导出。要清空并重新开始，点击“新训练”。
6. 可暂停、静音、切换视频测试。自动模式需要做一次完整动作；有唯一明确候选时会确认动作并回放刚才的关键点，将符合完整周期的一次也计入次数。无法确认时请手动选择，避免强行误判。

摄像头许可由你的浏览器询问。页面会先请求摄像头，再加载姿态模型；若在聊天内嵌预览中无法授权，请把测试地址复制到 Chrome / Edge 独立标签页。遇到权限拒绝，请检查地址栏左侧的网站摄像头设置；遇到设备占用，请关闭其他摄像头应用后刷新设备重试。HTTP 服务仅提供本机静态文件；页面不会将视频帧或关键点发到服务端。建议用开发者工具 Network 验证，仅应有静态资源 GET。

## Python 桌面版

建议 Python 3.11–3.12。Apple Silicon 请使用原生 arm64 Python。

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python pose_camera.py
python app.py
```

`pose_camera.py` 是最小姿态验收入口；`app.py` 是独立摄像头/推理线程的 Tk Dashboard。
桌面版也支持设置本组目标、扫描摄像头、保留多动作训练摘要、结束平板支撑组，以及主动导出 JSON/CSV。按钮“New session”会清空当前未导出的摘要。
桌面版需要带 Tk 的 Python；官方 python.org 安装通常包含 Tk。摄像头权限在 macOS“系统设置 → 隐私与安全性 → 摄像头”中开启。Windows 请开启桌面应用摄像头权限。
不要同时安装 opencv-python 与 opencv-python-headless；桌面版需要前者。

```bash
python pose_camera.py --list-cameras
python pose_camera.py --source 1
python app.py --source my_training.mp4
python pose_camera.py --source tests/assets/smoke.mp4 --headless --frames 40
python scripts/run_video.py my_training.mp4 --exercise squat --output results.json
```

`smoke.mp4` 是公共测试图片重复生成的输入连通性视频，**不是人体运动准确率数据**。`run_video.py` 按源视频时间逐帧处理；实时 UI 丢弃积压旧帧。
`pose_camera.py --output path.mp4` 可显式记录可视化视频；默认不录像。该调试输出保留输入 FPS，跳帧时播放时长可能缩短；正式评估使用逐帧脚本。

## 测试和性能

```bash
python -m pip install pytest
python -m pytest -q
python tests/benchmark.py
python tests/benchmark_camera.py --camera 0 --seconds 15
cd web
node --test tests.mjs
```

实际结果见 `docs/validation.md` 与 `docs/benchmark.json`。服务器结果不能当作 M2、Windows 或真实摄像头性能。首次安装 Python 依赖需要网络，运行识别不需要网络。

## 模型和配置

模型：`models/pose_model.onnx`，320×320、float32 NCHW、COCO17、无嵌入 NMS，输出 `[1,56,2100]`。`manifest.json` 包含 SHA256。
路径与摄像头配置在 `config.yaml`；`--model` 可覆盖路径。禁止直接换入其他输出结构后继续使用同一解码器。替换 RTMPose 等架构需另写 PoseEstimator 适配器。

需要重新导出时（仅开发阶段联网）：

```bash
python -m pip install ultralytics onnx
python scripts/export_model.py --size 320
```

修改 Python 规则后运行 `python scripts/sync_rules.py` 更新网页配置。
需要重建浏览器运行库：`cd web && npm ci && npm run setup`。
有经受试者同意且含专家分数的训练数据时，可安装 `pandas scikit-learn joblib`，用 `python evaluation/train_random_forest.py labelled.csv` 训练。`core.expert_model.ExpertScoreModel` 提供可选预测接口；缺测时返回 `None`，默认规则评分不依赖此模型，也没有附带虚构的训练权重。

## 当前边界

- 九动作是二维规则原型；自动分类是会拒绝不确定输入的启发式模式，均未经真人数据有效性验证。
- 单目二维角度随视角变化，不能测绝对厘米距离、关节真实三维运动、下背部是否贴地、损伤风险。
- 侧面遮挡时仅取一侧；在两侧之间切换不会立即取消未完成动作，但多人或遮挡严重时可能跟踪错误。
- 弓步蹲优先使用面向方向和前后脚判断前腿；这些不可见时采用膝角较小的一侧作为估计，可能选错。卷腹无个人基线校准。髋部偏高/偏低仅在有效侧面投影中判断，无法推断三维骨盆方向。
- 平板支撑时长为符合可观测条件的时长，和姿态分数分开；不是有效训练或医学结论。
- 中文与英文语音均包含可用的纠错提示；操作系统缺少对应的本地语音时保持文字反馈。语音默认关闭，需要用户开启。
- macOS / Windows 实体摄像头和 Tk 窗口尚需目标设备验收；虚拟摄像头与浏览器 WASM 推理已经验证。网页当前使用 WASM 推理，不依赖 WebGPU。
- 站点已独立发布，无需连接 GitHub；项目里的 GitHub Pages 配置仅作为可选示例，未启用。

完整范围与待办见 `PROJECT_STATUS.md`、`TODO.md`。本项目用于辅助动作评价，不用于医疗诊断。

## 第三方材料

模型与 Ultralytics 测试图片来自上游项目；遵循其 AGPL-3.0 / enterprise 条款。ONNX Runtime 为 MIT。见 `THIRD_PARTY_NOTICES.md`。请保留第三方声明和源代码。
