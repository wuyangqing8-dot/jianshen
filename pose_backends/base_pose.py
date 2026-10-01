from abc import ABC,abstractmethod
class PoseEstimator(ABC):
    @abstractmethod
    def load_model(self,path): pass
    @abstractmethod
    def preprocess(self,frame): pass
    @abstractmethod
    def postprocess(self,outputs,transform): pass
    @abstractmethod
    def infer(self,frame): pass
    def get_keypoints(self):
        return None if self.last_result is None else self.last_result.keypoints
