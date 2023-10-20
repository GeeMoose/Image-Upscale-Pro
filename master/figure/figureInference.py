import os
import cv2
# import gradio as gr
import torch
from basicsr.archs.srvgg_arch import SRVGGNetCompact
from basicsr.archs.rrdbnet_arch import RRDBNet
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer

SLASH  = "/" 

# 增强背景可使用RealESRGAN_x2plus.pth模型
def set_realesrgan(model_name, model_path):
    # device到底是GPU or CPU
    half=True if torch.cuda.is_available() else False
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
    return RealESRGANer(scale=2, model_path=model_path + SLASH + model_name, model=model, tile=400, tile_pad=10, pre_pad=0, half=half)

def set_figure_face_enhancer(upsampler, model, model_path):
    if model != 'RestoreFormer.pth':
        return GFPGANer(model_path=model_path + SLASH + model, upscale=2, arch='clean', channel_multiplier=2, bg_upsampler=upsampler)
    else:
        return GFPGANer(model_path=model_path + SLASH + model, upscale=2, arch='RestoreFormer', channel_multiplier=2, bg_upsampler=upsampler)
        

def figure_inference(input_img, outFile, models_path, general_model, figure_model, scale, gpuid, saveImageAs):
# def figure_inference(input_img, outFile, scale, model_path, model, gpuid, saveImageAs):
    # 根据已有的模型做输出
    scale = int(scale)
    
    try:
        # img_name = os.path.splitext(os.path.basename(str(input_img)))[0]
        # 图片模式分彩色和灰白两种
        img = cv2.imread(input_img, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 4:
            img_mode = 'RGBA'
        elif len(img.shape) == 2:  # for gray inputs
            img_mode = None
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_mode = None

        h, w = img.shape[0:2]
        if h > 5000 or w > 5000:
            print(f'origin image {input_img} is too large size')
            return None, None
        
        # FIX 过分小的图片要不要先做处理??
        # if h < 300 or w < 300:
        #     img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)

        bg_upsampler = set_realesrgan(general_model, models_path)
        face_enhancer = set_figure_face_enhancer(bg_upsampler, figure_model, models_path)
        
        try:
            _, _, output = face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True, weight=0.5)
        except RuntimeError as error:
            print('Error', error)

        try:
            if scale != 2:
                # 根据scale自适应调整
                interpolation = cv2.INTER_AREA if scale < 2 else cv2.INTER_LANCZOS4
                # h, w = img.shape[0:2]
                output = cv2.resize(output, (int(w * scale), int(h * scale)), interpolation=interpolation)
        except Exception as error:
            print('wrong scale input.', error)
        
        if img_mode == 'RGBA' and saveImageAs != 'png':  # RGBA images should be saved in png format
            saveImageAs = 'png'
            tmp = 0
            for i in range(len(outFile)-1,-1,-1):
                if outFile[i] == ".":
                    tmp = i
                    break
            if tmp > 0:
                outFile = outFile[0:tmp + 1] + saveImageAs
                print("outFile: ",outFile)

        cv2.imwrite(outFile, output)

        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output, outFile
    
    except Exception as error:
        return None, None
 

        
