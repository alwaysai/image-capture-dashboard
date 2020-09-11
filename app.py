import time
import edgeiq
import argparse
import socketio as so
from helpers import *
from sample_writer import *
from flask_socketio import SocketIO
from flask import Flask, render_template, request
import cv2
import base64
import threading
import logging
from eventlet.green import threading as eventlet_threading
import cv2
from collections import deque

app = Flask(__name__)
socketio_logger = logging.getLogger('socketio')
socketio = SocketIO(app, logger=socketio_logger, engineio_logger=socketio_logger)
SAMPLE_RATE = 25
SESSION = date_time = time.strftime("%d%H%M%S", time.localtime())
video_stream = edgeiq.WebcamVideoStream()

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@socketio.on('connect')
def connect_cv():
    print('[INFO] connected: {}'.format(request.sid))

@socketio.on('disconnect')
def disconnect_cv():
    print('[INFO] disconnected: {}'.format(request.sid))

@socketio.on('write_data')
def write_data():
    controller.start_writer()
    socketio.sleep(0.01)
    controller.update_text('Data Collection Started!')
    print('start signal received')
    file_name = file_set_up("video", SESSION)
    
    with edgeiq.VideoWriter(output_path=file_name, fps=SAMPLE_RATE) as video_writer:
        if SAMPLE_RATE > video_stream.fps:
            raise RuntimeError(
                "Sampling rate {} cannot be greater than the camera's FPS {}".
                format(SAMPLE_RATE, video_stream.fps))

        print('Data Collection Started!')
        while True:
            t_start = time.time()
            frame = controller.cvclient.video_frames.popleft()
            video_writer.write_frame(frame)
            t_end = time.time() - t_start
            t_wait = (1 / SAMPLE_RATE) - t_end
            if t_wait > 0:
                time.sleep(t_wait)

            if controller.is_writing() == False:
                print("ended")
                controller.update_text('Data Collection Ended')
                print('Data Collection Ended')
                break
            
            socketio.sleep(0.0001)

@socketio.on('stop_writing')
def stop_writing():
    print('stop signal received')
    controller.stop_writer()
    
@socketio.on('take_snapshot')
def take_snapshot():
    """Takes a single snapshot and saves it.
    """
    print('snapshot signal received')
    file_name = file_set_up("image", SESSION)
    controller.update_text('Taking Snapshot')
    print('Taking Snapshot')
    frame = controller.cvclient.all_frames.popleft()
    cv2.imwrite(file_name, frame)
    controller.update_text('Snapshot Saved')
    print('Snapshot Saved')

@socketio.on('close_app')
def close_app():
    print('Stop Signal Received')
    controller.close_writer()
    controller.close()

class CVClient(eventlet_threading.Thread):
    def __init__(self, fps, exit_event):
        """The original code was created by Eric VanBuhler
        (https://github.com/alwaysai/video-streamer) and is modified here.

        Initializes a customizable streamer object that 
        communicates with a flask server via sockets. 

        Args:
            stream_fps (float): The rate to send frames to the server.
            exit_event: Threading event
        """
        self._stream_fps = SAMPLE_RATE
        self.fps = fps
        self._last_update_t = time.time()
        self._wait_t = (1/self._stream_fps)
        self.exit_event = exit_event
        self.writer = SampleWriter()
        self.all_frames = deque()
        self.video_frames = deque()
        super().__init__()

    def setup(self):
        """Starts the thread running.

        Returns:
            CVClient: The CVClient object
        """
        self.start()
        time.sleep(1)
        return self

    def run(self):
        # loop detection
        print("running thread")
        video_stream.start()
        # Allow Webcam to warm up
        socketio.sleep(2.0)
        self.fps.start()
        
        # loop detection
        while True:
            frame = video_stream.read()
            text = [""]
            text.append(self.writer.text)

            # enqueue the frames
            self.all_frames.append(frame)
            if self.writer.write == True:
                self.video_frames.append(frame)

            self.send_data(frame, text)

            self.fps.update()

            if self.check_exit():
                video_stream.stop()
                break
        
        
    def _convert_image_to_jpeg(self, image):
        """Converts a numpy array image to JPEG

        Args:
            image (numpy array): The input image

        Returns:
            string: base64 encoded representation of the numpy array
        """
        # Encode frame as jpeg
        frame = cv2.imencode('.jpg', image)[1].tobytes()
        # Encode frame in base64 representation and remove
        # utf-8 encoding
        frame = base64.b64encode(frame).decode('utf-8')
        return "data:image/jpeg;base64,{}".format(frame)

    def send_data(self, frame, text):
        """Sends image and text to the flask server.

        Args:
            frame (numpy array): the image
            text (string): the text
        """
        cur_t = time.time()
        if cur_t - self._last_update_t > self._wait_t:
            self._last_update_t = cur_t
            frame = edgeiq.resize(
                    frame, width=640, height=480, keep_scale=True)
            socketio.emit(
                    'server2web',
                    {
                        'image': self._convert_image_to_jpeg(frame),
                        'text': '<br />'.join(text)
                    })
            socketio.sleep(0.0001)

    def check_exit(self):
        """Checks if the writer object has had
        the 'close' variable set to True.

        Returns:
            boolean: value of 'close' variable
        """
        return self.writer.close

    def close(self):
        """Disconnects the cv client socket.
        """
        self.exit_event.set()

class Controller(object):
    def __init__(self):
        self.write = False
        self.fps = edgeiq.FPS()
        self.cvclient = CVClient(self.fps, threading.Event())

    def start(self):
        self.cvclient.start()
        print('[INFO] Starting server at http://localhost:5000')
        socketio.run(app=app, host='0.0.0.0', port=5000)

    def close(self):
        self.fps.stop()
        print("elapsed time: {:.2f}".format(self.fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(self.fps.compute_fps()))

        if self.cvclient.is_alive():
            self.cvclient.close()
            self.cvclient.join()

        print("Program Ending")

    def close_writer(self):
        self.cvclient.writer.close = True

    def start_writer(self):
        self.cvclient.writer.write = True

    def stop_writer(self):
        self.cvclient.writer.write = False

    def is_writing(self):
        return self.cvclient.writer.write

    def update_text(self, text):
        self.cvclient.writer.text = text

controller = Controller()

if __name__ == "__main__":
    try:
        controller.start()
    finally:
        controller.close()
