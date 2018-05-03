# This code based on Harrison Kinsley's (Sentdex) code (https://github.com/Sentdex/pygta5)

"""
Data collection module (saves data in CSV and JPG formats).
Saves screen captures and pressed keys into a file
for further trainings of NN.
"""

import csv
import os
import re
import threading
import time

import cv2

from data_collection.img_process import grab_screen
from data_collection.keycap import key_check, Gamepad

lock = threading.Lock()

# files to save training data
path = "E:\Graduation_Project"
img = "img\img{}.jpg"
img_path = os.path.join(path, "img\img{}.jpg")
table = 'training_data.csv'
# read previously stored data to avoid overwriting
img_num = 1
if os.path.isfile(os.path.join(path, table)):
    with open(os.path.join(path, table), 'r') as f:
        img_num = int(re.findall('\d+', f.readlines()[-1])[0]) + 1


# in case of using a keyboard
def keys_to_output(keys):
    # initial values: no key pressed
    throttle = 0
    steering = 0

    if 'W' in keys:
        throttle = 1
    elif 'S' in keys:
        throttle = -1

    if 'A' in keys:
        steering = -1
    elif 'D' in keys:
        steering = 1

    return throttle, steering


def save(data):
    global img_num

    with lock:  # make sure that data is consistent
        # last_time = time.time()
        with open(os.path.join(path, table), 'a', newline='') as f:
            writer = csv.writer(f)

            for td in data:
                # write in csv: image_name, throttle, steering
                writer.writerow([img.format(img_num), td[1], td[2]])
                # write captures in files
                cv2.imwrite(img_path.format(img_num), td[0])
                img_num += 1
        # print('Saving took {} seconds'.format(time.time() - last_time))


def main():
    # TODO: add speed and direction into input data

    # initialize gamepad
    gamepad = Gamepad()
    gamepad.open()

    # countdown for having time to open GTA V window
    for i in list(range(5))[::-1]:
        print(i + 1)
        time.sleep(1)
    print("Start!")

    # last_time = time.time()  # to measure the number of frames
    close = False  # to exit execution
    pause = False  # to pause execution
    training_data = []  # list for storing training data

    while not close:
        while not pause:
            screen = cv2.resize(grab_screen("Grand Theft Auto V"), (320, 240))
            # read throttle and steering values from the keyboard
            # throttle, steering = keys_to_output(key_check())
            # read throttle and steering values from the gamepad
            throttle, steering = gamepad.get_state()
            training_data.append([screen, throttle, steering])

            # save the data every 500 iterations
            if len(training_data) % 500 == 0:
                threading.Thread(target=save, args=(training_data,)).start()
                training_data = []

            time.sleep(0.02)  # in order to slow down fps
            # print('Main loop took {} seconds'.format(time.time() - last_time))
            # last_time = time.time()

            keys = key_check()
            if 'T' in keys:
                gamepad.close()
                pause = True
                print('Paused. To exit the program press Z.')
                time.sleep(0.5)

        keys = key_check()
        if 'T' in keys:
            gamepad.open()
            pause = False
            print('Unpaused')
            time.sleep(1)
        elif 'Z' in keys:
            close = True
            print('Saving data and closing the program.')
            save(training_data)


if __name__ == '__main__':
    main()
