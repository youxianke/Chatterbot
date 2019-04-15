import time
import pygame
import speech_recognition as sr
from aip import AipSpeech
import requests
import json


# 百度语音API参数，请根据自己的参数修改
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''


# 图灵机器人API参数，请修改为自己的参数
TURING_KEY = ""
URL = "http://openapi.tuling123.com/openapi/api/v2"
HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}

# 定义保存通过百度语音接口将文字转换为语音的五个语音文件，为什么这么干？
# 主要是发现如果用一个语音文件，再下一次对话的时候，容易发生读写权限错误
file_name = ['audio1.mp3', 'audio2.mp3', 'audio3.mp3', 'audio4.mp3', 'audio5.mp3']
file_index = 0
voice_text = ""   # 定义一个全局变量，保存语音转换文字的结果


# 使用SpeechRecognition进行录音
def rec(rate=16000):             # 百度语音接口只支持8K和16K采样，支持pcm和wav格式
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:
        print("您请说！！！")
        audio = r.listen(source)

    with open("recording.wav", "wb") as f:
        f.write(audio.get_wav_data())


# 调用百度语音进行语音->文字转换
def voice_to_text():
    with open('recording.wav', 'rb') as f:
        audio_data = f.read()

    result = client.asr(audio_data, 'wav', 16000, {
        'dev_pid': 1536,
    })

    # voice_text = result["result"][0]
    # print("您刚才说的是: " + voice_text)
    # return voice_text

    # 这里建议不要按照上面三行代码直接提取文字，因为网络返回可能会有错误

    error_msg = result["err_msg"]
    if error_msg == "success.":
        global voice_text
        voice_text = result["result"][0]
        print("您刚才说的是: " + voice_text)
        return True
    else:
        print("error_msg: " + error_msg)
        return False


# 调用图灵机器人进行对话
def tuning_robot(text=""):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": ""
            },
            "selfInfo": {
                "location": {
                    "city": "哈尔滨",
                    "street": "文兴路"
                }
            }
        },
        "userInfo": {
            "apiKey": TURING_KEY,
            "userId": "12345678"  # 这个值可以自己定义，不要超过32位
        }
    }

    data["perception"]["inputText"]["text"] = text
    response = requests.request("post", URL, json=data, headers=HEADERS)
    response_dict = json.loads(response.text)

    result = response_dict["results"][0]["values"]["text"]
    print("机器人说: " + result)
    return result


# 百度语音接口将文字合成语音
def text_to_voice(filename, text="",):
    result = client.synthesis(text, 'zh', 1, {
        'spd': 4,
        'vol': 5,
        'per': 4,
    })

    if not isinstance(result, dict):
        with open(filename, 'wb') as f:
            f.write(result)
            f.close()


# 使用pygame模块播放语音
def play(filename):
    # filename = r'audio.mp3'
    pygame.mixer.init(frequency=16500)
    # 载入音乐文件
    pygame.mixer.music.load(filename)
    # 保存当前音量
    v = pygame.mixer.music.get_volume()
    # 设置为静音，防止开始的爆破音
    pygame.mixer.music.set_volume(0)
    # 播放声音
    pygame.mixer.music.play()
    # 延时0.01秒打开声音，避过爆破音
    pygame.time.delay(10)
    # 恢复音量
    pygame.mixer.music.set_volume(v)
    # 播放10秒钟
    # pygame.time.delay(1000 * 10)

    while pygame.mixer.music.get_busy():
        time.sleep(1)
    # 停止播放
    pygame.mixer.music.stop()
    # 退出声音库和显示库
    pygame.mixer.quit()


if __name__ == "__main__":

    # 定义一个百度语音API的接口对象
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    while True:
        if file_index == 5:
            file_index = 0

        now_file_name = file_name[file_index]

        rec()

        if voice_to_text():
            # print("发送给机器人：" + voice_text)
            robot_said = tuning_robot(voice_text)
            text_to_voice(now_file_name, robot_said)
            play(now_file_name)
        else:
            print("不好意思，刚才没听清，请您再说一遍！！！")
            text_to_voice(now_file_name, "不好意思，刚才没听清，请您再说一遍")
            play(now_file_name)

        file_index = file_index + 1
