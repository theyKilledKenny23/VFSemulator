# Эмулятор оболочки UNIX-подобной ОС

## Общее описание

Графический эмулятор командной строки (GUI на tkinter).
Поддерживает парсинг аргументов в кавычках, команды-заглушки
`ls`, `cd`, `help`, `exit` и вывод сообщений об ошибках.

Заголовок окна содержит имя VFS.

## Функции и настройки

| Команда | Описание                              |
|---------|---------------------------------------|
| ls      | Выводит имя команды и аргументы       |
| cd      | Выводит имя команды и аргументы       |
| help    | Список доступных команд               |
| exit    | Завершение работы эмулятора           |

Парсер корректно обрабатывает аргументы в кавычках
(например, `ls "my folder" file.txt`).

## Сборка и запуск

### Запуск приложения

```bash
# Linux / macOS
bash run.sh

# Windows
run.bat

# или напрямую
python src/main.py
```

### Параметры командной строки

| Параметр       | Описание                    |
|----------------|-----------------------------|
| `--vfs-path`   | Путь к физическому VFS      |
| `--log-file`   | Путь к CSV лог-файлу        |
| `--script`     | Путь к стартовому скрипту   |

### Примеры запуска

```bash
# С логированием
python src/main.py --log-file logs/run.csv

# Со стартовым скриптом
python src/main.py --script scripts/demo.txt

# Со всеми параметрами
python src/main.py --vfs-path ./data/vfs.zip \
                   --script scripts/demo.txt \
                   --log-file logs/run.csv
```
### Тестирование различных VFS

```bash
# Минимальная VFS (1 файл)
scripts\run_minimal_vfs.bat

# Простая VFS (несколько файлов и папок)
scripts\run_simple_vfs.bat

# Сложная VFS (3+ уровней вложенности)
scripts\run_complex_vfs.bat

# Тестирование всех команд через стартовый скрипт
python src\main.py --vfs-path vfs\simple.xml --script scripts\test_stage3.txt --log-file logs\test_stage3.csv