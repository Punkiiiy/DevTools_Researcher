# Advanced Agent — Исследователь инструментов для разработчиков

Инструмент для автоматического исследования developer tools. По запросу пользователя система ищет в интернете статьи и сайты, извлекает названия инструментов, анализирует их характеристики и выдаёт рекомендации.

## Возможности

- **Поиск инструментов** — поиск статей и извлечение конкретных продуктов по теме запроса
- **Анализ** — скрапинг официальных сайтов и структурированный анализ (цены, стек, API, языки, интеграции)
- **Рекомендации** — краткие советы по выбору инструмента

## Архитектура

Проект использует **LangGraph** с графом из трёх узлов:

```
extract_tools → research → analyze → END
```

1. **extract_tools** — поиск статей через Firecrawl, извлечение названий инструментов с помощью LLM
2. **research** — поиск официальных сайтов, скрапинг и анализ каждого инструмента
3. **analyze** — формирование итоговых рекомендаций

## Структура проекта

```
DevTools_Researcher/
├── main.py              # Точка входа, интерактивный цикл
├── requirements.txt     # Зависимости
└── src/
    ├── workflow.py      # Граф LangGraph
    ├── models.py        # Pydantic-модели (CompanyInfo, ResearchState и др.)
    ├── firecrawl_service.py  # Интеграция с Firecrawl API
    └── prompts.py       # Промпты для LLM
├── README.md
```

## Установка

1. Клонируйте репозиторий и перейдите в папку `DevTools_Researcher`:

```bash
cd DevTools_Researcher
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```env
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

## Запуск

```bash
python main.py
```

Введите запрос (например, «базы данных для Python» или «CI/CD tools») и получите список инструментов с анализом. Для выхода введите `exit`.

## Зависимости

- **firecrawl-py** — поиск и скрапинг веб-страниц
- **langchain**, **langchain-openai**, **langgraph** — оркестрация LLM и граф workflow
- **pydantic** — валидация и модели данных
- **python-dotenv** — загрузка переменных окружения

## Пример вывода

```
📊 Results for: database for Python

1. 🏢 Supabase
   * Website: https://supabase.com
   * Pricing: Freemium
   * Open Source: True
   * Tech Stack: PostgreSQL, REST, Realtime
   * Language Support: Python, JavaScript, Go
   * API: Available
   * Description: Open source Firebase alternative with PostgreSQL

Developer Recommendations:
---------------------------
Supabase is the best choice for Python developers...
```
