# OCR FastAPI

## 简介

本项目是一个基于 FastAPI 的 OCR API，用于从图像中提取文本，并将提取结果存储到 MySQL 数据库中。它支持多种 OCR 模型，并提供了易于使用的接口。

## 特性

-   支持 QWen2.5-VL-7B-Instruct 和 MiniCPM2.6-V-8B 模型
-   可以处理印刷体和手写体
-   忽略图像中被划掉或涂改的部分
-   支持通过 HTTP 接口上传图像或传递 base64 编码的图像数据
-   异步 OCR 处理，避免阻塞主线程
-   将图像来源、版面分析坐标和识别结果存储到 MySQL 数据库

## 依赖

-   fastapi
-   uvicorn
-   opencv-python
-   Pillow
-   pydantic
-   requests
-   ultralytics
-   mysql-connector-python
-   mysql: 5.7.42-0ubuntu0.18.04.1

## 数据库配置

本项目使用 MySQL 数据库存储 OCR 结果。请确保已安装 MySQL 数据库，并配置以下信息：

-   **主机**: `192.168.4.56`
-   **端口**: `3306`
-   **数据库名**: `xs_ocr_ret`
-   **用户名**: `root`
-   **密码**: `*******`
-   **测试表**: `my_test`

数据库表结构如下：

```sql
CREATE TABLE xs_ocr_ret (
    img_id INT AUTO_INCREMENT PRIMARY KEY,  # 图像 ID
    img_name VARCHAR(255), # 图像文件名
    url MEDIUMTEXT,  # 图像 base64 编码
    crop_box TEXT,  # 前端传递的 box 信息
    ocr_text TEXT  # 提取的文本
);
```

## 快速开始

1.  安装依赖：

```shell
pip install fastapi uvicorn opencv-python Pillow pydantic requests ultralytics mysql-connector-python
```

或者

```shell
npm install mysql
```

2.  启动服务：

```shell
python ocr_start.py --device cpu --port 8899
```

或者，您可以使用提供的 `ocr_start.sh` 脚本：

```shell
bash ocr_start.sh
```

## API 接口

### 1.  /OCR-QWen2.5-7B-VL1

-   **方法**: POST
-   **描述**: 原始多模态 OCR
-   **请求参数**:
    -   `img` (UploadFile): 上传的图像文件。
-   **返回**:

```json
{
  "code": 200,
  "message": "成功",
  "ocr": "提取的文本"
}
```

-   **数据库操作**:
    -   将 `img_name` (图像文件名), `url` (图像 base64 编码), `crop_box` (None), 和 `ocr` (提取的文本) 存储到 `xs_ocr_ret` 表中。

### 2.  /OCR-QWen2.5-7B-VL

-   **方法**: POST
-   **描述**: 接收前端传递的图像 base64 编码和 box 信息，进行 OCR 识别。
-   **请求体**:

```json
{
  "image": "base64 编码的图像数据",
  "box": {
    "x": 0.0,
    "y": 0.0,
    "width": 1.0,
    "height": 1.0
  }
}
```

-   **返回**:

```json
{
  "code": 200,
  "message": "成功",
  "ocr_text": "提取的文本"
}
```

-   **数据库操作**:
    -   将 `img_name` (frontend_image_{timestamp}), `url` (图像 base64 编码), `crop_box` (前端传递的 box 信息), 和 `ocr_text` (提取的文本) 存储到 `xs_ocr_ret` 表中。

### 3.  /OCR-MiniCPM2.6-V-8B

-   **方法**: POST
-   **描述**: 原始多模态 OCR，用于测试未擦除的原图像。
-   **请求参数**:
    -   `img` (UploadFile): 上传的图像文件。
-   **返回**:

```json
{
  "code": 200,
  "message": "成功",
  "ocr": "提取的文本"
}
```

-   **数据库操作**:
    -   将 `img_name` (图像文件名), `url` (图像 base64 编码), `crop_box` (None), 和 `ocr` (提取的文本) 存储到 `xs_ocr_ret` 表中。

## 配置

您可以通过以下环境变量配置 OCR 模型和 API：

-   `OCR_MODEL`: OCR 模型名称，默认为 "Qwen2.5-VL-7B-Instruct"。
-   `OCR_HOST`: OCR 服务的主机地址，默认为 'http://192.168.4.22:9008'。

您还可以通过命令行参数配置设备和端口：

-   `--device`: 指定用于模型推理的设备，默认为 "0"。
-   `--port`: 指定 FastAPI 的端口，默认为 8892。

## 示例

### 使用 curl 调用 API

```shell
curl -X POST -F "img=@/path/to/image.png" http://localhost:8899/OCR-QWen2.5-7B-VL1
```

### 使用 Python 调用 API

```python
import requests
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

image_path = "/path/to/your/image.png"
base64_image = image_to_base64(image_path)

payload = {
    "image": f"data:image/png;base64,{base64_image}",
    "box": {
        "x": 0.0,
        "y": 0.0,
        "width": 1.0,
        "height": 1.0
    }
}

response = requests.post("http://localhost:8899/OCR-QWen2.5-7B-VL", json=payload)
print(response.json())
```

## 注意事项

-   确保 OCR 服务已启动并可访问。
-   确保 MySQL 数据库已启动并可访问，并且已创建 `xs_ocr_ret` 表。
-   根据您的硬件配置选择合适的设备。
-   根据需要调整 OCR 模型的参数。
