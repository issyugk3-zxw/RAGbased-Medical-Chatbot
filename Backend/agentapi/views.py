from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from http import HTTPStatus
import os
import uuid
from datetime import datetime
import json
import dashscope
from Models.CustomLLM import VoiceDataTransfer
import re
from typing import Dict, List, Tuple
import requests
from Models import analyzer
# Create your views here.

def process_transcription_result(transcription_url: str) -> Tuple[str, Dict[str, int]]:

    response = requests.get(transcription_url)
    data = response.json()
    
    if 'transcripts' not in data:
        return "", {}

    full_text = ""
    emotion_counts = {}
    
    for transcript in data['transcripts']:
        text = transcript.get('text', '')
        
        speech_parts = re.findall(r'<\|Speech\|>(.*?)<\|/Speech\|>', text)
        full_text += ' '.join(speech_parts)

        emotion_tags = re.findall(r'<\|([^|>]+)\|>', text)
        for tag in emotion_tags:
            if tag not in ['Speech', '/Speech', 'BGM', '/BGM']:
                emotion_counts[tag] = emotion_counts.get(tag, 0) + 1
    
    return full_text.strip(), emotion_counts

@csrf_exempt
def transcribe_audio(request):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)
    

    audio_file = request.FILES.get('audio')
    
    if not audio_file:
        return JsonResponse({'error': '未找到音频文件'}, status=400)
    

    chat_id = request.POST.get('chatId', '')
    # chat_{chat_id}_{timestamp}_{random_uuid}.mp3
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位作为唯一标识
    if chat_id:
        filename = f"chat_{chat_id}_{timestamp}_{unique_id}.mp3"
    else:
        filename = f"audio_{timestamp}_{unique_id}.mp3"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "../resource/tmp")
    os.makedirs(target_dir, exist_ok=True)
    

    file_path = os.path.join(target_dir, filename)
    print(file_path)

    with open(file_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    file_url = VoiceDataTransfer.upload(filename)
    dashscope.api_key = 'sk-e9254bb01b1840c4b42c0e23f9f3d39c'
    task_response = dashscope.audio.asr.Transcription.async_call(
        model='sensevoice-v1',
        file_urls=[file_url],
        language_hints=['zh'],
    )

    transcribe_response = dashscope.audio.asr.Transcription.wait(task=task_response.output.task_id)
    if transcribe_response.status_code == HTTPStatus.OK:
        print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
        print('transcription done!')
        
        # 获取转写结果URL
        if transcribe_response.output.get('results'):
            transcription_url = transcribe_response.output['results'][0].get('transcription_url')
            if transcription_url:
                processed_text, emotion_stats = process_transcription_result(transcription_url)
                return JsonResponse({
                    'success': True,
                    'query': processed_text,
                    'emotion_stats': emotion_stats
                })
        return JsonResponse({
            'success': True,
            'query': transcribe_response.output,
            'emotion_stats': {}
        })
    
    return JsonResponse({'error': True}, status=500)



@csrf_exempt
def download_pdf(request):
    if request.method != 'GET':
        return JsonResponse({'error': '只支持GET请求'}, status=405)
    
    userid = request.GET.get('userid', '')
    sessionid = request.GET.get('sessionid', '')
    
    if not userid or not sessionid:
        return JsonResponse({'error': 'userid和sessionid不能为空'}, status=400)
    
    file_path = analyzer.get_report(userid, sessionid)
    
    if not file_path:
        return JsonResponse({'error': '报告生成失败'}, status=500)
    
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    
    
