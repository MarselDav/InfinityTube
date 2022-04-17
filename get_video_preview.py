import cv2


def get_standart_preview(video_name):
    video_file = cv2.VideoCapture("static/video/" + video_name)  # открытие файла
    # fps = video_file.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_file.get(cv2.CAP_PROP_FRAME_COUNT))
    # duration = frame_count/fps
    # print(duration)
    recording_step = frame_count // 3 - 1
    first_save_frame = recording_step
    cnt_save = 1

    currentframe = 0
    while True:
        success, frame = video_file.read()

        if success:
            if currentframe == first_save_frame:
                imgname = "static/img/" + video_name + " " + str(cnt_save) + ".jpg"
                cv2.imwrite(imgname, frame)
                first_save_frame += recording_step
                cnt_save += 1
            currentframe += 1
        else:
            video_file.release()
            cv2.destroyAllWindows()
            break


#
# print(get_standart_preview("The Witcher 3 2021.07.07 - 00.10.00.01.mp4"))
