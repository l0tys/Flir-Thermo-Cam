from check_conn import check_connection
from image_handling import capture_and_save_heatmap, visualize_data, test_capture_and_save_heatmap
from constants import IMAGE_SAVE_PATH, DATA_SAVE_PATH, DATA_TO_IMAGE_SAVE_PATH


# Tests if there is a camera connection
check_connection()

# try:
#     capture_and_save_heatmap(
#         save_path=IMAGE_SAVE_PATH, text_path=DATA_SAVE_PATH, cam_index=0, temp_min=20, temp_max=200)
#     print("Photo captured")
# except Exception as e:
#     print("An error occured: {e}")

# try:
#     visualize_data(data_path=DATA_SAVE_PATH,
#                    save_path=DATA_TO_IMAGE_SAVE_PATH, temp_min=20, temp_max=200)
#     print("Photo visualized from data")
# except Exception as e:
#     print("An error occured: {e}")

test_capture_and_save_heatmap(
    save_path=IMAGE_SAVE_PATH, text_file_path=DATA_SAVE_PATH)
