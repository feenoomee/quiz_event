
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# ==============================================
# ПРОЕКТ: ИТ-СТРАТЕГИЯ ООО «МАКСИМА»
# ==============================================

FILE_NAME = "IT_strategy_Maksima.xml"
PROJECT_NAME = "Разработка ИТ-стратегии ООО «Максима»"

NS = "http://schemas.microsoft.com/project"
ET.register_namespace("", NS)


def add(parent, tag, value):
    item = ET.SubElement(parent, f"{{{NS}}}{tag}")
    if value is not None:
        item.text = str(value)
    return item


def parse_date(value):
    return datetime.strptime(value, "%d.%m.%Y")


def iso(value, hour):
    return value.strftime("%Y-%m-%d") + f"T{hour}:00:00"


def workdays(start, finish):
    current = parse_date(start)
    end = parse_date(finish)
    count = 0

    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)

    return count


# ==============================================
# РЕСУРСЫ
# ==============================================

resources = {
    1: "Генеральный директор (Петров В.Г.)",
    2: "Финансовый директор (Козлова Е.П.)",
    3: "Коммерческий директор (Иванов Д.С.)",
    4: "Логистический директор (Смирнов А.В.)",
    5: "Менеджер по продажам (Орлова К.М.)",
    6: "Бухгалтер (Федорова Н.А.)",
    7: "Складской менеджер (Попов И.Ю.)",
    8: "Водитель (Николаев А.Б.)",
    9: "Все члены рабочей группы",
}

# ==============================================
# ЗАДАЧИ
#
# level=1 — сводный этап
# level=2 — вложенная задача
# prev — UID предшествующей задачи
#
# Для последней задачи используется связь
# начало-начало, потому что обе задачи
# запланированы на 20 марта.
# ==============================================

tasks = [
    # ЭТАП 1
    {
        "name": "Организационно-подготовительный этап",
        "start": "22.01.2026",
        "finish": "26.01.2026",
        "level": 1
    },
    {
        "name": "Издание приказа о создании рабочей группы",
        "start": "22.01.2026",
        "finish": "22.01.2026",
        "level": 2,
        "res": [1]
    },
    {
        "name": "Проведение установочного заседания, распределение ролей",
        "start": "23.01.2026",
        "finish": "23.01.2026",
        "level": 2,
        "res": [2],
        "prev": 2,
        "note": "Заседание РГ №1. Ответственная — Козлова Е.П."
    },
    {
        "name": "Утверждение регламента работы и графика заседаний",
        "start": "26.01.2026",
        "finish": "26.01.2026",
        "level": 2,
        "res": [2],
        "prev": 3,
        "note": "Установить периодичность заседаний: каждую среду"
    },

    # ЭТАП 2
    {
        "name": "Анализ текущего состояния бизнеса и ИТ",
        "start": "27.01.2026",
        "finish": "12.02.2026",
        "level": 1
    },
    {
        "name": "Сбор документации по бизнес-процессам (склад, продажи, логистика)",
        "start": "27.01.2026",
        "finish": "30.01.2026",
        "level": 2,
        "res": [3, 4],
        "prev": 4
    },
    {
        "name": "Проведение анкетирования сотрудников (20+ чел.)",
        "start": "02.02.2026",
        "finish": "06.02.2026",
        "level": 2,
        "res": [5],
        "prev": 6
    },
    {
        "name": "Интервью с руководителями подразделений",
        "start": "09.02.2026",
        "finish": "10.02.2026",
        "level": 2,
        "res": [2],
        "prev": 7
    },
    {
        "name": "Инвентаризация существующего ПО (1С, Excel) и оборудования",
        "start": "11.02.2026",
        "finish": "11.02.2026",
        "level": 2,
        "res": [2, 6],
        "prev": 8
    },
    {
        "name": "Подготовка отчета по текущему ИТ-ландшафту",
        "start": "12.02.2026",
        "finish": "12.02.2026",
        "level": 2,
        "res": [2],
        "prev": 9,
        "note": "Заседание РГ №2. Ответственная — Козлова Е.П."
    },

    # ЭТАП 3
    {
        "name": "Формирование целевой ИТ-архитектуры",
        "start": "13.02.2026",
        "finish": "27.02.2026",
        "level": 1
    },
    {
        "name": "Определение требований к CRM (учет клиентов, воронка)",
        "start": "13.02.2026",
        "finish": "17.02.2026",
        "level": 2,
        "res": [3, 5],
        "prev": 10
    },
    {
        "name": "Определение требований к складу (партионный учет, сроки годности)",
        "start": "18.02.2026",
        "finish": "20.02.2026",
        "level": 2,
        "res": [4, 7],
        "prev": 12
    },
    {
        "name": "Определение требований к ЭДО и мобильному приложению для водителей",
        "start": "24.02.2026",
        "finish": "26.02.2026",
        "level": 2,
        "res": [6, 8],
        "prev": 13
    },
    {
        "name": "Согласование целевой архитектуры",
        "start": "27.02.2026",
        "finish": "27.02.2026",
        "level": 2,
        "res": [9],
        "prev": 14,
        "note": "Заседание РГ №3. Ответственная — Козлова Е.П."
    },

    # ЭТАП 4
    {
        "name": "Разработка портфеля ИТ-проектов и бюджета",
        "start": "02.03.2026",
        "finish": "06.03.2026",
        "level": 1
    },
    {
        "name": "Выбор приоритетных ИТ-проектов и оценка затрат",
        "start": "02.03.2026",
        "finish": "04.03.2026",
        "level": 2,
        "res": [2],
        "prev": 15
    },
    {
        "name": "Формирование дорожной карты и бюджета",
        "start": "05.03.2026",
        "finish": "06.03.2026",
        "level": 2,
        "res": [2, 1],
        "prev": 17,
        "note": "Заседание РГ №4. Ответственная — Козлова Е.П."
    },

    # ЭТАП 5
    {
        "name": "Разработка итогового документа и утверждение",
        "start": "09.03.2026",
        "finish": "20.03.2026",
        "level": 1
    },
    {
        "name": "Оформление проекта ИТ-стратегии (текст, таблицы, BSC)",
        "start": "09.03.2026",
        "finish": "13.03.2026",
        "level": 2,
        "res": [2],
        "prev": 18
    },
    {
        "name": "Предварительное рассмотрение проекта членами РГ",
        "start": "16.03.2026",
        "finish": "17.03.2026",
        "level": 2,
        "res": [9],
        "prev": 20
    },
    {
        "name": "Внесение корректировок по замечаниям",
        "start": "18.03.2026",
        "finish": "19.03.2026",
        "level": 2,
        "res": [2],
        "prev": 21
    },
    {
        "name": "Финальное заседание РГ, утверждение ИТ-стратегии",
        "start": "20.03.2026",
        "finish": "20.03.2026",
        "level": 2,
        "res": [1, 9],
        "prev": 22,
        "note": "Итоговое заседание РГ №5. Ответственная — Козлова Е.П."
    },
    {
        "name": "Издание приказа о введении ИТ-стратегии в действие",
        "start": "20.03.2026",
        "finish": "20.03.2026",
        "level": 2,
        "res": [1],
        "prev": 23,
        "link_type": 3
    }
]

# ==============================================
# СОЗДАНИЕ XML
# ==============================================

project = ET.Element(f"{{{NS}}}Project")

project_settings = {
    "Name": PROJECT_NAME,
    "Title": "План-график разработки ИТ-стратегии ООО «Максима»",
    "ScheduleFromStart": 1,
    "StartDate": "2026-01-22T09:00:00",
    "FinishDate": "2026-03-20T18:00:00",
    "CalendarUID": 1,
    "DefaultStartTime": "09:00:00",
    "DefaultFinishTime": "18:00:00",
    "MinutesPerDay": 480,
    "MinutesPerWeek": 2400,
    "DaysPerMonth": 20,
    "DurationFormat": 7,
    "WorkFormat": 2,
    "CurrencySymbol": "₽",
    "CurrencyCode": "RUB",
    "NewTasksEffortDriven": 0
}

for tag, value in project_settings.items():
    add(project, tag, value)

# ==============================================
# РАБОЧИЙ КАЛЕНДАРЬ
# ==============================================

calendars_el = add(project, "Calendars", None)
calendar = add(calendars_el, "Calendar", None)

add(calendar, "UID", 1)
add(calendar, "Name", "Стандартный (пн–пт)")
add(calendar, "IsBaseCalendar", 1)
add(calendar, "BaseCalendarUID", -1)

weekdays = add(calendar, "WeekDays", None)

# Microsoft Project:
# 1 = воскресенье
# 2 = понедельник
# ...
# 7 = суббота

for day_number in range(1, 8):
    weekday = add(weekdays, "WeekDay", None)
    add(weekday, "DayType", day_number)

    is_working = day_number in (2, 3, 4, 5, 6)
    add(weekday, "DayWorking", int(is_working))

    if is_working:
        times = add(weekday, "WorkingTimes", None)

        for start_time, end_time in [
            ("09:00:00", "13:00:00"),
            ("14:00:00", "18:00:00")
        ]:
            period = add(times, "WorkingTime", None)
            add(period, "FromTime", start_time)
            add(period, "ToTime", end_time)

# ==============================================
# ЗАПИСЬ ЗАДАЧ
# ==============================================

tasks_el = add(project, "Tasks", None)


def create_task(uid, name, start, finish, level,
                resources_list=None, predecessor=None,
                link_type=1, note=""):

    task = add(tasks_el, "Task", None)

    start_date = parse_date(start)
    finish_date = parse_date(finish)

    days = workdays(start, finish)
    hours = days * 8

    summary = level == 1

    fields = {
        "UID": uid,
        "ID": uid,
        "Name": name,
        "Type": 0,
        "IsNull": 0,
        "WBS": "",
        "OutlineLevel": level,
        "Summary": int(summary),
        "Milestone": 0,
        "Priority": 500,
        "Start": iso(start_date, "09"),
        "Finish": iso(finish_date, "18"),
        "Duration": f"PT{hours}H0M0S",
        "DurationFormat": 7,
        "ConstraintType": 2 if not summary else 1,
        "CalendarUID": 1,
        "Notes": note,
        "PercentComplete": 0,
        "Manual": 0
    }

    for tag, value in fields.items():
        add(task, tag, value)

    if not summary:
        add(task, "ConstraintDate", iso(start_date, "09"))

    if predecessor is not None:
        link = add(task, "PredecessorLink", None)
        add(link, "PredecessorUID", predecessor)
        add(link, "Type", link_type)
        add(link, "CrossProject", 0)

    return task


# Нулевая запись — весь проект
create_task(
    uid=0,
    name=PROJECT_NAME,
    start="22.01.2026",
    finish="20.03.2026",
    level=0
)

# Добавляем 24 записи: 5 этапов + 19 задач
for uid, item in enumerate(tasks, start=1):
    create_task(
        uid=uid,
        name=item["name"],
        start=item["start"],
        finish=item["finish"],
        level=item["level"],
        resources_list=item.get("res"),
        predecessor=item.get("prev"),
        link_type=item.get("link_type", 1),
        note=item.get("note", "")
    )

# ==============================================
# ЗАПИСЬ РЕСУРСОВ
# ==============================================

resources_el = add(project, "Resources", None)

for uid, name in resources.items():
    resource = add(resources_el, "Resource", None)

    add(resource, "UID", uid)
    add(resource, "ID", uid)
    add(resource, "Name", name)
    add(resource, "Type", 1)
    add(resource, "MaxUnits", 1.0)
    add(resource, "CalendarUID", 1)

# ==============================================
# НАЗНАЧЕНИЕ РЕСУРСОВ ЗАДАЧАМ
# ==============================================

assignments_el = add(project, "Assignments", None)

assignment_uid = 1

for task_uid, item in enumerate(tasks, start=1):
    assigned_resources = item.get("res", [])

    for resource_uid in assigned_resources:
        assignment = add(assignments_el, "Assignment", None)

        add(assignment, "UID", assignment_uid)
        add(assignment, "TaskUID", task_uid)
        add(assignment, "ResourceUID", resource_uid)
        add(assignment, "Units", 1.0)

        assignment_uid += 1

# ==============================================
# СОХРАНЕНИЕ
# ==============================================

tree = ET.ElementTree(project)

ET.indent(tree, space="  ", level=0)

tree.write(
    FILE_NAME,
    encoding="utf-8",
    xml_declaration=True
)

print("Файл успешно создан:", FILE_NAME)
print("Этапов: 5")
print("Обычных задач: 19")
print("Ресурсов:", len(resources))
print("Назначений:", assignment_uid - 1)
print("Начало проекта: 22.01.2026")
print("Окончание проекта: 20.03.2026")
