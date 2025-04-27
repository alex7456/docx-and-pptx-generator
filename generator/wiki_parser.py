import wikipedia
import re

wikipedia.set_lang("ru")

def get_clean_article(title):
    try:
        page = wikipedia.page(title)
        text = page.content
        text = re.split(r"==\s*См\. также\s*==", text)[0]
        text = re.sub(r"==+\s*(.*?)\s*==+", r"§\1§", text)
        return text.strip()
    except:
        return None

def split_into_sections(text, max_sections):
    sections = []
    parts = re.split(r'§(.*?)§', text)
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip()
        sections.append((title, content))
    return sections[:max_sections]
