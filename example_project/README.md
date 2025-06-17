# DFT Example Project

Пример использования DFT для аналитических пайплайнов.

## 🚀 Быстрый запуск

### 1. Установка DFT

```bash
# Перейти в основную директорию DFT
cd ..

# Установить пакет (зависимости установятся автоматически)
pip install .

# Вернуться в example_project
cd example_project
```

### 2. Настройка проекта

```bash
# Скопировать example .env файл
cp .env.example .env

# Отредактировать .env файл с вашими подключениями
nano .env
```

### 3. Тестовый запуск (CSV)

```bash
# Запустить простой CSV пример без БД
dft run --select simple_csv_example
```

### 4. Настройка БД подключений

Отредактируйте `.env` файл:

```bash
# PostgreSQL (ваша продакшн БД)
POSTGRES_HOST=your-postgres-host.com
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# ClickHouse (аналитическое хранилище)
CH_HOST=your-clickhouse-host.com
CH_DATABASE=analytics
CH_USER=default
CH_PASSWORD=your_ch_password
```

### 5. Запуск реальных пайплайнов

```bash
# Ежедневная загрузка выручки (инкрементально)
dft run --select daily_revenue

# Еженедельный анализ когорт
dft run --select user_cohorts

# Запуск всех daily пайплайнов
dft run --select tag:daily

# Полный перезапуск (игнорировать state)
dft run --select daily_revenue --full-refresh
```

## 📁 Структура проекта

```
example_project/
├── dft_project.yml          # Конфигурация проекта и подключений к БД
├── .env                     # Секретные переменные (создать из .env.example)
├── .env.example            # Пример переменных окружения
├── data/                   # Тестовые данные
│   └── sample_data.csv
├── pipelines/              # YAML пайплайны
│   ├── daily_revenue.yml   # Инкрементальная загрузка выручки
│   ├── user_cohorts.yml    # Еженедельный анализ когорт  
│   └── simple_csv_example.yml  # Простой пример без БД
└── output/                 # Выходные файлы (создается автоматически)
```

## 🔧 Примеры пайплайнов

### 1. simple_csv_example.yml
- **Назначение**: Простой пример для тестирования без БД
- **Входные данные**: CSV файл
- **Обработка**: Валидация данных
- **Выходные данные**: Обработанный CSV

### 2. daily_revenue.yml  
- **Назначение**: Ежедневная загрузка данных о выручке
- **Входные данные**: PostgreSQL таблица transactions
- **Обработка**: Валидация и фильтрация данных
- **Выходные данные**: ClickHouse таблица daily_revenue_raw
- **Инкрементальность**: Автоматически обрабатывает только новые даты

### 3. user_cohorts.yml
- **Назначение**: Еженедельный анализ пользовательских когорт
- **Входные данные**: PostgreSQL таблицы users, user_daily_stats  
- **Обработка**: Валидация размера когорт
- **Выходные данные**: ClickHouse таблицы cohorts и activity
- **Частота**: Еженедельно (до последнего понедельника)

## 🎯 Инкрементальная обработка

DFT автоматически отслеживает состояние каждого пайплайна:

```yaml
variables:
  # При первом запуске: начать с 7 дней назад
  # При следующих запусках: начать с последней обработанной даты + 1 день
  start_date: "{{ state.get('last_processed_date', days_ago(7)) }}"
  end_date: "{{ yesterday() }}"
```

State файлы сохраняются в `.dft/state/` и автоматически обновляются после успешного выполнения.

## 🔍 Мониторинг и отладка

```bash
# Проверить все пайплайны на ошибки конфигурации
dft validate

# Проверить зависимости
dft deps

# Посмотреть state конкретного пайплайна
cat .dft/state/pipeline_daily_revenue_last_processed_date.json

# Посмотреть логи
tail -f .dft/logs/pipeline_execution.log
```

## 🚨 Решение проблем

### Ошибка подключения к БД
1. Проверьте `.env` файл
2. Убедитесь, что БД доступна из вашей сети
3. Проверьте права пользователя

### Пайплайн не находит данные
1. Проверьте диапазон дат в variables
2. Убедитесь, что данные существуют в источнике
3. Запустите с `--full-refresh` для полного перезапуска

### Проблемы с инкрементальностью
1. Удалите state файл: `rm .dft/state/pipeline_NAME_*.json`
2. Запустите с нужными датами: `--vars start_date=2024-01-01,end_date=2024-01-31`