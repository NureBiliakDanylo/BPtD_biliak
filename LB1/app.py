import base64
import tkinter as tk
from tkinter import ttk, messagebox
from des_core import DESCipher, check_weak_key

def parse_key_input(raw: str) -> bytes:
    raw = raw.strip()
    if len(raw) == 16:
        try:
            return bytes.fromhex(raw)
        except ValueError:
            pass
    b = raw.encode('utf-8')
    if len(b) < 8:
        b = b.ljust(8, b'\0')
    return b[:8]

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

class DESApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DES Шифрування та Розрахунок Ентропії — ЛР №1")
        self.geometry("920x660")
        self.minsize(800, 560)

        self._create_widgets()
        self._check_key()

    def _create_widgets(self):
        key_frame = ttk.LabelFrame(self, text=" Ключ шифрування DES ", padding=(12, 8))
        key_frame.pack(fill="x", padx=12, pady=(10, 6))

        key_inner = ttk.Frame(key_frame)
        key_inner.pack(fill="x")

        ttk.Label(key_inner, text="Ключ (8 символів або 16 HEX):").pack(side="left", padx=(0, 8))
        
        self.key_var = tk.StringVar(value="Secret12")
        self.key_entry = ttk.Entry(key_inner, textvariable=self.key_var, width=24, font=("Consolas", 10))
        self.key_entry.pack(side="left", padx=(0, 12))
        self.key_var.trace_add("write", lambda *args: self._check_key())
        attach_edit_helpers(self.key_entry)

        self.lbl_key_status = ttk.Label(key_inner, text="", font=("Segoe UI", 9))
        self.lbl_key_status.pack(side="left")

        io_frame = ttk.Frame(self)
        io_frame.pack(fill="both", expand=True, padx=12, pady=4)

        left_box = ttk.LabelFrame(io_frame, text=" Вхідне повідомлення ", padding=8)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.txt_input = tk.Text(left_box, height=8, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_input.pack(fill="both", expand=True)
        self.txt_input.insert("1.0", "Програмна безпека та криптографічний алгоритм DES з розрахунком ентропії.")
        attach_edit_helpers(self.txt_input)

        right_box = ttk.LabelFrame(io_frame, text=" Результат шифрування / розшифрування ", padding=8)
        right_box.pack(side="right", fill="both", expand=True, padx=(4, 0))

        ttk.Label(right_box, text="Шифротекст (HEX):", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.entry_hex = ttk.Entry(right_box, font=("Consolas", 9))
        self.entry_hex.pack(fill="x", pady=(0, 6))
        attach_edit_helpers(self.entry_hex)

        ttk.Label(right_box, text="Розшифрований текст:", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.txt_output = tk.Text(right_box, height=5, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.txt_output.pack(fill="both", expand=True)
        attach_edit_helpers(self.txt_output)

        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", padx=12, pady=6)

        self.btn_enc = ttk.Button(btn_bar, text="Зашифрувати", command=self._encrypt)
        self.btn_enc.pack(side="left", padx=(0, 6))

        self.btn_dec = ttk.Button(btn_bar, text="Розшифрувати", command=self._decrypt)
        self.btn_dec.pack(side="left", padx=6)

        self.btn_clear = ttk.Button(btn_bar, text="Очистити", command=self._clear)
        self.btn_clear.pack(side="right")

        entropy_frame = ttk.LabelFrame(self, text=" Ентропія появи біту '1' на 16 раундах Фейстеля ", padding=8)
        entropy_frame.pack(fill="both", expand=True, padx=12, pady=(4, 10))

        cols = ("round", "state_hex", "ones", "zeros", "p", "entropy")
        self.tree = ttk.Treeview(entropy_frame, columns=cols, show="headings", height=8)

        self.tree.heading("round", text="Раунд")
        self.tree.heading("state_hex", text="Вектор стану (L + R) у HEX")
        self.tree.heading("ones", text="Одиниці ('1')")
        self.tree.heading("zeros", text="Нулі ('0')")
        self.tree.heading("p", text="Частка p(1)")
        self.tree.heading("entropy", text="Ентропія H")

        self.tree.column("round", width=70, anchor="center")
        self.tree.column("state_hex", width=230, anchor="center")
        self.tree.column("ones", width=100, anchor="center")
        self.tree.column("zeros", width=100, anchor="center")
        self.tree.column("p", width=100, anchor="center")
        self.tree.column("entropy", width=120, anchor="center")

        scroll = ttk.Scrollbar(entropy_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._attach_tree_menu()

        self.lbl_avg = ttk.Label(self, text="Ентропія Шеннона: H = -p·log₂(p) - (1-p)·log₂(1-p)", font=("Segoe UI", 8), foreground="#555555")
        self.lbl_avg.pack(anchor="w", padx=15, pady=(0, 6))

    def _attach_tree_menu(self):
        menu = tk.Menu(self.tree, tearoff=0)

        def copy_row():
            sel = self.tree.selection()
            if not sel:
                return
            lines = []
            for item in sel:
                vals = self.tree.item(item, "values")
                lines.append("\t".join(str(v) for v in vals))
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))

        def copy_all():
            lines = ["Раунд\tВектор стану HEX\tОдиниці\tНулі\tЧастка p(1)\tЕнтропія H"]
            for item in self.tree.get_children():
                vals = self.tree.item(item, "values")
                lines.append("\t".join(str(v) for v in vals))
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))

        menu.add_command(label="Копіювати виділений рядок", command=copy_row)
        menu.add_command(label="Копіювати всю таблицю", command=copy_all)

        def show_menu(event):
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
            menu.tk_popup(event.x_root, event.y_root)

        self.tree.bind("<Button-3>", show_menu)
        self.tree.bind("<Control-c>", lambda e: copy_row())
        self.tree.bind("<Control-C>", lambda e: copy_row())

    def _check_key(self):
        raw = self.key_var.get()
        try:
            key_bytes = parse_key_input(raw)
            is_weak, msg = check_weak_key(key_bytes)
            if is_weak:
                self.lbl_key_status.config(text=f"Увага: {msg}", foreground="#c00000")
            else:
                self.lbl_key_status.config(text="Ключ коректний", foreground="#008000")
        except Exception as e:
            self.lbl_key_status.config(text=f"Помилка: {e}", foreground="#c00000")

    def _encrypt(self):
        text = self.txt_input.get("1.0", "end-1c")
        if not text:
            messagebox.showwarning("Попередження", "Введіть текст для шифрування!")
            return

        key_bytes = parse_key_input(self.key_var.get())
        try:
            cipher = DESCipher(key_bytes)
            enc_bytes, rounds = cipher.encrypt(text.encode('utf-8'))

            self.entry_hex.delete(0, "end")
            self.entry_hex.insert(0, enc_bytes.hex().upper())

            self.txt_output.delete("1.0", "end")
            self.txt_output.insert("1.0", "(Натисніть 'Розшифрувати' для перевірки результату)")

            self._update_table(rounds)
            if cipher.is_weak:
                messagebox.showwarning("Слабкий ключ", f"Увага! {cipher.key_status}. У DES шифрування слабким ключем є самозворотним.")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _decrypt(self):
        hex_str = self.entry_hex.get().strip()
        if not hex_str:
            messagebox.showwarning("Попередження", "Поле HEX шифротексту порожнє!")
            return

        key_bytes = parse_key_input(self.key_var.get())
        try:
            raw_bytes = bytes.fromhex(hex_str)
            cipher = DESCipher(key_bytes)
            dec_bytes, rounds = cipher.decrypt(raw_bytes)

            self.txt_output.delete("1.0", "end")
            self.txt_output.insert("1.0", dec_bytes.decode('utf-8', errors='replace'))
            self._update_table(rounds, is_decrypt=True)
        except Exception as e:
            messagebox.showerror("Помилка розшифрування", str(e))

    def _update_table(self, rounds, is_decrypt=False):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in rounds:
            self.tree.insert("", "end", values=(
                f"Раунд {r['round']}",
                r['state_hex'],
                r['ones_count'],
                r['zeros_count'],
                f"{r['probability_one']:.4f}",
                f"{r['entropy']:.5f}"
            ))

        avg_h = sum(r['entropy'] for r in rounds) / len(rounds) if rounds else 0.0
        mode = "Розшифрування" if is_decrypt else "Шифрування"
        self.lbl_avg.config(text=f"{mode}: Середня ентропія = {avg_h:.5f} (максимум: 1.00000)")

    def _clear(self):
        self.txt_input.delete("1.0", "end")
        self.entry_hex.delete(0, "end")
        self.txt_output.delete("1.0", "end")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_avg.config(text="Ентропія Шеннона: H = -p·log₂(p) - (1-p)·log₂(1-p)")

def main():
    app = DESApp()
    app.mainloop()

if __name__ == "__main__":
    main()
