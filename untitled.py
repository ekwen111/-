import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# --- Настройки ---
DATA_FILE = "expense_data.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Прочее"]

# --- Класс основного приложения ---
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        # Загрузка данных из JSON
        self.expenses = self.load_data()

        # --- Создание виджетов ---
        self.create_widgets()
        # Заполнение таблицы при запуске
        self.update_table()

    def create_widgets(self):
        # Рамка для ввода данных
        frame_input = ttk.LabelFrame(self.root, text="Добавить расход")
        frame_input.pack(pady=10, fill="x")

        # Сумма
        ttk.Label(frame_input, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_amount = ttk.Entry(frame_input)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        ttk.Label(frame_input, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_category = ttk.Combobox(frame_input, values=CATEGORIES)
        self.combo_category.current(0)
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)

        # Дата (с подсказкой формата)
        ttk.Label(frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_date = ttk.Entry(frame_input)
        self.entry_date.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        ttk.Button(frame_input, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)

        # Таблица расходов
        self.columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("id", width=30)
        self.tree.column("amount", width=100)
        self.tree.column("category", width=120)
        self.tree.column("date", width=100)
        
        self.tree.pack(expand=True, fill="both", pady=10)

        # Рамка для фильтрации и подсчёта
        frame_tools = ttk.LabelFrame(self.root, text="Фильтрация и подсчёт")
        frame_tools.pack(pady=10, fill="x")

        # Фильтр по категории
        ttk.Label(frame_tools, text="Фильтр по категории:").grid(row=0, column=0, padx=5)
        self.filter_combo = ttk.Combobox(frame_tools, values=["Все"] + CATEGORIES)
        self.filter_combo.current(0)
        self.filter_combo.grid(row=0, column=1, padx=5)
        
        ttk.Button(frame_tools, text="Фильтровать", command=self.filter_table).grid(row=0, column=2, padx=5)

        # Подсчёт суммы за период
        ttk.Label(frame_tools, text="Период:").grid(row=1, column=0, padx=5)
        
        ttk.Label(frame_tools, text="С:").grid(row=1, column=1, padx=(20,0))
        self.entry_date_from = ttk.Entry(frame_tools)
        self.entry_date_from.grid(row=1, column=2, padx=5)
        
        ttk.Label(frame_tools, text="По:").grid(row=1, column=3, padx=(20,0))
        self.entry_date_to = ttk.Entry(frame_tools)
        self.entry_date_to.grid(row=1, column=4, padx=(5,0))
        
        ttk.Button(frame_tools, text="Подсчитать сумму", command=self.calculate_sum).grid(row=1, column=5, padx=(10))
        
    # --- Логика работы с данными ---
    def load_data(self):
       """Загрузка данных из JSON файла."""
       try:
           with open(DATA_FILE, 'r', encoding='utf-8') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           return []
   
    def save_data(self):
       """Сохранение данных в JSON файл."""
       with open(DATA_FILE, 'w', encoding='utf-8') as f:
           json.dump(self.expenses, f, ensure_ascii=False, indent=4)
   
    def update_table(self):
       """Обновление таблицы Treeview."""
       for i in self.tree.get_children():
           self.tree.delete(i)
       
       for expense in self.expenses:
           self.tree.insert("", "end", values=(expense["id"], expense["amount"], expense["category"], expense["date"]))
   
    def add_expense(self):
       """Добавление нового расхода."""
       amount_str = self.entry_amount.get().strip()
       category = self.combo_category.get()
       date_str = self.entry_date.get().strip()
       
       # Валидация суммы
       try:
           amount = float(amount_str.replace(',', '.'))
           if amount <= 0:
               raise ValueError("Сумма должна быть положительной.")
       except ValueError as e:
           messagebox.showerror("Ошибка ввода", str(e))
           return

       # Валидация даты
       try:
           datetime.strptime(date_str, "%Y-%m-%d")
       except ValueError:
           messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД (например: 2026-05-01)")
           return

       # Генерация уникального ID (можно заменить на UUID для больших проектов)
       new_id = max([e["id"] for e in self.expenses], default=0) + 1

       new_expense = {
           "id": new_id,
           "amount": amount,
           "category": category,
           "date": date_str
       }
       
       self.expenses.append(new_expense)
       self.save_data()
       self.update_table()
       
       # Очистка полей после добавления
       self.entry_amount.delete(0, tk.END)
       self.entry_date.delete(0, tk.END)
       
    def filter_table(self):
       """Фильтрация таблицы по категории."""
       selected_category = self.filter_combo.get()
       
       if selected_category == "Все":
           filtered_expenses = self.expenses
       else:
           filtered_expenses = [e for e in self.expenses if e["category"] == selected_category]
       
       self.update_table_with_list(filtered_expenses)
   
    def update_table_with_list(self, expense_list):
       """Обновление таблицы из переданного списка."""
       for i in self.tree.get_children():
           self.tree.delete(i)
       
       for expense in expense_list:
           self.tree.insert("", "end", values=(expense["id"], expense["amount"], expense["category"], expense["date"]))
   
    def calculate_sum(self):
       """Подсчёт суммы расходов за выбранный период."""
       date_from_str = self.entry_date_from.get().strip()
       date_to_str = self.entry_date_to.get().strip()
       
       try:
           date_from = datetime.strptime(date_from_str or "1970-01-01", "%Y-%m-%d").date()
           date_to   = datetime.strptime(date_to_str or "2100-12-31", "%Y-%m-%d").date()
           
           if date_from > date_to:
               raise ValueError("Дата начала не может быть позже даты окончания.")
               
           total_sum = 0.0
           for expense in self.expenses:
               expense_date = datetime.strptime(expense["date"], "%Y-%m-%d").date()
               if date_from <= expense_date <= date_to:
                   total_sum += expense["amount"]
                   
           messagebox.showinfo("Сумма расходов", f"Сумма за период с {date_from} по {date_to}: {total_sum:.2f} ₽")
           
       except ValueError as e:
           messagebox.showerror("Ошибка ввода даты", str(e))


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()