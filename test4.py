# -*- coding: UTF-8 -*-
import BaiduAI.EasyEdge as edge
import cv2
import logging
import numpy as np
import os
import ffmpeg
import numpy
import cv2
import urllib.request
import urllib.parse
import base64
import json

edge.Log.set_level(logging.DEBUG)
edge.set_auth_license_key("5337-70C4-FF0A-D00D")
#RES
model_dir='/home/daquan/temp/EasyEdge-Linux-m25517-b69804-x86/RES'


# 读取帧 解析并且画框
def read_frame_and_draw_box(in_file, frame_num, stream, width, height):
    pred = edge.Program()
    pred.init(model_dir=model_dir, device=edge.Device.CPU,
              engine=edge.Engine.PADDLE_FLUID)
    # 指定帧数读取任意帧
    out, err = (
        ffmpeg.input(in_file)
            .filter('select', 'gte(n,{})'.format(frame_num))
            .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
            .run(capture_stdout=True)
    )
    # 输出图片 解析
    image_array = numpy.asarray(bytearray(out), dtype="uint8")
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    #阀值为0.1
    res = pred.infer_image(image, threshold=0.1)
    for r in res:
        if pred.model_type == edge.c.ModelType.ObjectDetection:
            # 画框
            stream = ffmpeg.drawbox(stream, int(r['x1'] * width), int(r['y1'] * height),
                                    int((r['x2'] - r['x1']) * width), int((r['y2'] - r['y1']) * height), color='red',
                                    thickness=3)
        elif pred.model_type == edge.c.ModelType.ImageSegmentation:
            print("图像切割!!!")
        # print(r)
        print("\033[1;31m" + str(r) + "\033[0m \n")
    pred.close()
    return stream


def test(input, output):
    info = ffmpeg.probe(input)
    vs = next(c for c in info['streams'] if c['codec_type'] == 'video')
    num_frames = int(vs['nb_frames']) / 10
    height = vs['height']
    width = vs['width']
    in_file = ffmpeg.input(input)
    f = open("filelist.txt", 'w')

    for i in range(int(num_frames / 20) + 1):
        startTime = i * 20
        endTime = (1 + i) * 20
        if endTime >= int(num_frames):
            endTime = int(num_frames)
        # more more
        print("开始" + str(startTime))
        print("结束" + str(endTime))
        stream = ffmpeg.trim(in_file, start_frame=startTime, end_frame=endTime).setpts('PTS-STARTPTS')
        stream = read_frame_and_draw_box('test.mp4', startTime + (endTime - startTime) / 2, stream, width, height)  # 解析
        stream = ffmpeg.output(stream, 'tmp/out' + str(i) + '.mp4')
        ffmpeg.run(stream, overwrite_output=True)
        f.write('file \'tmp/out' + str(i) + '.mp4\'\n')

    f = os.popen('ffmpeg -y -f concat -i filelist.txt -c copy ' + output)
    shuchu = f.read()
    f.close()
    print(shuchu)


if __name__ == '__main__':
    test("test2.mp4", "out.mp4")
