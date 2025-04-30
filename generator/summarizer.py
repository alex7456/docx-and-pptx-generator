from transformers import pipeline

try:
    summarizer = pipeline("summarization", model="IlyaGusev/rut5_base_sum_gazeta")
except:
    summarizer = None

def smart_conclusion(title, sections):
    FALLBACK = "Изучение темы важно для современного общества."
    combined = "\n".join([f"{sec[0]}: {sec[1]}" for sec in sections if len(sec[1].strip()) > 30])

    if len(combined) < 200:
        return FALLBACK

    clean_text = ' '.join(combined.replace("\n", " ").split())

    if summarizer is None:
        return FALLBACK

    try:
        result = summarizer(clean_text, max_length=120, min_length=60, do_sample=False)
        return result[0]['summary_text']
    except:
        return FALLBACK

def smart_conclusion_human_style(title, sections):
    FALLBACK = (
        f"Тема «{title}» представляет собой важную и актуальную область для изучения. "
        "Она затрагивает множество аспектов и имеет практическое значение для различных сфер жизни. "
        "Продолжение изучения этой темы открывает новые горизонты для науки и общества."
    )

    combined = "\n".join([f"{sec[0]}: {sec[1]}" for sec in sections if len(sec[1].strip()) > 30])
    if len(combined) < 200:
        return FALLBACK

    clean_text = ' '.join(combined.replace("\n", " ").split())
    if summarizer is None:
        return FALLBACK

    try:
        result = summarizer(clean_text, max_length=120, min_length=60, do_sample=False)
        summary = result[0]['summary_text']

        # Оборачиваем в осмысленный финал
        conclusion = (
            f"Подводя итог, можно сказать, что тема «{title}» является крайне значимой и интересной.\n\n"
            f"{summary}\n\n"
            f"Знания в этой области важны не только для науки, но и для понимания мира вокруг нас."
        )
        return conclusion
    except Exception as e:
        return FALLBACK
