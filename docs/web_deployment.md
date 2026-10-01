# Browser deployment

## Local
On Windows 10/11 double-click `start_web.bat`. It uses Windows PowerShell to serve only the `web/`, `models/`, and `locales/` paths over loopback, chooses an available port from 8000–8010, and opens the browser. Keep its terminal open; no Python or Node installation is required for the browser app. On macOS run `bash start_web.command`, which needs Python 3, or run `python3 -m http.server 8000 --bind 127.0.0.1` at the project root and open http://localhost:8000/web/. Both `web/vendor` and `models/pose_model.onnx` are included. Camera requires localhost or HTTPS. Safari may use WASM; this does not guarantee 30 FPS. The Windows launcher source has been reviewed but still needs a physical Windows acceptance run.

## GitHub Pages
A workflow is provided at `.github/workflows/pages.yml`. No external repository credentials or repository URL were provided, so no remote repository or public deployment was created.

1. Put project contents at the root of your own GitHub repository, including models/pose_model.onnx and web/package-lock.json. Do not commit node_modules, recordings or personal training data.
2. Settings → Pages → Source: GitHub Actions.
3. Run “Publish local fitness web app” manually in Actions. It installs the pinned runtime, copies only static web/model files, and deploys.
4. Open the HTTPS Pages URL, allow camera access, verify Network contains only static resource GETs.

The model uses a relative ../models/ path, compatible with repository Pages prefixes. The page has no server-inference endpoint. Static hosting exposes source/model assets; user camera frames remain local.

No service worker is installed; offline operation means the page and local assets are served from the local computer, or the already-open page has finished loading its assets. We do not claim a remote-hosted page can always be reopened offline.
