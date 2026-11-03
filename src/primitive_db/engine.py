import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def enter_command():
    return prompt.string("Введите команду: ")


# def welcome():
#     print("Первая попытка запустить проект!")
#     print()
#     print("***")

#     print(
#         "<command> exit - выйти из программы\n"
#         "<command> help - справочная информация"
#     )
#     response = enter_command()

#     while response != "exit":
#         if response == "help":
#             print(
#                 "\n<command> exit - выйти из программы\n"
#                 "<command> help - справочная информация"
#             )
#         response = enter_command()


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***\n")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()
    while True:
        data = load_metadata('db_meta.json')

        response = enter_command()
        try:
            args = shlex.split(response)
        except ValueError:
            print('Ошибка при вводе данных. Введите еще раз!\n')
            continue

        if not args:
            continue

        match args[0]:
            case 'create_table':
                if len(args) < 3:
                    print('Ошибка: Не хватает аргументов\n')
                    continue
                upd_data = create_table(
                    metadata=data,
                    table_name=args[1],
                    columns=[*args[2:]]
                )
                print(f'Таблица "{args[1]}" успешно создана со столбцами: {args[2:]}\n')
                save_metadata('db_meta.json', upd_data)

            case 'list_tables':
                list_tables(data)
                print()
            case 'drop_table':
                if len(args) != 2:
                    print('Ошибка при вводе параметров\n')
                    continue
                upd_data = drop_table(
                    metadata=data,
                    table_name=args[1]
                    )
                print(f'Таблица "{args[1]}" успешно удалена.\n')
                save_metadata('db_meta.json', upd_data)

            case 'exit':
                break

            case 'help':
                print_help()

            case _:
                print(f'Функции {args[0]} нет. Попробуйте снова.\n')
