import os
from waste_detection.pipeline.training_pipeline import TrainPipeline
from waste_detection.utils.main_utils import decodeImage, encodeImageIntoBase64


def train():
    obj = TrainPipeline()
    obj.run_pipeline()
    print("Training Successful!!")


if __name__ == "__main__":
    train()
    
