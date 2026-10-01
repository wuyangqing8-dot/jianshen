from dataclasses import dataclass
import numpy as np
NAMES=['nose','left_eye','right_eye','left_ear','right_ear','left_shoulder','right_shoulder','left_elbow','right_elbow','left_wrist','right_wrist','left_hip','right_hip','left_knee','right_knee','left_ankle','right_ankle']
EDGES=[(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]
@dataclass
class PoseResult:
    bbox: list
    keypoints: np.ndarray
    person_confidence: float
    person_count: int=1
    def as_dict(self):
        return dict(bbox=self.bbox,person_confidence=self.person_confidence,person_count=self.person_count,keypoints=[dict(name=n,x=float(p[0]),y=float(p[1]),confidence=float(p[2])) for n,p in zip(NAMES,self.keypoints)])
