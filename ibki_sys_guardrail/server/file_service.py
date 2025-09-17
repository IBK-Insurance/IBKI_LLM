"""
파일 처리 서비스 모듈
- PDF, DOCX 파일에서 텍스트 추출
- 이미지 파일 처리
"""

import streamlit as st
from PyPDF2 import PdfReader
import docx
from PIL import Image

def extract_text_from_pdf(file):
    """PDF 파일에서 텍스트 추출"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"PDF 텍스트 추출 실패: {str(e)}")
        return ""

def extract_text_from_docx(file):
    """DOCX 파일에서 텍스트 추출"""
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX 텍스트 추출 실패: {str(e)}")
        return ""

def process_uploaded_image(uploaded_file):
    """업로드된 이미지 파일 처리"""
    try:
        image = Image.open(uploaded_file)
        return image
    except Exception as e:
        st.error(f"이미지 처리 실패: {str(e)}")
        return None
