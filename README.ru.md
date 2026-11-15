# QuickDock

Кроссплатформенный лаунчер команд, приложений, скриптов и папок проектов.

**Платформы:** Windows, Linux, Android/Termux (CLI).  
**Языки:** русский и английский.

## Возможности
- Добавление, редактирование, удаление и поиск записей
- Избранное и история запусков
- Типы: `command`, `application`, `script`, `project`
- SQLite и импорт/экспорт JSON
- Графический интерфейс PySide6 и терминальный режим
- Обычные команды запускаются через `subprocess.Popen([...], shell=False)`

## Установка

Нужен Python 3.10 или новее.

### Windows (PowerShell)
```powershell
py -3 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Android / Termux
```bash
pkg update
pkg install python
cd QuickDock
python main.py --cli
```
CLI работает на стандартной библиотеке Python. Обычный Termux не предоставляет desktop-среду для PySide6, поэтому Android GUI в этот релиз не входит.

## Запуск
```bash
python main.py          # графический интерфейс
python main.py --cli    # терминал
python main.py --lang ru
python main.py --lang en --cli
```

## Типы записей
- `command` — команда и аргументы, например `python` + `--version`
- `application` — исполняемый файл приложения, например `code`
- `script` — скрипт; интерпретатор указывается явно
- `project` — существующая папка, открываемая файловым менеджером

В GUI аргументы вводятся по одному на строку. В CLI аргументы с пробелами нужно заключать в кавычки.

## Безопасность
- Для обычных команд shell не используется.
- QuickDock не запрашивает root/администратора.
- Команды всё равно могут изменять файлы и запускать другие программы с правами текущего пользователя. Добавляй только доверенные команды.
- Запись `project` открывает папку, но не запускает её код.
- История хранит название, время и статус, но не вывод процесса.

## Данные
- База: `~/.quickdock/quickdock.db`

## Тесты
```bash
python -m unittest discover -s tests -v
```

## Лицензия
MIT. См. `LICENSE`.
