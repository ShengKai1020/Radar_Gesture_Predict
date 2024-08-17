
import time

import pyrealsense2 as rs
import numpy as np
from threading import Thread


# Configure depth and color streams
class RealSense:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.depth_image = None
        self.color_image = None
        self.start_stream = False

        # # Get device product line for setting a supporting resolution
        # pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        # pipeline_profile = self.config.resolve(pipeline_wrapper)
        # device = pipeline_profile.get_device()
        # device_product_line = str(device.get_info(rs.camera_info.product_line))
        #
        # found_rgb = False
        # for s in device.sensors:
        #     if s.get_info(rs.camera_info.name) == 'RGB Camera':
        #         found_rgb = True
        #         break
        # if not found_rgb:
        #     print("The demo requires Depth camera with Color sensor")
        #     exit(0)
        #
        # self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        #
        # if device_product_line == 'L500':
        #     self.config.enable_stream(rs.stream.color, 960, 540, rs.format.rgb8, 30)
        # else:
        #     self.config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)

    def start(self):
        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            self.config.enable_stream(rs.stream.color, 960, 540, rs.format.rgb8, 30)
        else:
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
        # Start streaming
        self.pipeline.start(self.config)
        self.start_stream = True
        T = Thread(target=self.getImageTread)
        T.start()

    def getImageTread(self):
        while self.start_stream:
            try:
                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    # self.depth_image = None
                    # self.color_image = None
                    continue
                # Convert images to numpy arrays
                self.depth_image = np.asanyarray(depth_frame.get_data())
                self.color_image = np.asanyarray(color_frame.get_data())
            except Exception as error:
                print(error)



    def getImage(self):
        # try:
        #     # Wait for a coherent pair of frames: depth and color
        #     frames = self.pipeline.wait_for_frames(timeout_ms=50)
        #     depth_frame = frames.get_depth_frame()
        #     color_frame = frames.get_color_frame()
        #     if not depth_frame or not color_frame:
        #         return None, None
        #     # Convert images to numpy arrays
        #     self.depth_image = np.asanyarray(depth_frame.get_data()).T
        #     self.color_image = np.asanyarray(color_frame.get_data())
        #
        #     return self.depth_image.T, self.color_image.transpose((1,0,2))[:,:,:]
        # except Exception as error:
        #     print(error)
        #     return None, None
        return self.depth_image.T, self.color_image.transpose((1, 0, 2))[:, :, :]

    def stop(self):
        # Stop streaming
        self.start_stream = False
        self.pipeline.stop()

if __name__ == '__main__':
    r = RealSense()
    r.start()
    while True:
        r.getImage()


