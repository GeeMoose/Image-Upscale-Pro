# Image-Upscale
running the image upscale for the various upscaling algorithms

## See the Link , See the community more
[Upscale Community](https://openmodeldb.info/)
不同场景下的增强画质模型，支持不同的商业用途！

## download models
一些模型的size 比较大，上传会显示失败！在部署前的预处理先下载这些模型，并存放指定路径。

**人脸超分模型：**

[GFPGANv1.3.pth](https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth) 

[GFPGANv1.4.pth](https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth)

**检测人脸模型：**

detection_Resnet50_Final.pth 

parsing_parsenet.pth

## Dir Construct

```code
Image-Upscale/
|
|-- assets/                         # Directory to store assets
|-- bin/                            # Directory for image-upscale executor
|-- master/                         # Directory for main processors
|   |-- figure                      # Preprocessing functions and utilities
|   |-- |-- figureInference.py      # Figure model processing scripts 
|   |-- gfpgan                      # Detect figure basic model
|   |-- |-- weights                 # Repo for face weights model
|   |-- |-- |-- detection_Resnet50_Final.pth # Detect protrait 
|   |-- |-- |-- parsing_parsenet.pth         # Parsing protrait
|   |-- constants.py                # File contains all default constants
|   |-- instance.py                 # Input args test file
|   |-- logsConfig.py               # Logs config file
|   |-- main.py                     # main file
|
|-- models/                         # Directory for saving all models
|
|-- output/                         # Directory for output image file
|-- .gitignore                      # not uploaded file or dir
|-- LICENSE                         # MIT LICENSE
|-- README.md                       # Project documentation and instructions
|-- requirements.txt                # List of dependencies and required libraries

```

## LOGGING MODULE

master/constants.py的 DEBUG_MODE 决定日志是否开启debug模式
