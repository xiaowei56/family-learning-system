"""
PaddleOCR REST API 服务

提供 OCR 文字识别接口，供家庭学习系统主应用调用。
独立 Docker 容器运行，通过 HTTP 与 FastAPI 后端通信。
"""

import os
import logging

from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paddleocr-server")

app = Flask(__name__)

# 全局初始化 PaddleOCR（首次调用时加载模型）
ocr_engine = None


def get_ocr():
    """获取或初始化 PaddleOCR 引擎（懒加载）。"""
    global ocr_engine
    if ocr_engine is None:
        from paddleocr import PaddleOCR

        logger.info("正在初始化 PaddleOCR 引擎...")
        ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            use_gpu=False,
            show_log=False,
        )
        logger.info("PaddleOCR 引擎初始化完成")
    return ocr_engine


@app.route("/health", methods=["GET"])
def health():
    """健康检查接口。"""
    return jsonify({"status": "ok", "service": "paddleocr"})


@app.route("/ocr", methods=["POST"])
def ocr_recognize():
    """
    OCR 文字识别接口。

    请求：multipart/form-data，字段名 "image"
    返回：{"text": "识别文本", "confidence": 0.95, "boxes": [...]}
    """
    if "image" not in request.files:
        return jsonify({"error": "缺少 image 字段"}), 400

    file = request.files["image"]
    image_bytes = file.read()

    if not image_bytes:
        return jsonify({"error": "图片数据为空"}), 400

    # 保存临时文件供 PaddleOCR 读取
    temp_path = "/tmp/ocr_input.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        ocr = get_ocr()
        result = ocr.ocr(temp_path, cls=True)

        if not result or not result[0]:
            return jsonify({"text": "", "confidence": 0.0, "boxes": []})

        # 合并识别结果
        lines = []
        total_conf = 0.0
        boxes_data = []

        for line in result[0]:
            box = line[0]  # 文本框坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            text = line[1][0]  # 识别文本
            confidence = line[1][1]  # 置信度

            lines.append(text)
            total_conf += confidence
            boxes_data.append({
                "box": box,
                "text": text,
                "confidence": confidence,
            })

        avg_conf = total_conf / len(result[0]) if result[0] else 0.0
        full_text = "\n".join(lines)

        return jsonify({
            "text": full_text,
            "confidence": round(avg_conf, 4),
            "boxes": boxes_data,
        })

    except Exception as e:
        logger.error(f"OCR 识别失败: {e}")
        return jsonify({"error": f"OCR 识别失败: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.route("/ocr/image", methods=["POST"])
def ocr_with_image():
    """
    OCR 识别图片文件并返回可搜索的文本块。

    与 /ocr 接口相同，但返回结构更适合前端展示：
    返回: {"text": "全文", "blocks": [{"text": "...", "box": [...], "confidence": 0.95}]}
    """
    if "image" not in request.files:
        return jsonify({"error": "缺少 image 字段"}), 400

    file = request.files["image"]
    image_bytes = file.read()

    temp_path = "/tmp/ocr_input.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    try:
        ocr = get_ocr()
        result = ocr.ocr(temp_path, cls=True)

        if not result or not result[0]:
            return jsonify({"text": "", "blocks": []})

        lines = []
        blocks = []

        for line in result[0]:
            box = line[0]
            text = line[1][0]
            confidence = line[1][1]

            lines.append(text)
            blocks.append({
                "text": text,
                "box": box,
                "confidence": round(confidence, 4),
            })

        return jsonify({
            "text": "\n".join(lines),
            "blocks": blocks,
        })

    except Exception as e:
        logger.error(f"OCR 识别失败: {e}")
        return jsonify({"error": f"OCR 识别失败: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
