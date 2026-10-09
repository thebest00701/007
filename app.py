import io, json, os, sqlite3, time, zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image
from jarvis_core import (
    get_api_key, get_client, analyze_product, generate_visual, generate_video,
    save_project, list_projects, load_project, chat_with_jarvis, DB_PATH, safe_filename
)

APP_DIR = Path(__file__).parent
OUTPUT_DIR = APP_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="JARVIS MAX | AI Creative Studio", page_icon="🤖", layout="wide")

st.markdown("""
<style>
:root { --jarvis-cyan:#63e6ff; }
.stApp { background: radial-gradient(ellipse at 10% 0%, #17243d 0%, #0b1020 42%, #080b13 100%); }
[data-testid="stSidebar"] { background: #0d1422; border-right: 1px solid #26354b; }
.hero { padding: 1.4rem 1.6rem; border: 1px solid #29445d; border-radius: 22px;
        background: linear-gradient(120deg, rgba(25,45,68,.95), rgba(13,19,33,.92)); margin-bottom: 1.2rem; }
.kicker { letter-spacing: .25em; text-transform: uppercase; color: #63e6ff; font-size: .75rem; }
.hero h1 { margin: .2rem 0; font-size: 2.25rem; }
.hero p { color: #b8c7d9; margin-bottom: 0; }
.panel { border: 1px solid #26354b; border-radius: 16px; padding: 1rem; background: rgba(15,23,38,.72); }
.smallmuted { color: #98a9bf; font-size: .88rem; }
div.stButton > button[kind="primary"] { border: 0; background: linear-gradient(90deg,#167caa,#2cc9d9); color: #04101b; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("## 🤖 JARVIS MAX")
    st.caption("AI Creative & Marketing Suite")
    page = st.radio("РАЗДЕЛ", ["Студия", "AI Чат", "История проектов", "Настройки и запуск"], label_visibility="collapsed")
    st.divider()
    api_key = get_api_key()
    if api_key:
        st.success("Gemini API: ключ найден")
    else:
        st.warning("Gemini API: ключ не настроен")
    st.caption("Ключ хранится вне исходного кода.")

st.markdown("""
<div class="hero">
  <div class="kicker">Personal AI creative system</div>
  <h1>J A R V I S <span style="color:#63e6ff">MAX</span></h1>
  <p>От фотографии товара до концепции рекламы, инфографики и видеоролика.</p>
</div>
""", unsafe_allow_html=True)

if page == "Студия":
    left, right = st.columns([0.92, 1.08], gap="large")
    with left:
        st.markdown("### 01 · Настрой проект")
        project_name = st.text_input("Название проекта", value="Новый рекламный проект")
        mode = st.selectbox("Режим работы", [
            "DESIGN · Инфографика", "PRODUCT · Рекламная съёмка",
            "AI · Анализ товара", "VIDEO · Видеоролик"
        ])
        platform = st.selectbox("Площадка", ["Wildberries", "Ozon", "Amazon", "Instagram / Facebook", "TikTok", "Универсальный"])
        style = st.selectbox("Визуальный стиль", [
            "Premium / Apple Minimal", "Modern / Neon", "Eco / Natural",
            "Sport / Dynamic", "Luxury / Gold", "Editorial / Clean"
        ])
        if mode.startswith("DESIGN"):
            slides_count = st.slider("Количество слайдов", 3, 8, 5)
        else:
            slides_count = 5
        aspect = st.selectbox("Формат", ["3:4 · карточка товара", "1:1 · квадрат", "4:5 · соцсети", "9:16 · вертикальное видео", "16:9 · горизонтальное видео"])
        prompt = st.text_area("Задача / пожелания", placeholder="Например: подчеркни материалы, удобство и премиальное качество. Не выдумывай характеристики, которых нет на фото.", height=110)
        make_visual = False
        if mode.startswith(("DESIGN", "PRODUCT")):
            make_visual = st.toggle("Сгенерировать дополнительное изображение", value=True,
                                   help="Требует доступа к модели Imagen и может расходовать API-квоту.")
        uploaded = st.file_uploader("Загрузи фото товара", type=["jpg", "jpeg", "png", "webp"])
        if uploaded:
            try:
                product_image = Image.open(uploaded).convert("RGB")
                st.image(product_image, caption="Исходное фото", use_container_width=True)
            except Exception:
                product_image = None
                st.error("Не удалось прочитать изображение.")
        else:
            product_image = None
            st.info("Фото необязательно для текстового анализа, но нужно для image-to-video.")

        generate_button = st.button("🚀 Запустить JARVIS", type="primary", use_container_width=True)

    with right:
        st.markdown("### 02 · Рабочая область")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.caption("Результаты генерации появятся здесь. Генерация изображений и видео требует соответствующего доступа API и может тарифицироваться отдельно.")
        if st.session_state.last_result:
            result = st.session_state.last_result
            st.markdown(f"#### {result.get('title', 'Результат JARVIS')}")
            st.markdown(result.get("text", ""))
            for img_path in result.get("images", []):
                if Path(img_path).exists():
                    st.image(img_path, use_container_width=True)
            for video_path in result.get("videos", []):
                if Path(video_path).exists():
                    st.video(video_path)
            if result.get("files"):
                for f
