from DataProcessing.label_mask_conversion import SegmentationMasksConversion
from src.DataProcessing.unprojector import unproject_dataset

if __name__ == "__main__":
    # dc = SegmentationMasksConversion(use_grayscale=True)
    unproject_dataset(multithreaded=False)

