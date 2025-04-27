from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from generator.wiki_parser import get_clean_article, split_into_sections
from generator.summarizer import smart_conclusion
from generator.image_fetcher import fetch_image_urls_bing
from generator.report_maker import generate_report
from generator.presentation_maker import generate_presentation

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H2("Автоматический генератор доклада и презентации"),
    dbc.Row([
        dbc.Col([
            html.Label("Тема"),
            dcc.Input(id="topic", type="text", value="Космос", style={"width": "100%"}),
            html.Br(), html.Br(),
            html.Label("Что сгенерировать:"),
            dcc.RadioItems(
                id="mode", options=[
                    {"label": "Доклад", "value": "report"},
                    {"label": "Презентация", "value": "presentation"},
                    {"label": "Оба", "value": "both"},
                ],
                value="both",
                labelStyle={'display': 'block'}
            ),
            html.Label("Детализация текста:"),
            dcc.Dropdown(
                options=[
                    {"label": "Краткий", "value": "краткий"},
                    {"label": "Средний", "value": "средний"},
                    {"label": "Подробный", "value": "подробный"}
                ],
                value="средний",
                id="detail"
            ),
            html.Label("Слайдов (если презентация):"),
            dcc.Input(id="slides", type="number", value=8, min=5, max=15),
            html.Br(), html.Br(),
            dbc.Button("Сгенерировать", id="generate", color="primary"),
        ], width=6)
    ]),
    html.Br(),
    html.Div(id="output")
])

@app.callback(
    Output("output", "children"),
    Input("generate", "n_clicks"),
    State("topic", "value"),
    State("mode", "value"),
    State("detail", "value"),
    State("slides", "value"),
)
def run_generator(n, topic, mode, detail, slides):
    if not n:
        return ""

    text = get_clean_article(topic)
    if not text:
        return "❌ Не удалось получить статью с Википедии."

    intro = text[:400]
    conclusion = text[-400:]
    sections = split_into_sections(text, slides - 3)

    if mode in ["report", "both"]:
        generate_report(topic, intro, sections, conclusion)
    if mode in ["presentation", "both"]:
        image_urls = fetch_image_urls_bing(topic, len(sections))
        generate_presentation(topic, intro, sections, conclusion, image_urls)

    return f"✅ Готово! Файлы сохранены: {topic}_report.docx и/или {topic}_presentation.pptx"

if __name__ == "__main__":
    app.run_server(debug=True)
