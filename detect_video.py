import time
from threading import Thread, Timer

import numpy as np
import tensorflow as tf
from absl import app, flags, logging
from absl.flags import FLAGS

import cv2
from Poker_Game import Hand, Hands, Ranks, Suits, poker_card
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.models import YoloV3, YoloV3Tiny
from yolov3_tf2.utils import draw_outputs

# Flags definable via command
flags.DEFINE_string("classes", "./data/coco.names", "path to classes file")
flags.DEFINE_string(
    "weights", "./checkpoints/yolov3-cardgame.tf", "path to weights file"
)
flags.DEFINE_boolean("tiny", False, "yolov3 or yolov3-tiny")
flags.DEFINE_integer("size", 608, "resize images to")
flags.DEFINE_string("video", "0", "path to video file or number for webcam)")
flags.DEFINE_string("video2", "1", "path to video file or number for webcam)")
flags.DEFINE_string("output", None, "path to output video")
flags.DEFINE_string(
    "output_format", "XVID", "codec used in VideoWriter when saving video to file"
)
flags.DEFINE_integer("num_classes", 52, "number of classes in the model")

# static variables
found_cards = [[], []]
found_cards_strings = [[], []]
timer_running = False
nb_of_cards = [0, 0]
time_to_wait_for_clear = 10
input_image = None
input_image2 = None
parsed_image = None
parsed_image2 = None
exit_program = False

actualHand = [[], []]

font = cv2.FONT_HERSHEY_SIMPLEX
fontsize = 0.5
fontColor = (255, 255, 255)
thickness = 2
lineType = 10


def test_for_reset():
    global found_cards, found_cards_strings, nb_of_cards, timer_running, actualHand

    found_cards = [[], []]
    found_cards_strings = [[], []]
    actualHand = [[], []]
    timer_running = False
    nb_of_cards = [0, 0]


def show_changed_image(out):

    global timer_running, found_cards, found_cards_strings, nb_of_cards, parsed_image, parsed_image2, actualHand

    # yolo related configuration of weights

    if FLAGS.tiny:
        yolo = YoloV3Tiny(classes=FLAGS.num_classes)
    else:
        yolo = YoloV3(classes=FLAGS.num_classes)

    yolo.load_weights(FLAGS.weights)
    logging.info("weights loaded")

    class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
    logging.info("classes loaded")

    # variables
    times = []
    odd_iteration = True
    temp_image = input_image

    # start camera until q is pressed and close all cv2 windows
    while True:

        # switch between the two camera frames every iteration
        if not odd_iteration:
            temp_image = input_image
            iterator = 0
        else:
            temp_image = input_image2
            iterator = 1

        if temp_image is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            continue

        # yolo prediction along with drawing on the images
        img_in = cv2.cvtColor(temp_image, cv2.COLOR_BGR2RGB) 
        img_in = tf.expand_dims(img_in, 0)
        img_in = transform_images(img_in, FLAGS.size)

        t1 = time.time()
        boxes, scores, classes, nums = yolo.predict(img_in)

        t2 = time.time()
        times.append(t2 - t1)
        times = times[-20:]

        img = draw_outputs(temp_image, (boxes, scores, classes, nums), class_names)

        img = cv2.putText(
            img,
            "Time: {:.2f}ms".format(sum(times) / len(times) * 2 * 1000),
            (0, 30),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            1,
            (0, 0, 255),
            2,
        )

        boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]

        # start a timer if no card is detected anymore to save detected cards a specific amount of time
        if nums == 0:
            if timer_running == False:
                timer = Timer(time_to_wait_for_clear, test_for_reset)
                timer.start()
                timer_running = True
        else:
            if timer_running:
                timer.cancel()
                timer_running = False

        # for each newly detected card, which detection score is better than 0.95, get the poker_cards via poker_game
        for i in range(nums):

            card_name = class_names[int(classes[i])]

            if card_name not in found_cards_strings[iterator] and scores[i] >= 0.98:
                found_cards_strings[iterator].append(card_name)
                splitted_card_name = card_name.split("-", 2)
                card = poker_card(
                    Ranks[splitted_card_name[0]], Suits[splitted_card_name[1]]
                )
                found_cards[iterator].append(card)

        if len(found_cards_strings[iterator]) > nb_of_cards[iterator]:
            actualHand[iterator] = Hand(found_cards[iterator])
            nb_of_cards[iterator] = len(found_cards_strings[iterator])

        if FLAGS.output:
            out.write(img)

        # save the images to a global variable to let the main method be able to display the image
        if not odd_iteration:
            parsed_image = temp_image
        else:
            parsed_image2 = temp_image

        # if 'q' is pressed in the main, exit the program and cancel the timer
        if exit_program:
            timer.cancel()
            timer_running = False
            break

        odd_iteration = not odd_iteration


def main(_argv):

    global input_image, input_image2, exit_program

    print("bla")

    # check for the used hardware
    physical_devices = tf.config.experimental.list_physical_devices("GPU")

    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)

    # try to use the cameras one and two
    try:
        vid = cv2.VideoCapture(int(FLAGS.video))
        vid2 = cv2.VideoCapture(int(FLAGS.video2))
    except:
        vid = cv2.VideoCapture(FLAGS.video)
        vid2 = cv2.VideoCapture(FLAGS.video2)

    out = None

    # output parameters for the processed image
    if FLAGS.output:
        # by default VideoCapture returns float instead of int
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
        out = cv2.VideoWriter(FLAGS.output, codec, fps, (width, height))

    # get camera stream
    _, input_image = vid.read()
    _, input_image2 = vid2.read()

    # open the thread with yolo for the card proocessing
    t = Thread(target=show_changed_image, args=[out])
    t.start()

    # configure the window for the camera streams
    cv2.namedWindow("Input-Images", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Input-Images", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_KEEPRATIO)

    # show the merged camera streams along with an overlay and
    while True:
        _, input_image = vid.read()
        if input_image is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            continue

        _, input_image2 = vid2.read()
        if input_image is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            continue

        # merge the two camera stream into one window
        input_images_horizontal = np.hstack((input_image, input_image2))

        ############### overlay #####################
        # Player1 Text
        if not actualHand[0]:
            text = "Player 1: No Cards visible!"
        else:
            text = "Player 1 Cards: " + actualHand[0].print_bestHand()

        textsize = cv2.getTextSize(text, font, fontsize, 2)[0]

        textX = int((input_images_horizontal.shape[1] - textsize[0]) / 2)
        textY = int((input_images_horizontal.shape[0] + textsize[1]) / 20)
        cv2.putText(
            img=input_images_horizontal,
            text=text,
            org=(textX, textY),
            fontFace=font,
            fontScale=fontsize,
            color=(255, 255, 255),
            thickness=thickness,
            lineType=lineType,
        )

        if actualHand[0]:
            text = "Player 1's best Hand: " + actualHand[0].get_hand()

            textsize = cv2.getTextSize(text, font, fontsize, 2)[0]

            textX = int((input_images_horizontal.shape[1] - textsize[0]) / 2)
            textY = int((input_images_horizontal.shape[0] + textsize[1]) / 10)
            cv2.putText(
                img=input_images_horizontal,
                text=text,
                org=(textX, textY),
                fontFace=font,
                fontScale=fontsize,
                color=(255, 255, 255),
                thickness=thickness,
                lineType=lineType,
            )

        #Player2-Text
        if not actualHand[1]:
            text = "Player 2: No Cards visible!"
        else:
            text = "Player 2 Cards: " + actualHand[1].print_bestHand()

        textsize = cv2.getTextSize(text, font, fontsize, 2)[0]

        textX = int((input_images_horizontal.shape[1] - textsize[0]) / 2)
        textY = int((input_images_horizontal.shape[0] + textsize[1]) / 5)
        cv2.putText(
            img=input_images_horizontal,
            text=text,
            org=(textX, textY),
            fontFace=font,
            fontScale=fontsize,
            color=(255, 255, 255),
            thickness=thickness,
            lineType=lineType,
        )

        if actualHand[1]:
            text = "Player 2's best Hand: " + actualHand[1].get_hand()

            textsize = cv2.getTextSize(text, font, fontsize, 2)[0]

            textX = int((input_images_horizontal.shape[1] - textsize[0]) / 2)
            textY = int((input_images_horizontal.shape[0] + textsize[1]) / 4)
            cv2.putText(
                img=input_images_horizontal,
                text=text,
                org=(textX, textY),
                fontFace=font,
                fontScale=fontsize,
                color=(255, 255, 255),
                thickness=thickness,
                lineType=lineType,
            )

        if actualHand[0] and actualHand[1]:

            #Comparison of the two players + text overlay
            actualWinner = actualHand[0].compareHands(actualHand[1]) #compares the first with the second player for an actual better hand

            if actualWinner == 1:
                text = "Player 1 is winning at the moment!"
                if actualHand[0].kicker_card:
                    text = "Player 1 is winning with the Kicker Card " + actualHand[0].get_kicker_card() + " at the moment!"
            elif actualWinner == 2:
                text = "Player 2 is winning at the moment!"
                if actualHand[0].kicker_card:
                    text = "Player 2 is winning with the Kicker Card " + actualHand[0].get_kicker_card() + " at the moment!"
            else:
                text = "The two players hands are a draw at the moment!"

            textsize = cv2.getTextSize(text, font, fontsize, 2)[0]

            textX = int((input_images_horizontal.shape[1] - textsize[0]) / 2)
            textY = int((input_images_horizontal.shape[0] + textsize[1]) / 3)
            cv2.putText(
                img=input_images_horizontal,
                text=text,
                org=(textX, textY),
                fontFace=font,
                fontScale=fontsize,
                color=(255, 255, 255),
                thickness=thickness,
                lineType=lineType,
            )

        ########## end overlay ###############

        # display all the windows, first the camera input, secondly after yolo is loaded, the processed image
        cv2.imshow("Input-Images", input_images_horizontal)

        # cv2.imshow('Input-Images2', numpy_vertical)

        if not parsed_image is None or not parsed_image is None:

            cv2.imshow("Parsed Image", parsed_image)
            cv2.imshow("Parsed Image 2", parsed_image2)

        if cv2.waitKey(1) == ord("q"):
            exit_program = True
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        app.run(main)
    except SystemExit:
        pass
