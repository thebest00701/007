import json, os, sqlite3, time, uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from PIL import Image
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_PATH = BASE_DIR / "jarvis_history.sqlite3"
TEXT_MODEL = os.getenv("JARVIS_TEXT_MODEL", "gemini-3.8-flash")
IMAGE_MODEL = os.getenv("JARVIS_IMAGE_MODEL", "imagen-4.0-generate-001")
VIDEO_MODEL = os.getenv("JARVIS_VIDEO_MODEL", "veo-3.1-generate-preview")


def get_api_key() -> Optional[str]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        return None


def get_client():
    key = get_api_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY не настроен. Добавь ключ в .streamlit/secrets.toml или переменные окружения.")
    return genai.Client(api_key=key)


def safe_filename(value: str) -> str:
    value = "".join(c if c.isalnum() or c in "-_." else "_" for c in value.strip())
    return (value[:70] or "jarvis_output")


def _image_description_hint(image: Optional[Image.Image]) -> str:
    if image is None:
        return "Изображение не предоставлено."
    return "Изображение товара приложено к запросу. Опирайся только на видимые детали; неизвестные характеристики помечай как требующие подтверждения."


def analyze_product(mode, platform, style, prompt, slides_count, aspect, image=None):
    client = get_client()
    if mode.startswith("DESIGN"):
        task = f"""
Создай профессиональный план инфографики для товара из фотографии.
Нужно ровно {slides_count} слайдов для площадки {platform}; стиль: {style}; формат: {aspect}.
Для каждого слайда выведи: номер и цель, заголовок, короткий текст на изображении, композицию, фон/свет, визуальные акценты.
Добавь в конце: единый арт-дирекшн, список фактов о товаре, которые нельзя утверждать без подтверждения.
"""
    elif mode.startswith("PRODUCT"):
        task = f"""
Разработай концепцию премиальной рекламной съёмки товара для {platform} в стиле {style}, формат {aspect}.
Выведи: краткий анализ видимого товара, 3 идеи рекламного кадра, один подробный image-generation prompt на английском,
предлагаемые ракурсы/свет/материалы, и короткий рекламный текст. Не придумывай характеристики.
"""
    elif mode.startswith("VIDEO"):
        task = f"""
Подготовь сценарий рекламного ролика с использованием товара для {platform}, стиль {style}, формат {aspect}.
Выведи: идею, длительность 5–8 секунд, таймлайн по секундам, движение камеры, свет, фон, переход/финальный кадр,
звуковую атмосферу и отдельный подробный prompt на английском для video generation.
"""
    else:
        task = f"""
Проанализируй товар для маркетинга на площадке {platform}. Стиль: {style}.
Структура: что видно на фото, вероятная категория (с оговоркой), видимые преимущества, целевая аудитория,
позиционирование, 5 идей контента, варианты заголовков, что нужно уточнить у владельца товара.
Не выдавай предположения за факты.
"""
    contents = [task, f"Пожелания пользователя: {prompt or 'Не указаны.'}", _image_description_hint(image)]
    if image is not None:
        contents.append(image)
    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Ты JARVIS MAX — внимательный AI арт-директор, дизайнер инфографики и маркетолог. "
                    "Пиши по-русски, структурно и без воды. Не выдумывай характеристики, сертификаты, "
                    "гарантии, цифры, медицинские эффекты или бренды, которых нельзя подтвердить."
                ),
                temperature=0.7,
            )
        )
    except Exception as e:
        raise RuntimeError(f"Ошибка API Gemini: {e}")
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Модель вернула пустой текст. Проверь доступ к модели и попробуй ещё раз.")
    return text


def chat_with_jarvis(history: List[Dict[str, str]]) -> str:
    client = get_client()
    # Собираем историю диалога в стандартный формат для generate_content, избегая агентских методов
    contents = []
    for msg in history:
        role = "Пользователь" if msg["role"] == "user" else "JARVIS"
        contents.append(f"{role}: {msg['content']}")
    
    prompt_text = "\n".join(contents) + "\nJARVIS:"
    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=[prompt_text],
            config=types.GenerateContentConfig(
                system_instruction="Ты JARVIS MAX — профессиональный AI-ассистент по маркетингу и дизайну. Отвечай вежливо, четко и по делу.",
                temperature=0.7
            )
        )
        return getattr(response, "text", "Нет ответа от модели.")
    except Exception as e:
        raise RuntimeError(f"Ошибка чата Gemini: {e}")


def generate_visual(prompt: str, aspect: str = "3:4 · карточка товара") -> Path:
    client = get_client()
    ratio = aspect.split("·")[0].strip()
    full_prompt = (
        "Create a high-end commercial product advertising image. "
        "Keep the product visually coherent, use professional studio lighting and a clean composition. "
        "Do not add fake logos, watermarks, illegible text, fake labels, or unsupported claims. "
        f"Requested aspect ratio: {ratio}. Prompt: {prompt}"
    )
    response = client.models.generate_images(
        model=IMAGE_MODEL,
        prompt=full_prompt,
        config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/png")
    )
    generated = getattr(response, "generated_images", None) or []
    if not generated:
        raise RuntimeError("Модель изображений не вернула результат. Возможно, у API-ключа нет доступа к Imagen.")
    image_obj = generated[0].image
    image_bytes = getattr(image_obj, "image_bytes", None)
    if not image_bytes:
        raise RuntimeError("Изображение получено в неожиданном формате SDK.")
    path = OUTPUT_DIR / f"jarvis_visual_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}.png"
    path.write_bytes(image_bytes)
    return path


def generate_video(prompt: str, image: Optional[Image.Image] = None) -> Path:
    client = get_client()
    if image is not None:
        tmp = OUTPUT_DIR / f"source_{uuid.uuid4().hex[:8]}.png"
        image.save(tmp, format="PNG")
        try:
            source_image = types.Image.from_file(location=str(tmp))
            operation = client.models.generate_videos(
                model=VIDEO_MODEL,
                source=types.GenerateVideosSource(prompt=prompt, image=source_image),
                config=types.GenerateVideosConfig(number_of_videos=1, duration_seconds=8, resolution="720p")
            )
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except Exception:
                pass
    else:
        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            source=types.GenerateVideosSource(prompt=prompt),
            config=types.GenerateVideosConfig(number_of_videos=1, duration_seconds=8, resolution="720p")
        )
    deadline = time.time() + 900
    while not operation.done:
        if time.time() > deadline:
            raise TimeoutError("Генерация видео не завершилась за 15 минут.")
        time.sleep(10)
        operation = client.operations.get(operation)
    response = operation.response
    generated = getattr(response, "generated_videos", None) or []
    if not generated:
        raise RuntimeError("Veo не вернул видео. Проверь доступ к модели, регион, квоты и биллинг.")
    video_obj = generated[0].video
    video_bytes = getattr(video_obj, "video_bytes", None)
    if not video_bytes:
        try:
            client.files.download(file=video_obj, download_path=str(OUTPUT_DIR / "jarvis_video_temp.mp4"))
            temp_path = OUTPUT_DIR / "jarvis_video_temp.mp4"
            final_path = OUTPUT_DIR / f"jarvis_video_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}.mp4"
            temp_path.rename(final_path)
            return final_path
        except Exception as exc:
            raise RuntimeError(f"Видео сгенерировано, но SDK не смог скачать файл: {exc}")
    path = OUTPUT_DIR / f"jarvis_video_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}.mp4"
    path.write_bytes(video_bytes)
    return path


def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mode TEXT NOT NULL,
            platform TEXT NOT NULL,
            style TEXT NOT NULL,
            prompt TEXT,
            result_text TEXT NOT NULL,
            source_name TEXT,
            output_paths TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_project(name, mode, platform, style, prompt, result_text, source_name=None, output_paths=None):
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO projects(name, mode, platform, style, prompt, result_text, source_name, output_paths, created_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (name or "Новый проект", mode, platform, style, prompt or "", result_text,
             source_name, json.dumps(output_paths or [], ensure_ascii=False),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        return cur.lastrowid


def list_projects(limit=100):
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]


def load_project(project_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        return dict(row) if row else None
