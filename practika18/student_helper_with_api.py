import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError


DATA_FILE = "student_helper_data.json"


class StudentHelperApp:
    def __init__(self, root, weather_api_key=""):
        self.root = root
        self.weather_api_key = weather_api_key

        self.root.title("Студенческий помощник")
        self.root.geometry("980x700")

        self.tasks = []
        self.notes = []
        self.grades = []
        self.schedule = []

        self.create_interface()
        self.load_data()
        self.refresh_all()

    def create_interface(self):
        title = tk.Label(self.root, text="Студенческий помощник", font=("Arial", 22, "bold"))
        title.pack(pady=8)

        self.status_label = tk.Label(self.root, text="Готово", anchor="w")
        self.status_label.pack(fill="x", padx=10)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_tasks = ttk.Frame(self.tabs)
        self.tab_notes = ttk.Frame(self.tabs)
        self.tab_grades = ttk.Frame(self.tabs)
        self.tab_schedule = ttk.Frame(self.tabs)
        self.tab_weather = ttk.Frame(self.tabs)
        self.tab_search = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_tasks, text="Задачи")
        self.tabs.add(self.tab_notes, text="Заметки")
        self.tabs.add(self.tab_grades, text="Оценки")
        self.tabs.add(self.tab_schedule, text="Расписание")
        self.tabs.add(self.tab_weather, text="Погода API")
        self.tabs.add(self.tab_search, text="Поиск")

        self.create_tasks_tab()
        self.create_notes_tab()
        self.create_grades_tab()
        self.create_schedule_tab()
        self.create_weather_tab()
        self.create_search_tab()
        self.create_bottom_buttons()

    # ---------- ЗАДАЧИ ----------
    def create_tasks_tab(self):
        form = ttk.LabelFrame(self.tab_tasks, text="Новая задача")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Задача:").grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = ttk.Entry(form, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Предмет:").grid(row=0, column=2, padx=5, pady=5)
        self.task_subject_entry = ttk.Entry(form, width=20)
        self.task_subject_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Дедлайн дд.мм.гггг:").grid(row=1, column=0, padx=5, pady=5)
        self.task_deadline_entry = ttk.Entry(form, width=20)
        self.task_deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Приоритет:").grid(row=1, column=2, padx=5, pady=5)
        self.task_priority = ttk.Combobox(form, values=["низкий", "средний", "высокий"], state="readonly", width=17)
        self.task_priority.set("средний")
        self.task_priority.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(form, text="Добавить", command=self.add_task).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(form, text="Ближайшие дедлайны", command=self.show_deadlines).grid(row=2, column=3, padx=5, pady=5)

        table_frame = ttk.LabelFrame(self.tab_tasks, text="Список задач")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("task", "subject", "deadline", "priority", "status")
        self.tasks_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tasks_table.heading("task", text="Задача")
        self.tasks_table.heading("subject", text="Предмет")
        self.tasks_table.heading("deadline", text="Дедлайн")
        self.tasks_table.heading("priority", text="Приоритет")
        self.tasks_table.heading("status", text="Статус")

        self.tasks_table.column("task", width=350)
        self.tasks_table.column("subject", width=140)
        self.tasks_table.column("deadline", width=120)
        self.tasks_table.column("priority", width=100)
        self.tasks_table.column("status", width=130)

        self.tasks_table.pack(fill="both", expand=True)

        buttons = ttk.Frame(self.tab_tasks)
        buttons.pack(fill="x", padx=10, pady=5)

        ttk.Button(buttons, text="Выполнено / не выполнено", command=self.toggle_task).pack(side="left", padx=5)
        ttk.Button(buttons, text="Удалить", command=self.delete_task).pack(side="left", padx=5)

    def add_task(self):
        task = self.task_entry.get().strip()
        subject = self.task_subject_entry.get().strip() or "Без предмета"
        deadline = self.task_deadline_entry.get().strip() or "без дедлайна"
        priority = self.task_priority.get()

        if not task:
            messagebox.showwarning("Ошибка", "Введите задачу.")
            return

        if deadline != "без дедлайна" and not self.is_valid_date(deadline):
            messagebox.showerror("Ошибка", "Дата должна быть в формате дд.мм.гггг.")
            return

        self.tasks.append({
            "task": task,
            "subject": subject,
            "deadline": deadline,
            "priority": priority,
            "status": "не выполнено"
        })

        self.task_entry.delete(0, tk.END)
        self.task_subject_entry.delete(0, tk.END)
        self.task_deadline_entry.delete(0, tk.END)

        self.refresh_tasks()
        self.save_data()

    def toggle_task(self):
        index = self.selected_index(self.tasks_table)
        if index is None:
            return

        old_status = self.tasks[index]["status"]
        self.tasks[index]["status"] = "выполнено" if old_status == "не выполнено" else "не выполнено"
        self.refresh_tasks()
        self.save_data()

    def delete_task(self):
        index = self.selected_index(self.tasks_table)
        if index is None:
            return

        del self.tasks[index]
        self.refresh_tasks()
        self.save_data()

    def show_deadlines(self):
        result = []
        for task in self.tasks:
            if task["status"] == "выполнено":
                continue
            if self.is_valid_date(task["deadline"]):
                deadline = datetime.strptime(task["deadline"], "%d.%m.%Y").date()
                days = (deadline - date.today()).days
                result.append((deadline, days, task))

        result.sort(key=lambda x: x[0])

        if not result:
            messagebox.showinfo("Дедлайны", "Нет активных задач с датами.")
            return

        text = "Ближайшие дедлайны:\n\n"
        for deadline, days, task in result[:10]:
            if days < 0:
                day_text = f"просрочено на {abs(days)} дн."
            elif days == 0:
                day_text = "сегодня"
            else:
                day_text = f"осталось {days} дн."

            text += f"{task['deadline']} — {task['task']} — {day_text}\n"

        messagebox.showinfo("Дедлайны", text)

    def refresh_tasks(self):
        self.clear_table(self.tasks_table)
        for task in self.tasks:
            self.tasks_table.insert(
                "",
                tk.END,
                values=(task["task"], task["subject"], task["deadline"], task["priority"], task["status"])
            )


    def create_notes_tab(self):
        form = ttk.LabelFrame(self.tab_notes, text="Новая заметка")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Тема:").grid(row=0, column=0, padx=5, pady=5)
        self.note_title_entry = ttk.Entry(form, width=30)
        self.note_title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Предмет:").grid(row=0, column=2, padx=5, pady=5)
        self.note_subject_entry = ttk.Entry(form, width=25)
        self.note_subject_entry.grid(row=0, column=3, padx=5, pady=5)

        self.note_text = tk.Text(form, width=80, height=5)
        self.note_text.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        ttk.Button(form, text="Добавить заметку", command=self.add_note).grid(row=2, column=1, padx=5, pady=5)

        columns = ("title", "subject", "date")
        self.notes_table = ttk.Treeview(self.tab_notes, columns=columns, show="headings")
        self.notes_table.heading("title", text="Тема")
        self.notes_table.heading("subject", text="Предмет")
        self.notes_table.heading("date", text="Дата")
        self.notes_table.pack(fill="both", expand=True, padx=10, pady=10)

        buttons = ttk.Frame(self.tab_notes)
        buttons.pack(fill="x", padx=10, pady=5)

        ttk.Button(buttons, text="Открыть", command=self.open_note).pack(side="left", padx=5)
        ttk.Button(buttons, text="Удалить", command=self.delete_note).pack(side="left", padx=5)

    def add_note(self):
        title = self.note_title_entry.get().strip()
        subject = self.note_subject_entry.get().strip() or "Без предмета"
        text = self.note_text.get("1.0", "end-1c").strip()

        if not title or not text:
            messagebox.showwarning("Ошибка", "Введите тему и текст заметки.")
            return

        self.notes.append({
            "title": title,
            "subject": subject,
            "text": text,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })

        self.note_title_entry.delete(0, tk.END)
        self.note_subject_entry.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)

        self.refresh_notes()
        self.save_data()

    def open_note(self):
        index = self.selected_index(self.notes_table)
        if index is None:
            return

        note = self.notes[index]
        messagebox.showinfo(
            "Заметка",
            f"Тема: {note['title']}\nПредмет: {note['subject']}\nДата: {note['date']}\n\n{note['text']}"
        )

    def delete_note(self):
        index = self.selected_index(self.notes_table)
        if index is None:
            return

        del self.notes[index]
        self.refresh_notes()
        self.save_data()

    def refresh_notes(self):
        self.clear_table(self.notes_table)
        for note in self.notes:
            self.notes_table.insert("", tk.END, values=(note["title"], note["subject"], note["date"]))


    def create_grades_tab(self):
        form = ttk.LabelFrame(self.tab_grades, text="Добавить оценку")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Предмет:").grid(row=0, column=0, padx=5, pady=5)
        self.grade_subject_entry = ttk.Entry(form, width=25)
        self.grade_subject_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Оценка:").grid(row=0, column=2, padx=5, pady=5)
        self.grade_entry = ttk.Entry(form, width=10)
        self.grade_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Комментарий:").grid(row=0, column=4, padx=5, pady=5)
        self.grade_comment_entry = ttk.Entry(form, width=30)
        self.grade_comment_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form, text="Добавить", command=self.add_grade).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(form, text="Удалить", command=self.delete_grade).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(form, text="Средний балл", command=self.show_average).grid(row=1, column=3, padx=5, pady=5)

        columns = ("subject", "grade", "comment", "date")
        self.grades_table = ttk.Treeview(self.tab_grades, columns=columns, show="headings")
        self.grades_table.heading("subject", text="Предмет")
        self.grades_table.heading("grade", text="Оценка")
        self.grades_table.heading("comment", text="Комментарий")
        self.grades_table.heading("date", text="Дата")
        self.grades_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.average_label = tk.Label(self.tab_grades, text="Средний балл: —", font=("Arial", 13, "bold"))
        self.average_label.pack(pady=5)

    def add_grade(self):
        subject = self.grade_subject_entry.get().strip()
        value = self.grade_entry.get().strip().replace(",", ".")
        comment = self.grade_comment_entry.get().strip() or "без комментария"

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

        self.grades.append({
            "subject": subject,
            "grade": grade,
            "comment": comment,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })

        self.grade_subject_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.grade_comment_entry.delete(0, tk.END)

        self.refresh_grades()
        self.update_average()
        self.save_data()

    def delete_grade(self):
        index = self.selected_index(self.grades_table)
        if index is None:
            return

        del self.grades[index]
        self.refresh_grades()
        self.update_average()
        self.save_data()

    def update_average(self):
        if not self.grades:
            self.average_label.config(text="Средний балл: —")
            return

        average = sum(item["grade"] for item in self.grades) / len(self.grades)
        self.average_label.config(text=f"Средний балл: {average:.2f}")

    def show_average(self):
        if not self.grades:
            messagebox.showinfo("Средний балл", "Оценок пока нет.")
            return

        subjects = {}
        for item in self.grades:
            subjects.setdefault(item["subject"], []).append(item["grade"])

        text = "Средний балл по предметам:\n\n"
        for subject, grades in subjects.items():
            text += f"{subject}: {sum(grades) / len(grades):.2f}\n"

        messagebox.showinfo("Средний балл", text)

    def refresh_grades(self):
        self.clear_table(self.grades_table)
        for item in self.grades:
            self.grades_table.insert(
                "",
                tk.END,
                values=(item["subject"], item["grade"], item["comment"], item["date"])
            )


    def create_schedule_tab(self):
        form = ttk.LabelFrame(self.tab_schedule, text="Добавить занятие")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="День:").grid(row=0, column=0, padx=5, pady=5)
        self.day_box = ttk.Combobox(
            form,
            values=["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"],
            state="readonly",
            width=18
        )
        self.day_box.set("Понедельник")
        self.day_box.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Время:").grid(row=0, column=2, padx=5, pady=5)
        self.time_entry = ttk.Entry(form, width=12)
        self.time_entry.insert(0, "09:00")
        self.time_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Предмет:").grid(row=0, column=4, padx=5, pady=5)
        self.schedule_subject_entry = ttk.Entry(form, width=25)
        self.schedule_subject_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Аудитория:").grid(row=1, column=0, padx=5, pady=5)
        self.room_entry = ttk.Entry(form, width=20)
        self.room_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(form, text="Добавить", command=self.add_schedule).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(form, text="Удалить", command=self.delete_schedule).grid(row=1, column=4, padx=5, pady=5)

        columns = ("day", "time", "subject", "room")
        self.schedule_table = ttk.Treeview(self.tab_schedule, columns=columns, show="headings")
        self.schedule_table.heading("day", text="День")
        self.schedule_table.heading("time", text="Время")
        self.schedule_table.heading("subject", text="Предмет")
        self.schedule_table.heading("room", text="Аудитория")
        self.schedule_table.pack(fill="both", expand=True, padx=10, pady=10)

    def add_schedule(self):
        subject = self.schedule_subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("Ошибка", "Введите предмет.")
            return

        self.schedule.append({
            "day": self.day_box.get(),
            "time": self.time_entry.get().strip() or "н/д",
            "subject": subject,
            "room": self.room_entry.get().strip() or "н/д"
        })

        self.schedule_subject_entry.delete(0, tk.END)
        self.room_entry.delete(0, tk.END)

        self.refresh_schedule()
        self.save_data()

    def delete_schedule(self):
        index = self.selected_index(self.schedule_table)
        if index is None:
            return

        del self.schedule[index]
        self.refresh_schedule()
        self.save_data()

    def refresh_schedule(self):
        self.clear_table(self.schedule_table)
        order = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5, "Суббота": 6}
        self.schedule.sort(key=lambda item: (order.get(item["day"], 99), item["time"]))

        for item in self.schedule:
            self.schedule_table.insert("", tk.END, values=(item["day"], item["time"], item["subject"], item["room"]))

    # ---------- ПОГОДА API ----------
    def create_weather_tab(self):
        form = ttk.LabelFrame(self.tab_weather, text="OpenWeather API")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Город:").grid(row=0, column=0, padx=5, pady=8)
        self.city_entry = ttk.Entry(form, width=35)
        self.city_entry.insert(0, "Saint Petersburg")
        self.city_entry.grid(row=0, column=1, padx=5, pady=8)

        ttk.Button(form, text="Получить погоду", command=self.get_weather).grid(row=0, column=2, padx=5, pady=8)

        self.weather_text = tk.Text(self.tab_weather, height=22, font=("Arial", 12))
        self.weather_text.pack(fill="both", expand=True, padx=10, pady=10)

        info = (
            "API ключ хранится в другом файле — run_student_helper.py.\n"
            "Запускать нужно именно run_student_helper.py."
        )
        ttk.Label(self.tab_weather, text=info).pack(anchor="w", padx=10, pady=5)

    def get_weather(self):
        city = self.city_entry.get().strip()

        if not city:
            messagebox.showwarning("Ошибка", "Введите город.")
            return

        if not self.weather_api_key or self.weather_api_key == "ВСТАВЬ_СЮДА_СВОЙ_API_КЛЮЧ":
            messagebox.showerror(
                "Нет API ключа",
                "Открой файл run_student_helper.py и вставь свой OpenWeather API ключ."
            )
            return

        params = {
            "q": city,
            "appid": self.weather_api_key,
            "units": "metric",
            "lang": "ru"
        }

        url = "https://api.openweathermap.org/data/2.5/weather?" + urlencode(params)

        try:
            with urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            description = data["weather"][0]["description"]
            city_name = data["name"]
            country = data["sys"]["country"]

            advice = self.get_weather_advice(temp, description, wind)

            result = (
                f"Город: {city_name}, {country}\n"
                f"Температура: {temp} °C\n"
                f"Ощущается как: {feels_like} °C\n"
                f"Описание: {description}\n"
                f"Влажность: {humidity}%\n"
                f"Давление: {pressure} гПа\n"
                f"Ветер: {wind} м/с\n\n"
                f"Совет:\n{advice}"
            )

            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert("1.0", result)
            self.status_label.config(text="Погода получена через API.")

        except HTTPError as error:
            if error.code == 401:
                messagebox.showerror("Ошибка API", "Неверный API ключ или ключ ещё не активирован.")
            elif error.code == 404:
                messagebox.showerror("Ошибка API", "Город не найден.")
            else:
                messagebox.showerror("Ошибка API", f"HTTP ошибка: {error.code}")

        except URLError:
            messagebox.showerror("Ошибка сети", "Нет подключения к интернету.")

        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def get_weather_advice(self, temp, description, wind):
        advice = []

        if temp <= 0:
            advice.append("Оденься теплее.")
        elif temp <= 10:
            advice.append("Лучше взять куртку.")
        elif temp >= 25:
            advice.append("Жарко, возьми воду.")

        description = description.lower()

        if "дожд" in description:
            advice.append("Возьми зонт.")
        if "снег" in description:
            advice.append("Обувь лучше выбрать потеплее.")
        if wind >= 8:
            advice.append("Сильный ветер, лучше не идти без верхней одежды.")

        if not advice:
            advice.append("Погода нормальная, можно спокойно идти на учёбу.")

        return "\n".join("- " + item for item in advice)

    # ---------- ПОИСК ----------
    def create_search_tab(self):
        form = ttk.LabelFrame(self.tab_search, text="Поиск")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Запрос:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(form, width=50)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(form, text="Найти", command=self.search_all).pack(side="left", padx=5)

        self.search_text = tk.Text(self.tab_search, height=25, font=("Arial", 11))
        self.search_text.pack(fill="both", expand=True, padx=10, pady=10)

    def search_all(self):
        query = self.search_entry.get().strip().lower()

        if not query:
            messagebox.showwarning("Ошибка", "Введите запрос.")
            return

        result = "Результаты поиска:\n\n"
        found = False

        for task in self.tasks:
            full = f"{task['task']} {task['subject']} {task['deadline']} {task['priority']} {task['status']}".lower()
            if query in full:
                found = True
                result += f"[Задача] {task['task']} — {task['subject']}\n"

        for note in self.notes:
            full = f"{note['title']} {note['subject']} {note['text']}".lower()
            if query in full:
                found = True
                result += f"[Заметка] {note['title']} — {note['subject']}\n"

        for grade in self.grades:
            full = f"{grade['subject']} {grade['grade']} {grade['comment']}".lower()
            if query in full:
                found = True
                result += f"[Оценка] {grade['subject']} — {grade['grade']}\n"

        for item in self.schedule:
            full = f"{item['day']} {item['time']} {item['subject']} {item['room']}".lower()
            if query in full:
                found = True
                result += f"[Расписание] {item['day']} {item['time']} — {item['subject']}\n"

        if not found:
            result += "Ничего не найдено."

        self.search_text.delete("1.0", tk.END)
        self.search_text.insert("1.0", result)


    def create_bottom_buttons(self):
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=8)

        ttk.Button(bottom, text="Сохранить", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(bottom, text="Загрузить", command=self.load_data_button).pack(side="left", padx=5)
        ttk.Button(bottom, text="Экспорт TXT", command=self.export_txt).pack(side="left", padx=5)
        ttk.Button(bottom, text="Очистить всё", command=self.clear_all).pack(side="left", padx=5)
        ttk.Button(bottom, text="Выход", command=self.root.destroy).pack(side="right", padx=5)


    def save_data(self):
        data = {
            "tasks": self.tasks,
            "notes": self.notes,
            "grades": self.grades,
            "schedule": self.schedule
        }

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        self.status_label.config(text="Данные сохранены.")

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

        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл с данными повреждён.")

    def load_data_button(self):
        self.load_data()
        self.refresh_all()
        self.status_label.config(text="Данные загружены.")

    def export_txt(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить отчёт",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write("ОТЧЁТ СТУДЕНЧЕСКОГО ПОМОЩНИКА\n\n")

            file.write("ЗАДАЧИ:\n")
            for task in self.tasks:
                file.write(f"- {task['task']} | {task['subject']} | {task['deadline']} | {task['status']}\n")

            file.write("\nЗАМЕТКИ:\n")
            for note in self.notes:
                file.write(f"- {note['title']} | {note['subject']} | {note['date']}\n{note['text']}\n\n")

            file.write("\nОЦЕНКИ:\n")
            for grade in self.grades:
                file.write(f"- {grade['subject']} | {grade['grade']} | {grade['comment']}\n")

            file.write("\nРАСПИСАНИЕ:\n")
            for item in self.schedule:
                file.write(f"- {item['day']} | {item['time']} | {item['subject']} | {item['room']}\n")

        messagebox.showinfo("Экспорт", "Отчёт сохранён.")

    def clear_all(self):
        if not messagebox.askyesno("Подтверждение", "Точно удалить все данные?"):
            return

        self.tasks = []
        self.notes = []
        self.grades = []
        self.schedule = []
        self.refresh_all()
        self.save_data()


    def refresh_all(self):
        self.refresh_tasks()
        self.refresh_notes()
        self.refresh_grades()
        self.refresh_schedule()
        self.update_average()

    def clear_table(self, table):
        for item in table.get_children():
            table.delete(item)

    def selected_index(self, table):
        selected = table.selection()

        if not selected:
            messagebox.showwarning("Ошибка", "Выберите строку.")
            return None

        return table.index(selected[0])

    def is_valid_date(self, text):
        try:
            datetime.strptime(text, "%d.%m.%Y")
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentHelperApp(root)
    root.mainloop()
