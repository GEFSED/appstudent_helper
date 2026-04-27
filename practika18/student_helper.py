import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date


DATA_FILE = "student_helper_data.json"


class StudentHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Студенческий помощник")
        self.root.geometry("980x680")
        self.root.minsize(900, 620)

        self.tasks = []
        self.notes = []
        self.grades = []
        self.schedule = []

        self.create_widgets()
        self.load_data()
        self.refresh_all()
    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Студенческий помощник",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=8)

        self.status_label = tk.Label(
            self.root,
            text="Готово",
            font=("Arial", 10),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_tasks = ttk.Frame(self.notebook)
        self.tab_notes = ttk.Frame(self.notebook)
        self.tab_grades = ttk.Frame(self.notebook)
        self.tab_schedule = ttk.Frame(self.notebook)
        self.tab_search = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_tasks, text="Задачи")
        self.notebook.add(self.tab_notes, text="Заметки")
        self.notebook.add(self.tab_grades, text="Оценки")
        self.notebook.add(self.tab_schedule, text="Расписание")
        self.notebook.add(self.tab_search, text="Поиск")

        self.create_tasks_tab()
        self.create_notes_tab()
        self.create_grades_tab()
        self.create_schedule_tab()
        self.create_search_tab()
        self.create_bottom_buttons()
    def create_tasks_tab(self):
        input_frame = ttk.LabelFrame(self.tab_tasks, text="Добавить задачу")
        input_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(input_frame, text="Задача:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.task_text_entry = ttk.Entry(input_frame, width=45)
        self.task_text_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Предмет:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.task_subject_entry = ttk.Entry(input_frame, width=20)
        self.task_subject_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Дедлайн дд.мм.гггг:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.task_deadline_entry = ttk.Entry(input_frame, width=20)
        self.task_deadline_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Приоритет:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.task_priority_box = ttk.Combobox(
            input_frame,
            values=["низкий", "средний", "высокий"],
            state="readonly",
            width=17
        )
        self.task_priority_box.set("средний")
        self.task_priority_box.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Button(input_frame, text="Добавить", command=self.add_task).grid(row=2, column=1, pady=6)
        ttk.Button(input_frame, text="Очистить поля", command=self.clear_task_inputs).grid(row=2, column=2, pady=6)

        table_frame = ttk.LabelFrame(self.tab_tasks, text="Список задач")
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("task", "subject", "deadline", "priority", "status")
        self.tasks_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tasks_tree.heading("task", text="Задача")
        self.tasks_tree.heading("subject", text="Предмет")
        self.tasks_tree.heading("deadline", text="Дедлайн")
        self.tasks_tree.heading("priority", text="Приоритет")
        self.tasks_tree.heading("status", text="Статус")

        self.tasks_tree.column("task", width=330)
        self.tasks_tree.column("subject", width=130)
        self.tasks_tree.column("deadline", width=100)
        self.tasks_tree.column("priority", width=90)
        self.tasks_tree.column("status", width=110)

        self.tasks_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        buttons_frame = ttk.Frame(self.tab_tasks)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(buttons_frame, text="Выполнено / не выполнено", command=self.toggle_task_status).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Удалить выбранную задачу", command=self.delete_task).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Показать ближайшие дедлайны", command=self.show_deadlines).pack(side="left", padx=5)

    def add_task(self):
        task = self.task_text_entry.get().strip()
        subject = self.task_subject_entry.get().strip()
        deadline = self.task_deadline_entry.get().strip()
        priority = self.task_priority_box.get()

        if not task:
            messagebox.showwarning("Ошибка", "Введите текст задачи.")
            return

        if not subject:
            subject = "Без предмета"

        if deadline:
            if not self.is_valid_date(deadline):
                messagebox.showerror("Ошибка", "Дедлайн должен быть в формате дд.мм.гггг, например 25.04.2026.")
                return
        else:
            deadline = "без дедлайна"

        self.tasks.append({
            "task": task,
            "subject": subject,
            "deadline": deadline,
            "priority": priority,
            "status": "не выполнено"
        })

        self.clear_task_inputs()
        self.refresh_tasks()
        self.save_data()
        self.set_status("Задача добавлена.")

    def clear_task_inputs(self):
        self.task_text_entry.delete(0, tk.END)
        self.task_subject_entry.delete(0, tk.END)
        self.task_deadline_entry.delete(0, tk.END)
        self.task_priority_box.set("средний")

    def toggle_task_status(self):
        index = self.get_selected_index(self.tasks_tree)
        if index is None:
            return

        current = self.tasks[index]["status"]
        self.tasks[index]["status"] = "выполнено" if current == "не выполнено" else "не выполнено"
        self.refresh_tasks()
        self.save_data()

    def delete_task(self):
        index = self.get_selected_index(self.tasks_tree)
        if index is None:
            return

        del self.tasks[index]
        self.refresh_tasks()
        self.save_data()
        self.set_status("Задача удалена.")

    def show_deadlines(self):
        active_tasks = [task for task in self.tasks if task["status"] != "выполнено"]

        dated_tasks = []
        for task in active_tasks:
            if self.is_valid_date(task["deadline"]):
                deadline_date = datetime.strptime(task["deadline"], "%d.%m.%Y").date()
                dated_tasks.append((deadline_date, task))

        dated_tasks.sort(key=lambda item: item[0])

        if not dated_tasks:
            messagebox.showinfo("Дедлайны", "Активных задач с датами дедлайна нет.")
            return

        text = "Ближайшие дедлайны:\n\n"
        for deadline_date, task in dated_tasks[:10]:
            days_left = (deadline_date - date.today()).days
            if days_left < 0:
                time_text = f"просрочено на {abs(days_left)} дн."
            elif days_left == 0:
                time_text = "сегодня"
            else:
                time_text = f"осталось {days_left} дн."

            text += f"{task['deadline']} — {task['task']} ({task['subject']}) — {time_text}\n"

        messagebox.showinfo("Дедлайны", text)

    def refresh_tasks(self):
        self.clear_tree(self.tasks_tree)
        for task in self.tasks:
            self.tasks_tree.insert(
                "",
                tk.END,
                values=(
                    task["task"],
                    task["subject"],
                    task["deadline"],
                    task["priority"],
                    task["status"]
                )
            )

    def create_notes_tab(self):
        input_frame = ttk.LabelFrame(self.tab_notes, text="Добавить заметку")
        input_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(input_frame, text="Тема:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.note_title_entry = ttk.Entry(input_frame, width=35)
        self.note_title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Предмет:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.note_subject_entry = ttk.Entry(input_frame, width=25)
        self.note_subject_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Текст заметки:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.note_text = tk.Text(input_frame, width=75, height=6)
        self.note_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить заметку", command=self.add_note).grid(row=2, column=1, pady=6)
        ttk.Button(input_frame, text="Очистить поля", command=self.clear_note_inputs).grid(row=2, column=2, pady=6)

        list_frame = ttk.LabelFrame(self.tab_notes, text="Список заметок")
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("title", "subject", "date")
        self.notes_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.notes_tree.heading("title", text="Тема")
        self.notes_tree.heading("subject", text="Предмет")
        self.notes_tree.heading("date", text="Дата")

        self.notes_tree.column("title", width=350)
        self.notes_tree.column("subject", width=180)
        self.notes_tree.column("date", width=160)

        self.notes_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        buttons_frame = ttk.Frame(self.tab_notes)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(buttons_frame, text="Открыть заметку", command=self.open_note).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Удалить заметку", command=self.delete_note).pack(side="left", padx=5)

    def add_note(self):
        title = self.note_title_entry.get().strip()
        subject = self.note_subject_entry.get().strip()
        text = self.note_text.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showwarning("Ошибка", "Введите тему заметки.")
            return

        if not text:
            messagebox.showwarning("Ошибка", "Введите текст заметки.")
            return

        if not subject:
            subject = "Без предмета"

        self.notes.append({
            "title": title,
            "subject": subject,
            "text": text,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })

        self.clear_note_inputs()
        self.refresh_notes()
        self.save_data()
        self.set_status("Заметка добавлена.")

    def clear_note_inputs(self):
        self.note_title_entry.delete(0, tk.END)
        self.note_subject_entry.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)

    def open_note(self):
        index = self.get_selected_index(self.notes_tree)
        if index is None:
            return

        note = self.notes[index]
        text = f"Тема: {note['title']}\nПредмет: {note['subject']}\nДата: {note['date']}\n\n{note['text']}"
        messagebox.showinfo("Заметка", text)

    def delete_note(self):
        index = self.get_selected_index(self.notes_tree)
        if index is None:
            return

        del self.notes[index]
        self.refresh_notes()
        self.save_data()
        self.set_status("Заметка удалена.")

    def refresh_notes(self):
        self.clear_tree(self.notes_tree)
        for note in self.notes:
            self.notes_tree.insert(
                "",
                tk.END,
                values=(note["title"], note["subject"], note["date"])
            )

    def create_grades_tab(self):
        input_frame = ttk.LabelFrame(self.tab_grades, text="Добавить оценку")
        input_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(input_frame, text="Предмет:").grid(row=0, column=0, padx=5, pady=5)
        self.grade_subject_entry = ttk.Entry(input_frame, width=25)
        self.grade_subject_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Оценка:").grid(row=0, column=2, padx=5, pady=5)
        self.grade_value_entry = ttk.Entry(input_frame, width=10)
        self.grade_value_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Комментарий:").grid(row=0, column=4, padx=5, pady=5)
        self.grade_comment_entry = ttk.Entry(input_frame, width=30)
        self.grade_comment_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить", command=self.add_grade).grid(row=1, column=1, pady=6)
        ttk.Button(input_frame, text="Удалить выбранную", command=self.delete_grade).grid(row=1, column=2, pady=6)
        ttk.Button(input_frame, text="Посчитать средний балл", command=self.calculate_grades).grid(row=1, column=3, pady=6)

        table_frame = ttk.LabelFrame(self.tab_grades, text="Оценки")
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("subject", "grade", "comment", "date")
        self.grades_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.grades_tree.heading("subject", text="Предмет")
        self.grades_tree.heading("grade", text="Оценка")
        self.grades_tree.heading("comment", text="Комментарий")
        self.grades_tree.heading("date", text="Дата")

        self.grades_tree.column("subject", width=180)
        self.grades_tree.column("grade", width=80)
        self.grades_tree.column("comment", width=360)
        self.grades_tree.column("date", width=160)

        self.grades_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.grades_result_label = tk.Label(
            self.tab_grades,
            text="Средний балл: —",
            font=("Arial", 13, "bold")
        )
        self.grades_result_label.pack(pady=6)

    def add_grade(self):
        subject = self.grade_subject_entry.get().strip()
        value = self.grade_value_entry.get().strip().replace(",", ".")
        comment = self.grade_comment_entry.get().strip()

        if not subject:
            messagebox.showwarning("Ошибка", "Введите предмет.")
            return

        try:
            grade = float(value)
        except ValueError:
            messagebox.showerror("Ошибка", "Оценка должна быть числом.")
            return

        if grade < 1 or grade > 5:
            messagebox.showerror("Ошибка", "Оценка должна быть от 1 до 5.")
            return

        if not comment:
            comment = "без комментария"

        self.grades.append({
            "subject": subject,
            "grade": grade,
            "comment": comment,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })

        self.grade_subject_entry.delete(0, tk.END)
        self.grade_value_entry.delete(0, tk.END)
        self.grade_comment_entry.delete(0, tk.END)

        self.refresh_grades()
        self.calculate_grades(show_message=False)
        self.save_data()
        self.set_status("Оценка добавлена.")

    def delete_grade(self):
        index = self.get_selected_index(self.grades_tree)
        if index is None:
            return

        del self.grades[index]
        self.refresh_grades()
        self.calculate_grades(show_message=False)
        self.save_data()

    def calculate_grades(self, show_message=True):
        if not self.grades:
            self.grades_result_label.config(text="Средний балл: —")
            if show_message:
                messagebox.showinfo("Средний балл", "Оценок пока нет.")
            return

        total = sum(item["grade"] for item in self.grades)
        average = total / len(self.grades)

        by_subject = {}
        for item in self.grades:
            by_subject.setdefault(item["subject"], []).append(item["grade"])

        text = f"Средний балл общий: {average:.2f}\n\nПо предметам:\n"
        for subject, grades in by_subject.items():
            subject_average = sum(grades) / len(grades)
            text += f"{subject}: {subject_average:.2f}\n"

        self.grades_result_label.config(text=f"Средний балл: {average:.2f}")

        if show_message:
            messagebox.showinfo("Средний балл", text)

    def refresh_grades(self):
        self.clear_tree(self.grades_tree)
        for item in self.grades:
            self.grades_tree.insert(
                "",
                tk.END,
                values=(item["subject"], item["grade"], item["comment"], item["date"])
            )

    def create_schedule_tab(self):
        input_frame = ttk.LabelFrame(self.tab_schedule, text="Добавить занятие")
        input_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(input_frame, text="День:").grid(row=0, column=0, padx=5, pady=5)
        self.schedule_day_box = ttk.Combobox(
            input_frame,
            values=["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
            state="readonly",
            width=18
        )
        self.schedule_day_box.set("Понедельник")
        self.schedule_day_box.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Время:").grid(row=0, column=2, padx=5, pady=5)
        self.schedule_time_entry = ttk.Entry(input_frame, width=15)
        self.schedule_time_entry.insert(0, "09:00")
        self.schedule_time_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Предмет:").grid(row=0, column=4, padx=5, pady=5)
        self.schedule_subject_entry = ttk.Entry(input_frame, width=25)
        self.schedule_subject_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(input_frame, text="Аудитория:").grid(row=1, column=0, padx=5, pady=5)
        self.schedule_room_entry = ttk.Entry(input_frame, width=20)
        self.schedule_room_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Преподаватель:").grid(row=1, column=2, padx=5, pady=5)
        self.schedule_teacher_entry = ttk.Entry(input_frame, width=25)
        self.schedule_teacher_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить занятие", command=self.add_schedule_item).grid(row=1, column=4, padx=5, pady=6)
        ttk.Button(input_frame, text="Удалить выбранное", command=self.delete_schedule_item).grid(row=1, column=5, padx=5, pady=6)

        table_frame = ttk.LabelFrame(self.tab_schedule, text="Расписание")
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        columns = ("day", "time", "subject", "room", "teacher")
        self.schedule_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.schedule_tree.heading("day", text="День")
        self.schedule_tree.heading("time", text="Время")
        self.schedule_tree.heading("subject", text="Предмет")
        self.schedule_tree.heading("room", text="Аудитория")
        self.schedule_tree.heading("teacher", text="Преподаватель")

        self.schedule_tree.column("day", width=130)
        self.schedule_tree.column("time", width=80)
        self.schedule_tree.column("subject", width=230)
        self.schedule_tree.column("room", width=100)
        self.schedule_tree.column("teacher", width=220)

        self.schedule_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def add_schedule_item(self):
        day = self.schedule_day_box.get()
        time = self.schedule_time_entry.get().strip()
        subject = self.schedule_subject_entry.get().strip()
        room = self.schedule_room_entry.get().strip()
        teacher = self.schedule_teacher_entry.get().strip()

        if not subject:
            messagebox.showwarning("Ошибка", "Введите предмет.")
            return

        if not time:
            time = "время не указано"

        if not room:
            room = "н/д"

        if not teacher:
            teacher = "н/д"

        self.schedule.append({
            "day": day,
            "time": time,
            "subject": subject,
            "room": room,
            "teacher": teacher
        })

        self.schedule_subject_entry.delete(0, tk.END)
        self.schedule_room_entry.delete(0, tk.END)
        self.schedule_teacher_entry.delete(0, tk.END)

        self.refresh_schedule()
        self.save_data()
        self.set_status("Занятие добавлено.")

    def delete_schedule_item(self):
        index = self.get_selected_index(self.schedule_tree)
        if index is None:
            return

        del self.schedule[index]
        self.refresh_schedule()
        self.save_data()

    def refresh_schedule(self):
        self.clear_tree(self.schedule_tree)

        days_order = {
            "Понедельник": 1,
            "Вторник": 2,
            "Среда": 3,
            "Четверг": 4,
            "Пятница": 5,
            "Суббота": 6,
            "Воскресенье": 7
        }

        sorted_schedule = sorted(
            self.schedule,
            key=lambda item: (days_order.get(item["day"], 99), item["time"])
        )

        self.schedule = sorted_schedule

        for item in self.schedule:
            self.schedule_tree.insert(
                "",
                tk.END,
                values=(item["day"], item["time"], item["subject"], item["room"], item["teacher"])
            )
    def create_search_tab(self):
        top_frame = ttk.LabelFrame(self.tab_search, text="Поиск")
        top_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(top_frame, text="Введите запрос:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(top_frame, width=50)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(top_frame, text="Найти", command=self.search_items).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Очистить", command=self.clear_search).pack(side="left", padx=5)

        self.search_result = tk.Text(self.tab_search, height=25, font=("Arial", 11))
        self.search_result.pack(fill="both", expand=True, padx=10, pady=8)

    def search_items(self):
        query = self.search_entry.get().strip().lower()

        if not query:
            messagebox.showwarning("Ошибка", "Введите запрос.")
            return

        result = "РЕЗУЛЬТАТЫ ПОИСКА\n"
        result += "=" * 40 + "\n\n"

        found = False

        result += "ЗАДАЧИ:\n"
        for task in self.tasks:
            text = f"{task['task']} {task['subject']} {task['deadline']} {task['priority']} {task['status']}".lower()
            if query in text:
                found = True
                result += f"- {task['task']} | {task['subject']} | {task['deadline']} | {task['status']}\n"

        result += "\nЗАМЕТКИ:\n"
        for note in self.notes:
            text = f"{note['title']} {note['subject']} {note['text']}".lower()
            if query in text:
                found = True
                result += f"- {note['title']} | {note['subject']} | {note['date']}\n"

        result += "\nОЦЕНКИ:\n"
        for grade in self.grades:
            text = f"{grade['subject']} {grade['grade']} {grade['comment']}".lower()
            if query in text:
                found = True
                result += f"- {grade['subject']} | {grade['grade']} | {grade['comment']}\n"

        result += "\nРАСПИСАНИЕ:\n"
        for item in self.schedule:
            text = f"{item['day']} {item['time']} {item['subject']} {item['room']} {item['teacher']}".lower()
            if query in text:
                found = True
                result += f"- {item['day']} {item['time']} | {item['subject']} | {item['room']} | {item['teacher']}\n"

        if not found:
            result += "\nНичего не найдено."

        self.search_result.delete("1.0", tk.END)
        self.search_result.insert("1.0", result)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_result.delete("1.0", tk.END)
    def create_bottom_buttons(self):
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=8)

        ttk.Button(bottom, text="Сохранить", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(bottom, text="Загрузить", command=self.load_data_from_button).pack(side="left", padx=5)
        ttk.Button(bottom, text="Экспорт отчёта TXT", command=self.export_txt).pack(side="left", padx=5)
        ttk.Button(bottom, text="Очистить все данные", command=self.clear_all_data).pack(side="left", padx=5)
        ttk.Button(bottom, text="Выход", command=self.root.destroy).pack(side="right", padx=5)
    def save_data(self):
        data = {
            "tasks": self.tasks,
            "notes": self.notes,
            "grades": self.grades,
            "schedule": self.schedule
        }

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            self.set_status(f"Данные сохранены в {DATA_FILE}")
        except OSError as error:
            messagebox.showerror("Ошибка сохранения", str(error))

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.tasks = data.get("tasks", [])
            self.notes = data.get("notes", [])
            self.grades = data.get("grades", [])
            self.schedule = data.get("schedule", [])
            self.set_status(f"Данные загружены из {DATA_FILE}")
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showerror("Ошибка загрузки", str(error))

    def load_data_from_button(self):
        self.load_data()
        self.refresh_all()

    def export_txt(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить отчёт",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write("ОТЧЁТ ИЗ СТУДЕНЧЕСКОГО ПОМОЩНИКА\n")
                file.write("=" * 45 + "\n\n")

                file.write("ЗАДАЧИ\n")
                file.write("-" * 20 + "\n")
                if self.tasks:
                    for task in self.tasks:
                        file.write(
                            f"{task['task']} | {task['subject']} | "
                            f"{task['deadline']} | {task['priority']} | {task['status']}\n"
                        )
                else:
                    file.write("Нет задач.\n")

                file.write("\nЗАМЕТКИ\n")
                file.write("-" * 20 + "\n")
                if self.notes:
                    for note in self.notes:
                        file.write(f"{note['title']} | {note['subject']} | {note['date']}\n")
                        file.write(note["text"] + "\n\n")
                else:
                    file.write("Нет заметок.\n")

                file.write("\nОЦЕНКИ\n")
                file.write("-" * 20 + "\n")
                if self.grades:
                    for grade in self.grades:
                        file.write(
                            f"{grade['subject']} | {grade['grade']} | "
                            f"{grade['comment']} | {grade['date']}\n"
                        )
                else:
                    file.write("Нет оценок.\n")

                file.write("\nРАСПИСАНИЕ\n")
                file.write("-" * 20 + "\n")
                if self.schedule:
                    for item in self.schedule:
                        file.write(
                            f"{item['day']} | {item['time']} | "
                            f"{item['subject']} | {item['room']} | {item['teacher']}\n"
                        )
                else:
                    file.write("Нет расписания.\n")

            messagebox.showinfo("Экспорт", "Отчёт успешно сохранён.")
        except OSError as error:
            messagebox.showerror("Ошибка экспорта", str(error))

    def clear_all_data(self):
        answer = messagebox.askyesno(
            "Подтверждение",
            "Точно удалить все задачи, заметки, оценки и расписание?"
        )

        if not answer:
            return

        self.tasks = []
        self.notes = []
        self.grades = []
        self.schedule = []
        self.refresh_all()
        self.save_data()
        self.set_status("Все данные очищены.")
    def refresh_all(self):
        self.refresh_tasks()
        self.refresh_notes()
        self.refresh_grades()
        self.refresh_schedule()
        self.calculate_grades(show_message=False)

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def get_selected_index(self, tree):
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Ошибка", "Выберите строку в таблице.")
            return None

        item_id = selected[0]
        index = tree.index(item_id)
        return index

    def is_valid_date(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def set_status(self, text):
        self.status_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentHelperApp(root)
    root.mainloop()
