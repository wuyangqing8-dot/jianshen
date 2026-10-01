"""Pure summaries for deliberate export; video/keypoints are never included."""
from collections import Counter

COLUMNS=('exercise','set','reps','duration_seconds','average_score','best_score','worst_score','main_error','quality_seconds','status')


def goal_progress(exercise,reps,hold_seconds,target):
    plank=exercise=='plank'
    try:limit=max(1,min(3600,int(target)))
    except (TypeError,ValueError):limit=30 if plank else 10
    progress=max(0,float(hold_seconds or 0)) if plank else max(0,int(reps or 0))
    return dict(progress=progress,target=limit,unit='秒' if plank else '次',percent=min(100,100*progress/limit),reached=progress>=limit)


def summary_rows(engine,score=None):
    if engine is None:return []
    name=engine.exercise;session=engine.session
    rows=[dict(exercise=name,set=s['set'],reps=s['reps'],duration_seconds=s['duration'],average_score=s['average_score'],best_score=s['best_score'],worst_score=s['worst_score'],main_error=s['main_error'],quality_seconds=s.get('quality_seconds',''),status='completed') for s in session.sets]
    if name=='plank':
        if engine.hold>0:rows.append(dict(exercise=name,set=len(rows)+1,reps=0,duration_seconds=round(engine.hold,1),average_score=round(engine.hold_score_sum/engine.hold_score_count,1) if engine.hold_score_count else score,best_score=engine.hold_best if engine.hold_best is not None else '',worst_score=engine.hold_worst if engine.hold_worst is not None else '',main_error=engine.hold_errors.most_common(1)[0][0] if engine.hold_errors else '',quality_seconds=round(engine.quality_hold,1),status='current'))
    elif session.current:
        scores=[r['total_score'] for r in session.current if r.get('total_score') is not None]
        errors=Counter(key for r in session.current for key in r.get('detected_errors',[]))
        rows.append(dict(exercise=name,set=len(rows)+1,reps=len(session.current),duration_seconds=round(max(0,(session.last_activity or 0)-(session.start or 0)),1),average_score=round(sum(scores)/len(scores),1) if scores else None,best_score=max(scores) if scores else None,worst_score=min(scores) if scores else None,main_error=errors.most_common(1)[0][0] if errors else '',quality_seconds='',status='current'))
    return rows
