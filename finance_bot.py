"""
Фінансовий трекер студента — консольний чат-бот
Варіант 2: Індивідуальний підсумковий проєкт
"""

import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# Константи
# ─────────────────────────────────────────────
DATA_FILE = "finance_data.json"

# ─────────────────────────────────────────────
# Робота з файлом (збереження / завантаження)
# ─────────────────────────────────────────────

def load_data() -> dict:
    """Зчитує дані з JSON-файлу. Якщо файл не існує — повертає порожню структуру."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Початкова структура даних
    return {"budget": 0.0, "expenses": []}


def save_data(data: dict) -> None:
    """Записує поточний стан даних у JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# Допоміжні функції
# ─────────────────────────────────────────────

def total_expenses(data: dict) -> float:
    """Повертає загальну суму всіх витрат."""
    return sum(e["amount"] for e in data["expenses"])


def check_budget_exceeded(data: dict) -> None:
    """Виводить попередження, якщо витрати перевищують бюджет."""
    spent = total_expenses(data)
    budget = data["budget"]
    if budget > 0 and spent > budget:
        over = spent - budget
        print(f"\nУВАГА! Ви перевищили бюджет на {over:.2f} грн!\n")


def parse_date(date_str: str) -> datetime | None:
    """Перетворює рядок дати у формат datetime. Повертає None при помилці."""
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def format_expense(exp: dict) -> str:
    """Форматує запис витрати для відображення у консолі."""
    comment = f" | {exp['comment']}" if exp.get("comment") else ""
    return (
        f"  [{exp['date']}] {exp['category']:15s} — {exp['amount']:8.2f} грн{comment}"
    )


# ─────────────────────────────────────────────
# Команди бота
# ─────────────────────────────────────────────

def show_help() -> None:
    """Виводить список доступних команд."""
    commands = [
        ("допомога",              "Показати цей список команд"),
        ("встановити бюджет",     "Задати загальний бюджет"),
        ("додати витрату",        "Записати нову витрату"),
        ("показати витрати",      "Переглянути всі витрати"),
        ("фільтр дата",           "Витрати за конкретну дату"),
        ("фільтр період",         "Витрати за діапазон дат"),
        ("фільтр категорія",      "Витрати за категорією"),
        ("залишок",               "Скільки коштів залишилось"),
        ("звіт за категоріями",   "Сума витрат по категоріях"),
        ("вийти",                 "Завершити роботу програми"),
    ]
    print("\nДоступні команди:")
    for cmd, desc in commands:
        print(f"  {cmd:<25} — {desc}")
    print()


def set_budget(data: dict) -> None:
    """Зчитує суму бюджету від користувача та зберігає її."""
    try:
        amount = float(input("Введіть суму бюджету (грн): ").strip())
        if amount < 0:
            print("Сума не може бути від'ємною.")
            return
        data["budget"] = amount
        save_data(data)
        print(f"Бюджет встановлено: {amount:.2f} грн")
    except ValueError:
        print("Некоректне значення. Введіть число.")


def add_expense(data: dict) -> None:
    """Запитує дані нової витрати та додає її до списку."""
    # Сума
    try:
        amount = float(input("Сума витрати (грн): ").strip())
        if amount <= 0:
            print("Сума має бути більше нуля.")
            return
    except ValueError:
        print("Некоректне значення суми.")
        return

    # Категорія
    category = input("Категорія (напр. їжа, транспорт, навчання): ").strip()
    if not category:
        print("Категорія не може бути порожньою.")
        return

    # Дата
    date_input = input("Дата (дд.мм.рррр, або Enter для сьогодні): ").strip()
    if not date_input:
        date_str = datetime.today().strftime("%d.%m.%Y")
    else:
        parsed = parse_date(date_input)
        if parsed is None:
            print("Невірний формат дати. Використовуйте дд.мм.рррр")
            return
        date_str = parsed.strftime("%d.%m.%Y")

    # Коментар (необов'язково)
    comment = input("Коментар (необов'язково, Enter щоб пропустити): ").strip()

    # Формуємо запис
    expense = {
        "amount":   amount,
        "category": category,
        "date":     date_str,
        "comment":  comment,
    }
    data["expenses"].append(expense)
    save_data(data)
    print(f"Витрату додано: {format_expense(expense)}")

    # Перевірка бюджету
    check_budget_exceeded(data)


def show_expenses(data: dict) -> None:
    """Виводить всі збережені витрати."""
    expenses = data["expenses"]
    if not expenses:
        print("Витрат ще немає.")
        return
    print(f"\nВсі витрати ({len(expenses)} записів):")
    for exp in expenses:
        print(format_expense(exp))
    print(f"\n  Разом: {total_expenses(data):.2f} грн\n")


def filter_by_date(data: dict) -> None:
    """Виводить витрати за введену конкретну дату."""
    date_input = input("Введіть дату (дд.мм.рррр): ").strip()
    parsed = parse_date(date_input)
    if parsed is None:
        print("Невірний формат дати.")
        return
    date_str = parsed.strftime("%d.%m.%Y")

    result = [e for e in data["expenses"] if e["date"] == date_str]
    if not result:
        print(f"Витрат за {date_str} не знайдено.")
        return
    print(f"\nВитрати за {date_str}:")
    for exp in result:
        print(format_expense(exp))
    print(f"\n  Разом: {sum(e['amount'] for e in result):.2f} грн\n")


def filter_by_period(data: dict) -> None:
    """Виводить витрати за діапазон дат (від ... до ...)."""
    from_input = input("Початок періоду (дд.мм.рррр): ").strip()
    to_input   = input("Кінець  періоду (дд.мм.рррр): ").strip()

    date_from = parse_date(from_input)
    date_to   = parse_date(to_input)

    if date_from is None or date_to is None:
        print("Невірний формат дати.")
        return
    if date_from > date_to:
        print("Початкова дата не може бути пізніше кінцевої.")
        return

    result = [
        e for e in data["expenses"]
        if date_from <= datetime.strptime(e["date"], "%d.%m.%Y") <= date_to
    ]
    if not result:
        print("Витрат за вказаний період не знайдено.")
        return
    print(f"\nВитрати з {from_input} по {to_input}:")
    for exp in result:
        print(format_expense(exp))
    print(f"\n  Разом: {sum(e['amount'] for e in result):.2f} грн\n")


def filter_by_category(data: dict) -> None:
    """Виводить витрати за введеною категорією."""
    category = input("Введіть категорію: ").strip().lower()
    result = [e for e in data["expenses"] if e["category"].lower() == category]
    if not result:
        print(f"Витрат у категорії «{category}» не знайдено.")
        return
    print(f"\nВитрати у категорії «{category}»:")
    for exp in result:
        print(format_expense(exp))
    print(f"\n  Разом: {sum(e['amount'] for e in result):.2f} грн\n")


def show_balance(data: dict) -> None:
    """Виводить залишок бюджету."""
    budget = data["budget"]
    if budget <= 0:
        print("Бюджет ще не встановлено. Використайте команду 'встановити бюджет'.")
        return
    spent     = total_expenses(data)
    remaining = budget - spent
    print(f"\nБюджет:   {budget:.2f} грн")
    print(f"   Витрачено: {spent:.2f} грн")
    if remaining >= 0:
        print(f"   Залишок:   {remaining:.2f} грн\n")
    else:
        print(f"   Перевищення: {abs(remaining):.2f} грн\n")


def category_report(data: dict) -> None:
    """Виводить загальну суму витрат по кожній категорії."""
    expenses = data["expenses"]
    if not expenses:
        print("📭 Витрат ще немає.")
        return

    # Збираємо суми по категоріях
    report: dict[str, float] = {}
    for exp in expenses:
        cat = exp["category"]
        report[cat] = report.get(cat, 0.0) + exp["amount"]

    # Сортуємо за спаданням суми
    sorted_report = sorted(report.items(), key=lambda x: x[1], reverse=True)

    print("\nЗвіт за категоріями:")
    for cat, total in sorted_report:
        print(f"  {cat:20s} — {total:.2f} грн")
    print(f"\n  Всього: {sum(report.values()):.2f} грн\n")


# ─────────────────────────────────────────────
# Головний цикл бота
# ─────────────────────────────────────────────

def main() -> None:
    """Точка входу: вітання, завантаження даних, основний командний цикл."""
    # Завантаження збережених даних
    data = load_data()

    # Вітання
    print("=" * 50)
    print("  Фінансовий трекер студента")
    print("=" * 50)
    print("Вітаю! Я допоможу стежити за твоїми витратами.")
    print("Введи «допомога», щоб побачити список команд.\n")

    # Команди → функції
    commands = {
        "допомога":            lambda: show_help(),
        "встановити бюджет":   lambda: set_budget(data),
        "додати витрату":      lambda: add_expense(data),
        "показати витрати":    lambda: show_expenses(data),
        "фільтр дата":         lambda: filter_by_date(data),
        "фільтр період":       lambda: filter_by_period(data),
        "фільтр категорія":    lambda: filter_by_category(data),
        "залишок":             lambda: show_balance(data),
        "звіт за категоріями": lambda: category_report(data),
    }

    # Основний цикл
    while True:
        user_input = input(">>> ").strip().lower()

        if not user_input:
            continue

        if user_input == "вийти":
            print("До побачення! Бережи свої кошти!")
            break

        if user_input in commands:
            commands[user_input]()
        else:
            print("Невідома команда. Введи «допомога» для списку команд.")


# ─────────────────────────────────────────────
# Запуск програми
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
