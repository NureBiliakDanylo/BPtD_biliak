import tkinter as tk
from tkinter import ttk, messagebox
from otp_core import MachineOTP, CryptanalysisLab

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

class PZ2App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Практичне заняття №2: Одноразовий блокнот та криптоаналіз")
        self.geometry("980x720")
        self.minsize(880, 620)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_otp_tab()
        self._build_cryptanalysis_tab()

    def _build_otp_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="Машинний блокнот")

        f_top = ttk.LabelFrame(tab, text=" Параметри та керування ключем ", padding=8)
        f_top.pack(fill="x", pady=(0, 8))

        ttk.Label(f_top, text="Ключ шифрування (HEX):").pack(anchor="w")
        self.ent_key_hex = ttk.Entry(f_top, font=("Consolas", 10))
        self.ent_key_hex.pack(fill="x", pady=(2, 6))
        attach_edit_helpers(self.ent_key_hex)

        btn_row = ttk.Frame(f_top)
        btn_row.pack(fill="x")

        def gen_key():
            t = self.txt_in.get("1.0", "end-1c").encode('utf-8')
            length = max(len(t), 16)
            k = MachineOTP.generate_key(length)
            self.ent_key_hex.delete(0, "end")
            self.ent_key_hex.insert(0, k.hex().upper())
            self.lbl_key_info.config(text=f"Згенеровано ключ довжиною {length} байтів.")

        ttk.Button(btn_row, text="Згенерувати випадковий ключ", command=gen_key).pack(side="left", padx=(0, 10))
        self.lbl_key_info = ttk.Label(btn_row, text="", font=("Segoe UI", 9))
        self.lbl_key_info.pack(side="left")

        io_frame = ttk.Frame(tab)
        io_frame.pack(fill="both", expand=True)

        left = ttk.LabelFrame(io_frame, text=" Вхідний відкритий текст (UTF-8) ", padding=8)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.txt_in = tk.Text(left, height=10, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_in.pack(fill="both", expand=True)
        self.txt_in.insert("1.0", "Безпека програм та даних")
        attach_edit_helpers(self.txt_in)

        right = ttk.LabelFrame(io_frame, text=" Результат (HEX та розшифрування) ", padding=8)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ttk.Label(right, text="Шифротекст (HEX):").pack(anchor="w")
        self.txt_cipher_hex = tk.Text(right, height=5, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_cipher_hex.pack(fill="x", pady=(2, 6))
        attach_edit_helpers(self.txt_cipher_hex)

        ttk.Label(right, text="Розшифрований текст:").pack(anchor="w")
        self.txt_decrypted = tk.Text(right, height=5, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_decrypted.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_decrypted)

        action_bar = ttk.Frame(tab)
        action_bar.pack(fill="x", pady=8)

        def do_encrypt():
            t = self.txt_in.get("1.0", "end-1c")
            k_hex = self.ent_key_hex.get().strip()
            k_bytes = bytes.fromhex(k_hex) if k_hex else None
            c_hex, k_used_hex, _ = MachineOTP.encrypt_text(t, k_bytes)
            self.ent_key_hex.delete(0, "end")
            self.ent_key_hex.insert(0, k_used_hex)
            self.txt_cipher_hex.delete("1.0", "end")
            self.txt_cipher_hex.insert("1.0", c_hex)
        def do_decrypt():
            c_hex = self.txt_cipher_hex.get("1.0", "end-1c").strip()
            k_hex = self.ent_key_hex.get().strip()
            if not c_hex or not k_hex:
                messagebox.showwarning("Увага", "Введіть шифротекст у HEX та ключ!")
                return
            dec = MachineOTP.decrypt_text(c_hex, k_hex)
            self.txt_decrypted.delete("1.0", "end")
            self.txt_decrypted.insert("1.0", dec)

        ttk.Button(action_bar, text="Зашифрувати (XOR)", command=do_encrypt).pack(side="left", padx=(0, 6))
        ttk.Button(action_bar, text="Розшифрувати (XOR)", command=do_decrypt).pack(side="left")

    def _build_cryptanalysis_tab(self):
        tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(tab, text="Криптоаналітична лабораторія")

        f_caesar = ttk.LabelFrame(tab, text=" Атака повного перебору на шифр Цезаря ", padding=8)
        f_caesar.pack(fill="x", pady=(0, 8))

        row_c = ttk.Frame(f_caesar)
        row_c.pack(fill="x", pady=(0, 4))
        ttk.Label(row_c, text="Зашифрований текст Цезаря:").pack(side="left", padx=(0, 6))
        self.ent_c_attack = ttk.Entry(row_c, font=("Consolas", 10))
        self.ent_c_attack.insert(0, "Воу Увщґдгб, ягаг еаорвши ґгдгсщр, р ефащ Еєодгбж Ягуояж цшр егпщ бгагушю агібов Яодґг Афємїшю.")
        self.ent_c_attack.pack(side="left", fill="x", expand=True, padx=(0, 8))
        attach_edit_helpers(self.ent_c_attack)

        def do_attack_caesar():
            t = self.ent_c_attack.get().strip()
            res = CryptanalysisLab.break_caesar(t)
            best = res[0]
            self.txt_attack_log.delete("1.0", "end")
            self.txt_attack_log.insert("end", f"РЕЗУЛЬТАТ КРИПТОАНАЛІЗУ ЦЕЗАРЯ\n")
            self.txt_attack_log.insert("end", f"Визначено найбільш імовірний зсув: k = {best['shift']} (рейтинг частотності: {best['score']:.6f})\n\n")
            self.txt_attack_log.insert("end", f"ВІДНОВЛЕНИЙ ВІДКРИТИЙ ТЕКСТ:\n{best['text']}\n\n")
            self.txt_attack_log.insert("end", f"Топ-3 кандидати перебору:\n")
            for i in range(min(3, len(res))):
                self.txt_attack_log.insert("end", f"k={res[i]['shift']}: {res[i]['text'][:60]}... (бал: {res[i]['score']:.5f})\n")

        ttk.Button(row_c, text="Зламати повним перебором", command=do_attack_caesar).pack(side="right")

        f_otp = ttk.LabelFrame(tab, text=" Атака на повторне використання ключа OTP (Two-Time Pad / Crib Dragging) ", padding=8)
        f_otp.pack(fill="x", pady=(0, 8))

        row_otp1 = ttk.Frame(f_otp)
        row_otp1.pack(fill="x", pady=2)
        ttk.Label(row_otp1, text="Повідомлення 1:", width=16).pack(side="left")
        self.ent_p1 = ttk.Entry(row_otp1, font=("Consolas", 9))
        self.ent_p1.insert(0, "ЗУСТРІЧ ПРИЗНАЧЕНО НА ДЕВЯТУ ГОДИНУ")
        self.ent_p1.pack(side="left", fill="x", expand=True)
        attach_edit_helpers(self.ent_p1)

        row_otp2 = ttk.Frame(f_otp)
        row_otp2.pack(fill="x", pady=2)
        ttk.Label(row_otp2, text="Повідомлення 2:", width=16).pack(side="left")
        self.ent_p2 = ttk.Entry(row_otp2, font=("Consolas", 9))
        self.ent_p2.insert(0, "НАКАЗ НАСТУПАТИ О ПІВДЕННІЙ СТОРОНІ")
        self.ent_p2.pack(side="left", fill="x", expand=True)
        attach_edit_helpers(self.ent_p2)

        row_crib = ttk.Frame(f_otp)
        row_crib.pack(fill="x", pady=4)
        ttk.Label(row_crib, text="Слово-здогадка (Crib):").pack(side="left", padx=(0, 6))
        self.ent_crib = ttk.Entry(row_crib, width=15, font=("Consolas", 10))
        self.ent_crib.insert(0, "ЗУСТРІЧ")
        self.ent_crib.pack(side="left", padx=(0, 10))
        attach_edit_helpers(self.ent_crib)

        def do_two_time_pad():
            p1 = self.ent_p1.get().strip().encode('utf-8')
            p2 = self.ent_p2.get().strip().encode('utf-8')
            k = MachineOTP.generate_key(max(len(p1), len(p2)))
            c1 = MachineOTP.encrypt_bytes(p1, k)
            c2 = MachineOTP.encrypt_bytes(p2, k)
            c1_xor_c2 = CryptanalysisLab.two_time_pad_xor(c1, c2)

            crib = self.ent_crib.get().strip()
            matches = CryptanalysisLab.crib_drag(c1_xor_c2, crib)

            self.txt_attack_log.delete("1.0", "end")
            self.txt_attack_log.insert("end", "АТАКА НА ПОРУШЕННЯ ПРАВИЛА ОДНОРАЗОВОСТІ OTP\n")
            self.txt_attack_log.insert("end", f"Повідомлення 1 і 2 зашифровано ОДНИМ спільним ключем.\n")
            self.txt_attack_log.insert("end", f"Обчислено C1 XOR C2 = P1 XOR P2 (ключ повністю нейтралізовано!):\n{c1_xor_c2.hex().upper()}\n\n")
            self.txt_attack_log.insert("end", f"Результати Crib Dragging для слова '{crib}':\n")
            if matches:
                for m in matches:
                    self.txt_attack_log.insert("end", f"Позиція {m['position']}: Слово '{m['crib']}' розкриває у паралельному тексті -> '{m['revealed_counterpart']}'\n")
                self.txt_attack_log.insert("end", f"\nВисновок: знання навіть короткого фрагмента одного повідомлення миттєво розкриває друге без знання ключа!\n")
            else:
                self.txt_attack_log.insert("end", "Не знайдено правдоподібних фрагментів для цього слова.\n")

        ttk.Button(row_crib, text="Виконати атаку Crib Dragging", command=do_two_time_pad).pack(side="left")

        f_out = ttk.LabelFrame(tab, text=" Протокол атаки криптоаналізу ", padding=8)
        f_out.pack(fill="both", expand=True)

        self.txt_attack_log = tk.Text(f_out, height=10, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_attack_log.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_attack_log)

def main():
    app = PZ2App()
    app.mainloop()

if __name__ == "__main__":
    main()
