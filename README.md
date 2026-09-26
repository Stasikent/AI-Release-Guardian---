# AI Release Guardian

AI Release Guardian — прототип нейро-сотрудника для анализа веб-интерфейсов и оценки рисков изменений между релизами.

Система автоматически анализирует структуру веб-страницы, декомпозирует интерфейс на тестируемые элементы и использует LLM для генерации тестов и выявления потенциальных зон регрессии.

Проект демонстрирует применение **RAG-архитектуры**, **LLM reasoning** и **DOM-анализа интерфейса** для задач QA-аналитики.

---

# Цель проекта

Основная цель системы — помочь QA-инженеру автоматизировать анализ интерфейса и подготовку тестирования перед релизом.

AI Release Guardian позволяет:

- анализировать структуру DOM веб-страницы
- выделять testable objects (тестируемые элементы интерфейса)
- генерировать тестовые сценарии
- выявлять потенциальные зоны риска
- анализировать изменения интерфейса между версиями сайта
- оценивать release risk

---

# Архитектура системы

Архитектура проекта построена по принципу:

**Code extracts facts → LLM performs reasoning**

Это позволяет снизить вероятность галлюцинаций модели, поскольку LLM работает с реальными структурированными данными интерфейса.

## Общий pipeline системы
```mermaid
flowchart TD
    A[TARGET_URL]
    B[DOM анализ страницы]
    C[Testable objects]
    D[Representative elements]
    E[RAG retrieval]
    F[LLM reasoning]
    G[Генерация тестов]
    H[Page summary]
    I[Site-level UI checks]
    J[Visual checks]
    K[AI risk analysis]
    L[UI diff]
    M[Release risk score]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K --> L --> M
```

# Основные компоненты системы

## DOM-анализ страницы

Система получает HTML веб-страницы и извлекает структуру интерфейса.

Используемые технологии:

- Selenium — загрузка страницы
- BeautifulSoup — анализ DOM

На этом этапе извлекаются основные элементы интерфейса:

- input  
- button  
- form  
- link  
- table  
- image  

---

## Декомпозиция интерфейса

DOM преобразуется в **testable objects** — нормализованные элементы интерфейса, пригодные для тестирования.

Примеры:
##
```
Sites/
site_name/
runs/
run_001/
run_002/
run_003/
```

Каждый run содержит артефакты анализа.

---

# Артефакты запуска

В папке run сохраняются:

- testable_objects.json  
- representative_elements.json  
- generated_test_cases.json  
- site_risk_analysis.json  
- ui_diff_report.json  
- run_summary.json  

Это позволяет анализировать историю изменений интерфейса.

---

# Diff-анализ интерфейса

Система сравнивает DOM между двумя запусками.

Определяются:

- добавленные элементы
- удалённые элементы
- изменённые элементы

После этого LLM выполняет **AI-анализ изменений** и выявляет потенциальные зоны регрессии.

---

# Release Risk Score

На основе diff интерфейса вычисляется метрика **Release Risk Score**, которая помогает оценить потенциальную опасность изменений.

Score учитывает:

- количество добавленных элементов
- количество удалённых элементов
- количество изменённых элементов

Это позволяет QA-инженеру быстрее определить приоритеты тестирования.

---

# Используемые технологии

- Python  
- Selenium  
- BeautifulSoup  
- LlamaIndex  
- Sentence Transformers  
- HuggingFace Embeddings  
- Transformers  
- VSEGPT API  

---

# Итог

AI Release Guardian демонстрирует архитектуру нейро-сотрудника, который помогает QA-инженеру анализировать интерфейсы и выявлять потенциальные риски перед релизом.

Проект объединяет:

- DOM-анализ интерфейса
- RAG-архитектуру
- LLM reasoning
- diff-анализ интерфейсов

и показывает возможный подход к построению **AI-инструментов для QA-аналитики**.


## CI/CD release gate

The deterministic release policy is available as a machine-readable endpoint:

`GET /api/v1/projects/{project_id}/release-gate`

Example response:

```json
{
  "project_id": 1,
  "status": "READY",
  "allowed": true,
  "exit_code": 0,
  "reason": "Comparable routes satisfy the configured deterministic release policy.",
  "overall_risk_score": 18,
  "overall_risk_level": "LOW",
  "comparable_routes": 3,
  "incomplete_routes": 0
}
```

CI runners should treat `allowed=false` (or `exit_code=1`) as a failed quality gate before deployment. The HTTP request itself returns 200 when the gate was evaluated successfully; gate failure is represented in the response body rather than conflated with an API transport error.


### GitHub Actions integration

A ready-to-run example is included at `.github/workflows/release-gate-example.yml`.

Run it manually with the Guardian API URL and project ID. The workflow calls the machine-readable release gate, prints the evaluated status/reason/risk, and exits non-zero when `allowed=false`. A real deployment job can use the same gate job as a prerequisite with `needs: release-gate`, so deployment only starts after Guardian returns `READY`.

For production use, point `guardian_url` at the deployed Guardian API rather than localhost and protect the endpoint appropriately when it is not on a trusted private network.
