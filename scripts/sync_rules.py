from pathlib import Path
import dataclasses,json,sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from core.exercise_rules import RULES
(root/'web/rules.json').write_text(json.dumps(RULES,default=dataclasses.asdict,ensure_ascii=False,indent=2),encoding='utf-8')
