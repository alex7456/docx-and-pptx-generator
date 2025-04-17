import wikipedia
import os
import re
import json
import urllib.parse
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT

wikipedia.set_lang("ru")

TOPIC_TRANSLATIONS = {
    "горы": "mountains",
    "космос": "space",
    "море": "sea",
    "океан": "ocean",
    "животные": "animals",
    "человек": "human",
    "природа": "nature",
    "город": "city",
    "архитектура": "architecture",
    "история": "history",
    "техника": "technology",
    "наука": "science",
    "музыка": "music",
    "спорт": "sport",
    "еда": "food",
}

def get_clean_article(title):
    try:
        page = wikipedia.page(title)
        text = page.content
        text = re.split(r"==\s*См\. также\s*==", text)[0]
        text = re.sub(r"==\s*(Примечания|Ссылки).*", "", text, flags=re.DOTALL)
        text = re.sub(r"==+\s*(.*?)\s*==+", r"§\1§", text)
        return text.strip()
    except Exception as e:
        print(f"❌ Ошибка при получении статьи: {e}")
        return None

def split_into_sections(text, max_sections):
    sections = []
    parts = re.split(r'§(.*?)§', text)
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip()
        sections.append((title, content))
    return sections[:max_sections]

def chunk_text_to_bullets(text, max_lines=4):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 20][:max_lines]

def generate_report(title, intro, sections, conclusion):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_heading("Введение", level=1)
    doc.add_paragraph(intro)
    doc.add_heading("Основная часть", level=1)
    for i, (sec_title, sec_text) in enumerate(sections, start=1):
        doc.add_heading(sec_title, level=2)
        doc.add_paragraph(sec_text)
    doc.add_heading("Заключение", level=1)
    doc.add_paragraph(conclusion)
    filename = f"{title}_report.docx"
    doc.save(filename)
    print(f"📄 Доклад сохранён: {os.path.abspath(filename)}")

def fetch_image_urls_bing(query, count):
    print(f"\n🔽 Ищем картинки в Bing по теме: {query}")
    search_term = TOPIC_TRANSLATIONS.get(query.lower(), query)
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(search_term)}&form=HDRSC2&first=1&tsc=ImageHoverTitle"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_tags = soup.find_all("a", class_="iusc")

    urls = []
    for tag in image_tags:
        try:
            m_json = json.loads(tag.get("m"))
            img_url = m_json["murl"]
            if img_url.endswith((".jpg", ".jpeg", ".png")):
                urls.append(img_url)
            if len(urls) >= count:
                break
        except Exception:
            continue

    for u in urls:
        print(f"🖼 Найдено: {u}")

    if not urls:
        print("❌ Не удалось найти картинки.")

    return urls

def generate_presentation(title, intro, sections, conclusion, image_urls):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title
    slide.placeholders[1].text = "Презентация по теме"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Введение"
    tf = slide.placeholders[1].text_frame
    tf.text = intro

    for i, (sec_title, sec_text) in enumerate(sections):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = sec_title
        bullets = chunk_text_to_bullets(sec_text)
        tf = slide.placeholders[1].text_frame
        tf.clear()
        for bullet in bullets:
            p = tf.add_paragraph()
            p.text = bullet
            p.level = 0
            p.font.size = Pt(16)
        if i < len(image_urls):
            try:
                response = requests.get(image_urls[i], timeout=10)
                if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
                    img_stream = BytesIO(response.content)
                    slide.shapes.add_picture(img_stream, Inches(5.5), Inches(2.5), width=Inches(3.5))
                    print(f"🖼 Вставлена картинка из: {image_urls[i]}")
                else:
                    print(f"❌ Не изображение: {image_urls[i]}")
            except Exception as e:
                print(f"⚠ Ошибка вставки: {e}")

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Заключение"
    bullets = chunk_text_to_bullets(conclusion)
    tf = slide.placeholders[1].text_frame
    tf.clear()
    for bullet in bullets:
        p = tf.add_paragraph()
        p.text = bullet
        p.level = 0
        p.font.size = Pt(16)

    filename = f"{title}_presentation.pptx"
    prs.save(filename)
    print(f"📊 Презентация сохранена: {os.path.abspath(filename)}")

def generate_all(topic, slides_count, detail_level, image_count):
    print(f"🔍 Генерация по теме: {topic}")
    raw_text = get_clean_article(topic)
    if not raw_text:
        print("❌ Не удалось получить статью.")
        return

    intro = raw_text[:400]
    conclusion = raw_text[-400:]
    sections = split_into_sections(raw_text, slides_count - 3)

    generate_report(topic, intro, sections, conclusion)
    image_urls = fetch_image_urls_bing(topic, image_count)
    generate_presentation(topic, intro, sections, conclusion, image_urls)

# === Запуск ===
topic = input("Введите тему: ").strip()
while True:
    try:
        slides = int(input("Сколько слайдов (5–15)? "))
        if 5 <= slides <= 15:
            break
        print("❗ Введите число от 5 до 15.")
    except:
        print("❗ Нужно ввести число.")

while True:
    detail = input("Детализация (краткий / средний / подробный): ").lower()
    if detail in ["краткий", "средний", "подробный"]:
        break
    print("❗ Введите корректное значение.")

while True:
    try:
        img_count = int(input("Сколько картинок вставить (0–12)? "))
        if 0 <= img_count <= 12:
            break
        print("❗ Введите число от 0 до 12.")
    except:
        print("❗ Нужно ввести число.")

generate_all(topic, slides, detail, img_count)
