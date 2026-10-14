/* ui-tools.js — 界面语言 / 字体大小 / 语音音色增强 */
(function () {
  'use strict';

  /* ============ 1. 界面语言 ============ */
  const TEXT_MAP = {
    '运动有迹可循': 'Your movement, made visible',
    '本机处理 · 视频不上传 · 2026.09.28 校准版': 'On-device · No upload · 2026.09.28 build',
    '每一次动作，都更从容。': 'Every rep, more composed.',
    '让关键节点可见，让训练过程可复盘。': 'Key moments made visible. Every session reviewable.',
    '研究原型 / 实验性评分': 'Research prototype / experimental scoring',
    '摄像头 ': 'Camera ',
    '系统默认摄像头': 'System default camera',
    '刷新设备': 'Refresh devices',
    '授权后可显示设备名称；切换摄像头会保留本组记录': 'Device names appear after permission; switching camera keeps this set',
    '在独立标签页打开摄像头': 'Open camera in a new tab',
    '本组目标 ': 'Set goal ',
    '次': ' reps',
    '准备好，开始你的训练': 'Ready when you are',
    '选择动作，允许摄像头访问，并让身体进入画面': 'Pick an exercise, allow camera access, and step into frame',
    '待开始': 'Idle',
    '推荐：侧面 / 45°': 'Recommended: side / 45°',
    '训练动作': 'Exercise',
    '计数灵敏度': 'Counting sensitivity',
    '宽松（推荐）': 'Lenient (recommended)',
    '更灵敏（可能多计）': 'More sensitive (may overcount)',
    '标准': 'Standard',
    '按我的动作校准': 'Calibrate to my motion',
    '查看当前动作的判定依据': 'How this exercise is judged',
    '按你的动作校准': 'Calibrate to your motion',
    '先保持起始姿势约 1 秒并记录，再保持动作另一端约 1 秒并记录。完成后重复一遍即可测试计数。': 'Hold the start position ~1s and capture, then the end position ~1s and capture. Repeat once to test counting.',
    '记录起始姿势': 'Capture start pose',
    '记录动作另一端': 'Capture end pose',
    '恢复默认': 'Restore defaults',
    '尚未校准；可直接使用默认规则。': 'Not calibrated; default rules are active.',
    '动作阶段': 'Phase',
    '完成次数': 'Reps',
    '最近评分': 'Last score',
    '本组平均 —': 'Set average —',
    '检测进度': 'Pipeline',
    '摄像头 · 人体 · 关键关节 · 起始姿势': 'Camera · Body · Joints · Start pose',
    '实时检测': 'Live tracking',
    '开启摄像头后显示人体识别与动作角度': 'Body detection and joint angles appear after camera starts',
    '动作提示': 'Coaching',
    '先选择动作，并参考推荐视角摆放摄像头。': 'Pick an exercise and set up the camera at the recommended angle.',
    '姿态推理 ': 'Pose inference ',
    '画面刷新 ': 'Render ',
    '推理耗时 ': 'Inference ',
    '质量时长 ': 'Quality time ',
    '开合跳频率 ': 'Jumping-jack rate ',
    '开启摄像头': 'Start camera',
    '暂停': 'Pause',
    '重置当前动作': 'Reset exercise',
    '结束本组': 'End set',
    '新训练': 'New workout',
    '语音 ': 'Voice ',
    '关闭': 'Off',
    '每次反馈': 'Every cue',
    '每 5 次': 'Every 5 reps',
    '调试': 'Debug',
    '导出 JSON': 'Export JSON',
    '导出 CSV': 'Export CSV',
    '下载检测诊断': 'Download diagnostics',
    '视频测试与训练记录': 'Video test & session history',
    '选择本机视频进行测试。文件只在当前浏览器中解码。自动识别是保守实验模式，先做一次明显的动作供系统判断；无法确定时请手动选择。': 'Pick a local video to test. Decoded in your browser only. Auto-detection is conservative — do one clear rep first, or select manually.',
    '暂无已完成组': 'No completed sets yet',
    '辅助动作评价，不用于医疗诊断。二维投影与遮挡会影响结果；评分阈值尚需真人数据校准。九动作依据项目几何规则，非经真人数据验证的标准动作库。模型就绪后可断网使用。': 'Assistive feedback only — not for medical diagnosis. 2D projection and occlusion affect results; thresholds still need real-human calibration. Works offline once the model is ready.'
  };

  const originalTexts = new WeakMap();

  function walkTextNodes(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    const out = [];
    let n;
    while ((n = walker.nextNode())) {
      if (n.nodeValue && n.nodeValue.trim()) out.push(n);
    }
    return out;
  }

  function applyLanguage(lang) {
    walkTextNodes(document.body).forEach(function (node) {
      const p = node.parentNode;
      if (!p) return;
      const tag = p.nodeName;
      if (tag === 'SCRIPT' || tag === 'STYLE') return;

      if (!originalTexts.has(node)) originalTexts.set(node, node.nodeValue);
      const orig = originalTexts.get(node);

      if (lang === 'en') {
        const key = orig.trim();
        const t = TEXT_MAP[key];
        if (t) node.nodeValue = orig.replace(key, t);
      } else {
        node.nodeValue = orig;
      }
    });
    document.documentElement.lang = lang === 'en' ? 'en' : 'zh-CN';
    try { localStorage.setItem('uiLang', lang); } catch (e) {}
  }

  /* ============ 2. 字体大小 ============ */
  function setZoom(level) {
    // level: 0=默认，正数放大，负数缩小
    document.body.style.zoom = String(1 + level * 0.1);
    try { localStorage.setItem('uiZoomLevel', String(level)); } catch (e) {}
  }

  /* ============ 3. 语音增强（音色 + 语速） ============ */
  function installTtsHook() {
    if (!('speechSynthesis' in window)) return;
    const synth = window.speechSynthesis;
    const origSpeak = synth.speak.bind(synth);

    synth.speak = function (utter) {
      try {
        const rate = parseFloat(localStorage.getItem('ttsRate') || '1');
        const pitch = parseFloat(localStorage.getItem('ttsPitch') || '1');
        const voiceName = localStorage.getItem('ttsVoiceName');

        if (!isNaN(rate)) utter.rate = rate;
        if (!isNaN(pitch)) utter.pitch = pitch;

        if (voiceName) {
          const v = synth.getVoices().find(function (x) { return x.name === voiceName; });
          if (v) utter.voice = v;
        }
      } catch (e) {}
      return origSpeak(utter);
    };
  }

  function populateVoices() {
    const sel = document.getElementById('ttsVoiceSelect');
    if (!sel) return;
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    let saved = null;
    try { saved = localStorage.getItem('ttsVoiceName'); } catch (e) {}

    sel.innerHTML = '';
    const auto = document.createElement('option');
    auto.value = '';
    auto.textContent = '自动 / Auto';
    sel.appendChild(auto);

    voices.forEach(function (v) {
      const opt = document.createElement('option');
      opt.value = v.name;
      opt.textContent = v.name + ' (' + v.lang + ')';
      sel.appendChild(opt);
    });

    if (saved) sel.value = saved;
  }

  /* ============ 启动 ============ */
  function init() {
    installTtsHook();

    // 语言
    const langSel = document.getElementById('uiLang');
    let savedLang = 'zh';
    try { savedLang = localStorage.getItem('uiLang') || 'zh'; } catch (e) {}
    if (langSel) {
      langSel.value = savedLang;
      langSel.addEventListener('change', function () { applyLanguage(langSel.value); });
    }
    applyLanguage(savedLang);

    // 字体
    let savedZoom = 0;
    try { savedZoom = parseInt(localStorage.getItem('uiZoomLevel') || '0', 10); } catch (e) {}
    if (isNaN(savedZoom)) savedZoom = 0;
    setZoom(savedZoom);

    document.querySelectorAll('[data-font]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const d = parseInt(btn.getAttribute('data-font'), 10);
        if (d === 0) savedZoom = 0;
        else savedZoom = Math.max(-3, Math.min(5, savedZoom + d));
        setZoom(savedZoom);
      });
    });

    // 语音
    populateVoices();
    if (window.speechSynthesis && 'onvoiceschanged' in window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = populateVoices;
    }

    const vSel = document.getElementById('ttsVoiceSelect');
    if (vSel) vSel.addEventListener('change', function () {
      try { localStorage.setItem('ttsVoiceName', vSel.value); } catch (e) {}
    });

    const rInput = document.getElementById('ttsRate');
    if (rInput) {
      let savedRate = '1';
      try { savedRate = localStorage.getItem('ttsRate') || '1'; } catch (e) {}
      rInput.value = savedRate;
      rInput.addEventListener('input', function () {
        try { localStorage.setItem('ttsRate', rInput.value); } catch (e) {}
      });
    }

    const preview = document.getElementById('ttsPreview');
    if (preview) preview.addEventListener('click', function () {
      if (!window.speechSynthesis) return;
      const lang = (document.getElementById('uiLang') || {}).value || 'zh';
      const text = lang === 'en' ? 'This is a voice preview.' : '这是一段语音试听。';
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      const voiceName = (function () { try { return localStorage.getItem('ttsVoiceName'); } catch (e) { return null; } })();
      if (voiceName) {
        const v = window.speechSynthesis.getVoices().find(function (x) { return x.name === voiceName; });
        if (v) u.voice = v;
      }
      u.rate = parseFloat((function () { try { return localStorage.getItem('ttsRate'); } catch (e) { return null; } })() || '1');
      window.speechSynthesis.speak(u);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
