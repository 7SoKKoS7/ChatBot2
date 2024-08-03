import tkinter as tk
from tkinter import scrolledtext, font, simpledialog, messagebox
from chat_gpt import create_session, end_session, add_message, chat_with_gpt, load_chat_history, get_important_events, \
    delete_event, process_message_with_model
import time


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with GPT-4o mini-2024-07-18")

        # Настройки шрифта
        self.user_font_size = 10
        self.bot_font_size = 12
        self.user_font = font.Font(size=self.user_font_size, slant="italic")
        self.bot_font = font.Font(size=self.bot_font_size)
        self.input_font = font.Font(size=self.user_font_size)

        # Создание текстового поля для отображения чата
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=self.bot_font)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создание текстового поля для ввода текста пользователем
        self.user_input = tk.Entry(root, width=100, font=self.input_font)
        self.user_input.pack(padx=10, pady=10, fill=tk.X)
        self.user_input.bind("<Return>", self.send_message)

        # Кнопка для отправки сообщения
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)

        # Кнопки для изменения шрифта
        self.increase_font_button = tk.Button(root, text="Increase Font", command=self.increase_font_size)
        self.increase_font_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.decrease_font_button = tk.Button(root, text="Decrease Font", command=self.decrease_font_size)
        self.decrease_font_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Кнопка для отображения важных заметок
        self.show_notes_button = tk.Button(root, text="Show Important Notes", command=self.show_important_notes)
        self.show_notes_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Создание сессии
        self.session_id = create_session()
        self.chat_history = load_chat_history()
        self.load_history_into_display()

    def send_message(self, event=None):
        user_message = self.user_input.get()
        if user_message.strip():
            self.display_message("You", user_message, self.user_font, "right", user=True)
            self.user_input.delete(0, tk.END)

            self.display_message("GPT-4o mini", "Ищу в интернете...", self.bot_font, "left")
            self.root.after(100, self.process_message, user_message)

    def process_message(self, user_message):
        response, is_important = process_message_with_model(self.session_id, self.chat_history, user_message)
        self.display_message("GPT-4o mini", response, self.bot_font, "left", animated=True)
        add_message(self.session_id, "user", user_message)
        add_message(self.session_id, "assistant", response, is_important)

    def display_message(self, sender, message, font, align, animated=False, user=False):
        self.chat_display.configure(state='normal')
        if align == "right":
            self.chat_display.tag_configure("right", justify='right')
            if user:
                self.chat_display.tag_configure("user", foreground="gray",
                                                font=("Helvetica", self.user_font_size, "italic"))
                self.chat_display.insert(tk.END, f"{sender}: {message}\n", ("right", "user"))
            else:
                self.chat_display.insert(tk.END, f"{sender}: {message}\n", ("right",))
        else:
            if animated:
                for char in message:
                    self.chat_display.insert(tk.END, char, font)
                    self.chat_display.see(tk.END)
                    self.chat_display.update_idletasks()
                    time.sleep(0.02)
                self.chat_display.insert(tk.END, "\n", font)
            else:
                self.chat_display.insert(tk.END, f"{sender}: {message}\n", font)
        self.chat_display.configure(state='disabled')
        self.chat_display.yview(tk.END)

    def increase_font_size(self):
        self.user_font_size += 2
        self.bot_font_size += 2
        self.user_font.configure(size=self.user_font_size)
        self.bot_font.configure(size=self.bot_font_size)
        self.input_font.configure(size=self.user_font_size)

    def decrease_font_size(self):
        self.user_font_size -= 2
        self.bot_font_size -= 2
        self.user_font.configure(size=self.user_font_size)
        self.bot_font.configure(size=self.bot_font_size)
        self.input_font.configure(size=self.user_font_size)

    def load_history_into_display(self):
        for message in self.chat_history:
            sender = "You" if message["role"] == "user" else "GPT-4o mini"
            font = self.user_font if message["role"] == "user" else self.bot_font
            align = "right" if message["role"] == "user" else "left"
            user = True if message["role"] == "user" else False
            self.display_message(sender, message["content"], font, align, user=user)

    def show_important_notes(self):
        events = get_important_events()
        if not events:
            messagebox.showinfo("Important Notes", "No important notes found.")
            return

        notes_window = tk.Toplevel(self.root)
        notes_window.title("Important Notes")

        notes_listbox = tk.Listbox(notes_window, width=50, height=20)
        notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(notes_window, orient="vertical")
        scrollbar.config(command=notes_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        notes_listbox.config(yscrollcommand=scrollbar.set)

        for event_id, timestamp, description in events:
            notes_listbox.insert(tk.END, f"ID: {event_id}, Time: {timestamp}, Note: {description}")

        delete_button = tk.Button(notes_window, text="Delete Selected Note",
                                  command=lambda: self.delete_selected_note(notes_listbox))
        delete_button.pack(pady=10)

    def delete_selected_note(self, notes_listbox):
        selected_note = notes_listbox.curselection()
        if not selected_note:
            return

        note_text = notes_listbox.get(selected_note)
        event_id = int(note_text.split(',')[0].split(': ')[1])

        delete_event(event_id)
        notes_listbox.delete(selected_note)
        messagebox.showinfo("Note Deleted", f"Note with ID {event_id} has been deleted.")

    def on_closing(self):
        end_session(self.session_id)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
