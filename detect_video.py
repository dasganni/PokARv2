import time

import tensorflow as tf
from absl import app, flags, logging
from absl.flags import FLAGS

import cv2
from Poker_Game import poker_card, Hand, Ranks, Suits, Hands
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.models import YoloV3, YoloV3Tiny
from yolov3_tf2.utils import draw_outputs
from threading import Timer, Thread

flags.DEFINE_string("classes", "./data/coco.names", "path to classes file")
flags.DEFINE_string("weights", "./checkpoints/yolov3-cardgame.tf", "path to weights file")
flags.DEFINE_boolean("tiny", False, "yolov3 or yolov3-tiny")
flags.DEFINE_integer("size", 608, "resize images to")
flags.DEFINE_string(
    "video", "0", "path to video file or number for webcam)"
)
flags.DEFINE_string(
    "video2", "1", "path to video file or number for webcam)"
)
flags.DEFINE_string("output", None, "path to output video")
flags.DEFINE_string(
    "output_format", "XVID", "codec used in VideoWriter when saving video to file"
)
flags.DEFINE_integer("num_classes", 52, "number of classes in the model")

found_cards=[]
found_cards_strings=[]
timer_running=False
nb_of_cards=0
time_to_wait_for_clear=10
input_image=cv2.VideoCapture().read
input_image2=cv2.VideoCapture().read



def test_for_reset():
    global found_cards, found_cards_strings, nb_of_cards, timer_running

    found_cards=[]
    found_cards_strings=[]
    print("No cards found, resetted!")
    timer_running = False
    nb_of_cards = 0

def show_changed_image(out):

    global found_cards, found_cards_strings, nb_of_cards, timer_running


    if FLAGS.tiny:
        yolo = YoloV3Tiny(classes=FLAGS.num_classes)
    else:
        yolo = YoloV3(classes=FLAGS.num_classes)

    yolo.load_weights(FLAGS.weights)
    logging.info("weights loaded")

    class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
    logging.info("classes loaded")

    times = []
    odd_iteration = True
    temp_image = input_image

    while True:
        
        if not odd_iteration:
            temp_image = input_image
        else:
            temp_image = input_image2


        if temp_image is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            continue

        img_in = tf.expand_dims(temp_image, 0)
        img_in = transform_images(img_in, FLAGS.size)

        t1 = time.time()
        boxes, scores, classes, nums = yolo.predict(img_in)
        t2 = time.time()
        times.append(t2 - t1)
        times = times[-20:]

        img = draw_outputs(temp_image, (boxes, scores, classes, nums), class_names)

        img = cv2.putText(
            img,
            "Time: {:.2f}ms".format(sum(times) / len(times) * 1000),
            (0, 30),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            1,
            (0, 0, 255),
            2,
        )

        boxes, scores, classes, nums = boxes[0], scores[0], classes[0], nums[0]

        if nums==0:
            if timer_running==False:
                timer = Timer(time_to_wait_for_clear, test_for_reset) 
                timer.start() 
                timer_running=True
        else:
            timer.cancel()
            timer_running=False


        for i in range(nums):

            card_name = class_names[int(classes[i])]
            #print(card_name)
            if card_name not in found_cards_strings and scores[i]>=0.95:
                #print(scores[i])
                found_cards_strings.append(card_name)
                splitted_card_name=card_name.split('-', 2)
                #print(splitted_card_name)
                card = poker_card(Ranks[splitted_card_name[0]], Suits[splitted_card_name[1]])
                found_cards.append(card)
                #print(class_names[int(classes[i])])
        if len(found_cards_strings) > nb_of_cards:
            actualHand=Hand(found_cards)
            actualHand.print_hand()
            print(actualHand.get_hand())
            nb_of_cards = len(found_cards_strings)

        
        #print(actualHand.get_highest())
        #print(actualHand.is_straight_flush())

        if FLAGS.output:
            out.write(img)

        cv2.imshow("Parsed Image", img)


        if cv2.waitKey(1) == ord("q"):
            timer.cancel()
            timer_running=False
            break
        odd_iteration = not odd_iteration
    cv2.destroyAllWindows()


def main(_argv):

    global input_image, input_image2

    physical_devices = tf.config.experimental.list_physical_devices("GPU")

    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)

    try:
        vid = cv2.VideoCapture(int(FLAGS.video))
        vid2 = cv2.VideoCapture(int(FLAGS.video2))
    except:
        vid = cv2.VideoCapture(FLAGS.video)
        vid2 = cv2.VideoCapture(FLAGS.video2)


    out = None

    if FLAGS.output:
        # by default VideoCapture returns float instead of int
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
        out = cv2.VideoWriter(FLAGS.output, codec, fps, (width, height))
    
    _, input_image = vid.read()
    _, input_image2 = vid2.read()


    t = Thread(target=show_changed_image, args=[out])
    t.start()

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


        cv2.imshow("Input Image", input_image)
        cv2.imshow("Input Image2", input_image2)


        if cv2.waitKey(1) == ord("q"):
            end_program=True
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        app.run(main)
    except SystemExit:
        pass
