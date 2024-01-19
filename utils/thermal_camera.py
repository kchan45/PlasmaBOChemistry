##################################################################################################################
# THERMAL CAMERA HELPERS
##################################################################################################################

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils.uvctypes import *
import time
import cv2
import numpy as np

try:
    from queue import Queue
except ImportError:
    from Queue import Queue
import platform

BUF_SIZE = 2
q = Queue(BUF_SIZE)


def py_frame_callback(frame, userptr):
    array_pointer = cast(
        frame.contents.data,
        POINTER(c_uint16 * (frame.contents.width * frame.contents.height)),
    )
    data = np.frombuffer(array_pointer.contents, dtype=np.dtype(np.uint16)).reshape(
        frame.contents.height, frame.contents.width
    )  # no copy

    # data = np.fromiter(
    #   frame.contents.data, dtype=np.dtype(np.uint8), count=frame.contents.data_bytes
    # ).reshape(
    #   frame.contents.height, frame.contents.width, 2
    # ) # copy

    if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
        return

    if not q.full():
        q.put(data)


PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)


def ktof(val):
    return 1.8 * ktoc(val) + 32.0


def ktoc(val):
    return (val - 27315) / 100.0


def raw_to_8bit(data):
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(data, 8, data)
    return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)


def display_temperature(img, val_k, loc, color):
    val = ktoc(val_k)
    return val
    # cv2.putText(img,"{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
    # x, y = loc
    # cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    # cv2.line(img, (x, y - 2), (x, y + 2), color, 1)


# def main():
# ctx = POINTER(uvc_context)()
# dev = POINTER(uvc_device)()
# devh = POINTER(uvc_device_handle)()
# ctrl = uvc_stream_ctrl()

# res = libuvc.uvc_init(byref(ctx), 0)
# if res < 0:
#   print("uvc_init error")
#   exit(1)

# try:
#   res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
#   if res < 0:
#     print("uvc_find_device error")
#     exit(1)

#   try:
#     res = libuvc.uvc_open(dev, byref(devh))
#     if res < 0:
#       print("uvc_open error")
#       exit(1)

#     print("device opened!")

#     print_device_info(devh)
#     print_device_formats(devh)

#     frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
#     if len(frame_formats) == 0:
#       print("device does not support Y16")
#       exit(1)

#     libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
#       frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
#     )

#     res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
#     if res < 0:
#       print("uvc_start_streaming failed: {0}".format(res))
#       exit(1)

#     try:
#       while True:
#         data = q.get(True, 500)
#         if data is None:
#           break
#         data = cv2.resize(data[:,:], (640, 480))
#         minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
#         img = raw_to_8bit(data)
#         display_temperature(img, minVal, minLoc, (255, 0, 0))
#         display_temperature(img, maxVal, maxLoc, (0, 0, 255))
#         cv2.imshow('Lepton Radiometry', img)
#         cv2.waitKey(1)

#       cv2.destroyAllWindows()
#     finally:
#       libuvc.uvc_stop_streaming(devh)

#     print("done")
#   finally:
#     libuvc.uvc_unref_device(dev)
# finally:
#   libuvc.uvc_exit(ctx)

# if __name__ == '__main__':
#   main()


def openThermalCamera():
    ctx = POINTER(uvc_context)()
    dev = POINTER(uvc_device)()
    devh = POINTER(uvc_device_handle)()
    ctrl = uvc_stream_ctrl()

    res = libuvc.uvc_init(byref(ctx), 0)
    if res < 0:
        print("uvc_init error")
        exit(1)

    try:
        res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
        if res < 0:
            print("uvc_find_device error")
            exit(1)

        try:
            res = libuvc.uvc_open(dev, byref(devh))
            if res < 0:
                print("uvc_open error")
                exit(1)

            print("device opened!")

            # print_device_info(devh)
            # print_device_formats(devh)

            frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
            if len(frame_formats) == 0:
                print("device does not support Y16")
                exit(1)

            libuvc.uvc_get_stream_ctrl_format_size(
                devh,
                byref(ctrl),
                UVC_FRAME_FORMAT_Y16,
                frame_formats[0].wWidth,
                frame_formats[0].wHeight,
                int(1e7 / frame_formats[0].dwDefaultFrameInterval),
            )

            res = libuvc.uvc_start_streaming(
                devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0
            )
            if res < 0:
                print("uvc_start_streaming failed: {0}".format(res))
                exit(1)

        # try:
        #   data = q.get(True, 500)
        #   data = cv2.resize(data[:,:], (640, 480))
        #   minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
        #   img = raw_to_8bit(data)
        #   Ts_max = display_temperature(img, maxVal, maxLoc, (0, 0, 255))
        #   Ts_min = display_temperature(img, minVal, minLoc, (255, 0, 0))
        # finally:
        #     pass
        #   libuvc.uvc_stop_streaming(devh)
        finally:
            pass
            # libuvc.uvc_unref_device(dev)
    finally:
        pass
        # libuvc.uvc_exit(ctx)

    return dev, ctx


def getSurfaceTemperature(save_spatial=False, save_image=False):
    data = q.get(True, 500)
    data = cv2.resize(data[:, :], (640, 480))
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
    img = raw_to_8bit(data)
    Ts_max = display_temperature(img, maxVal, maxLoc, (0, 0, 255))
    Ts_min = display_temperature(img, minVal, minLoc, (255, 0, 0))

    # get offset values of surface temperature (added 2021/03/18)
    # TODO: add spatial measurements to return values as desired
    # 2 pixels away
    n_offset1 = 2
    Ts2 = get_avg_spatial_temp(n_offset1, data, maxLoc)

    # 12 pixels away
    n_offset2 = 12
    Ts3 = get_avg_spatial_temp(n_offset2, data, maxLoc)

    if save_spatial and save_image:
        return Ts_max, (Ts2, Ts3), (data, img)
    elif save_spatial:
        return Ts_max, (Ts2, Ts3)
    elif save_image:
        return Ts_max, (data, img)
    else:
        return Ts_max


def get_avg_spatial_temp(n_pix, data, loc):
    """
    function to get the average temperature about a certain radius of the
    surface temperature. function gets the values from the four cardinal
    directions and returns the average value of those four values. while the
    function accounts for data out of the image bounds, the best practice is to
    make sure the measured area is near the center of the captured image

    Inputs:
    n_pix        number of pixels offset from the surface temperature measurement
    data        raw image data
    loc            location of the surface temperature measurement

    Outputs:
    avg_temp    average value of the temperature from measurements in the four
                cardinal directions
    """
    # extract the x and y values from the location
    maxX, maxY = loc
    # east
    if maxX + n_pix >= 640:
        maxValE = ktoc(data[maxY, maxX])
    else:
        maxValE = ktoc(data[maxY, maxX + n_pix])
    # west
    if maxX - n_pix < 0:
        maxValW = ktoc(data[maxY, maxX])
    else:
        maxValW = ktoc(data[maxY, maxX - n_pix])
    # south
    if maxY + n_pix >= 480:
        maxValS = ktoc(data[maxY, maxX])
    else:
        maxValS = ktoc(data[maxY + n_pix, maxX])
    # north
    if maxY - n_pix < 0:
        maxValN = ktoc(data[maxY, maxY])
    else:
        maxValN = ktoc(data[maxY - n_pix, maxX])

    avg_temp = (maxValE + maxValW + maxValN + maxValS) / 4
    return avg_temp


def closeThermalCamera(dev, ctx):
    libuvc.uvc_unref_device(dev)
    libuvc.uvc_exit(ctx)
