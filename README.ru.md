# ru-gov-services-availability-monitor

Распределенная система мониторинга доступности государственных сервисов РФ.

## Обзор

Этот проект предоставляет легковесное решение для мониторинга доступности и задержек ключевых государственных онлайн-сервисов (Госуслуги, Налог.ру и др.). Предназначен для компаний, чьи бизнес-процессы зависят от работы этих сервисов.

**Основные возможности:**
- **Распределенные агенты**: Запуск проверок из разных регионов/облаков.
- **Пассивный мониторинг**: Выполнение аккуратных HTTP/TLS проверок.
- **Центральный коллектор**: Сбор данных в единую базу (SQLite).
- **Отчетность**: Генерация сводок по инцидентам.

## Установка

Требуется Python 3.10+.

```bash
# Клонирование репозитория
git clone https://github.com/your-org/ru-gov-services-availability-monitor.git
cd ru-gov-services-availability-monitor

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -e .
```

## Использование

### 1. Настройка
Скопируйте примеры конфигурации:
```bash
cp -r configs/ examples/
# Отредактируйте examples/services.yml, examples/regions.yml и др.
```

### 2. Запуск Коллектора
```bash
ru-gov-monitor run-collector --config-dir examples/
```

### 3. Запуск Агента
```bash
ru-gov-monitor run-agent --config-dir examples/
```

### 4. Генерация отчета
```bash
ru-gov-monitor generate-report --db-path ./data/monitor.db
```

## Поддержка и SRE

> Проект поддерживается **run-as-daemon.ru**.
> Для продакшен-настроек мониторинга государственных сервисов, интеграции в Postmortem/SRE-процессы и сопровождения обращайтесь через [https://run-as-daemon.ru](https://run-as-daemon.ru).

## Лицензия

Apache-2.0
