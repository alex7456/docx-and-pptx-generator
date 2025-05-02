from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from generator.wiki_parser import get_clean_article, split_into_sections
from generator.summarizer import smart_conclusion
from generator.image_fetcher import fetch_image_urls_bing
from generator.report_maker import generate_report
from generator.presentation_maker import generate_presentation
from generator.summarizer import smart_conclusion_human_style
from flask import send_from_directory
import os


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server
DOWNLOAD_DIR = os.getcwd()
@server.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
app.layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H2("🧠 Генератор докладов и презентаций", className="text-center text-primary mb-4"),
            dbc.Card([
                dbc.CardBody([

                    # Тема
                    html.Div([
                        html.Label("📝 Тема"),
                        dcc.Input(
                            id="topic",
                            type="text",
                            value="Космос",
                            placeholder="Введите тему...",
                            className="form-control"
                        )
                    ], className="mb-3"),

                    # Что сгенерировать
                    html.Div([
                        html.Label("📄 Что сгенерировать:"),
                        dbc.RadioItems(
                            id="mode",
                            options=[
                                {"label": "Доклад", "value": "report"},
                                {"label": "Презентация", "value": "presentation"},
                                {"label": "Оба", "value": "both"}
                            ],
                            value="both",
                            inline=True
                        )
                    ], className="mb-3"),

                    # Детализация
                    html.Div([
                        html.Label("🔍 Детализация текста:"),
                        dcc.Dropdown(
                            options=[
                                {"label": "Краткий", "value": "краткий"},
                                {"label": "Средний", "value": "средний"},
                                {"label": "Подробный", "value": "подробный"}
                            ],
                            value="средний",
                            id="detail",
                            className="mb-3"
                        )
                    ], className="mb-3"),

                    # Кол-во слайдов
                    html.Div([
                        html.Label("📊 Кол-во слайдов (если презентация):"),
                        dcc.Input(
                            id="slides",
                            type="number",
                            value=8,
                            min=5,
                            max=15,
                            className="form-control"
                        )
                    ], className="mb-3"),

                    # Кнопка
                    dbc.Button("🚀 Сгенерировать", id="generate", color="primary", className="w-100")
                ])
            ], className="shadow-sm")
        ], width=6)
    ], justify="center"),

    html.Br(),

    # Вывод результата
    dbc.Row([
        dbc.Col(
            dbc.Alert(id="output", color="success", is_open=False, dismissable=True),
            width=6
        )
    ], justify="center")
], fluid=True)


@app.callback(
    Output("output", "children"),
    Output("output", "is_open"),
    Input("generate", "n_clicks"),
    State("topic", "value"),
    State("mode", "value"),
    State("detail", "value"),
    State("slides", "value"),
)
def run_generator(n, topic, mode, detail, slides):
    if not n:
        return "", False

    text = get_clean_article(topic)
    if not text:
        return "❌ Не удалось получить статью с Википедии.", True

    intro = text[:400]
    sections = split_into_sections(text, slides - 3)
    conclusion = smart_conclusion_human_style(topic, sections)
    buttons = []

    if mode in ["report", "both"]:
        generate_report(topic, intro, sections, conclusion)
        buttons.append(
            dbc.Button("📄 Скачать доклад (.docx)", href=f"/download/{topic}_report.docx", color="secondary", className="me-2", target="_blank")
        )

    if mode in ["presentation", "both"]:
        image_urls = fetch_image_urls_bing(topic, len(sections))
        generate_presentation(topic, intro, sections, conclusion, image_urls)
        buttons.append(
            dbc.Button("📊 Скачать презентацию (.pptx)", href=f"/download/{topic}_presentation.pptx", color="info", target="_blank")
        )

    return dbc.ButtonGroup(buttons, className="mt-3"), True




if __name__ == "__main__":
    app.run_server(debug=True)
