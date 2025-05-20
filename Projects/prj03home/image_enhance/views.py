import sys
import os
import torch
import numpy as np
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import cv2
import torch.nn.functional as F
from torchvision.transforms import ToTensor, ToPILImage
import random
from torchvision.transforms.functional import rgb_to_grayscale

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nafnet_dir = os.path.join(BASE_DIR, 'NAFNet')
if nafnet_dir not in sys.path:
    sys.path.insert(0, nafnet_dir)

# NAFNet 모델 정의
class NAFBlock(torch.nn.Module):
    def __init__(self, c, DW_Expand=2, FFN_Expand=1, drop_out_rate=0.):
        super().__init__()
        dw_channel = c * DW_Expand
        self.conv1 = torch.nn.Conv2d(in_channels=c, out_channels=dw_channel, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.conv2 = torch.nn.Conv2d(in_channels=dw_channel, out_channels=dw_channel, kernel_size=3, padding=1, stride=1, groups=dw_channel, bias=True)
        self.conv3 = torch.nn.Conv2d(in_channels=dw_channel//2, out_channels=c, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        
        # Channel Attention (SCA)
        self.sca = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Conv2d(in_channels=dw_channel//2, out_channels=dw_channel//2, kernel_size=1, padding=0, stride=1, groups=1, bias=True),
            torch.nn.Sigmoid()
        )

        # FFN
        self.conv4 = torch.nn.Conv2d(in_channels=c, out_channels=c*FFN_Expand, kernel_size=1, padding=0, stride=1, groups=1, bias=True)
        self.conv5 = torch.nn.Conv2d(in_channels=c*FFN_Expand, out_channels=c, kernel_size=1, padding=0, stride=1, groups=1, bias=True)

        self.norm1 = torch.nn.LayerNorm(c)
        self.norm2 = torch.nn.LayerNorm(c)

        self.dropout1 = torch.nn.Dropout(drop_out_rate) if drop_out_rate > 0. else torch.nn.Identity()
        self.dropout2 = torch.nn.Dropout(drop_out_rate) if drop_out_rate > 0. else torch.nn.Identity()

        self.beta = torch.nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
        self.gamma = torch.nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)

    def forward(self, inp):
        x = inp

        x = self.norm1(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = torch.sigmoid(x)
        x = x * self.conv3(x)
        x = self.sca(x)
        x = self.dropout1(x)
        y = inp + x * self.beta

        x = self.conv4(self.norm2(y))
        x = torch.sigmoid(x)
        x = self.conv5(x)
        x = self.dropout2(x)
        return y + x * self.gamma

class NAFNet(torch.nn.Module):
    def __init__(self, img_channel=3, width=16, middle_blk_num=1, enc_blk_nums=[], dec_blk_nums=[]):
        super().__init__()

        self.intro = torch.nn.Conv2d(in_channels=img_channel, out_channels=width, kernel_size=3, padding=1, stride=1, groups=1, bias=True)
        self.ending = torch.nn.Conv2d(in_channels=width, out_channels=img_channel, kernel_size=3, padding=1, stride=1, groups=1, bias=True)

        self.encoders = torch.nn.ModuleList()
        self.decoders = torch.nn.ModuleList()
        self.middle_blks = torch.nn.ModuleList()
        self.ups = torch.nn.ModuleList()
        self.downs = torch.nn.ModuleList()

        chan = width
        for num in enc_blk_nums:
            self.encoders.append(
                torch.nn.Sequential(
                    *[NAFBlock(chan) for _ in range(num)]
                )
            )
            self.downs.append(
                torch.nn.Conv2d(chan, 2*chan, 2, 2)
            )
            chan = chan * 2

        self.middle_blks = \
            torch.nn.Sequential(
                *[NAFBlock(chan) for _ in range(middle_blk_num)]
            )

        for num in dec_blk_nums:
            self.ups.append(
                torch.nn.Sequential(
                    torch.nn.Conv2d(chan, chan * 2, 1, bias=False),
                    torch.nn.PixelShuffle(2)
                )
            )
            chan = chan // 2
            self.decoders.append(
                torch.nn.Sequential(
                    *[NAFBlock(chan) for _ in range(num)]
                )
            )

        self.padder_size = 2 ** len(self.encoders)

    def forward(self, inp):
        B, C, H, W = inp.shape
        inp = self.check_image_size(inp)

        x = self.intro(inp)

        encs = []

        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)

        x = self.middle_blks(x)

        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)

        x = self.ending(x)
        x = x + inp

        return x[:, :, :H, :W]

    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))
        return x

# 모델 초기화
def create_model():
    model = NAFNet(
        img_channel=3,
        width=32,
        middle_blk_num=12,
        enc_blk_nums=[2, 2, 4, 8],
        dec_blk_nums=[2, 2, 2, 2]
    )
    return model

def convert_checkpoint(ckpt):
    """Convert checkpoint to match the original model structure"""
    new_ckpt = {}
    for k, v in ckpt.items():
        if 'sca' in k:
            # Convert sca to se
            new_k = k.replace('sca', 'se')
            new_ckpt[new_k] = v
        elif 'conv5.weight' in k:
            # Expand channels for FFN
            old_shape = v.shape
            new_shape = (old_shape[0] * 2, old_shape[1] * 2, old_shape[2], old_shape[3])
            new_v = torch.zeros(new_shape)
            new_v[:old_shape[0], :old_shape[1]] = v
            new_ckpt[k] = new_v
        else:
            new_ckpt[k] = v
    return new_ckpt

# 전역 변수로 모델 저장
model = None

def image_enhance_view(request):
    return render(request, 'image_enhance/image_enhance.html')

@csrf_exempt
def process_image(request):
    import logging
    import tempfile
    import shutil
    import subprocess
    from django.utils.crypto import get_random_string
    from django.conf import settings
    import os
    from django.http import JsonResponse
    import glob

    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            valid_ext = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
            ext = os.path.splitext(image_file.name)[-1].lower().replace('.', '')
            if ext not in valid_ext:
                return JsonResponse({'success': False, 'message': '지원하지 않는 이미지 형식입니다.'})
            if image_file.size > 10 * 1024 * 1024:
                return JsonResponse({'success': False, 'message': '이미지 파일 크기는 10MB 이하만 가능합니다.'})

            # demo.py 경로 및 NAFNet root 경로 정의 (최상단에 위치시켜 참조 오류 방지)
            demo_py = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NAFNet', 'basicsr', 'demo.py')
            nafnet_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NAFNet')

            # 임시폴더를 NAFNet/demo/enhance 하위로 지정
            enhance_dir = os.path.join(nafnet_root, 'demo', 'enhance')
            os.makedirs(enhance_dir, exist_ok=True)
            temp_dir = tempfile.mkdtemp(dir=enhance_dir)
            temp_input_path = os.path.join(temp_dir, f"input_{get_random_string(8)}.{ext}")
            temp_output_path = os.path.join(temp_dir, f"output_{get_random_string(8)}.{ext}")

            # 업로드 이미지는 원본 해상도 또는 70% 축소 중 선택 저장
            from PIL import Image as PILImage
            image_file.seek(0)
            img = PILImage.open(image_file)
            resize_mode = request.POST.get('resize_mode', 'original')
            if resize_mode == 'half':
                new_size = (max(1, int(img.width * 0.7)), max(1, int(img.height * 0.7)))
                img = img.resize(new_size, PILImage.LANCZOS)
            img.save(temp_input_path)
            resized_shape = img.size  # (width, height)

            # 옵션 파일 자동 탐색 (test > train, 알파벳순) + opt_name 파라미터 지원
            import yaml
            opt_candidates = []
            opt_name = request.POST.get('opt_name')
            for subdir in ['test', 'train']:
                search_path = os.path.join(nafnet_root, 'options', subdir, '**', '*.yml')
                opt_candidates.extend(sorted(glob.glob(search_path, recursive=True)))
            if opt_name:
                # opt_name이 포함된 옵션만 필터링
                opt_candidates = [p for p in opt_candidates if opt_name in os.path.basename(p)]
            else:
                # opt_name이 없으면 REDS-width32가 포함된 옵션을 최우선으로 사용
                reds32_opts = [p for p in opt_candidates if 'REDS-width32' in os.path.basename(p)]
                if reds32_opts:
                    opt_candidates = reds32_opts + [p for p in opt_candidates if p not in reds32_opts]
            selected_opt = None
            selected_model = None
            for opt_path in opt_candidates:
                # NAFSSR, StereoSR, stereo 등 스테레오 옵션은 제외
                base = os.path.basename(opt_path)
                if any(x in base.lower() for x in ['nafssr', 'stereosr', 'stereo']):
                    continue
                try:
                    with open(opt_path, 'r', encoding='utf-8') as f:
                        opt_yaml = yaml.safe_load(f)
                    desc = str(opt_yaml.get('name', base)).lower()
                    if any(x in desc for x in ['nafssr', 'stereosr', 'stereo']):
                        continue
                    pretrain_rel = opt_yaml.get('path', {}).get('pretrain_network_g')
                    if not pretrain_rel:
                        continue
                    if not os.path.isabs(pretrain_rel):
                        model_path = os.path.normpath(os.path.join(nafnet_root, pretrain_rel.replace('/', os.sep)))
                    else:
                        model_path = pretrain_rel
                    if os.path.exists(model_path):
                        selected_opt = opt_path
                        selected_model = model_path
                        break
                except Exception as ex:
                    continue
            if not selected_opt:
                shutil.rmtree(temp_dir)
                return JsonResponse({'success': False, 'message': '옵션 파일과 연결된 pretrained model(.pth) 파일이 NAFNet/experiments/pretrained_models/에 존재하지 않습니다. 모델 파일을 확인해 주세요.'})
            opt_path = selected_opt
            # demo.py가 참조하는 working directory를 nafnet_root로 강제 지정
            import sys
            python_exe = sys.executable  # 현재 가상환경의 python 경로 사용
            env = os.environ.copy()
            env['PYTHONPATH'] = nafnet_root + os.pathsep + env.get('PYTHONPATH', '')
            # 디버깅용 로그
            print(f"[DEBUG] 선택된 옵션 파일: {opt_path}")
            print(f"[DEBUG] 선택된 모델 파일: {selected_model}")
            command = [
                python_exe, demo_py,
                '-opt', opt_path,
                '--input_path', temp_input_path,
                '--output_path', temp_output_path
            ]
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True, env=env, cwd=nafnet_root)
            except subprocess.CalledProcessError as e:
                logging.exception('demo.py 실행 오류')
                shutil.rmtree(temp_dir)
                return JsonResponse({'success': False, 'message': f'demo.py 실행 오류: {e.stderr}\n[DEBUG] 옵션: {opt_path}\n[DEBUG] 모델: {selected_model}'})

            # 결과 이미지 MEDIA_ROOT로 이동
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if not media_root:
                media_root = os.path.join(BASE_DIR, 'media')
            elif not os.path.isabs(media_root):
                media_root = os.path.join(BASE_DIR, media_root)
            if not os.path.exists(media_root):
                os.makedirs(media_root, exist_ok=True)
            if not os.path.exists(temp_output_path):
                shutil.rmtree(temp_dir)
                return JsonResponse({'success': False, 'message': '이미지 개선 결과 파일이 생성되지 않았습니다.'})
            # 개선 결과도 입력(리사이즈본)과 동일한 크기로 강제 리사이즈
            output_fname = f"enhanced_{get_random_string(8)}_{image_file.name}"
            output_path = os.path.join(media_root, output_fname)
            try:
                out_img = PILImage.open(temp_output_path)
                if out_img.size != resized_shape:
                    out_img = out_img.resize(resized_shape, PILImage.LANCZOS)
                    out_img.save(output_path)
                    out_img.close()
                else:
                    out_img.close()
                    shutil.move(temp_output_path, output_path)
            except Exception:
                try:
                    out_img.close()
                except:
                    pass
                shutil.move(temp_output_path, output_path)
            shutil.rmtree(temp_dir)

            return JsonResponse({
                'success': True,
                'message': f'이미지가 성공적으로 처리되었습니다. (옵션: {os.path.relpath(opt_path, nafnet_root)})',
                'output_url': f'/media/{output_fname}'
            })
        except Exception as e:
            logging.exception('알 수 없는 오류')
            return JsonResponse({'success': False, 'message': f'이미지 처리 중 알 수 없는 오류가 발생했습니다: {str(e)}'})
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

@require_GET
def get_available_nafnet_options(request):
    import glob
    import yaml
    nafnet_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NAFNet')
    model_dir = os.path.join(nafnet_root, 'experiments', 'pretrained_models')
    opt_candidates = []
    for subdir in ['test', 'train']:
        search_path = os.path.join(nafnet_root, 'options', subdir, '**', '*.yml')
        opt_candidates.extend(sorted(glob.glob(search_path, recursive=True)))
    options = []
    for opt_path in opt_candidates:
        try:
            with open(opt_path, 'r', encoding='utf-8') as f:
                opt_yaml = yaml.safe_load(f)
            pretrain_rel = opt_yaml.get('path', {}).get('pretrain_network_g')
            if not pretrain_rel:
                continue
            if not os.path.isabs(pretrain_rel):
                model_path = os.path.normpath(os.path.join(nafnet_root, pretrain_rel.replace('/', os.sep)))
            else:
                model_path = pretrain_rel
            # NAFSSR, StereoSR, stereo 등 스테레오 옵션은 제외
            base = os.path.basename(opt_path)
            desc = str(opt_yaml.get('name', base)).lower()
            if any(x in base.lower() for x in ['nafssr', 'stereosr', 'stereo']) or any(x in desc for x in ['nafssr', 'stereosr', 'stereo']):
                continue
            if os.path.exists(model_path):
                options.append({
                    'opt_name': base,
                    'opt_path': os.path.relpath(opt_path, nafnet_root),
                    'model_path': os.path.relpath(model_path, nafnet_root),
                    'desc': opt_yaml.get('name', base)
                })
        except Exception:
            continue
    return JsonResponse({'options': options})

def circular_lowpass_kernel(cutoff, kernel_size, pad_to=0):
    """2D sinc filter, ref: https://dsp.stackexchange.com/questions/58301/2-d-circularly-symmetric-low-pass-filter
    """
    assert kernel_size % 2 == 1, 'Kernel size must be an odd number.'
    kernel = torch.zeros((kernel_size, kernel_size))
    kernel_center = kernel_size // 2
    for i in range(kernel_size):
        for j in range(kernel_size):
            di2, dj2 = (i - kernel_center) ** 2, (j - kernel_center) ** 2
            kernel[i, j] = torch.exp(-cutoff * (di2 + dj2))
    kernel = kernel / kernel.sum()
    if pad_to > kernel_size:
        pad_size = (pad_to - kernel_size) // 2
        kernel = torch.nn.functional.pad(kernel, (pad_size, pad_size, pad_size, pad_size))
    return kernel
