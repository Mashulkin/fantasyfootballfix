# Fantasy Football Fix Parser v2.0

Улучшенный парсер для получения статистики игроков и команд с сайта Fantasy Football Fix с автоматической авторизацией, расширенным логированием и обработкой ошибок.

## Новые возможности v2.0

✅ **Автоматическая авторизация** - больше не нужно вручную копировать session ID  
✅ **Улучшенная обработка ошибок** - надежная работа при сетевых сбоях  
✅ **Подробное логирование** - отслеживание всех операций  
✅ **Валидация данных** - проверка и очистка полученных данных  
✅ **Прогресс-трекинг** - отчеты о ходе выполнения  
✅ **Соответствие PEP 8** - чистый и читаемый код  
✅ **Гибкие настройки** - переменные окружения и конфигурация  
✅ **Поддержка команд** - парсер для команд обновлен до v2.0  

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd fff-parser
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации

#### Вариант A: Переменные окружения (рекомендуется)
```bash
# Linux/Mac
export FFF_EMAIL="your-email@example.com"
export FFF_PASSWORD="your-password"
export ENVIRONMENT="production"

# Windows
set FFF_EMAIL=your-email@example.com
set FFF_PASSWORD=your-password
set ENVIRONMENT=production
```

#### Вариант B: Файл .env
Создайте файл `.env` в корне проекта:
```env
FFF_EMAIL=your-email@example.com
FFF_PASSWORD=your-password
ENVIRONMENT=development
```

#### Вариант C: Прямое редактирование settings/general.py
```python
EMAIL = 'your-email@example.com'
PASSWORD = 'your-password'
```

## Использование

### Базовое использование

```bash
# Парсинг всего сезона (все игровые недели, дома и в гостях)
python players.py
python teams.py
```

### Расширенные опции

```bash
# Парсинг конкретного диапазона игровых недель
python players.py --min-gw 1 --max-gw 5
python teams.py --min-gw 1 --max-gw 5

# Парсинг только домашних игр
python players.py --venue home
python teams.py --venue home

# Парсинг только гостевых игр  
python players.py --venue away
python teams.py --venue away

# Парсинг одной игровой недели
python players.py --min-gw 10 --max-gw 10
python teams.py --min-gw 10 --max-gw 10

# Использование кастомного конфига
python players.py --config ./my_settings/custom.py
python teams.py --config ./my_settings/custom.py
```

### Примеры команд

```bash
# Полный сезон для игроков и команд
python players.py --min-gw 1 --max-gw 38 --venue home/away
python teams.py --min-gw 1 --max-gw 38 --venue home/away

# Первые 10 недель только дома
python players.py --min-gw 1 --max-gw 10 --venue home
python teams.py --min-gw 1 --max-gw 10 --venue home

# Текущая неделя для команд
python teams.py --min-gw 15 --max-gw 15 --venue home/away
```

## Структура проекта

```
project/
├── common_modules/          # Общие модули
│   ├── __init__.py
│   ├── parser.py           # HTTP клиент с retry логикой
│   ├── csv_w.py           # Запись CSV
│   ├── json_rw.py         # Работа с JSON
│   ├── validation.py      # Валидация данных
│   ├── config.py          # Конфигурация
│   └── logger.py          # Логирование
├── functions/              # Функции парсера
│   ├── __init__.py
│   ├── auth.py            # Модуль авторизации
│   ├── statistic.py       # API клиент для FFF
│   └── format.py          # Форматирование данных
├── players.py             # Основной скрипт для игроков
├── teams.py               # Основной скрипт для команд (v2.0)
├── settings/
│   ├── general.py         # Основные настройки
│   ├── FFFplayers.txt     # Колонки для игроков
│   └── FFFteams.txt       # Колонки для команд
├── data/                  # Выходные CSV файлы
├── logs/                  # Лог файлы
└── requirements.txt       # Зависимости
```

## Настройки

### Основные параметры в settings/general.py

```python
# Аутентификация
EMAIL = 'your-email@example.com'
PASSWORD = 'your-password'

# Сезон
YEAR = '2024'

# Пути к файлам игроков
COLUMNS = './settings/FFFplayers.txt'
RESULT_FILE = ['./data/FFFplayers.csv']

# Пути к файлам команд
COLUMNS_TEAMS = './settings/FFFteams.txt'
RESULT_FILE_TEAMS = ['./data/FFFteams.csv']

# HTTP настройки
REQUEST_TIMEOUT = 30
REQUEST_RETRIES = 3
REQUEST_DELAY = 1
```

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `FFF_EMAIL` | Email для авторизации | `user@example.com` |
| `FFF_PASSWORD` | Пароль для авторизации | `mypassword` |
| `FFF_SESSION_ID` | Ручной session ID (fallback) | `abc123...` |
| `ENVIRONMENT` | Окружение (development/production) | `production` |

## Логирование

Все операции логируются в файлы в папке `logs/`:

```
logs/
├── parser_fff_players_2025-06-13.log    # Логи парсера игроков
├── parser_fff_teams_2025-06-13.log      # Логи парсера команд
├── parser_fff_auth_2025-06-13.log       # Логи авторизации
└── parser_fff_stats_2025-06-13.log      # Логи API запросов
```

### Уровни логирования

- **DEBUG**: Детальная информация для отладки
- **INFO**: Общая информация о процессе
- **WARNING**: Предупреждения (не критичные ошибки)
- **ERROR**: Ошибки выполнения

## Обработка ошибок

### Автоматические повторные попытки

- HTTP запросы автоматически повторяются при сбоях
- Экспоненциальная задержка между попытками
- Автоматическое восстановление сессии при истечении

### Типичные ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Authentication failed` | Неверные credentials | Проверьте EMAIL и PASSWORD |
| `Session expired` | Истекла сессия | Автоматически перелогинится |
| `Connection timeout` | Медленное соединение | Увеличьте REQUEST_TIMEOUT |
| `Rate limited` | Слишком частые запросы | Увеличьте REQUEST_DELAY |

## Валидация данных

Автоматическая валидация включает:

- ✅ Проверка email адресов
- ✅ Очистка текстовых полей
- ✅ Валидация числовых значений
- ✅ Проверка обязательных полей
- ✅ Форматирование позиций игроков
- ✅ Нормализация названий команд

## Миграция с v1.0

### Обратная совместимость

Все старые скрипты продолжат работать без изменений.

### Поэтапная миграция

1. **Установите зависимости**: `pip install -r requirements.txt`
2. **Добавьте credentials**: настройте EMAIL и PASSWORD
3. **Протестируйте**: запустите `python players.py --min-gw 1 --max-gw 1`
4. **Протестируйте команды**: запустите `python teams.py --min-gw 1 --max-gw 1`
5. **Обновите скрипты**: постепенно переходите на новые возможности

### Изменения в API

```python
# Старый способ
from functions.statistic import get_statisticPlayers, get_statisticTeams
players_stats = get_statisticPlayers(1, 1, 'home', '2024')
teams_stats = get_statisticTeams(1, 1, 'home', '2024')

# Новый способ (рекомендуется)
from statistic import FFFStatsClient
from auth import get_fff_session

session_id = get_fff_session('email', 'password')
client = FFFStatsClient('api_url', session_id)
players_stats = client.get_players_stats(1, 1, 'home', '2024')
teams_stats = client.get_teams_stats(1, 1, 'home', '2024')
```

## Мониторинг и статистика

### Статистика выполнения

В конце каждого запуска выводится подробная статистика:

```
=== Parser Statistics ===
successful_gameweeks: 38
total_gameweeks: 38
success_rate: 100.0%
duration_seconds: 125.5
teams_processed: 760  # для teams.py
players_processed: 2850  # для players.py
errors_encountered: 0
requests_made: 76
successful_requests: 76
failed_requests: 0
========================
```

### Отслеживание прогресса

```
2025-06-13 12:00:01 - parser.fff_players - INFO - Processing gameweek 1/38
2025-06-13 12:00:05 - parser.fff_players - INFO - Successfully completed GW1, venue: home
2025-06-13 12:00:10 - parser.fff_players - INFO - Processing gameweek 2/38

2025-06-13 12:05:01 - parser.fff_teams - INFO - Processing gameweek 1/38
2025-06-13 12:05:03 - parser.fff_teams - INFO - Successfully completed GW1, venue: home
2025-06-13 12:05:05 - parser.fff_teams - INFO - Processing gameweek 2/38
```

## Производительность

### Оптимизации

- **Retry логика**: Автоматические повторы при сбоях
- **Session reuse**: Переиспользование HTTP сессий
- **Smart delays**: Умные задержки между запросами
- **Data validation**: Проверка данных на этапе получения
- **Memory efficient**: Обработка данных по частям

### Рекомендации

- Используйте `REQUEST_DELAY >= 1` для production
- Мониторьте логи на предмет ошибок
- Регулярно проверяйте актуальность credentials
- Используйте переменные окружения для sensitive данных

## Troubleshooting

### Проблемы с авторизацией

```bash
# Проверьте credentials
python -c "from functions.auth import get_fff_session; print(get_fff_session('email', 'password'))"

# Очистите кэш сессии
rm data/.fff_session_cache.json
```

### Проблемы с данными

```bash
# Проверьте колонки
cat settings/FFFplayers.txt
cat settings/FFFteams.txt

# Проверьте выходные файлы
head -n 5 data/FFFplayers.csv
head -n 5 data/FFFteams.csv
```

### Проблемы с сетью

```bash
# Тест соединения
curl -I https://www.fantasyfootballfix.com

# Проверьте логи
tail -f logs/parser_fff_players_$(date +%Y-%m-%d).log
tail -f logs/parser_fff_teams_$(date +%Y-%m-%d).log
```

## Разработка

### Запуск тестов

```bash
pytest tests/
```

### Форматирование кода

```bash
black *.py common_modules/*.py functions/*.py
flake8 *.py common_modules/*.py functions/*.py
```

### Добавление новых функций

1. Создайте ветку: `git checkout -b feature/new-feature`
2. Следуйте PEP 8
3. Добавьте тесты
4. Обновите документацию
5. Создайте pull request

## FAQ

**Q: Как часто нужно обновлять session ID?**  
A: Не нужно! Теперь авторизация происходит автоматически.

**Q: Можно ли запускать парсер параллельно?**  
A: Не рекомендуется из-за rate limiting на стороне сервера.

**Q: Как добавить новые поля в вывод?**  
A: Отредактируйте `settings/FFFplayers.txt` или `settings/FFFteams.txt`.

**Q: Парсер работает медленно, как ускорить?**  
A: Уменьшите `REQUEST_DELAY`, но будьте осторожны с rate limiting.

**Q: Как парсить только определенных игроков/команды?**  
A: Используйте фильтры после получения данных или модифицируйте API запросы.

**Q: В чем разница между players.py и teams.py?**  
A: `players.py` парсит статистику отдельных игроков, `teams.py` - статистику команд.

## Поддержка

- 📧 Email: 
- 🐛 Issues: 
- 📖 Docs: 

## Лицензия



---

**Версия 2.0** | Последнее обновление: 13 июня 2025