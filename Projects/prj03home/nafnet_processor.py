import sys
import os
import subprocess
from PIL import Image
import numpy as np

def resize_image(input_path):
    """이미지 크기를 원본의 50%로 조정합니다."""
    img = Image.open(input_path)
    
    # 원본 크기의 50%로 조정
    width, height = img.size
    new_width = width // 2
    new_height = height // 2
    
    # 32의 배수로 조정
    new_width = (new_width // 32) * 32
    new_height = (new_height // 32) * 32
    
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 리사이즈된 이미지 저장
    img.save(input_path)
    return input_path

def process_image(input_path, output_path):
    try:
        # 이미지 크기 조정
        input_path = resize_image(input_path)
        
        # 현재 작업 디렉토리 저장
        current_dir = os.getcwd()
        
        # NAFNet 디렉토리로 이동
        nafnet_dir = os.path.join(current_dir, 'NAFNet')
        os.chdir(nafnet_dir)
        
        try:
            # demo.py 실행 (GoPro 모델 사용)
            result = subprocess.run([
                'python',
                'basicsr/demo.py',
                '-opt', 'options/test/GoPro/NAFNet-width32.yml',  # GoPro 설정 파일 (width32)
                '--input_path', input_path,
                '--output_path', output_path,
                '--model_path', 'experiments/pretrained_models/NAFNet-GoPro-width32.pth'  # GoPro 모델 (width32)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Demo execution failed: {result.stderr}"
                
            return True, "Success"
        finally:
            # 원래 디렉토리로 복귀
            os.chdir(current_dir)
            
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python nafnet_processor.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    success, message = process_image(input_path, output_path)
    if not success:
        print(f"Error: {message}")
        sys.exit(1)
    print("Processing completed successfully") 