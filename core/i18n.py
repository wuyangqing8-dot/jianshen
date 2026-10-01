import json
from pathlib import Path
ZH=json.loads((Path(__file__).resolve().parents[1]/'locales/zh.json').read_text(encoding='utf-8'))
def feedback_zh(exercise,errors,fallback):
    messages=[ZH.get(exercise+'.'+name) for name in errors[:2]]
    messages=[message for message in messages if message]
    return '；'.join(messages) if messages else ZH.get('generic.'+fallback,fallback)
