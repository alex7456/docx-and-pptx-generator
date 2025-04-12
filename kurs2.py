import wikipedia
from docx import Document
from pptx import Presentation
import re
import os

# Устанавливаем русский язык
wikipedia.set_lang("ru")

# --- Получение и очистка статьи ---
def get_clean_article(title):
    try:
        page = wikipedia.page(title)
        text = page.content

        # Удаляем всё, что после "== См. также =="
        text = re.split(r"==\s*См\. также\s*==", text)[0]

        # Удаляем разделы "Примечания", "Ссылки"
        text = re.sub(r"==\s*(Примечания|Ссылки).*", "", text, flags=re.DOTALL)

        # Заменяем заголовки вида "== Раздел ==" на просто "Раздел"
        text = re.sub(r"==+\s*(.*?)\s*==+", r"\1", text)

        # Удаляем лишние пробелы
        text = re.sub(r'\n{2,}', '\n\n', text).strip()

        return text
    except Exception as e:
        print(f"Ошибка при получении статьи: {e}")
        return None

# --- Структурирование текста ---
def structure_text(text):
    paragraphs = text.split('\n\n')

    # Введение — первые 2 абзаца
    intro = '\n\n'.join(paragraphs[:2])

    # Заключение — последние 1-2 абзаца
    conclusion = '\n\n'.join(paragraphs[-2:])

    # Основные разделы — всё между ними
    middle = paragraphs[2:-2]
    section_size = max(1, len(middle) // 8)
    sections = [
        '\n\n'.join(middle[i:i+section_size]) for i in range(0, len(middle), section_size)
    ][:8]  # максимум 8 разделов

    return {
        "intro": intro,
        "sections": sections,
        "conclusion": conclusion
    }

# --- Генерация доклада ---
def generate_report(title, structured):
    doc = Document()
    doc.add_heading(title, 0)

    doc.add_heading("Введение", level=1)
    doc.add_paragraph(structured["intro"])

    doc.add_heading("Основная часть", level=1)
    for i, section in enumerate(structured["sections"], start=1):
        doc.add_heading(f"Раздел {i}", level=2)
        doc.add_paragraph(section)

    doc.add_heading("Заключение", level=1)
    doc.add_paragraph(structured["conclusion"])

    filename = f"{title}_report.docx"
    doc.save(filename)
    print(f"✅ Доклад сохранён: {os.path.abspath(filename)}")

# --- Генерация презентации ---
def generate_presentation(title, structured):
    prs = Presentation()

    # Слайд 1: Заголовок
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = "Автоматически сгенерированная презентация"

    # Слайды 2-9: Основные разделы
    for i, section in enumerate(structured["sections"], start=1):
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = f"Раздел {i}"
        slide.placeholders[1].text = section[:800]  # ограничение по длине

    # Слайд 10: Заключение
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Заключение"
    slide.placeholders[1].text = structured["conclusion"]

    filename = f"{title}_presentation.pptx"
    prs.save(filename)
    print(f"✅ Презентация сохранена: {os.path.abspath(filename)}")

# --- Главная функция ---
def generate_all(topic):
    print(f"🔍 Генерация по теме: {topic}")
    article = get_clean_article(topic)
    if not article:
        print("❌ Не удалось получить статью.")
        return

    structured = structure_text(article)
    generate_report(topic, structured)
    generate_presentation(topic, structured)

# --- Запуск ---
# Пример: просто введи тему
topic = input("Введите тему: ")
generate_all(topic)
