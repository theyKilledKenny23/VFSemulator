import tkinter as tk
import shlex

state = {
    "vfs_name": "myOS",
    "current_dir": "~"
}

def write_output(text, is_error=False):
    '''Вывод в окно'''
    output.config(state=tk.NORMAL)
    if is_error:
        output.insert(tk.END, f"error: {text}\n", "error")
    else:
        output.insert(tk.END, text + "\n")
    output.see(tk.END)
    output.config(state=tk.DISABLED)

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

    if not raw.strip():
        return

    try:
        args = shlex.split(raw)
    except ValueError as e:
        write_output(f"не удалось разобрать команду: {e}", is_error=True)
        return

    cmd_name = args[0]
    cmd_args = args[1:]
    handler = COMMANDS.get(cmd_name)

    if handler is None:
        write_output(f"неизвестная команда: {cmd_name}", is_error=True)
        return
    handler(cmd_args)


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

write_output("Введите 'help' для списка команд.")

root.mainloop()