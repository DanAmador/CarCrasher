from DataProcessing.label_mask_conversion import SegmentationMasksConversion
# from src.DataProcessing.unprojector import unproject_dataset

if __name__ == "__main__":
    dc = SegmentationMasksConversion(use_grayscale=True)
    # dc.process_all_single_thread()
    dc.images_to_queue()
    dc.queue_worker.start_execution(200)
    # unproject_dataset(multithreaded=False)

