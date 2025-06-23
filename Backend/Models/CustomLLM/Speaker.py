from Models.CustomLLM.agent import Agent
import dashscope

class SpeakerAgent(Agent):
    def __init__(self):
        super(SpeakerAgent, self).__init__()

    def response(self, text):
        response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
            model="qwen-tts",
            api_key="put your api key here",
            text=text,
            voice="Cherry",
        )
        return response["output"]["audio"]["url"]