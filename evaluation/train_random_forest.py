"""Optional: pip install scikit-learn pandas joblib. User supplies expert labels."""
import argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--output',default='models/expert_score.joblib');a=p.parse_args()
import pandas as pd,joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error
cols=['knee_angle','hip_angle','trunk_lean','symmetry','stability','velocity']
df=pd.read_csv(a.csv).dropna(subset=cols+['expert_score','participant_id'])
if df.participant_id.nunique()<3:raise ValueError('Need at least 3 participant IDs; never split frames of one participant across train/test.')
train,test=next(GroupShuffleSplit(n_splits=1,test_size=.3,random_state=42).split(df,groups=df.participant_id))
m=RandomForestRegressor(n_estimators=200,min_samples_leaf=3,random_state=42);m.fit(df.iloc[train][cols],df.iloc[train].expert_score)
print('Held-out participant MAE:',mean_absolute_error(df.iloc[test].expert_score,m.predict(df.iloc[test][cols])))
Path(a.output).parent.mkdir(parents=True,exist_ok=True);joblib.dump({'model':m,'features':cols},a.output)
