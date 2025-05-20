import os
import subprocess
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from PIL import Image
import io
import base64

@csrf_exempt
def process_image_view(request):
    if request.method == "POST":
        try:
            # 이미지 데이터 받기
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)
            
            # Base64 이미지 데이터를 파일로 저장
            image_data = image_data.split(',')[1]  # Remove data URL prefix
            image_bytes = base64.b64decode(image_data)
            
            # 임시 입력/출력 파일 경로 설정
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            input_path = os.path.join(temp_dir, 'input.jpg')
            output_path = os.path.join(temp_dir, 'output.jpg')
            
            # 입력 이미지 저장
            with open(input_path, 'wb') as f:
                f.write(image_bytes)
            
            # Python 스크립트 호출
            result = subprocess.run([
                'python',  # Python 인터프리터
                'nafnet_processor.py',  # 스크립트 경로
                input_path,
                output_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return JsonResponse({
                    'error': f'Processing failed: {result.stderr}'
                }, status=500)
            
            # 처리된 이미지 읽기
            with open(output_path, 'rb') as f:
                processed_image = f.read()
            
            # Base64로 인코딩
            processed_image_base64 = base64.b64encode(processed_image).decode('utf-8')
            
            # 임시 파일 삭제
            os.remove(input_path)
            os.remove(output_path)
            
            return JsonResponse({
                'status': 'success',
                'processed_image': f'data:image/jpeg;base64,{processed_image_base64}'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def index(request):
    return render(request, 'home/index.html') 