import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import datetime
import pygame
from tkinter import simpledialog
import json
import calendar
import random

LEVEL_MAPPING = {
    "マル〇": 1,
    "バツ✖": 0

}
class App:
    def __init__(self, root):

        self.root = root
        self.root.geometry("800x670+0+0")
        self.root.title("aiTool")
        app_background_color = "cadetblue"
        root.configure(bg=app_background_color)
        root.iconbitmap("AI判断ツール.ico")
        self.frame1 = tk.Frame(root, bg="cadetblue")
        self.frame1.pack(side=tk.TOP)

        lbl_info = tk.Label(self.frame1, font=('aria', 36, 'bold'), text="AI判断ツール", fg="Brown", bd=12, anchor='c',bg=app_background_color)
        lbl_info.grid(row=0, column=0)

        # Thêm 'thứ' vào ngày tháng năm
        now = datetime.datetime.now()
        weekday = calendar.day_name[now.weekday()]
        date_info = tk.Label(self.frame1, font=('aria', 21), text=f"{now.year}年{now.month}月{now.day}日  {weekday}",
                             fg="black", anchor=tk.W,bg=app_background_color)
        date_info.grid(row=1, column=0)

        self.music_playing = True
        
        self.playlist = ["doraemon.mp3", "yourname.mp3", "always.mp3"]
        self.current_song = ""

        self.create_table()
        self.first_tema_value, self.first_tema_points_value = self.load_first_values()

        tk.Label(root, text="テーマ:", font=('ariel', 16),bg=app_background_color).pack()
        self.tema_entry = tk.Entry(root, font=('ariel', 16))
        self.tema_entry.pack()

        #Lop バイアス
        tk.Label(root, text="バイアス:1", font=('ariel', 16),bg=app_background_color).pack(pady=10)

        tk.Label(root, text="バイアスの重み(-0.1 ~ -5.0):", font=('ariel', 16),bg=app_background_color).pack(pady=10)
        # Tạo ô nhập liệu với giới hạn giá trị
        self.tema_points_entry = tk.Entry(root, validate='key',font=('ariel', 16))
        self.tema_points_entry.pack()

        self.first_tema_points_value = ""

        if self.first_tema_points_value is not None:
            self.tema_points_entry.delete(0, 'end')
            self.tema_points_entry.insert(0, self.first_tema_points_value)

        tk.Label(root, text="特徴(ポジティブな内容だけ):", font=('ariel', 16),bg=app_background_color).pack(pady=10)
        self.condi_text = tk.Text(root, font=('ariel', 16), height=3, width=20)
        self.condi_text.pack()

        tk.Label(root, text="選択は?", font=('ariel', 16),bg=app_background_color).pack(pady=10)
        self.level_var = tk.StringVar(root)
        self.level_var.set("マル〇")
        self.level_spinbox = ttk.Combobox(root, values=list(LEVEL_MAPPING.keys()), font=('ariel', 16),
                                          textvariable=self.level_var)
        self.level_spinbox.pack()

        tk.Button(root, text="追加", font=('ariel', 16), command=self.insert_data, bg="light green").pack(pady=5)
        tk.Button(root, text="表示", font=('ariel', 16), command=self.display_data, bg="light salmon").pack(pady=5)
        tk.Button(root, text="総和", font=('ariel', 16), command=self.calculate_total_level, bg="Dark Gray").pack(pady=5)
    
        self.edit_window = None

        pygame.mixer.init()
        self.load_and_play_random_song()

        #music
        self.play_icon = tk.PhotoImage(file="play.png")
        self.pause_icon = tk.PhotoImage(file="pause.png")
        self.music_button = tk.Button(root, image=self.play_icon, command=self.toggle_music)
        self.music_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

    def load_and_play_random_song(self):
        if self.playlist:
            self.current_song = random.choice(self.playlist)
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)

    def toggle_music(self):
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.music_button.config(image=self.play_icon)  # Change the button image to play
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.music_button.config(image=self.pause_icon)


    def create_table(self):
        with sqlite3.connect("mydatabase.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_data
                          (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                           tema TEXT,
                           tema_points FLOAT,
                           condi TEXT,
                           level FLOAT,
                           points FLOAT,
                           result FLOAT)''')

    def load_first_values(self):
        try:
            with open("first_values.json", "r") as file:
                data = json.load(file)
                return data.get("tema"), data.get("tema_points")
        except FileNotFoundError:
            return None, None

    def save_first_values(self, tema, tema_points):
        with open("first_values.json", "w") as file:
            json.dump({"tema": tema, "tema_points": tema_points}, file)

    def insert_data(self):
        tema = self.tema_entry.get()
        selected_tema_points = self.tema_points_entry.get()

        try:
            tema_points = float(selected_tema_points) if selected_tema_points and selected_tema_points != "0" else 0
        except ValueError:
            messagebox.showerror("エラー", "バイアスの重みを正しい数値で入力してください。")
            return

        condi = self.condi_text.get("1.0", "end-1c")
        level_text = self.level_var.get()
        
        try:
            level = float(LEVEL_MAPPING.get(level_text, 0))
        except ValueError:
            messagebox.showerror("エラー", "選択の値が無効です。")
            return

        points = self.ask_for_points()
        
        try:
            points = points
        except ValueError:
            messagebox.showerror("エラー", "重い付けを正しい数値で入力してください。")
            return

        result_value = tema_points + (points * level)

        if self.first_tema_value is None:
            self.first_tema_value = tema
        if self.first_tema_points_value is None:
            self.first_tema_points_value = tema_points

        self.save_first_values(self.first_tema_value, self.first_tema_points_value)

        with sqlite3.connect("mydatabase.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_data (tema, tema_points, condi, level, points, result) VALUES (?, ?, ?, ?, ?, ?)",
                (tema, tema_points, condi, level, points, result_value))

        self.tema_entry.delete(0, 'end')
        self.tema_points_entry.delete(0, 'end')
        self.condi_text.delete("1.0", "end")
        self.level_var.set("マル〇")
    def ask_for_points(self):
        if self.level_var.get() == "バツ✖":
            return 0
        else:
            points = simpledialog.askfloat("重み付け", "数値は0.1~5.0:")
            if points is None:
                return 0
            if 0.1 <= points <= 5.0:
                return points
            else:
                messagebox.showerror("エラー", "0.1~5.0 の重み付けを入力してください。")
                return 0


    def get_level_text(self, level):
        for text, value in LEVEL_MAPPING.items():
            if value == level:
                return text
        return "未知"

    def display_data(self):
        with sqlite3.connect("mydatabase.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_data")
            records = cursor.fetchall()

        if self.edit_window:
            self.edit_window.destroy()

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("入力されたデータ")

        tk.Label(self.edit_window, text="入力されたデータ:", font=('ariel', 16, 'bold')).pack()

        for record in records:
            tema, tema_points, condi, level, points, result_value = record[1], record[2], record[3], record[4], record[
                5], record[6]
            level_text = self.get_level_text(level)
            if points is not None:
                tk.Label(self.edit_window,
                         text=f"テーマ: {tema if tema else '未知'}, バイアスの重み: {tema_points if tema_points else 0}, 特徴: {condi}, 選択: {level_text}, 重い付け: {points}, 結果: {result_value}",
                         font=('ariel', 16)).pack()
            else:
                tk.Label(self.edit_window,
                         text=f"テーマ: {tema if tema else '未知'}, バイアスの重み: {tema_points if tema_points else 0}, 特徴: {condi}, 選択: {level_text}, 重い付け: {result_value}",
                         font=('ariel', 16)).pack()

            edit_button = tk.Button(self.edit_window, text="編集", font=('ariel', 12), bg="PaleGreen3", command=lambda r=record: self.edit_data(r))
            edit_button.pack(pady=5)

            delete_button = tk.Button(self.edit_window, text="削除", font=('ariel', 16), bg="red",
                                      command=lambda r=record[0]: self.delete_data(r))
            delete_button.pack(pady=5)

    def edit_data(self, record):
        if self.edit_window:
            self.edit_window.destroy()

        edit_window = tk.Toplevel(self.root)
        edit_window.title("データを編集")

        tk.Label(edit_window, text="テーマ:", font=('ariel', 16)).pack()
        new_tema = tk.Entry(edit_window, font=('ariel', 16))
        new_tema.pack()
        new_tema.insert(0, record[1])

        tk.Label(edit_window, text="バイアスの重み:", font=('ariel', 16)).pack()
        new_tema_points = tk.Entry(edit_window, font=('ariel', 16))
        new_tema_points.insert(0, record[2])
        new_tema_points.pack()

        tk.Label(edit_window, text="特徴:", font=('ariel', 16)).pack()
        new_condi = tk.Text(edit_window, font=('ariel', 16), height=3, width=20)
        new_condi.pack()
        new_condi.insert("1.0", record[3])

        tk.Label(edit_window, text="選択:", font=('ariel', 16)).pack()
        new_level = ttk.Combobox(edit_window, textvariable=self.level_var, values=list(LEVEL_MAPPING.keys()),
                                 font=('ariel', 16))
        new_level.set(self.get_level_text(record[4]))
        new_level.pack()

        tk.Label(edit_window, text="重い付け:", font=('ariel', 16)).pack()
        new_points = tk.Entry(edit_window, font=('ariel', 16))
        new_points.pack()
        if record[5] is not None:
            new_points.insert(0, record[5])

        def update_data():
            updated_tema = new_tema.get()
            updated_tema_points = float(new_tema_points.get())
            updated_condi = new_condi.get("1.0", "end-1c")
            updated_level_text = self.level_var.get()
            updated_points = float(new_points.get())

            updated_level = LEVEL_MAPPING.get(updated_level_text, 0)

            try:
                updated_points = float(updated_points)
                if not (0.1 <= updated_points <= 5.0):
                    raise ValueError("入力の重い付けは0.1~5.0ちょうだい!")
            except ValueError as e:
                messagebox.showerror("エラー", str(e))
                return

            updated_result_value = updated_tema_points  +  (updated_points * updated_level)

            with sqlite3.connect("mydatabase.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE user_data SET tema=?, tema_points=?, condi=?, level=?, points=?, result=? WHERE id=?",
                    (updated_tema, updated_tema_points, updated_condi, updated_level, updated_points,
                     updated_result_value, record[0]))

            edit_window.destroy()
            self.display_data()

        update_button = tk.Button(edit_window, text="更新", font=('ariel', 16),bg="dark cyan", command=update_data)
        update_button.pack()

    def delete_data(self, record_id):
        confirm = messagebox.askyesno("削除の確認", "この記録を削除しますか?")
        if confirm:
            with sqlite3.connect("mydatabase.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_data WHERE id=?", (record_id,))

            self.display_data()

    def get_first_tema_value(self):
        with sqlite3.connect("mydatabase.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tema FROM user_data ORDER BY id LIMIT 1")
            first_tema_value = cursor.fetchone()
            if first_tema_value:
                return first_tema_value[0]
            else:
                return None

    def calculate_total_level(self):
        first_tema_value = self.get_first_tema_value()

        result_text = f"{first_tema_value if first_tema_value else '未知'}"

        with sqlite3.connect("mydatabase.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(result) FROM user_data")
            total_level = cursor.fetchone()[0]

        result = "YES" if total_level > 0 else "NO"

        # Tạo một Toplevel mới
        result_window = tk.Toplevel(self.root)
        result_window.title("判定結果")

        # Hiển thị thông điệp
        message = f"{result_text}❓ : {result}"
        # Làm chữ YES và NO đậm hơn
        result_label = tk.Label(result_window, text=message, font=("Arial", 16, "bold"), padx=20, pady=20)
        result_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
