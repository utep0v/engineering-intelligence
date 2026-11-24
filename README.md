# Engineering Intelligence

Навык для Codex, который помогает разобраться в существующем продукте и решить, что менять дальше. При аудите Codex прослеживает реальные вызовы по коду и отмечает, какие выводы подтверждены, а какие вопросы ещё открыты. Для интерфейса он проходит основной сценарий в браузере. Если две трактовки бизнес-правила дают разные результаты, навык спрашивает владельца до изменения кода.

## Установка версии 1.0

Отправьте эту строку в Codex.

```text
$skill-installer Установи навык из https://github.com/utep0v/engineering-intelligence/tree/v1.0/skills/engineering-intelligence
```

Для установки вручную скачайте ZIP и следуйте короткой инструкции для Mac. [Скачать Engineering Intelligence 1.0](https://github.com/utep0v/engineering-intelligence/releases/download/v1.0/engineering-intelligence-1.0.zip) · [Инструкция по установке](skills/engineering-intelligence/README.md#установка-из-архива-на-mac)

## Первый запуск

Откройте нужный проект и отправьте один из запросов.

```text
$engineering-intelligence Проведи архитектурный аудит проекта. Пока ничего не меняй.
$engineering-intelligence Хотим добавить ночную выгрузку заказов для партнёра. Оцени архитектурные последствия для команды из двух человек.
$engineering-intelligence Проверь оформление заказа на телефоне и компьютере. Покажи, что мешает, а что стоит сохранить.
```

Режимы `audit`, `architecture/plan`, `implement`, `design-review` и `verify` выбираются по запросу. Для существенных решений ведущий привлекает независимого критика. Подтверждённые решения и планы можно восстановить в следующем сеансе из локального журнала проекта. [Описание режимов](skills/engineering-intelligence/SKILL.md) · [Правила ведения журнала](skills/engineering-intelligence/references/project-knowledge.md) · [Сценарии проверки](skills/engineering-intelligence/evals/scenarios.md)
