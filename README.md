# Эмулятор оболочки UNIX-подобной ОС

## Общее описание

Графический эмулятор командной строки (GUI на tkinter).
Поддерживает виртуальную файловую систему (VFS), загружаемую из XML-файла,
парсинг аргументов в кавычках, логирование в CSV и выполнение стартовых скриптов.

Все операции с VFS производятся **только в памяти** — исходный XML-файл
не распаковывается и не модифицируется.

Заголовок окна содержит имя VFS (из атрибута `name` XML-файла).

## Функции и настройки

### Параметры командной строки

| Параметр       | Описание                    |
|----------------|-----------------------------|
| `--vfs-path`   | Путь к XML-файлу VFS        |
| `--log-file`   | Путь к CSV лог-файлу        |
| `--script`     | Путь к стартовому скрипту   |

### Логирование

События вызова команд записываются в CSV-файл со следующими полями:

- `timestamp` — дата и время
- `username` — имя пользователя ОС
- `command` — выполненная команда
- `error` — сообщение об ошибке (если была)

### Стартовый скрипт

- Поддерживает комментарии (строки, начинающиеся с `#`)
- Останавливается при первой ошибке
- Имитирует диалог с пользователем (выводит ввод и вывод)

### Виртуальная файловая система (VFS)

Источник: XML-файл. Двоичные данные кодируются в base64.

Пример структуры XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vfs name="my_vfs">
    <root>
        <file name="hello.txt">Hello, World!</file>
        <dir name="folder">
            <file name="data.txt">Content</file>
        </dir>
    </root>
</vfs>
```
## Команды эмулятора

| Команда              | Описание                                              |
|----------------------|-------------------------------------------------------|
| `ls [путь...]`       | Список файлов и каталогов                             |
| `cd [путь]`          | Сменить текущий каталог                               |
| `pwd`                | Показать текущий каталог                              |
| `tac <файл>`         | Вывести содержимое файла в обратном порядке строк     |
| `du <путь>`          | Показать размер файла или каталога (в байтах)         |
| `mkdir <путь>`       | Создать новый каталог (только в памяти)               |
| `help`               | Показать список команд                                |
| `exit`               | Выйти из эмулятора                                    |

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
### Примеры запуска

```bash
# С логированием
python src/main.py --log-file logs/run.csv

# Со стартовым скриптом
python src/main.py --script scripts/demo.txt

# С VFS и всеми параметрами
python src/main.py --vfs-path vfs/complex.xml \
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
python src\main.py --vfs-path vfs\complex.xml --script scripts\demo.txt --log-file logs\demo.csv
```
## Примеры использования

### Интерактивный режим

Запуск эмулятора со сложной VFS и логированием:

```bash
python src/main.py --vfs-path vfs/complex.xml --log-file logs/demo.csv
```

Диалог с эмулятором (демонстрация навигации, чтения файлов и создания каталогов в памяти):

```text
=== Параметры запуска ===
VFS: vfs/complex.xml
Лог-файл: logs/demo.csv
Скрипт: не задан
Пользователь: User
=========================
VFS 'complex_vfs' успешно загружена из vfs/complex.xml
Введите 'help' для списка команд.
complex_vfs@vfs:/$ ls
root_file.txt  level1  projects
complex_vfs@vfs:/$ cd level1
complex_vfs@vfs:/level1$ pwd
/level1
complex_vfs@vfs:/level1$ cd level2/level3
complex_vfs@vfs:/level1/level2/level3$ ls
l3_file.txt  binary.dat
complex_vfs@vfs:/level1/level2/level3$ tac l3_file.txt
Level 3 file
complex_vfs@vfs:/level1/level2/level3$ du .
31	.
complex_vfs@vfs:/level1/level2/level3$ mkdir new_folder
mkdir: каталог 'new_folder' создан
complex_vfs@vfs:/level1/level2/level3$ ls
l3_file.txt  binary.dat  new_folder
complex_vfs@vfs:/level1/level2/level3$ cd nonexistent
error: cd: nonexistent: нет такого файла или каталога
complex_vfs@vfs:/level1/level2/level3$ exit
```

### Выполнение стартового скрипта

Запуск эмулятора с автоматическим выполнением команд из файла:

```bash
python src/main.py --vfs-path vfs/complex.xml --script scripts/demo.txt
```

Вывод в окне эмулятора (скрипт останавливается на первой ошибке согласно требованиям):

```text
=== Выполнение скрипта: scripts/demo.txt ===
complex_vfs@vfs:/$ help
Доступные команды:
  ls [путь...]     — список файлов и каталогов
  cd [путь]        — сменить текущий каталог
  pwd              — показать текущий каталог
  tac <файл>       — вывести файл в обратном порядке строк
  du <путь>        — показать размер файла или каталога
  mkdir <путь>     — создать новый каталог
  help             — показать эту справку
  exit             — выйти из эмулятора
complex_vfs@vfs:/$ pwd
/
complex_vfs@vfs:/$ ls
root_file.txt  level1  projects
complex_vfs@vfs:/$ cd level1
complex_vfs@vfs:/level1$ ls
l1_file.txt  level2
complex_vfs@vfs:/level1$ cd nonexistent
error: cd: nonexistent: нет такого файла или каталога
error: скрипт остановлен на строке 6
```

### Формат CSV-лога

Файл `logs/demo.csv`, автоматически созданный после интерактивной сессии:

```csv
timestamp,username,command,error
2026-10-08 15:30:12,User,ls,
2026-10-08 15:30:15,User,cd level1,
2026-10-08 15:30:20,User,cd nonexistent,cd: nonexistent: нет такого файла или каталога
2026-10-08 15:30:25,User,exit,
```