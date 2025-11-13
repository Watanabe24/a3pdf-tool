# streamlit_app.py
import streamlit as st
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO

# 背景色設定 (白)
BACKGROUND_COLOR = (255, 255, 255)

st.title("PDF → A3 変換ツール")
st.write("PDFファイルをアップロードしてA3サイズに変換できます。")

# PDFアップロード
uploaded_file = st.file_uploader("PDFを選択", type="pdf")

# 出力ファイル名
output_name = st.text_input("出力ファイル名", "251213-25_冬イベントスケジュール.pdf")

if uploaded_file is not None:
    # PDFを画像に変換
    if hasattr(uploaded_file, "name"):
        pages = convert_from_path(uploaded_file, dpi=300)
    else:
        pages = convert_from_path(BytesIO(uploaded_file.read()), dpi=300)

    a3_width, a3_height = A3
    buffer_output = BytesIO()
    c = canvas.Canvas(buffer_output, pagesize=A3)

    for page_img in pages:
        # 透過部分を背景色で埋める
        if page_img.mode in ("RGBA", "LA") or ('transparency' in page_img.info):
            bg = Image.new("RGB", page_img.size, BACKGROUND_COLOR)
            bg.paste(page_img, mask=page_img.split()[3] if page_img.mode == 'RGBA' else None)
            page_img = bg
        else:
            page_img = page_img.convert("RGB")

        img_width_px, img_height_px = page_img.size
        dpi = 300
        img_width_pt = img_width_px / dpi * 72
        img_height_pt = img_height_px / dpi * 72

        # 縦横比を維持してA3に収める
        scale = min(a3_width / img_width_pt, a3_height / img_height_pt)
        scaled_width = img_width_pt * scale
        scaled_height = img_height_pt * scale

        # 中央配置
        x_offset = (a3_width - scaled_width) / 2
        y_offset = (a3_height - scaled_height) / 2

        # 描画
        img_buffer = BytesIO()
        page_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        c.drawImage(img_reader, x_offset, y_offset, width=scaled_width, height=scaled_height)
        c.showPage()

    c.save()
    buffer_output.seek(0)

    # ダウンロードボタン
    st.download_button(
        label="変換済PDFをダウンロード",
        data=buffer_output,
        file_name=output_name,
        mime="application/pdf"
    )
