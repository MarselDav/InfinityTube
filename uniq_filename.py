import datetime


def get_uniq_filename():  # получить уникальное название файла
    uniq_filename = str(datetime.datetime.now().date()) + '_' \
                    + str(datetime.datetime.now().time()).replace(':', '.') + ".mp4"
    return uniq_filename
