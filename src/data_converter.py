from DataProcessing.label_mask_conversion import SegmentationMasksConversion
from src.DataProcessing.unprojector import unproject_dataset, merge_pcd_dataset

# from src.DataProcessing.unprojector import unproject_dataset
from src.util import beam2CityLabelMap

if __name__ == "__main__":
    merge_pcd_dataset()
  
    custom_mapping = beam2CityLabelMap.copy()
    #custom_mapping["CAR"] = "truck"
    dc = SegmentationMasksConversion(use_grayscale=True, mapping_dict=custom_mapping)


    # dc.process_all_single_thread()
    # dc.images_to_queue()
    # dc.queue_worker.start_execution(200)
    # unproject_dataset(multithreaded=False)

