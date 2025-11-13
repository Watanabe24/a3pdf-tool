import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.utils import ImageReader
from PIL import Image

st.title("PDF → A3 変換ツール (Poppler不要)")

uploaded_file = st.file_uploader("PDFを選択", type="pdf")
output_name = st.text_input("出力ファイル名", "251213-25_冬イベントスケジュール.pdf")

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    a3_width, a3_height = A3
    buffer_output = BytesIO()
    c = canvas.Canvas(buffer_output, pagesize=A3)
    
    for page_index in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_index)
        pix = page.get_pixmap()  # 画像化
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 縦横比を維持してA3に収める
        img_width_px, img_height_px = img.size
        img_width_pt = img_width_px / 96 * 72  # PyMuPDF デフォルト 96 dpi
        img_height_pt = img_height_px / 96 * 72
        scale = min(a3_width / img_width_pt, a3_height / img_height_pt)
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
