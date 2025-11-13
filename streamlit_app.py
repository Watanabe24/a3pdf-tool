!pip install pdf2image reportlab
!apt-get install -y poppler-utils

from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from google.colab import files
from io import BytesIO
from reportlab.lib.utils import ImageReader
from PIL import Image

# 背景色設定 (白 = (255,255,255))
BACKGROUND_COLOR = (255, 255, 255)

# PDFアップロード
uploaded = files.upload()
file_name = list(uploaded.keys())[0]

# PDFを画像に変換
pages = convert_from_path(file_name, dpi=300)

# 出力ファイル名を指定
output_file = "a3.pdf"
c = canvas.Canvas(output_file, pagesize=A3)
a3_width, a3_height = A3

for page_img in pages:
    # 透過部分を背景色で埋める
    if page_img.mode in ("RGBA", "LA") or ('transparency' in page_img.info):
        bg = Image.new("RGB", page_img.size, BACKGROUND_COLOR)
        bg.paste(page_img, mask=page_img.split()[3] if page_img.mode=='RGBA' else None)
        page_img = bg
    else:
        page_img = page_img.convert("RGB")  # 念のためRGB化

    img_width_px, img_height_px = page_img.size
    dpi = 300  # 変換時の DPI

    # 画像サイズをポイントに換算
    img_width_pt = img_width_px / dpi * 72
    img_height_pt = img_height_px / dpi * 72

    # 縦横比を維持してA3に収める
    scale = min(a3_width / img_width_pt, a3_height / img_height_pt)

    scaled_width = img_width_pt * scale
    scaled_height = img_height_pt * scale

    # 中央配置
    x_offset = (a3_width - scaled_width) / 2
    y_offset = (a3_height - scaled_height) / 2

    # PIL ImageをImageReaderで描画
    img_buffer = BytesIO()
    page_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_reader = ImageReader(img_buffer)

    c.drawImage(img_reader, x_offset, y_offset, width=scaled_width, height=scaled_height)
    c.showPage()

c.save()
files.download(output_file)
