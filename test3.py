# encoding:utf-8
# 公有云api方式进行处理
import os
import ffmpeg
import numpy
import cv2
import urllib.request
import urllib.parse
import base64
import json

request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/detection/car0101"
access_token = '24.dcdc4fdcf38dd472c5566b9e97a73adb.2592000.1599453251.282335-21865104'


# easyDL 检测
def easydlObjectDetection(image, request_url):
    params = {"image": image}
    data = bytes(json.dumps(params), 'utf8')

    request_url = request_url + "?access_token=" + access_token

    request = urllib.request.Request(request_url, data)
    request.add_header('Content-Type', 'application/json')

    response = urllib.request.urlopen(request)
    content = json.loads(response.read().decode())
    if content:
        # 结果
        # print(content)
        return content


# 读取帧
def read_frame_as_jpeg(in_file, frame_num):
    """
    指定帧数读取任意帧
    """
    out, err = (
        ffmpeg.input(in_file)
            .filter('select', 'gte(n,{})'.format(frame_num))
            .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
            .run(capture_stdout=True)
    )
    # 输出图片转BASE64
    image_array = numpy.asarray(bytearray(out), dtype="uint8")
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    image = cv2.imencode('.jpg', image)[1]
    base64_data = str(base64.b64encode(image))[2:-1]
    content = easydlObjectDetection(base64_data, request_url)
    return content


def test(inputName, outputName):
    info = ffmpeg.probe(inputName)
    vs = next(c for c in info['streams'] if c['codec_type'] == 'video')
    num_frames = int(vs['nb_frames'])/5
    in_file = ffmpeg.input(inputName)
    f = open("filelist.txt", 'w')
    for i in range(int(num_frames / 20) + 1):
        startTime = i * 20
        endTime = (1 + i) * 20
        if endTime >= int(num_frames):
            endTime = int(num_frames)
        # more more
        # print("开始" + str(startTime))
        # print("结束" + str(endTime))
        content = read_frame_as_jpeg(inputName, startTime + (endTime - startTime) / 2)  # 解析
        stream = ffmpeg.trim(in_file, start_frame=startTime, end_frame=endTime).setpts('PTS-STARTPTS')
        # 解析并且画框
        for result in content['results']:
            # 画框
            stream = ffmpeg.drawbox(stream, result['location']['left'], result['location']['top'],
                                    result['location']['width'], result['location']['height'], color='red', thickness=3)
        # 输出到临时文件夹
        stream = ffmpeg.output(stream, 'tmp/out' + str(i) + '.mp4')
        ffmpeg.run(stream, overwrite_output=True)
        f.write('file \'tmp/out' + str(i) + '.mp4\'\n')

    f = os.popen('ffmpeg -y -f concat -i filelist.txt -c copy '+outputName)
    shuchu = f.read()
    f.close()
    print(shuchu)


if __name__ == '__main__':
    test("test2.mp4","out.mp4")