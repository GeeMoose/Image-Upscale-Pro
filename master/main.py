from flask import Flask
from flask import request
from flask import send_file, jsonify

from flask_cors import CORS

from subprocess import check_call
from PIL import Image

from constants import *
from instance import *
from figure import figure_inference
from logsConfig import configure_logging

import os, base64
import logging
import requests

app = Flask(__name__)
CORS(app)

# Set up logging module
configure_logging()

logger = logging.getLogger(__name__)

# 批处理超分
def folder_upscale_image():
    return 

# 双倍超分
def double_upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs):
    arguments =getSingleImageArguments(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
    logger.info('INFO: Upscale Image has ready to invoke at first time.')
    logger.debug('DEBUG: Upscale Image has ready to invoke at first time.')
    ret = check_call(spawnUpscaling(COMMANDS,arguments))
    logger.info('INFO: Upscale Image has been invoked at first time.')
    logger.debug('DEBUG: Upscale Image has been invoked at first time.')
    if ret != 0:
        logger.error("ERROR: Double Upscale Image has happened CalledProcessError."
                     "errors have happened on first time")
        return jsonify({'errors': 'Double Upscale Image CalledProcessError： '+ ret})
    arguments =getDoubleUpscaleSecondPassArguments(outFile,modelsPath,model,scale,gpuid,saveImageAs)
    logger.info('INFO: Upscale Image has ready to invoke at second time.')
    logger.debug('DEBUG: Upscale Image has ready to invoke at second time.')
    ret = check_call(spawnUpscaling(COMMANDS,arguments))
    logger.info('INFO: Upscale Image has been invoked at second time.')
    logger.debug('DEBUG: Upscale Image has been invoked at second time.')
    if ret != 0:
        logger.error("ERROR: Double Upscale Image has happened CalledProcessError."
                     "errors have happened on second time")
        return jsonify({'errors': 'Double Upscale Images SecondPass CalledProcessError：'+ ret})

# 超分
def upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs):
    arguments =getSingleImageArguments(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
    logger.info('INFO: Upscale Image has ready to invoke.')
    logger.debug('DEBUG: Upscale Image has ready to invoke.')
    ret = check_call(spawnUpscaling(COMMANDS,arguments))
    logger.info('INFO: Upscale Image has been invoked.')
    logger.debug('DEBUG: Upscale Image has been invoked.')
    if ret != 0 :
        logger.error("ERROR: Upscale Image has happened CalledProcessError.")
        return jsonify({'errors': 'Upscale Image CalledProcessError： '+ ret})
    

def getDoubleUpscaleSecondPassArguments(outFile,modelsPath,model,scale,gpuid,saveImageAs):
    return [
    "-i",
    outFile,
    "-o",
    outFile,
    "-s",
    scale,
    "-m",
    modelsPath,
    "-n",
    model,
    "-g",
    gpuid,
    "-f",
    saveImageAs,
  ]
    
def getSingleImageArguments(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs):
    return [
    "-i",
    inputDir + SLASH + fullfileName,
    "-o",
    outFile,
    "-s",
    scale,
    "-m",
    modelsPath,
    "-n",
    model,
    "-g",
    gpuid,
    "-f",
    saveImageAs,
  ]

def spawnUpscaling(commands,arguments):
    args = ','.join([arg for arg in arguments])
    executor = commands + ',' + args
    return executor.split(',')

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
            logger.info(f'图片已成功保存为 {filename}')
        return True
    else:
        logger.error(f'下载图片时出错，地址: {url} 状态码：{response.status_code}')
        return False


@app.route('/')
def index():
    return "Editing Image Test"

@app.route('/image-upscaling', methods=['GET','POST'])
def imageUpscaling():
    if request.method == 'GET':
        return "Upscaling Image Test"
    if request.method == 'POST':
        # 如果ImageFile没有上传文件
        if request.files.get('ImageFile')  == None and request.json.get('imageUrl') == "":
            logger.error("ERROR: uploaded ImageFile has not been found."
                         "Unable to do subsequent operations")
            return jsonify({'errors': 'ImageFile does not meet specifications'})
        # 按照form-data的格式上传
        elif request.files.get('ImageFile')  != None:
            file_obj = request.files['ImageFile']
            # 如果ImageFile上传文件不符合规范
            if file_obj != None and file_obj.filename != "":
                fullfileName = file_obj.filename
                file_name,file_ext =  os.path.splitext(fullfileName)
                file_obj.save(inputDir + SLASH + fullfileName)
                imagePath = inputDir + SLASH + file_obj.filename
                model = request.form.get('model')
                imgScale = request.form.get('scale')
                saveImageAs =  file_ext[1:]
                # TODO: 到底要不要alpha channel
                outFile = outputDir + SLASH + file_name + "_upscaling_" + imgScale + "x_" + model + "." + saveImageAs
                if model == FIGURE_MODEL or model == FIGURE_PRO_MODEL :
                    logger.info('INFO: UPSACLE IMAGE CONTAINS FIGURE. '
                                'USES FIGURE INFERENCE')
                    logger.debug('DEBUG: UPSACLE IMAGE CONTAINS FIGURE. '
                                'USES FIGURE INFERENCE')
                    inputImg = inputDir + SLASH + fullfileName
                    _, outFile = figure_inference(inputImg, outFile, modelsPath, FIGURE_BACKGROUND_MODEL, model, imgScale, gpuid, saveImageAs)
                    
                elif int(imgScale) > DELIMITER:
                    # 双倍超分
                    # double_upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
                    upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)

                    # 8x 缩放
                    if imgScale != DOUBLEUPSCALEFSCALEFACTOR:
                        origin_im = Image.open(imagePath)
                        upscale_im = Image.open(outFile)
                        logger.info('INFO: UPSACLE IMAGE 6x,8x RESIZE LESS THAN 16.')
                        logger.debug('DEBUG: UPSACLE IMAGE 6x,8x RESIZE LESS THAN 16.')
                        new_upscale_im = upscale_im.resize((origin_im.size[0] * int(imgScale), origin_im.size[1] * int(imgScale)))
                        new_upscale_im.save(outFile)
               
                else:
                    upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
                    # 2x、3x 缩放
                    # e.g. '2' < '3' '3' <  '4'
                    if imgScale < scale:
                        origin_im = Image.open(imagePath)
                        upscale_im = Image.open(outFile)
                        logger.info('INFO: UPSACLE IMAGE 2x,3x RESIZE LESS THAN 4.')
                        logger.debug('DEBUG: UPSACLE IMAGE 2x,3x RESIZE LESS THAN 4.')
                        new_upscale_im = upscale_im.resize((origin_im.size[0] * int(imgScale), origin_im.size[1] * int(imgScale)))
                        new_upscale_im.save(outFile)

                with open(outFile, "rb") as img_file:
                    Response = base64.b64encode(img_file.read())
                    logger.info('INFO: RETURN THE RESPONSE FOR UPSCALING')
                    logger.debug('DEBUG: RETURN THE RESPONSE FOR UPSCALING')
                    return Response
        
            logger.error("ERROR: uploaded ImageFile format has not been satisified."
                            "The Problem is file_obj == None or file_obj.filename == \"\" ")
        
        # 按照json raw data格式上传
        elif request.json.get('imageUrl') != "":
            imageUrl = request.json.get('imageUrl') 
            model = request.json.get('model')
            imgScale = request.json.get('scale')
            fullfileName = imageUrl.split('/')[-1]
            # 正确解析imageUrl的话
            if fullfileName != "":
                file_name,file_ext =  os.path.splitext(fullfileName)
                # 原始图片保存地址
                imagePath = inputDir + SLASH + fullfileName
                if download_image(imageUrl,imagePath) != True:
                    return jsonify({'errors': 'Downloading image failed through imageUrl'})
                saveImageAs =  file_ext[1:]
                # TODO: 到底要不要alpha channel
                outFile = outputDir + SLASH + file_name + "_upscaling_" + imgScale + "x_" + model + "." + saveImageAs
                if model == FIGURE_MODEL or model == FIGURE_PRO_MODEL :
                    logger.info('INFO: UPSACLE IMAGE CONTAINS FIGURE. '
                                'USES FIGURE INFERENCE')
                    logger.debug('DEBUG: UPSACLE IMAGE CONTAINS FIGURE. '
                                'USES FIGURE INFERENCE')
                    inputImg = inputDir + SLASH + fullfileName
                    _, outFile = figure_inference(inputImg, outFile, modelsPath, FIGURE_BACKGROUND_MODEL, model, imgScale, gpuid, saveImageAs)
                    
                elif int(imgScale) > DELIMITER:
                    # 双倍超分
                    # double_upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
                    upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
                    # 8x 缩放
                    if imgScale != DOUBLEUPSCALEFSCALEFACTOR:
                        origin_im = Image.open(imagePath)
                        upscale_im = Image.open(outFile)
                        logger.info('INFO: UPSACLE IMAGE 6x,8x RESIZE LESS THAN 16.')
                        logger.debug('DEBUG: UPSACLE IMAGE 6x,8x RESIZE LESS THAN 16.')
                        new_upscale_im = upscale_im.resize((origin_im.size[0] * int(imgScale), origin_im.size[1] * int(imgScale)))
                        new_upscale_im.save(outFile)
                
                else:
                    upscale_image(inputDir,fullfileName,outFile,modelsPath,model,scale,gpuid,saveImageAs)
                    # 2x、3x 缩放
                    # e.g. '2' < '3' '3' <  '4'
                    if imgScale < scale:
                        origin_im = Image.open(imagePath)
                        upscale_im = Image.open(outFile)
                        logger.info('INFO: UPSACLE IMAGE 2x,3x RESIZE LESS THAN 4.')
                        logger.debug('DEBUG: UPSACLE IMAGE 2x,3x RESIZE LESS THAN 4.')
                        new_upscale_im = upscale_im.resize((origin_im.size[0] * int(imgScale), origin_im.size[1] * int(imgScale)))
                        new_upscale_im.save(outFile)

                with open(outFile, "rb") as img_file:
                    Response = base64.b64encode(img_file.read()).decode('utf-8')
                    logger.info('INFO: RETURN THE RESPONSE FOR UPSCALING')
                    logger.debug('DEBUG: RETURN THE RESPONSE FOR UPSCALING')
                    return {"result":f"data:image/{saveImageAs};base64,{Response}"}

            logger.error("ERROR: parse obtained imageUrl has not been satisified."
                    "The Problem is fullfileName == \"\" ")


        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)


     
# def main():
    
#     # instants实例
#     # commands args参数组合
#     file_name, _ =  os.path.splitext(fullfileName)
#     inputImg = inputDir + SLASH + "images.jpg"
#     generalModel = 'RealESRGAN_x2plus.pth'
#     figureModel = 'GFPGANv1.4.pth'
#     outFile = outputDir + SLASH + "images" + "_upscaling_" + scale + "x_" + figureModel + "." + saveImageAs
#     figure_inference(inputImg, outFile, modelsPath, generalModel, figureModel, scale, gpuid, saveImageAs)
#     return


# if __name__ == '__main__' :
#     main()
