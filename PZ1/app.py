import tkinter as tk
from tkinter import ttk, messagebox
from ciphers_core import (
    CaesarCipher,
    VigenereCipher,
    OneTimePadManual
)

def attach_edit_helpers(widget):
    menu = tk.Menu(widget, tearoff=0)

    def do_copy():
        widget.event_generate("<<Copy>>")

    def do_paste():
        widget.event_generate("<<Paste>>")

    def do_cut():
        widget.event_generate("<<Cut>>")

    def do_select_all():
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end")
            widget.mark_set("insert", "end")
        elif isinstance(widget, (ttk.Entry, tk.Entry)):
            widget.select_range(0, "end")
            widget.icursor("end")

    menu.add_command(label="Копіювати", command=do_copy)
    menu.add_command(label="Вставити", command=do_paste)
    menu.add_command(label="Вирізати", command=do_cut)
    menu.add_separator()
    menu.add_command(label="Виділити все", command=do_select_all)

    def show_popup(event):
        menu.tk_popup(event.x_root, event.y_root)

    widget.bind("<Button-3>", show_popup)

    def handle_ctrl(event):
        if event.state & 4 or event.state & 12:
            if event.keycode == 67:
                do_copy()
                return "break"
            elif event.keycode == 86:
                do_paste()
                return "break"
            elif event.keycode == 88:
                do_cut()
                return "break"
            elif event.keycode == 65:
                do_select_all()
                return "break"

    widget.bind("<KeyPress>", handle_ctrl, add="+")
    for k in ("<Control-Cyrillic_es>", "<Control-Cyrillic_ES>"):
        widget.bind(k, lambda e: (do_copy(), "break")[1])
    for k in ("<Control-Cyrillic_em>", "<Control-Cyrillic_EM>"):
        widget.bind(k, lambda e: (do_paste(), "break")[1])
    for k in ("<Control-Cyrillic_che>", "<Control-Cyrillic_CHE>"):
        widget.bind(k, lambda e: (do_cut(), "break")[1])
    for k in ("<Control-Cyrillic_ef>", "<Control-Cyrillic_EF>", "<Control-a>", "<Control-A>"):
        widget.bind(k, lambda e: (do_select_all(), "break")[1])

class PZ1App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Практичне заняття №1: Підстановочні шифри")
        self.geometry("960x700")
        self.minsize(860, 600)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_caesar_tab()
        self._build_vigenere_tab()
        self._build_otp_tab()

    def _build_caesar_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="Шифр Цезаря (Завдання 1)")

        param_bar = ttk.LabelFrame(tab, text=" Параметри ", padding=8)
        param_bar.pack(fill="x", pady=(0, 8))

        ttk.Label(param_bar, text="Величина зсуву k (0..32):").pack(side="left", padx=(0, 6))
        self.spin_shift = ttk.Spinbox(param_bar, from_=0, to_=32, width=6)
        self.spin_shift.set(3)
        self.spin_shift.pack(side="left")

        io_frame = ttk.Frame(tab)
        io_frame.pack(fill="both", expand=True)

        left = ttk.LabelFrame(io_frame, text=" Вхідний текст ", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.txt_c_in = tk.Text(left, height=12, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_c_in.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_c_in)

        right = ttk.LabelFrame(io_frame, text=" Результат перетворення ", padding=8)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.txt_c_out = tk.Text(right, height=12, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_c_out.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_c_out)

        btn_bar = ttk.Frame(tab)
        btn_bar.pack(fill="x", pady=8)

        def do_c_encrypt():
            t = self.txt_c_in.get("1.0", "end-1c")
            s = int(self.spin_shift.get())
            res = CaesarCipher.encrypt(t, s)
            self.txt_c_out.delete("1.0", "end")
            self.txt_c_out.insert("1.0", res)

        def do_c_decrypt():
            t = self.txt_c_in.get("1.0", "end-1c")
            s = int(self.spin_shift.get())
            res = CaesarCipher.decrypt(t, s)
            self.txt_c_out.delete("1.0", "end")
            self.txt_c_out.insert("1.0", res)

        ttk.Button(btn_bar, text="Зашифрувати", command=do_c_encrypt).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Розшифрувати", command=do_c_decrypt).pack(side="left")

    def _build_vigenere_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="Шифр Віженера (Завдання 2 та 3)")

        param_bar = ttk.LabelFrame(tab, text=" Параметри ", padding=8)
        param_bar.pack(fill="x", pady=(0, 8))

        ttk.Label(param_bar, text="Ключове слово:").pack(side="left", padx=(0, 6))
        self.ent_v_key = ttk.Entry(param_bar, width=24, font=("Consolas", 10))
        self.ent_v_key.insert(0, "безпека")
        self.ent_v_key.pack(side="left")
        attach_edit_helpers(self.ent_v_key)

        io_frame = ttk.Frame(tab)
        io_frame.pack(fill="both", expand=True)

        left = ttk.LabelFrame(io_frame, text=" Вхідне повідомлення ", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.txt_v_in = tk.Text(left, height=12, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_v_in.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_v_in)

        right = ttk.LabelFrame(io_frame, text=" Результат Віженера ", padding=8)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.txt_v_out = tk.Text(right, height=12, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_v_out.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_v_out)

        btn_bar = ttk.Frame(tab)
        btn_bar.pack(fill="x", pady=8)

        def do_v_encrypt():
            t = self.txt_v_in.get("1.0", "end-1c")
            k = self.ent_v_key.get().strip()
            res = VigenereCipher.encrypt(t, k)
            self.txt_v_out.delete("1.0", "end")
            self.txt_v_out.insert("1.0", res)

        def do_v_decrypt():
            t = self.txt_v_in.get("1.0", "end-1c")
            k = self.ent_v_key.get().strip()
            res = VigenereCipher.decrypt(t, k)
            self.txt_v_out.delete("1.0", "end")
            self.txt_v_out.insert("1.0", res)

        ttk.Button(btn_bar, text="Зашифрувати", command=do_v_encrypt).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Розшифрувати", command=do_v_decrypt).pack(side="left")

    def _build_otp_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="Одноразовий блокнот (Завдання 4-6)")

        info_bar = ttk.Frame(tab)
        info_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(info_bar, text="Таблиця стиснення: 1..7 (А,И,Т,Е,С,Н,О), 8x (Б..Ї), 9x (Й..Ц), 0x (Ч..Я, пробіл)", font=("Segoe UI", 9)).pack(side="left")

        f_inputs = ttk.LabelFrame(tab, text=" Вхідні параметри ", padding=8)
        f_inputs.pack(fill="x", pady=(0, 8))

        ttk.Label(f_inputs, text="Повідомлення (цифри шифротексту або відкритий текст):").pack(anchor="w")
        self.ent_otp_cipher = ttk.Entry(f_inputs, font=("Consolas", 10))
        self.ent_otp_cipher.pack(fill="x", pady=(2, 6))
        attach_edit_helpers(self.ent_otp_cipher)

        ttk.Label(f_inputs, text="Ключ (слово або послідовність цифр):").pack(anchor="w")
        self.ent_otp_key = ttk.Entry(f_inputs, font=("Consolas", 10))
        self.ent_otp_key.pack(fill="x", pady=(2, 6))
        attach_edit_helpers(self.ent_otp_key)

        btn_box = ttk.Frame(tab)
        btn_box.pack(fill="x", pady=(0, 8))

        def do_otp_decrypt():
            c = self.ent_otp_cipher.get().strip()
            k = self.ent_otp_key.get().strip()
            res = OneTimePadManual.decrypt(c, k)
            self.txt_otp_log.delete("1.0", "end")
            self.txt_otp_log.insert("end", f"Шифротекст (цифри): {res['cipher_digits']}\n")
            self.txt_otp_log.insert("end", f"Базовий цифровий ключ: {res['key_base']}\n")
            self.txt_otp_log.insert("end", f"Повний циклічний ключ: {res['full_key_digits']}\n")
            self.txt_otp_log.insert("end", f"Відкритий текст у цифрах (c - k mod 10): {res['plain_digits']}\n\n")
            self.txt_otp_log.insert("end", f"ДЕКОДОВАНИЙ ТЕКСТ:\n{res['decoded_text']}\n")

        def do_otp_encrypt():
            t = self.ent_otp_cipher.get().strip()
            k = self.ent_otp_key.get().strip()
            res = OneTimePadManual.encrypt(t, k)
            self.txt_otp_log.delete("1.0", "end")
            self.txt_otp_log.insert("end", f"Вихідний текст: {res['plain_text']}\n")
            self.txt_otp_log.insert("end", f"Закодований у цифри (таблиця стиснення): {res['plain_digits']}\n")
            self.txt_otp_log.insert("end", f"Базовий цифровий ключ: {res['key_base']}\n")
            self.txt_otp_log.insert("end", f"Повний ключ: {res['full_key_digits']}\n\n")
            self.txt_otp_log.insert("end", f"ШИФРОТЕКСТ (m + k mod 10):\n{res['cipher_digits']}\n")

        ttk.Button(btn_box, text="Розшифрувати (віднімання mod 10 + таблиця стиснення)", command=do_otp_decrypt).pack(side="left", padx=(0, 6))
        ttk.Button(btn_box, text="Зашифрувати (таблиця стиснення + додавання mod 10)", command=do_otp_encrypt).pack(side="left")

        f_res = ttk.LabelFrame(tab, text=" Протокол обчислень та результат ", padding=8)
        f_res.pack(fill="both", expand=True)

        self.txt_otp_log = tk.Text(f_res, height=12, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_otp_log.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_otp_log)

def main():
    app = PZ1App()
    app.mainloop()

if __name__ == "__main__":
    main()
