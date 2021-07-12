from DataProcessing.label_mask_conversion import SegmentationMasksConversion
from DataProcessing.point_cloud_generator import PointCloudGenerator

if __name__ == "__main__":
    # dc = SegmentationMasksConversion(use_grayscale=True)
    pc = PointCloudGenerator()
    pc.run(multithreaded=False)