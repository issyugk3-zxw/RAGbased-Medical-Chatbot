import oss2
import os
from http import HTTPStatus
import dashscope
import json

class VoiceTransfer:
    def __init__(self):
        self.access_key_id = 'put your access key id here'
        self.access_key_secret = 'put your access key secret here'
        self.bucket_name = "put your bucket name here"
        self.endpoint = "put your endpoint here"
        self.bucket = oss2.Bucket(oss2.Auth(self.access_key_id, self.access_key_secret), self.endpoint, self.bucket_name)

    def upload(self, file_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "../../resource/tmp", file_name), "rb") as f:
            data = f.read()
        self.bucket.put_object(f'voicedata/{file_name}', data)
        file_url = self.bucket.sign_url('GET', f'voicedata/{file_name}', 60 * 60 * 24)
        return  file_url



if __name__ == "__main__":
    vt = VoiceTransfer()
    file_url = vt.upload("test.mp3")
    dashscope.api_key = 'put your api key here'
    task_response = dashscope.audio.asr.Transcription.async_call(
        model='sensevoice-v1',
        file_urls=[file_url],
        language_hints=['zh'],
    )

    transcribe_response = dashscope.audio.asr.Transcription.wait(task=task_response.output.task_id)
    if transcribe_response.status_code == HTTPStatus.OK:
        print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
        print('transcription done!')