from datetime import datetime
import json
import os
import csv
import math

FILE_NAME = os.path.join(os.path.dirname(__file__), "expenses.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


def parse_date(date_string):
    return datetime.strptime(date_string, "%d/%m/%Y")


def is_valid_expense(item):
    if not isinstance(item, dict):
        return False

    required_fields = {"expense", "amount", "date", "category"}

    if not required_fields.issubset(item):
        return False

    if not isinstance(item["expense"], str) or not item["expense"].strip():
        return False

    if not isinstance(item["category"], str) or not item["category"].strip():
        return False

    if not isinstance(item["amount"], (int, float)):
        return False

    if isinstance(item["amount"], bool):
        return False

    if not math.isfinite(item["amount"]) or item["amount"] <= 0:
        return False

    if not isinstance(item["date"], str):
        return False

    try:
        parse_date(item["date"])
    except ValueError:
        return False

    return True


def load_expenses():
    try:
        with open(FILE_NAME, "r") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        valid_expenses = []

        for item in data:
            if not isinstance(item, dict):
                continue

            if not isinstance(item.get("category"), str) or not item["category"].strip():
                item["category"] = "Other"

            if not is_valid_expense(item):
                continue

            item["expense"] = item["expense"].strip()
            item["category"] = item["category"].strip().title()

            valid_expenses.append(item)

        return valid_expenses

    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_budget():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)

        if not isinstance(settings, dict):
            return 100000

        saved_budget = settings.get("budget", 100000)

        if (
            isinstance(saved_budget, bool)
            or not isinstance(saved_budget, (int, float))
            or not math.isfinite(saved_budget)
            or saved_budget <= 0
        ):
            return 100000

        return saved_budget

    except (FileNotFoundError, json.JSONDecodeError):
        return 100000


expenses = load_expenses()
budget = load_budget()


def add_expense():
    expense = get_valid_expense_name("What did you spend on? ")

    amount = get_valid_amount("Enter amount: ₦")

    date = get_valid_date(
        "Enter date (DD/MM/YYYY), or press Enter for today: ")

    category = get_valid_category("Enter category: ")

    expenses.append({
        "expense": expense,
        "amount": amount,
        "date": date,
        "category": category
    })

    save_expenses_with_message("Expense added successfully!")

    print()

    total = get_total()

    if total >= budget:
        over_budget = total - budget

        if over_budget == 0:
            print("warning: You have reached your budget.")
        else:
            print(f"Warning: You are over budget by ₦{over_budget:,.2f}.")


def get_sorted_expenses():
    return sorted(
        expenses,
        key=lambda item: parse_date(item['date']),
        reverse=True
    )


def get_total(expenses_list=None):
    if expenses_list is None:
        expenses_list = expenses

    return sum(item["amount"] for item in expenses_list)


def get_expense_count(expenses_list=None):
    if expenses_list is None:
        expenses_list = expenses

    return len(expenses_list)


def get_category_totals(expenses_list=None):
    if expenses_list is None:
        expenses_list = expenses

    categories = {}

    for item in expenses_list:
        category = item["category"]
        categories[category] = (
            categories.get(category, 0) + item["amount"]
        )

    return categories


def get_category_counts(expenses_list=None):
    if expenses_list is None:
        expenses_list = expenses

    category_counts = {}

    for item in expenses_list:
        category = item['category']
        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    return category_counts


def sort_categories(categories):
    return sorted(
        categories.items(),
        key=lambda item: item[1],
        reverse=True
    )


def get_highest_category(categories):
    if not categories:
        return None

    return max(
        categories.items(),
        key=lambda item: item[1]
    )


def get_lowest_category(categories):
    if not categories:
        return None

    return min(
        categories.items(),
        key=lambda item: item[1]
    )


def get_most_frequent_category(category_counts):
    if not category_counts:
        return None

    return max(
        category_counts.items(),
        key=lambda item: item[1]
    )


def get_largest_expense(expenses_list):
    if not expenses_list:
        return None

    return max(
        expenses_list,
        key=lambda item: item['amount']
    )


def get_smallest_expense(expenses_list):
    if not expenses_list:
        return None

    return min(
        expenses_list,
        key=lambda item: item['amount']
    )


def get_average_expense(expenses_list=None):
    if expenses_list is None:
        expenses_list = expenses

    if not expenses_list:
        return 0

    total = get_total(expenses_list)
    return total / len(expenses_list)


def get_average_monthly_spending(months):
    if not months:
        return 0

    total = sum(
        month_data['amount']
        for month_data in months.values()
    )
    return total / len(months)


def get_top_expenses(expenses_list, limit=3):
    if limit <= 0:
        return []

    return sorted(
        expenses_list,
        key=lambda item: item['amount'],
        reverse=True
    )[:limit]


def get_highest_month(months):
    if not months:
        return None

    return max(
        months.items(),
        key=lambda item: item[1]['amount']
    )


def get_lowest_month(months):
    if not months:
        return None

    return min(
        months.items(),
        key=lambda item: item[1]['amount']
    )


def get_percentage(amount, total):
    if total == 0:
        return 0

    return (amount / total) * 100


def get_valid_expense_name(prompt, default=None):
    while True:
        expense_name = input(prompt).strip()

        if not expense_name and default is not None:
            return default

        if expense_name:
            return expense_name

        print("Expense name cannot be empty")


def get_valid_amount(prompt, default=None):
    while True:
        amount_string = input(prompt).strip()

        if not amount_string and default is not None:
            return default

        try:
            amount = float(amount_string)

            if not math.isfinite(amount) or amount <= 0:
                print("Amount must be a finite number greater than zero")
                continue

            return amount

        except ValueError:
            print("Please enter a valid number")


def get_valid_date(prompt, default=None):
    while True:
        date_string = input(prompt).strip()

        if not date_string:
            if default is not None:
                x = input(
                    f"Press Enter to use the default date ({default}), or enter 'y' to use today's date: ").strip()
                if not x:
                    return default
                elif x.casefold() == "y":
                    return datetime.now().strftime("%d/%m/%Y")
                else:
                    print("Please press Enter or enter 'y'")
                    continue
            return datetime.now().strftime("%d/%m/%Y")

        try:
            parse_date(date_string)
            return date_string

        except ValueError:
            print("Please enter a valid date (DD/MM/YYYY).")


def get_valid_category(prompt, default=None):
    while True:
        category = input(prompt).strip().title()

        if not category and default is not None:
            return default

        if category:
            return category

        print("Category cannot be empty")


def get_remaining_budget(budget, spent):
    return budget - spent


def get_remaining_percentage(budget, spent):
    if budget <= 0:
        return 0

    remaining = get_remaining_budget(budget, spent)
    return get_percentage(remaining, budget)


def is_over_budget(budget, spent):
    return spent > budget


def get_budget_status(budget, spent):
    if budget <= 0:
        return "No budget set"
    if is_over_budget(budget, spent):
        return "Over budget"
    if spent == budget:
        return "Budget fully used"
    return "Within budget"


def get_budget_usage(budget, spent):
    if budget <= 0:
        return 0

    return get_percentage(spent, budget)


def confirm_action(prompt):
    while True:
        answer = input(prompt).strip().casefold()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please enter yes or no.")


def format_money(amount):
    return f"₦{amount:,.2f}"


def filter_by_date_range(expenses_list, start, end):
    return [
        item for item in expenses_list
        if start <= parse_date(item["date"]) <= end
    ]


def filter_by_year(expenses_list, year):
    return [
        item for item in expenses_list
        if parse_date(item['date']).strftime('%Y') == str(year)
    ]


def filter_by_month(expenses_list, month, year):
    return [
        item for item in expenses_list
        if parse_date(item["date"]).strftime("%m/%Y")
        == f"{int(month):02d}/{year}"
    ]


def filter_by_category(expense_list, category):
    return [
        item for item in expense_list
        if item["category"].casefold() == category.casefold()
    ]


def filter_by_expense_name(expenses_list, search):
    search = search.casefold()

    return [
        item for item in expenses_list
        if search in item["expense"].casefold()
    ]


def view_expenses():
    if not expenses:
        print("No expenses recorded.")
        return

    sorted_expenses = get_sorted_expenses()

    print()
    print("No.   Expense       Amount        Date        Category")
    print("------------------------------------------------------")
    for number, item in enumerate(sorted_expenses, start=1):
        print(
            f"{number:<6}"
            f"{item['expense']:<14}"
            f"{format_money(item['amount'])}     "
            f"{item['date']:<13}"
            f"{item['category']}"
        )
    print()


def recent_expenses(amount=5):
    if not expenses:
        print("No expenses recorded")
        return

    count = get_expense_count()

    if amount > count:
        print(f"You only have {count} items")

    sorted_expenses = get_sorted_expenses()

    print()
    print("========== RECENT EXPENSES ==========")
    print("No.   Expense      Amount      Date          Category")
    print("-----------------------------------------------------")

    for number, item in enumerate(sorted_expenses[:amount], start=1):
        print(
            f"{number:<6}"
            f"{item['expense']:<14}"
            f"{format_money(item['amount'])}       "
            f"{item['date']:<13}"
            f"{item['category']}"
        )

    print()


def total_spending():
    if not expenses:
        print("No expenses recorded")
        return

    total = get_total()
    count = get_expense_count()
    average = total / count

    categories = get_category_totals()

    print()
    print("========== EXPENSE SUMMARY ==========")
    print(f"Number of expenses: {count}")
    print(f"Total Expenses: {format_money(total)}")
    print(f"Average expense: {format_money(average)}")

    print()
    print("Spending by category")

    for category, amount in sorted(
        categories.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        print(category, format_money(amount))


def save_expenses():
    try:
        with open(FILE_NAME, "w") as file:
            json.dump(expenses, file, indent=4)
    except OSError as error:
        print(f"Error saving expenses: {error}")
        return False

    return True


def save_expenses_with_message(message):
    if save_expenses():
        print(message)


def save_budget():
    with open(SETTINGS_FILE, "w") as file:
        json.dump({"budget": budget}, file, indent=4)


def delete_expense():
    if not expenses:
        print("No expenses recorded")
        return

    view_expenses()

    try:
        number = int(input("Enter the expense number to delete: "))

        count = get_expense_count()

        if number < 1 or number > count:
            print("invalid expense number.")
            return

        sorted_expenses = get_sorted_expenses()
        deleted = sorted_expenses[number - 1]

        while True:
            confirm = confirm_action(
                "Are you sure you want to delete this expense? (y/n)"
            )

            if confirm:
                expenses.remove(deleted)
                save_expenses_with_message(
                    f"{deleted['expense']} deleted successfully.")
                return
            else:
                print("Deletion cancelled.")
                return

    except ValueError:
        print("Please enter a valid number.")
        return


def edit_expense():
    if not expenses:
        print("No expenses recorded.")
        return

    view_expenses()

    try:
        number = int(input("Enter the expense number to edit: "))

        count = get_expense_count()

        if number < 1 or number > count:
            print("Invalid expense number.")
            return

        sorted_expenses = get_sorted_expenses()
        item = sorted_expenses[number - 1]

        new_expense = get_valid_expense_name(
            f"Enter expense name ({item['expense']}): ",
            item["expense"]
        )
        item["expense"] = new_expense

        new_amount = get_valid_amount(
            f"Enter amount ({format_money(item['amount'])}): ",
            item["amount"]
        )
        item["amount"] = new_amount

        new_date = get_valid_date(
            f"Enter the date (DD/MM/YYYY) ({item['date']}): ",
            item["date"]
        )
        item["date"] = new_date

        new_category = get_valid_category(
            f"Enter category ({item['category']}): ",
            item["category"]
        )
        item['category'] = new_category

        save_expenses_with_message("Expense updated successfully.")

    except ValueError:
        print("Please enter a valid number.")


def clear_expenses():
    if not expenses:
        print("No expenses recorded.")
        return

    while True:
        confirm = confirm_action(
            "Are you sure you want to clear all expenses? This action cannot be undone. (y/n): "
        )

        if confirm:
            expenses.clear()
            save_expenses_with_message("All expenses cleared successfully.")
            break

        else:
            print("Clear expenses cancelled.")
            break


def search_expenses():
    if not expenses:
        print("No expenses recorded.")
        return

    print()
    print("Search by:")
    print("1. Expense")
    print("2. Category")

    choice = input("Enter your choice: ").strip()

    sorted_expenses = get_sorted_expenses()

    if choice == "1":
        search = input("Enter expense name ").strip().lower()

        results = filter_by_expense_name(sorted_expenses, search)

    elif choice == "2":
        search = input("Enter category: ").strip()

        results = filter_by_category(sorted_expenses, search)

    else:
        print("Invalid choice.")
        return

    if not search:
        print("Search cannot be empty")
        return

    print()
    print("Search Results")
    print("-------------------------------------------------------")

    for number, item in enumerate(results, start=1):
        print(
            f"{number:<6}"
            f"{item['expense']:<14}"
            f"{format_money(item['amount'])}       "
            f"{item['date']:<13}"
            f"{item['category']}"
        )

    print()


def monthly_spending():
    if not expenses:
        print("No expenses recorded.")
        return

    month = input("Enter month (MM/YYYY): ").strip()

    try:
        datetime.strptime(month, "%m/%Y")
    except ValueError:
        print("Please enter a valid month in the format MM/YYYY.")
        return

    month_number, year = month.split("/")
    monthly_expenses = filter_by_month(
        expenses,
        month_number,
        year
    )

    if not monthly_expenses:
        print("No expenses found for the month")
        return

    total = get_total(monthly_expenses)

    categories = get_category_totals(monthly_expenses)

    count = get_expense_count(monthly_expenses)

    print()
    print(f"========== {month} SUMMARY ==========")
    print(f"Number of expenses: {count}")
    print(f"Total spent: {format_money(total)}")
    print()

    print('Spending by category:')

    for category, amount in sorted(
        categories.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f"{category:<15} {format_money(amount)}")

    print()


def date_range_spending():
    if not expenses:
        print("No expenses recorded.")
        return

    while True:
        start_date = input(
            "Enter start date (DD/MM/YYYY): "
        ).strip()

        try:
            start = parse_date(start_date)
            break
        except ValueError:
            print("Please enter a valid date.")

    while True:
        end_date = input(
            "Enter end date (DD/MM/YYYY): "
        ).strip()

        try:
            end = parse_date(end_date)
            break
        except ValueError:
            print("Please enter a valid date.")

    if start > end:
        print("Start date cannot be after the end date.")
        return

    filtered_expenses = filter_by_date_range(
        expenses,
        start,
        end
    )

    if not filtered_expenses:
        print("No expenses found for that date range")
        return

    total = get_total(filtered_expenses)

    categories = get_category_totals(filtered_expenses)

    count = get_expense_count(filtered_expenses)

    print()
    print("========== DATE RANGE SUMMARY ==========")
    print(f"From {start_date}")
    print(f"To: {end_date}")
    print(f"Number of expenses: {count}")
    print(f"Total spent: {format_money(total)}")
    print()

    print("Expenses:")
    print("--------------------------------------------")

    for number, item in enumerate(filtered_expenses, start=1):
        print(
            f"{number:<6}"
            f"{item['expense']:<14}"
            f"{format_money(item['amount'])}    "
            f"{item['date']:<13}"
            f"{item['category']}"
        )

    print()
    print("Spending by category:")

    for category, amount in sort_categories(categories):
        print(f"{category:<15} {format_money(amount)}")

    print()


def yearly_spending():
    if not expenses:
        print("No expenses recorded")
        return

    year = input("Enter year (YYYY): ").strip()

    if not year.isdigit() or len(year) != 4:
        print("Please enter a valid year in the format YYYY.")
        return

    yearly_expenses = filter_by_year(expenses, year)

    if not yearly_expenses:
        print("No expenses found for that year")
        return

    total = get_total(yearly_expenses)

    average_expense = get_average_expense(yearly_expenses)

    print()
    print(f"========== {year} SUMMARY ==========")
    print(f"Number of expenses: {get_expense_count(yearly_expenses)}")
    print(f"Total spent: {format_money(total)}")
    print(f"Average expense: {format_money(average_expense)}")

    print()

    categories = get_category_totals(yearly_expenses)
    category_counts = get_category_counts(yearly_expenses)

    highest_category = get_highest_category(categories)

    lowest_category = get_lowest_category(categories)

    most_frequent_category = get_most_frequent_category(category_counts)

    largest_expense = get_largest_expense(yearly_expenses)

    print()
    print("Largest individual expense:")
    print(
        f"{largest_expense['expense']} - "
        f"{format_money(largest_expense['amount'])}"
    )
    print(f"Date: {largest_expense['date']}")
    print(f"Category: {largest_expense['category']}")

    smallest_expense = get_smallest_expense(yearly_expenses)

    print()
    print("Smallest individual expense:")
    print(
        f"{smallest_expense['expense']} - "
        f"{format_money(smallest_expense['amount'])}"
    )
    print(f"Date: {smallest_expense['date']}")
    print(f"Category: {smallest_expense['category']}")

    top_expenses = get_top_expenses(yearly_expenses)

    print()
    print("========== TOP 3 EXPENSES ==========")

    for number, item in enumerate(top_expenses, start=1):
        print(
            f"{number}. {item['expense']} - "
            f"{format_money(item['amount'])} "
            f"({item['date']})"
        )

    months = {}

    for item in yearly_expenses:
        date = parse_date(item['date'])
        month_key = date.strftime("%m/%Y")
        month_name = date.strftime("%B %Y")

        months[month_key] = {
            "name": month_name,
            "amount": months.get(month_key, {}).get("amount", 0) + item["amount"],
            "count": months.get(month_key, {}).get("count", 0) + 1
        }

    print()
    print("Spending by category")

    for category, amount in sort_categories(categories):
        percentage = get_percentage(amount, total)

        print(f"{category:<15}"
              f"{format_money(amount)}    "
              f"{percentage:.1f}%"
              )

    print()
    print("Spending by month:")

    for month, data in sorted(months.items()):
        percentage = get_percentage(data["amount"], total)

        print(
            f"{data['name']:<15}"
            f"{format_money(data['amount'])}    "
            f"{percentage:.1f}%    "
            f"{data['count']} expenses"
        )

    average_monthly = get_average_monthly_spending(months)
    print()
    print(f"Average monthly spending: {format_money(average_monthly)}")

    yearly_budget_percentage = get_percentage(total, budget)
    bar_length = 20
    filled = min(
        int(yearly_budget_percentage / 100 * bar_length),
        bar_length
    )

    bar = "█" * filled + "-" * (bar_length - filled)

    print(f"Yearly budget: [{bar}]")

    print(
        f"Yearly budget usage: "
        f"{yearly_budget_percentage:.1f}%"
    )

    if total < budget:
        remaining = get_remaining_budget(budget, total)
        print(f"Budget remaining: {format_money(remaining)}")
    elif total == budget:
        print("You have reached your yearly budget.")
    else:
        over_budget = total - budget
        print(f"Over budget by: {format_money(over_budget)}")

    highest_month = get_highest_month(months)
    if highest_month is not None:
        month_key, month_data = highest_month

        print(
            f"Highest spending month: "
            f"{month_data['name']} "
            f"({format_money(month_data['amount'])})"
        )

    lowest_month = get_lowest_month(months)
    if lowest_month is not None:
        month_key, month_data = lowest_month

        print(
            f"lowest spending month: "
            f"{month_data['name']} "
            f"({format_money(month_data['amount'])})"
        )

    print()
    if highest_category is not None:
        category_name, category_amount = highest_category

        print(
            f"Highest spending category: "
            f"{category_name} "
            f"({format_money(category_amount)})"
        )
    print()

    if lowest_category is not None:
        category_name, category_amount = lowest_category

        print(
            f"Lowest spending category: "
            f"{category_name} "
            f"({format_money(category_amount)})"
        )

    print()

    category_name, count = most_frequent_category

    print(
        f"Most frequent category: "
        f"{category_name} ({count} expenses)"
    )

    top_categories = sort_categories(category_counts)[:3]

    print()
    print("========== TOP 3 MOST FREQUENT CATEGORIES ==========")
    for number, (category, count) in enumerate(top_categories, start=1):
        print(f"{number}. {category}: {count} expenses")

    print()


def set_budget():
    global budget

    while True:
        try:
            new_budget = float(input("Enter your budget: "))

            if not math.isfinite(new_budget) or new_budget <= 0:
                print("Budget must be greater than 0.")
                continue

            budget = new_budget
            save_budget()
            print(f"Budget set to {format_money(budget)}")
            break
        except ValueError:
            print("Please enter a valid amount.")


def view_budget():
    total = get_total()
    percentage = get_budget_usage(budget, total)
    remaining = get_remaining_budget(budget, total)
    remaining_percentage = get_remaining_percentage(budget, total)

    print()
    print(f"Current budget: {format_money(budget)}")
    print(f"Total spent: {format_money(total)}")
    print(f"Budget used: {percentage:.1f}%")
    print(f"Budget remaining: {remaining_percentage:.1f}%")

    if not is_over_budget(budget, total):
        print(f"Remaining: {format_money(remaining)}")
    else:
        print(f"Over budget by: {format_money(-remaining)}")
    print()


def show_budget_status():
    total = get_total()
    percentage = get_budget_usage(budget, total)
    remaining = get_remaining_budget(budget, total)
    remaining_percentage = get_remaining_percentage(budget, total)
    count = get_expense_count()

    bar_length = 20
    filled = min(int(percentage / 100 * bar_length), bar_length)
    bar = "█" * filled + "-" * (bar_length - filled)

    status = get_budget_status(budget, total)

    if not is_over_budget(budget, total):
        print(
            f"Expenses: {count} | Budget: {format_money(budget)} | Spent: {format_money(total)} | Remaining: {format_money(remaining)} | Used budget: {percentage:.1f}% | Remaining budget: {remaining_percentage:.1f}%")
    else:
        print(
            f"Expenses: {count} | Budget: {format_money(budget)} | Spent: {format_money(total)} | Over budget: {format_money(-remaining)} | Used budget: {percentage:.1f}% | Remaining budget: {remaining_percentage:.1f}%"
        )

    print(f"[{bar}]")
    print(f"Budget status: {status}")


def export_expenses():
    if not expenses:
        print("No expenses recorded.")
        return

    if not confirm_action("Export expenses to CSV? (y/n): "):
        print("Export cancelled")
        return

    now = datetime.now()

    export_date = now.strftime("%d/%m/%Y %H:%M")
    filename = now.strftime("expenses_%Y%m%d_%H%M%S_%f.csv")

    export_folder = os.path.join(
        os.path.dirname(__file__),
        "exports"
    )

    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(
        export_folder,
        filename
    )

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        fieldnames = [
            "expense",
            "amount",
            "date",
            "category",
            "exported_at"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        for item in get_sorted_expenses():
            row = item.copy()
            row["exported_at"] = export_date
            writer.writerow(row)

        total = get_total()

        writer.writerow({
            "expense": "TOTAL",
            "amount": total,
            "date": "",
            "category": "",
            "exported_at": ""
        })

    total = get_total()

    print()
    print("========== EXPORT SUMMARY ==========")
    print(f"Expenses exported: {len(expenses)}")
    print(f"Total amount: {format_money(total)}")
    print(f"File saved to: {file_path}")


def show_menu():
    print()
    print("========================")
    print("      EXPENSE TRACKER")
    print("========================")
    show_budget_status()
    print()
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Recent Expenses")
    print("4. View Total Expenses")
    print("5. Delete expense")
    print("6. Edit expense")
    print("7. Clear expenses")
    print("8. Search Expenses")
    print("9. Monthly Spending")
    print("10. Set Budget")
    print("11. View Budget")
    print("12. Date Range Spending")
    print("13. Yearly spending")
    print("14. Export expenses to CSV")
    print("15. Exit")
    print()


running = True
while running:
    show_menu()

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        try:
            amount = int(input("How many recent item do you want to view: "))
            recent_expenses(amount)
        except ValueError:
            recent_expenses()

    elif choice == "4":
        total_spending()

    elif choice == "5":
        delete_expense()

    elif choice == "6":
        edit_expense()

    elif choice == "7":
        clear_expenses()

    elif choice == "8":
        search_expenses()

    elif choice == "9":
        monthly_spending()

    elif choice == "10":
        set_budget()

    elif choice == "11":
        view_budget()

    elif choice == "12":
        date_range_spending()

    elif choice == "13":
        yearly_spending()

    elif choice == "14":
        export_expenses()

    elif choice == "15":
        while True:
            confirm = input("Are you sure you want to exit? (y/n): ").lower()

            if confirm == "y":
                print("Goodbye!")
                running = False
                break
            elif confirm == "n":
                break
            else:
                print("Please enter y or n")

    else:
        print("Invalid choice. Please enter a number from 1 to 15")

    print()
    input("Press Enter to continue: ")
