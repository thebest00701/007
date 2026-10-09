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
                for f in result["files"]:
                    if Path(f).exists():
                        st.download_button(
                            f"⬇️ Скачать {Path(f).name}",
                            data=Path(f).read_bytes(),
                            file_name=Path(f).name,
                            mime="application/octet-stream",
                            key=f"download_{Path(f).name}"
                        )
            if result.get("project_id"):
                st.caption(f"Проект сохранён в истории · ID {result['project_id']}")
        else:
            st.markdown("#### Готов к работе")
            st.markdown("""
            - **DESIGN** — маркетинговая структура слайдов и генерация визуальных концептов.
            - **PRODUCT** — рекламная концепция и студийный визуал товара.
            - **AI** — описание, преимущества, аудитория и идеи продвижения.
            - **VIDEO** — сценарий и подключаемая генерация ролика через Veo.
            """)
            st.markdown('<p class="smallmuted">JARVIS не должен придумывать технические характеристики. Проверяй рекламные утверждения перед публикацией.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if generate_button:
        if not get_api_key():
            st.error("API-ключ не найден. Открой «Настройки и запуск» или добавь GEMINI_API_KEY в .streamlit/secrets.toml.")
        elif mode.startswith("VIDEO") and product_image is None:
            st.error("Для режима VIDEO загрузи исходное изображение товара.")
        else:
            try:
                with st.status("JARVIS выполняет задачу…", expanded=True) as status:
                    st.write("Подготавливаю контекст и анализирую запрос.")
                    result_text = analyze_product(
                        mode=mode, platform=platform, style=style, prompt=prompt,
                        slides_count=slides_count, aspect=aspect, image=product_image
                    )
                    st.write("Текстовая концепция готова.")
                    image_paths, video_paths, output_files = [], [], []
                    if mode.startswith("VIDEO"):
                        st.write("Отправляю запрос на генерацию видео. Операция может занять несколько минут.")
                        video_path = generate_video(prompt=(prompt or "Premium product commercial") + "\n" + result_text[:1200], image=product_image)
                        video_paths.append(str(video_path))
                        output_files.append(str(video_path))
                    elif mode.startswith(("DESIGN", "PRODUCT")) and make_visual:
                        st.write("Создаю один визуальный концепт через модель генерации изображений.")
                        visual_path = generate_visual(
                            prompt=f"{style} advertising visual for {platform}. {prompt}\n"
                                   f"Product context: {result_text[:1200]}\n"
                                   f"Aspect ratio: {aspect}. Make a clean commercial visual; avoid gibberish text and do not invent logos.",
                            aspect=aspect
                        )
                        image_paths.append(str(visual_path))
                        output_files.append(str(visual_path))
                    project_id = save_project(
                        name=project_name, mode=mode, platform=platform, style=style,
                        prompt=prompt, result_text=result_text,
                        source_name=uploaded.name if uploaded else None,
                        output_paths=output_files
                    )
                    st.session_state.last_result = {
                        "title": project_name, "text": result_text,
                        "images": image_paths, "videos": video_paths,
                        "files": output_files, "project_id": project_id
                    }
                    status.update(label="Готово — проект сохранён", state="complete", expanded=False)
                st.rerun()
            except Exception as exc:
                st.error(f"Не удалось завершить задачу: {exc}")
                st.info("Проверь API-ключ, доступность выбранной модели, интернет-соединение, квоты и биллинг проекта Google AI.")

elif page == "AI Чат":
    st.markdown("### AI Чат с JARVIS")
    st.caption("Обсуждай детали проектов, задавай вопросы по маркетингу и дизайну с сохранением контекста беседы.")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Напиши сообщение JARVIS..."):
        if not get_api_key():
            st.error("API-ключ не настроен.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)
            
            with st.chat_message("assistant"):
                with st.spinner("JARVIS думает..."):
                    try:
                        reply = chat_with_jarvis(st.session_state.chat_history)
                        st.markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    except Exception as exc:
                        st.error(f"Ошибка чата: {exc}")

elif page == "История проектов":
    st.markdown("### История проектов")
    projects = list_projects()
    if not projects:
        st.info("Пока нет сохранённых проектов. Создай первый в разделе «Студия».")
    else:
        for p in projects:
            with st.expander(f"#{p['id']} · {p['name']} · {p['created_at']}"):
                st.write(f"**Режим:** {p['mode']}  ·  **Площадка:** {p['platform']}  ·  **Стиль:** {p['style']}")
                st.write(f"**Запрос:** {p['prompt'] or '—'}")
                st.markdown(p["result_text"])
                outputs = json.loads(p["output_paths"] or "[]")
                for path in outputs:
                    if Path(path).exists():
                        if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                            st.image(path, use_container_width=True)
                        elif path.lower().endswith(".mp4"):
                            st.video(path)
                        st.download_button("Скачать файл", data=Path(path).read_bytes(), file_name=Path(path).name, key=f"hist_{p['id']}_{Path(path).name}")
                if st.button("Открыть этот проект в студии", key=f"open_{p['id']}"):
                    st.session_state.last_result = {
                        "title": p["name"], "text": p["result_text"], "images": [],
                        "videos": [], "files": outputs, "project_id": p["id"]
                    }
                    st.success("Проект загружен в рабочую область. Перейди в «Студия».")

else:
    st.markdown("### Настройка и запуск")
    st.markdown("""
    **Локально на Mac**
    1. Установи Python 3.11 или 3.12[cite: 4].
    2. В папке проекта выполни `python3 -m venv .venv`[cite: 4].
    3. Активируй окружение: `source .venv/bin/activate`[cite: 4].
    4. Установи зависимости: `pip install -r requirements.txt`[cite: 4].
    5. Создай `.streamlit/secrets.toml` на основе примеров и вставь свой ключ[cite: 4].
    6. Запусти: `streamlit run app.py`[cite: 4].

    **Публикация в интернете**
    - Загрузи проект в GitHub-репозиторий (без секретных файлов)[cite: 4].
    - На Streamlit Community Cloud выбери репозиторий и `app.py`[cite: 4].
    - В настройках Secrets добавь свой `GEMINI_API_KEY`[cite: 4].
    """)
    st.code("python3 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\nstreamlit run app.py", language="bash")
