LANG = "en"
TEXT = {
 "en": {
  "add":"Add entry","edit":"Edit","delete":"Delete","run":"Run","search":"Search entries...",
  "name":"Name","kind":"Type","executable":"Executable / path","arguments":"Arguments (one per line)",
  "working_dir":"Working directory (optional)","favorite":"Favorite","save":"Save","cancel":"Cancel",
  "choose":"Select an entry first.","confirm_delete":"Delete this entry?","done":"Entry saved.",
  "deleted":"Entry deleted.","run_started":"Started: ","run_failed":"Could not start: ",
  "project_opened":"Project folder opened.","import":"Import JSON","export":"Export JSON",
  "qt_missing":"PySide6 is not installed.","cli_hint":"Run with --cli for terminal mode.",
  "no_entries":"No entries yet. Add your first one.","recent":"Recent activity"
 },
 "ru": {
  "add":"Добавить","edit":"Изменить","delete":"Удалить","run":"Запустить","search":"Поиск записей...",
  "name":"Название","kind":"Тип","executable":"Программа / путь","arguments":"Аргументы (по одному на строку)",
  "working_dir":"Рабочая папка (необязательно)","favorite":"Избранное","save":"Сохранить","cancel":"Отмена",
  "choose":"Сначала выбери запись.","confirm_delete":"Удалить эту запись?","done":"Запись сохранена.",
  "deleted":"Запись удалена.","run_started":"Запущено: ","run_failed":"Не удалось запустить: ",
  "project_opened":"Папка проекта открыта.","import":"Импорт JSON","export":"Экспорт JSON",
  "qt_missing":"PySide6 не установлен.","cli_hint":"Для терминального режима запусти с --cli.",
  "no_entries":"Записей пока нет. Добавь первую.","recent":"Недавние запуски"
 }
}
def set_language(language=None):
    global LANG
    if language in ("en","ru"): LANG = language
def tr(key):
    return TEXT.get(LANG, TEXT["en"]).get(key, key)
