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
