import tkinter as tk
import shlex
import argparse
import csv
import datetime
import os
import xml.etree.ElementTree as ET
import base64

state = {
    "vfs_name": "EmulatorVFS",
    "current_dir": "~",
    "vfs_path": None,
    "log_file": None,
    "script_path": None,
    "username": os.environ.get("USERNAME",
                               os.environ.get("USER", "unknown")),
    "vfs_data": None
}

def parse_vfs_node(element):
    """Рекурсивно парсит XML-элемент в структуру VFS."""
    if element.tag == "file":
        name = element.get("name")
        encoding = element.get("encoding")
        content = element.text or ""

        if encoding == "base64":
            try:
                content = base64.b64decode(content).decode("utf-8", errors="replace")
            except Exception:
                content = "[binary data]"

        return {"type": "file", "name": name, "content": content}

    elif element.tag == "dir":
        name = element.get("name")
        children = {}
        for child in element:
            child_node = parse_vfs_node(child)
            if child_node and "name" in child_node:
                children[child_node["name"]] = child_node
        return {"type": "dir", "name": name, "children": children}

    return None

def load_vfs(path):
    """Загружает VFS из XML-файла в память."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        if root.tag != "vfs":
            raise ValueError("Неверный корневой элемент XML")

        vfs_name = root.get("name", "default_vfs")
        root_element = root.find("root")

        if root_element is None:
            raise ValueError("Отсутствует корневая директория 'root'")

        vfs_structure = parse_vfs_node(root_element)

        state["vfs_name"] = vfs_name
        state["vfs_data"] = vfs_structure
        state["current_dir"] = "/"

        write_output(f"VFS '{vfs_name}' успешно загружена из {path}")

    except FileNotFoundError:
        write_output(f"ошибка: файл VFS не найден: {path}", is_error=True)
    except ET.ParseError as e:
        write_output(f"ошибка: неверный формат XML: {e}", is_error=True)
    except ValueError as e:
        write_output(f"ошибка: неверная структура VFS: {e}", is_error=True)

def parse_args():
    '''Разбирает аргументы командной строки.'''
    parser = argparse.ArgumentParser(description="Эмулятор оболочки VFS")
    parser.add_argument("--vfs-path", help="Путь к VFS")
    parser.add_argument("--log-file", help="Путь к лог-файлу")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    return parser.parse_args()

def apply_args(args):
    '''Применяет аргументы к состоянию приложения.'''
    if args.vfs_path:
        state["vfs_path"] = args.vfs_path
        state["vfs_name"] = os.path.basename(args.vfs_path)
    if args.log_file:
        state["log_file"] = args.log_file
    if args.script:
        state["script_path"] = args.script

def print_debug_info():
    '''Выводит отладочную информацию о параметрах запуска.'''
    write_output("=== Параметры запуска ===")
    vfs = state["vfs_path"] or "не задан"
    log = state["log_file"] or "не задан"
    scr = state["script_path"] or "не задан"
    write_output(f"VFS: {vfs}")
    write_output(f"Лог-файл: {log}")
    write_output(f"Скрипт: {scr}")
    write_output(f"Пользователь: {state['username']}")
    write_output("=========================")

def log_event(command, error=None):
    """Записывает событие вызова команды в CSV-лог."""
    log_file = state["log_file"]
    if not log_file:
        return

    now = datetime.datetime.now()
    row = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "username": state["username"],
        "command": command,
        "error": error or "",
    }

    try:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_exists = os.path.isfile(log_file)
        fields = ["timestamp", "username", "command", "error"]
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except OSError as e:
        write_output(f"ошибка записи лога: {e}", is_error=True)

def write_output(text, is_error=False):
    '''Вывод в окно'''
    output.config(state=tk.NORMAL)
    if is_error:
        output.insert(tk.END, f"error: {text}\n", "error")
    else:
        output.insert(tk.END, text + "\n")
    output.see(tk.END)
    output.config(state=tk.DISABLED)

def execute_command(raw):
    '''
    Выполняет команду.
    Возвращает True при успехе, False при ошибке.
    '''
    if not raw.strip():
        return True

    try:
        args = shlex.split(raw)
    except ValueError as e:
        msg = f"не удалось разобрать команду: {e}"
        write_output(msg, is_error=True)
        log_event(raw, error=msg)
        return False

    cmd_name = args[0]
    cmd_args = args[1:]
    handler = COMMANDS.get(cmd_name)

    if handler is None:
        msg = f"неизвестная команда: {cmd_name}"
        write_output(msg, is_error=True)
        log_event(raw, error=msg)
        return False

    handler(cmd_args)
    log_event(raw)
    return True

def run_script(path):
    '''Выполняет стартовый скрипт команд эмулятора.'''
    if not os.path.isfile(path):
        write_output(f"скрипт не найден: {path}", is_error=True)
        return

    write_output(f"=== Выполнение скрипта: {path} ===")

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            prompt = f"{state['vfs_name']}@vfs:{state['current_dir']}$ "
            write_output(f"{prompt}{line}")

            success = execute_command(line)
            if not success:
                msg = f"скрипт остановлен на строке {line_num}"
                write_output(msg, is_error=True)
                log_event(line, error=msg)
                return

    write_output("=== Скрипт выполнен успешно ===")

def cmd_ls(args):
    '''Команда ls'''
    write_output(f"ls: вызов с аргументами {args}")

def cmd_cd(args):
    '''Команда cd'''
    if len(args) > 1:
        write_output("cd: слишком много аргументов", is_error=True)
        return
    write_output(f"cd: вызов с аргументами {args}")


def cmd_help(args):
    '''Команда help'''
    if args:
        write_output("help: команда не принимает аргументов", is_error=True)
        return

    text = "Доступные команды:\n"
    text += "  ls [аргументы]  — список файлов (заглушка)\n"
    text += "  cd [путь]       — сменить директорию (заглушка)\n"
    text += "  help            — показать эту справку\n"
    text += "  exit            — выйти из эмулятора"
    write_output(text)


def cmd_exit(args):
    '''Выход'''
    if args:
        write_output("exit: команда не принимает аргументов", is_error=True)
        return
    root.quit()

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "help": cmd_help,
    "exit": cmd_exit,
}

def on_enter(event):
    '''Нажатие enter'''
    raw = entry.get()
    entry.delete(0, tk.END)

    prompt_text = f"{state['vfs_name']}@vfs:{state['current_dir']}$ "
    write_output(f"{prompt_text}{raw}")
    execute_command(raw)

args = parse_args()
apply_args(args)

root = tk.Tk()
root.title(f"VFS: {state['vfs_name']}")
root.geometry("700x450")

output = tk.Text(root, height=20, state=tk.DISABLED, wrap=tk.WORD)
output.tag_config("error", foreground="red")
output.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

input_frame = tk.Frame(root)
input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

prompt_label = tk.Label(
    input_frame,
    text=f"{state['vfs_name']}@vfs:{state['current_dir']}$ ",
    anchor="w"
)
prompt_label.pack(side=tk.LEFT)

entry = tk.Entry(input_frame)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", on_enter)
entry.focus_set()

if state["vfs_path"]:
    load_vfs(state["vfs_path"])
else:
    write_output("VFS не указана, работа в режиме заглушек.")

print_debug_info()
write_output("Введите 'help' для списка команд.")

if state["script_path"]:
    run_script(state["script_path"])

root.mainloop()