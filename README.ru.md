# 📊 RU Gov Services Availability Monitor

[![CI](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

🇷🇺 Русская версия | 🇬🇧 [English version](README.md)

**Автор:** [Ranas Mukminov](https://github.com/ranas-mukminov) | **Сайт:** [https://run-as-daemon.ru](https://run-as-daemon.ru)

Распределённая система мониторинга доступности и производительности федеральных государственных онлайн-сервисов России. Разработана для организаций, MSP и IT-подразделений, которые зависят от государственных порталов и нуждаются в проактивном оповещении о сбоях или деградации сервисов.

## Описание

RU Gov Services Availability Monitor — это лёгкое Python-решение для пассивного мониторинга публичных государственных сервисов, таких как Госуслуги, порталы налоговой службы и другие федеральные сайты. Система использует архитектуру распределённых агентов для измерения доступности, задержек и состояния TLS-сертификатов из различных географических точек России.

В отличие от традиционных систем мониторинга, этот проект специально создан для:
- **Отслеживания бизнес-зависимостей**: Мониторинг сервисов, от которых зависят ваши операции (аутентификация, налоговая отчётность, проверка лицензий).
- **Мультирегиональной видимости**: Развёртывание агентов в разных городах для обнаружения региональных сбоев.
- **Интеграции с observability**: Хранение метрик в SQLite (MVP) с планами по экспорту в Prometheus и дашбордам Grafana.
- **Соблюдения законодательства**: Только пассивные проверки — без нагрузочного тестирования, обхода защиты, с уважением к robots.txt и rate limits.

## Основные возможности

- **Архитектура распределённых агентов** — Запуск агентов в Москве, Санкт-Петербурге и других регионах для обнаружения локальных сбоев.
- **Пассивные HTTP/HTTPS-проверки** — Неинтрузивные GET/HEAD-запросы с настраиваемыми интервалами (по умолчанию: 60 секунд).
- **Валидация TLS-сертификатов** — Отслеживание дат истечения и изменений в наборах шифров.
- **Центральный collector API** — Агенты передают метрики в collector на базе FastAPI с хранением в SQLite.
- **Отчёты об инцидентах** — Генерация отчётов с суммированием простоев, всплесков задержек и частоты ошибок.
- **Конфигурация как код** — YAML-конфигурация для сервисов, регионов и назначений агентов.
- **Готовность к CI/CD** — Автоматическое тестирование, линтинг (Black, Ruff) и проверка безопасности (Bandit, pip-audit).
- **Низкий расход ресурсов** — Работает на минимальных виртуальных машинах (1 vCPU, 512 МБ RAM на агента).

## Архитектура и компоненты

Система состоит из трёх основных компонентов:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Агент (МСК)   │────────▶│                 │◀────────│   Агент (СПБ)   │
│  HTTP-клиент    │  POST   │  Collector API  │  POST   │  HTTP-клиент    │
│  Периодич. чеки │         │  (FastAPI)      │         │  Периодич. чеки │
└─────────────────┘         └────────┬────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ SQLite-хранилище│
                            │  (monitor.db)   │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Генератор      │
                            │    отчётов      │
                            └─────────────────┘
```

**Компоненты:**
1. **Агент** — Выполняет периодические проверки указанных сервисов, измеряет задержку и доступность, отправляет результаты в collector.
2. **Collector** — REST API, принимающий метрики от агентов и сохраняющий их в SQLite-базу.
3. **Генератор отчётов** — CLI-инструмент для анализа сохранённых метрик и создания сводок по инцидентам.

## Требования

### Операционная система
- **Linux**: Ubuntu 22.04/24.04, Debian 11/12, Rocky Linux 9 или любой современный дистрибутив
- **Python**: 3.10 или выше (рекомендуется 3.11)

### Системные ресурсы
- **Агент**: 512 МБ RAM, 1 vCPU, 100 МБ дискового пространства на агента
- **Collector**: 1 ГБ RAM, 1 vCPU, 1 ГБ дискового пространства (растёт с объёмом метрик)

### Сеть
- Исходящий HTTPS (443) доступ к мониторируемым сервисам
- Входящий HTTP (порт по умолчанию 8080) для collector, если агенты удалённые
- Рекомендуется: правила firewall для ограничения доступа к collector только с известных IP агентов

### Зависимости
Все Python-зависимости управляются через `pyproject.toml`:
- `httpx` — Асинхронный HTTP-клиент для проверок сервисов
- `pydantic` — Валидация конфигурации
- `fastapi` + `uvicorn` — REST API collector'а
- `click` — CLI-интерфейс
- `PyYAML` — Парсинг конфигурационных файлов

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor
```

### 2. Настройка Python-окружения
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Настройка сервисов и регионов
Отредактируйте конфигурационные файлы в `configs/`:

```bash
# Определите сервисы для мониторинга
nano configs/services.yml

# Определите регионы мониторинга
nano configs/regions.yml

# Настройте параметры агента
nano configs/agent.yml

# Настройте параметры collector
nano configs/collector.yml
```

### 4. Запуск collector
```bash
ru-gov-monitor run-collector --config-dir ./configs
```
Collector API запустится по адресу `http://0.0.0.0:8080`.

### 5. Запуск агента
В отдельном терминале (или на удалённой машине):
```bash
ru-gov-monitor run-agent --config-dir ./configs
```

### 6. Генерация отчёта
После того, как агенты собрали метрики:
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

## Подробная установка

### Установка на Ubuntu / Debian

```bash
# Установите Python 3.10+, если ещё не установлен
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# Клонируйте репозиторий
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установите пакет
pip install -e .

# Проверьте установку
ru-gov-monitor --help
```

### Установка на RHEL / Rocky / Alma

```bash
# Установите Python 3.10+
sudo dnf install -y python3 python3-pip git

# Клонируйте репозиторий
git clone https://github.com/ranas-mukminov/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установите пакет
pip install -e .
```

### Запуск как systemd-сервис

Создайте unit-файл для collector:

```bash
sudo nano /etc/systemd/system/ru-gov-monitor-collector.service
```

```ini
[Unit]
Description=RU Gov Services Monitor Collector
After=network.target

[Service]
Type=simple
User=monitoring
WorkingDirectory=/opt/ru-gov-monitor
ExecStart=/opt/ru-gov-monitor/.venv/bin/ru-gov-monitor run-collector --config-dir /opt/ru-gov-monitor/configs
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Включите и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ru-gov-monitor-collector
sudo systemctl status ru-gov-monitor-collector
```

Повторите процесс для агентов, заменив `run-collector` на `run-agent`.

## Настройка

Вся конфигурация хранится в YAML-файлах в каталоге `configs/`.

### services.yml

Определяет государственные сервисы для мониторинга:

```yaml
services:
  - id: "gosuslugi"
    name: "Public Services Portal"
    url: "https://www.gosuslugi.ru"
    expected_status: 200
    tags: ["federal", "critical"]

  - id: "nalog"
    name: "Tax Service"
    url: "https://www.nalog.gov.ru"
    expected_status: 200
    tags: ["federal", "finance"]
```

**Поля:**
- `id` — Уникальный идентификатор сервиса
- `name` — Человекочитаемое имя
- `url` — Полный URL для проверки (должен быть публично доступен)
- `expected_status` — Ожидаемый HTTP-код статуса (по умолчанию: 200)
- `tags` — Опциональные метки для фильтрации и отчётов

### regions.yml

Определяет регионы мониторинга:

```yaml
regions:
  - id: "msk-1"
    name: "Moscow DC 1"
    location: "Moscow, Russia"

  - id: "spb-1"
    name: "St. Petersburg DC 1"
    location: "St. Petersburg, Russia"
```

### agent.yml

Настройка поведения агента:

```yaml
agent:
  region_id: "msk-1"
  collector_url: "http://collector.example.com:8080"
  services:
    - "gosuslugi"
    - "nalog"
  max_concurrency: 5
```

**Поля:**
- `region_id` — Регион, который представляет агент (должен совпадать с `regions.yml`)
- `collector_url` — Базовый URL Collector API
- `services` — Список ID сервисов для мониторинга (из `services.yml`)
- `max_concurrency` — Максимальное количество одновременных проверок

### collector.yml

Настройка Collector API:

```yaml
collector:
  host: "0.0.0.0"
  port: 8080
  storage_path: "./data/monitor.db"
```

**Поля:**
- `host` — Адрес привязки (используйте `0.0.0.0` для приёма соединений от удалённых агентов)
- `port` — Порт API
- `storage_path` — Путь к файлу базы данных SQLite

## Использование

### Валидация конфигурации

Перед запуском агентов или collector проверьте конфигурационные файлы:

```bash
ru-gov-monitor validate-config --config-dir ./configs
```

### Ручной запуск компонентов

**Collector:**
```bash
ru-gov-monitor run-collector --config-dir ./configs
```

**Агент:**
```bash
ru-gov-monitor run-agent --config-dir ./configs
```

### Генерация отчётов об инцидентах

```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

Пример вывода:
```
Incident Report
===============
Service: gosuslugi
- Total checks: 1440
- Availability: 99.8%
- Average latency: 123.4ms
- Incidents: 2
  - 2025-11-20 14:23:00 - 14:25:00 (2 min) - HTTP 503
  - 2025-11-20 18:10:00 - 18:10:30 (30 sec) - Timeout
```

### Доступ к API collector

Collector предоставляет REST API:

**Отправка метрик (используется агентами):**
```bash
POST http://localhost:8080/api/v1/metrics
Content-Type: application/json

{
  "service_id": "gosuslugi",
  "timestamp": "2025-11-21T12:00:00Z",
  "status_code": 200,
  "latency_ms": 123.4,
  "available": true,
  "region_id": "msk-1"
}
```

**Проверка работоспособности:**
```bash
curl http://localhost:8080/health
```

## Обновление

Для обновления системы мониторинга до последней версии:

```bash
cd /path/to/ru-gov-services-availability-monitor
git pull origin main
source .venv/bin/activate
pip install -e .
```

**Перезапустите сервисы:**
```bash
sudo systemctl restart ru-gov-monitor-collector
sudo systemctl restart ru-gov-monitor-agent
```

**Критические изменения:**
- Перед обновлением проверяйте [CHANGELOG.md](CHANGELOG.md) на наличие инструкций по миграции.
- Изменения схемы базы данных могут потребовать ручной миграции в будущих версиях.

## Логи и устранение неполадок

### Расположение логов

**Systemd-сервисы:**
```bash
journalctl -u ru-gov-monitor-collector -f
journalctl -u ru-gov-monitor-agent -f
```

**Ручной запуск:**
Логи выводятся в stdout/stderr. При необходимости перенаправьте в файл:
```bash
ru-gov-monitor run-agent --config-dir ./configs >> /var/log/ru-gov-agent.log 2>&1
```

### Типичные проблемы

**Проблема: Агент не может подключиться к collector**
```
ERROR: Failed to report to collector: Connection refused
```
**Решение:**
- Проверьте, что `collector_url` в `agent.yml` указан корректно.
- Убедитесь, что collector запущен: `curl http://collector-host:8080/health`
- Проверьте правила firewall — порт 8080 должен быть открыт.

**Проблема: Порт 8080 уже используется**
```
ERROR: [Errno 98] Address already in use
```
**Решение:**
- Измените `port` в `collector.yml` на другое значение (например, 8081).
- Или остановите конфликтующий сервис: `sudo lsof -i :8080`

**Проблема: Нет метрик в базе данных**
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
# Вывод: No metrics found
```
**Решение:**
- Проверьте, что агент запущен и настроен правильно.
- Убедитесь, что `collector_url` указывает на работающий collector.
- Изучите логи collector на наличие ошибок.

**Проблема: Ошибки валидации TLS-сертификата**
```
ERROR: SSL verification failed
```
**Решение:**
- Обновите системные CA-сертификаты: `sudo update-ca-certificates`
- Если мониторите тестовый сервис с самоподписанным сертификатом, настройте `--no-verify-ssl` (НЕ рекомендуется для продакшена).

## Замечания по безопасности

> **⚠️ ВАЖНО:** Этот инструмент выполняет только пассивный мониторинг. Операторы несут полную ответственность за соблюдение законодательства РФ и соглашений об использовании мониторируемых ресурсов.

### Чек-лист безопасности

1. **Ограничьте доступ к collector**: Используйте правила firewall или reverse proxy с аутентификацией для предотвращения несанкционированной отправки метрик.
2. **Защитите связь агент-collector**: Рассмотрите использование HTTPS с TLS-сертификатами в продакшене.
3. **Rate limiting**: Настраивайте интервалы проверок разумно (по умолчанию 60 секунд). Не создавайте избыточную нагрузку.
4. **Уважайте robots.txt**: Убедитесь, что мониторируемые URL не запрещены в `robots.txt`.
5. **Никаких секретов в конфигах**: Никогда не коммитьте реальные URL или API-ключи в систему контроля версий. Используйте переменные окружения или системы управления секретами.
6. **Применяйте обновления безопасности**: Регулярно обновляйте Python-зависимости:
   ```bash
   pip install --upgrade -e .[dev]
   pip-audit
   ```

### Соблюдение законодательства

- Эта система выполняет HTTP GET/HEAD-запросы к публичным URL. Она не обходит WAF, CAPTCHA или аутентификацию.
- Операторы должны согласовывать с владельцами сервисов использование системы для коммерческого мониторинга.
- Подробные юридические соображения см. в [docs/security.ru.md](docs/security.ru.md).

## Структура проекта

```
ru-gov-services-availability-monitor/
├── configs/               # YAML-конфигурационные файлы
│   ├── agent.yml
│   ├── collector.yml
│   ├── regions.yml
│   └── services.yml
├── src/                   # Исходный код Python
│   └── ru_gov_services_availability_monitor/
│       ├── agent/         # Логика агента (HTTP-клиент, runner)
│       ├── collector/     # Collector API и хранилище
│       ├── config/        # Модели конфигурации
│       ├── reports/       # Генерация отчётов
│       └── cli.py         # Точка входа CLI
├── tests/                 # Юнит- и интеграционные тесты
├── docs/                  # Дополнительная документация
│   └── security.ru.md
├── .github/workflows/     # CI/CD-пайплайн
│   └── ci.yml
├── LICENSE                # Лицензия Apache-2.0
├── pyproject.toml         # Метаданные Python-проекта
└── README.md              # Этот файл
```

## Как внести вклад

Мы приветствуем участие в разработке! Чтобы внести свой вклад:

1. **Сделайте форк репозитория** на GitHub.
2. **Создайте ветку для новой функции**: `git checkout -b feature/your-feature-name`
3. **Внесите изменения**:
   - Следуйте стилю PEP 8 (проверяется Black и Ruff).
   - Добавьте тесты для новой функциональности.
   - Обновите документацию при необходимости.
4. **Запустите проверки локально**:
   ```bash
   black .
   ruff check .
   pytest
   ```
5. **Закоммитьте изменения**: Используйте чёткие, описательные сообщения коммитов.
6. **Отправьте изменения и откройте Pull Request** в ветку `main`.

### Стиль кода

- **Python**: Используйте форматтер Black (длина строки 120), линтер Ruff.
- **YAML**: Отступы 2 пробела, алфавитный порядок ключей где возможно.
- **Сообщения коммитов**: Начинайте с глагола (например, "Add feature", "Fix bug").

## Планы развития

Планируемые возможности для будущих релизов:

- [ ] Prometheus-экспортер метрик
- [ ] Шаблоны Grafana-дашбордов
- [ ] Поддержка PostgreSQL/TimescaleDB для крупномасштабных развёртываний
- [ ] Web UI для конфигурации и визуализации
- [ ] Оповещения через Telegram, email, webhooks
- [ ] Валидация тела ответа (поиск ключевых слов)
- [ ] Отслеживание DNS-резолвинга

Полный бэклог см. в [GitHub Issues](https://github.com/ranas-mukminov/ru-gov-services-availability-monitor/issues).

## Лицензия

Этот проект распространяется под лицензией **Apache License 2.0**. Подробности см. в [LICENSE](LICENSE).

```
Copyright 2025 run-as-daemon.ru

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Автор и коммерческая поддержка

**Автор:** [Ranas Mukminov](https://github.com/ranas-mukminov)

Для внедрения системы мониторинга в продакшене, кастомных интеграций, аудита инфраструктуры и постоянной SRE-поддержки посетите **[https://run-as-daemon.ru](https://run-as-daemon.ru)** или свяжитесь с автором через GitHub.

Предлагаемые услуги:
- **Инфраструктура мониторинга и observability** — Prometheus, Grafana, Loki, распределённая трассировка.
- **Процессы реагирования на инциденты** — Определение SLO/SLA, автоматизация on-call.
- **DevOps-консалтинг** — CI/CD, инфраструктура как код, усиление безопасности.
