# streamlit_app.py
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.utils import ImageReader
from PIL import Image

st.title("PDF → A3 変換ツール")

uploaded_file = st.file_uploader("PDFを選択", type="pdf")
output_name = st.text_input("出力ファイル名", "251213-25_冬イベントスケジュール.pdf")

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    a3_width, a3_height = A3
    buffer_output = BytesIO()
    c = canvas.Canvas(buffer_output, pagesize=A3)

    zoom = 3  # 3倍 → 約288dpiでシャープに
    mat = fitz.Matrix(zoom, zoom)

    for page_index in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_index)
        pix = page.get_pixmap(matrix=mat)  # 高解像度で画像化
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 背景を白にして薄い線を消す
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img)
        img = bg

        # 薄い線を白に置き換え（セル線をほぼ消す）
        threshold = 200  # 180～200で調整可能
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                if r > threshold and g > threshold and b > threshold:
                    pixels[x, y] = (255, 255, 255)

        # 縦横比を維持して少し余裕をもってA3に収める
        img_width_px, img_height_px = img.size
        img_width_pt = img_width_px / (96 * zoom) * 72  # dpi換算
        img_height_pt = img_height_px / (96 * zoom) * 72
        scale = min(a3_width / img_width_pt, a3_height / img_height_pt) * 0.95
        scaled_width = img_width_pt * scale
        scaled_height = img_height_pt * scale
        x_offset = (a3_width - scaled_width) / 2
        y_offset = (a3_height - scaled_height) / 2

        # 描画
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        c.drawImage(img_reader, x_offset, y_offset, width=scaled_width, height=scaled_height)
        c.showPage()

    c.save()
    buffer_output.seek(0)

    st.download_button(
        label="変換済PDFをダウンロード",
        data=buffer_output,
        file_name=output_name,
        mime="application/pdf"
    )
