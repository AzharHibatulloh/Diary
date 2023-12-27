import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import csv
import os
from datetime import datetime


class DailyNoteApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Daily Note App")

        # File initialization
        self.users_filename = "users.csv"
        self.plan_folder = "plan"
        if not os.path.exists(self.plan_folder):
            os.makedirs(self.plan_folder)
        self.checkbox_vars = []
        self.active_user = None

        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.diary_text_var = tk.StringVar()
        self.notes_text_var = tk.StringVar()
        self.plan_text_var = tk.StringVar()
        self.selected_date = tk.StringVar()
        self.checkbox_text_var = tk.StringVar()

        # UI Elements
        self.login_frame = tk.Frame(self.master)
        self.diary_list = tk.Frame(self.master)
        self.diary_frame = tk.Frame(self.master)
        self.notes_frame = tk.Frame(self.master)
        self.plan_frame = tk.Frame(self.master)

        self.plan_checkbox_frame = tk.Frame(
            self.plan_frame
        )  # Frame untuk checkbox tugas
        self.checkbox_entry = tk.Entry(
            self.plan_frame, textvariable=self.checkbox_text_var, width=30
        )
        #   self.show_frame(self.notes_frame)
        self.current_frame = None  # Untuk melacak frame yang sedang ditampilkan

        self.create_widgets()

    def create_widgets(self):
        # Login Frame
        tk.Label(self.login_frame, text="Username:").pack()
        tk.Entry(self.login_frame, textvariable=self.username_var).pack()
        tk.Label(self.login_frame, text="Password:").pack()
        tk.Entry(self.login_frame, textvariable=self.password_var, show="*").pack()
        tk.Button(self.login_frame, text="Register", command=self.register_user).pack()
        tk.Button(self.login_frame, text="Login", command=self.login).pack()

        # Diary Frame
        tk.Label(self.diary_frame, text="Diary List:").pack()
        self.diary_listbox = tk.Listbox(
            self.diary_frame, height=5, selectmode=tk.SINGLE
        )
        self.diary_listbox.pack()
        self.refresh_diary_list()

        tk.Button(
            self.diary_frame, text="Add Diary File", command=self.add_diary
        ).pack()
        tk.Button(self.diary_frame, text="Open Diary", command=self.open_diary).pack()

        # Diary Frame
        tk.Label(self.diary_frame, text="Diary:").pack()
        self.diary_text = tk.Text(self.diary_frame, height=10, width=40, wrap=tk.WORD)
        self.diary_text.pack()
        tk.Button(self.diary_frame, text="Save Diary", command=self.save_diary).pack()

        # Notes Frame
        tk.Label(self.notes_frame, text="Notes:").pack()
        self.notes_text = tk.Text(self.notes_frame, height=10, width=40, wrap=tk.WORD)
        self.notes_text.pack()
        tk.Button(self.notes_frame, text="Save Notes", command=self.save_notes).pack()
        tk.Button(self.notes_frame, text="Read Notes", command=self.read_notes).pack()

        # Plan Frame
        tk.Label(self.plan_frame, text="Plan:", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self.plan_frame, text="Pick Date", command=self.show_calendar).pack(
            pady=5
        )

        # Entry untuk menambahkan isi checkbox
        self.checkbox_entry.pack(pady=5)
        tk.Button(self.plan_frame, text="Add Checkbox", command=self.add_checkbox).pack(
            pady=5
        )

        # Frame untuk menampilkan checkbox tugas
        self.plan_checkbox_frame.pack(pady=10)

        # Show login frame initially
        self.show_frame(self.login_frame)

    def create_users_file(self):
            # Add header if the CSV file is newly created
            if not os.path.exists(self.users_filename):
                with open(self.users_filename, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["username", "password"])

    def create_plan_file(self, selected_date):
        if self.active_user:
            username = self.active_user
            plan_dir = os.path.join("plan", username)
            if not os.path.exists(plan_dir):
                os.makedirs(plan_dir)

            filename = os.path.join(plan_dir, f"plan_{selected_date}.csv")
            file_exists = os.path.exists(filename)

            with open(filename, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Menulis header jika file tidak memiliki header
                if not file_exists or file.tell() == 0:
                    writer.writerow(["item", "checked"])

    def update_checkbox_status(self, checkbox_text, checked):
        selected_date = self.selected_date.get()
        if selected_date:
            # Membaca data plan yang ada
            plan_data = self.read_plan_from_csv(selected_date)

            # Membuat dictionary dari data yang sudah ada
            existing_tasks = (
                {row["item"]: row["checked"] for row in plan_data} if plan_data else {}
            )

            # Memperbarui atau menambahkan entri untuk checkbox yang diubah
            existing_tasks[checkbox_text] = str(checked)

            # Simpan data plan ke file CSV dengan nama file sesuai tanggal dan username
            username = self.username_var.get()
            user_plan_dir = os.path.join(self.plan_folder, username)
            if not os.path.exists(user_plan_dir):
                os.makedirs(user_plan_dir)

            filename = os.path.join(user_plan_dir, f"plan_{selected_date}.csv")

            # Tulis header
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["item", "checked"])

                # Tulis entri untuk setiap tugas
                for task_text, task_checked in existing_tasks.items():
                    writer.writerow([task_text, task_checked])

        # Tampilkan checkbox setelah menyimpan rencana
        self.show_plan_checkboxes()

        # Menampilkan pesan informasi
        messagebox.showinfo("Update Plan", "Plan updated successfully")

    def set_date(self):
        selected_date = self.selected_date.get()
        self.selected_date.set(selected_date)
        # top.destroy()
        self.show_plan_text()
        self.create_plan_file(
            selected_date
        )  # Memanggil fungsi untuk membuat file plan CSV

    def update_plan_text(self, event=None):
        selected_date_index = self.date_listbox.curselection()
        if selected_date_index:
            selected_date = self.date_listbox.get(selected_date_index)
            self.selected_date.set(selected_date)
            self.show_plan_text()

    def read_plan_from_csv(self, selected_date):
        if self.active_user:
            username = self.active_user
            plan_dir = os.path.join("plan", username)
            plan_file_path = os.path.join(plan_dir, f"plan_{selected_date}.csv")
            try:
                with open(
                    plan_file_path, mode="r", newline="", encoding="utf-8"
                ) as file:
                    reader = csv.DictReader(file)
                    return list(reader)
            except FileNotFoundError:
                return None

    def save_plan(self):
        selected_date = self.selected_date.get()

        # Mendapatkan teks dari entry plan
        new_plan_text = self.plan_text_var.get("1.0", tk.END).strip()

        # Menambahkan entri untuk checkbox baru (jika ada)
        if new_plan_text:
            # Membaca data plan yang sudah ada
            existing_data = self.read_plan_from_csv(selected_date)

            # Membuat list dari data yang sudah ada atau membuat list kosong jika tidak ada data
            existing_tasks = existing_data if existing_data else []

            # Menambahkan entri untuk checkbox baru
            existing_tasks.append({"item": new_plan_text, "checked": "False"})

            # Simpan data plan ke file CSV dengan nama file sesuai tanggal
            if self.active_user:
                username = self.active_user
                filename = os.path.join("plan", username)
                if not os.path.exists(filename):
                    os.makedirs(filename)

                plan_file_path = os.path.join(filename, f"plan_{selected_date}.csv")
                with open(
                    plan_file_path, mode="w", newline="", encoding="utf-8"
                ) as file:
                    writer = csv.writer(file)

                # Tulis header hanya jika file kosong
                if not existing_data:
                    writer.writerow(["item", "checked"])

                # Tulis entri untuk setiap tugas
                for task in existing_tasks:
                    writer.writerow([task["item"], task["checked"]])

        # Tampilkan checkbox setelah menyimpan rencana
        self.show_plan_checkboxes()

        # Menampilkan pesan informasi
        messagebox.showinfo("Save Plan", "Plan saved successfully")

    def populate_checkbox_vars(self, plan_data):
        # Clear the checkbox_vars list
        self.checkbox_vars = []

        # Initialize or update the checkbox_vars list
        for row in plan_data:
            checked = row["checked"] == "True"
            checkbox_var = tk.BooleanVar(value=checked)
            self.checkbox_vars.append(checkbox_var)

    def get_checked_items(self):
        checkboxes = self.plan_checkbox_frame.winfo_children()
        return [
            {"item": checkbox.cget("text"), "checked": checkbox.var.get()}
            for checkbox in checkboxes
            if isinstance(checkbox, tk.Checkbutton) and hasattr(checkbox, "var")
        ]

    def update_plan_text(self, event=None):
        selected_date = self.selected_date.get()
        if selected_date:
            plan_data = self.read_plan_from_csv(selected_date)
            if plan_data:
                self.plan_text_var.set(plan_data)
                self.show_plan_checkboxes()
            else:
                self.clear_plan_checkboxes()

    def show_plan_checkboxes(self):
        selected_date = self.selected_date.get()
        if selected_date:
            plan_data = self.read_plan_from_csv(selected_date)
            if plan_data:
                self.populate_checkbox_vars(plan_data)
                self.display_plan_checkboxes(plan_data)

    def display_plan_checkboxes(self, plan_data):
        # Clear all checkboxes in the frame before adding new ones
        for widget in self.plan_checkbox_frame.winfo_children():
            widget.destroy()

        # Display checkboxes for each task
        for row, checkbox_var in zip(plan_data, self.checkbox_vars):
            checked = row["checked"] == "True"
            checkbox_text = row["item"].replace("(checked)", "").strip()
            checkbox = tk.Checkbutton(
                self.plan_checkbox_frame,
                text=checkbox_text,
                variable=checkbox_var,
                command=lambda c=checkbox_text, v=checkbox_var: self.update_checkbox_status(
                    c, v.get()
                ),
            )
            checkbox.pack(anchor="w")

    def clear_plan_checkboxes(self):
        for widget in self.plan_checkbox_frame.winfo_children():
            widget.destroy()

    def add_checkbox(self):
        checkbox_text = self.checkbox_text_var.get().strip()
        if checkbox_text:
            checkbox_var = tk.BooleanVar(value=False)
            checkbox = tk.Checkbutton(
                self.plan_checkbox_frame,
                text=checkbox_text,
                variable=checkbox_var,
                command=lambda c=checkbox_text, v=checkbox_var: self.update_checkbox_status(
                    c, v.get()
                ),
            )
            checkbox.var = checkbox_var  # Simpan variabel di properti objek checkbox
            checkbox.pack(anchor="w")
            self.checkbox_vars.append(checkbox_var)  # Simpan BooleanVar dalam daftar
            self.checkbox_text_var.set("")

    def open_diary(self):
        selected_index = self.diary_listbox.curselection()
        if selected_index:
            selected_diary = self.diary_listbox.get(selected_index)

            username = self.username_var.get()  # Ambil username pengguna yang aktif
            diary_dir = os.path.join("diaries", username)
            diary_file_path = os.path.join(diary_dir, selected_diary)

            try:
                with open(diary_file_path, mode="r", encoding="utf-8") as file:
                    diary_content = file.read()

                self.diary_text.delete("1.0", tk.END)
                self.diary_text.insert(tk.END, diary_content)
                self.diary_text.config(state=tk.NORMAL)
            except FileNotFoundError:
                messagebox.showwarning("Open Diary", "No diary found.")
        else:
            messagebox.showwarning("Open Diary", "No diary selected.")

    def refresh_diary_list(self):
        username = self.username_var.get()  # Ambil username pengguna yang aktif

        self.diary_listbox.delete(0, tk.END)

        diary_dir = os.path.join("diaries", username)
        if not os.path.exists(diary_dir):
            os.makedirs(diary_dir)

        diary_files = [f for f in os.listdir(diary_dir) if f.endswith(".txt")]
        for diary_file in diary_files:
            self.diary_listbox.insert(tk.END, diary_file)

    def save_changes_diary(self):
        selected_index = self.diary_listbox.curselection()
        if selected_index:
            selected_diary = self.diary_listbox.get(selected_index)

            username = self.username_var.get()  # Ambil username pengguna yang aktif
            diary_dir = os.path.join("diaries", username)
            diary_file_path = os.path.join(diary_dir, selected_diary)
            with open(diary_file_path, mode="w", encoding="utf-8") as file:
                file.write(self.diary_text.get("1.0", tk.END))

            messagebox.showinfo("Save Diary", "Diary changes saved successfully")
            self.refresh_diary_list()
            self.diary_text.config(state=tk.DISABLED)

    def add_diary(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if username and password:
            diary_dir = os.path.join("diaries", username)
            if not os.path.exists(diary_dir):
                os.makedirs(diary_dir)

            timestamp = datetime.now().strftime("%d-%m-%Y")
            new_diary_file = os.path.join(diary_dir, f"{timestamp}.txt")

            with open(new_diary_file, mode="w", encoding="utf-8") as file:
                file.write(self.diary_text.get("1.0", tk.END))

            self.refresh_diary_list()
        else:
            messagebox.showwarning("Add Diary", "Please login first.")

    def save_diary(self):
        selected_index = self.diary_listbox.curselection()
        if selected_index:
            selected_diary = self.diary_listbox.get(selected_index)

            username = self.username_var.get()  # Ambil username pengguna yang aktif
            diary_dir = os.path.join("diaries", username)
            diary_file_path = os.path.join(diary_dir, selected_diary)
            with open(diary_file_path, mode="w", encoding="utf-8") as file:
                file.write(self.diary_text.get("1.0", tk.END))

            messagebox.showinfo("Save Diary", "Diary changes saved successfully")
            self.refresh_diary_list()
            self.diary_text.config(state=tk.DISABLED)

    def register_user(self):
        print("Entering register_user")
        username = self.username_var.get()
        password = self.password_var.get()

        with open(self.users_filename, mode="a", newline="", encoding="utf-8") as file:
            print(f"File position before writing: {file.tell()}")
            writer = csv.writer(file)
            # Add header if the CSV file is newly created
            if file.tell() == 0:
                print("Writing header")
                writer.writerow(["username", "password"])
            writer.writerow([username, password])

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        with open(self.users_filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username and row["password"] == password:
                    messagebox.showinfo("Login", "Login Successful")
                    self.active_user = username  # Simpan username yang aktif
                    self.show_menu_frame()
                    return

        messagebox.showerror("Login", "Invalid username or password")

    def show_calendar(self):
        top = tk.Toplevel(self.plan_frame)
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=10)

        def set_date():
            selected_date = cal.get_date()
            self.selected_date.set(selected_date)
            top.destroy()
            self.show_plan_text()

        tk.Button(top, text="Set Date", command=set_date).pack(pady=5)

    def show_plan_text(self):
        self.show_frame(self.plan_frame)
        self.update_plan_text()

    def get_distinct_dates(self):
        try:
            with open(
                self.users_filename, mode="r", newline="", encoding="utf-8"
            ) as file:
                reader = csv.reader(file)
                dates = set(row[0] for row in reader)
                return sorted(dates, reverse=True)
        except FileNotFoundError:
            return []

    def save_notes(self):
        notes_content = self.notes_text.get("1.0", tk.END).strip()
        username = self.username_var.get()

        if notes_content and username:
            notes_dir = os.path.join(
                "notes", username
            )  # Gunakan direktori berdasarkan username
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir)

            notes_file_path = os.path.join(notes_dir, "notes.txt")

            with open(notes_file_path, mode="w", encoding="utf-8") as file:
                file.write(notes_content)

            messagebox.showinfo("Save Notes", "Notes saved successfully")
        else:
            messagebox.showwarning("Save Notes", "Notes are empty. Nothing to save.")

    def read_notes(self):
        username = self.username_var.get()
        notes_dir = os.path.join("notes", username)
        notes_file_path = os.path.join(notes_dir, "notes.txt")

        try:
            with open(notes_file_path, mode="r", encoding="utf-8") as file:
                notes_content = file.read()

            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert(tk.END, notes_content)
            self.notes_text.config(state=tk.NORMAL)

            messagebox.showinfo("Read Notes", "Notes read successfully")
        except FileNotFoundError:
            messagebox.showwarning("Read Notes", "No notes found.")

    def show_menu_frame(self):
        self.login_frame.pack_forget()
        menu_frame = tk.Frame(self.master)

        tk.Button(
            menu_frame, text="Diary", command=lambda: self.show_frame(self.diary_frame)
        ).pack(side=tk.LEFT)
        tk.Button(
            menu_frame, text="Notes", command=lambda: self.show_frame(self.notes_frame)
        ).pack(side=tk.LEFT)
        tk.Button(
            menu_frame, text="Plan", command=lambda: self.show_frame(self.plan_frame)
        ).pack(side=tk.LEFT)
        tk.Button(menu_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT)

        menu_frame.pack(side=tk.TOP)

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.pack_forget()  # Hide the current frame
        frame.pack()  # Show the new frame
        self.current_frame = frame  # Update the current frame

    def logout(self):
        self.show_initial_view()
        self.username_var.set("")  # Membersihkan nilai username
        self.password_var.set("")  # Membersihkan nilai password
        self.notes_text.delete("1.0", tk.END)
        self.diary_text.delete("1.0", tk.END)

    def show_initial_view(self):
        if self.current_frame:
            self.current_frame.pack_forget()  # Sembunyikan frame saat ini

        # Tampilkan frame login
        self.show_frame(self.login_frame)
        self.hide_menu_buttons()

    def hide_menu_buttons(self):
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.login_frame:
                widget.pack_forget()


def main():
    root = tk.Tk()
    app = DailyNoteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
