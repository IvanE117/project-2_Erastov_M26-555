import shlex

import prompt

from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
    insert,
    select,
    update,
    delete,
)
from primitive_db.utils import (
    load_metadata,
    save_metadata,
    load_table_data,
    save_table_data,
)




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

    print()

    print("\n*** Операции с данными ***\n")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values <значение1> <значение2> ... - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.\n")

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
                data_for_save, flag = upd_data
                if flag:
                    print(f'Таблица "{args[1]}" успешно создана со столбцами: {args[2:]}\n')
                save_metadata('db_meta.json', data_for_save)

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
                if upd_data[1] is False:
                    continue

                print(f'Таблица "{args[1]}" успешно удалена.\n')
                save_metadata('db_meta.json', upd_data[0])

            case 'insert':
                if len(args) < 5:
                    print('Ошибка при вводе команды или параметров\n')
                    continue

                if not (args[1] == 'into' and args[3] == 'values'):
                    print('Ошибка: некорректная форма записи команды')
                    continue

                t_name = args[2]
                result = insert(
                    metadata=data,
                    table_name=t_name,
                    values=args[4:]
                )
                if result is None:
                    continue

                id_, table_data = result
                if isinstance(id_, int):
                    print(f'Запись с ID={id_} успешно добавлена в таблицу "{t_name}".\n')
                else:
                    print('Ошибка: данные отсутствуют')
                    continue
                save_table_data(t_name, table_data)

            case 'select':
                if len(args) < 3:
                    print('Ошибка при вводе команды или параметров\n')
                    continue

                if not args[1] == 'from':
                    print('Ошибка: некорректная форма записи команды\n')
                    continue

                if len(args) > 3:
                    if not (args[3] == 'where' and len(args) >= 5):
                        print('Ошибка при вводе команды или параметров\n')
                        continue

                tab_name = args[2]
                if tab_name not in data:
                    print(f'Ошибка: Таблицы {tab_name} в БД не обнаруженно!\n')
                    continue

                tab_data = load_table_data(
                    table_name=tab_name
                )
                res_for_print = select(
                    table_data=tab_data,
                    where_clause=" ".join(args[4:]) if len(args) > 3 else None
                )
                if isinstance(res_for_print, list):
                    table = PrettyTable()
                    table.field_names = list(data[tab_name].keys())
                    for row in res_for_print:
                        table.add_row(list(row.values()))
                    print(table)
                    print()
                else:
                    continue

            case 'update':
                if len(args) < 9:
                    print('Ошибка при вводе команды или параметров\n')
                    continue

                if not (
                    args[2] == 'set'
                    and args[4] == '='
                    and args[6] == 'where'
                    and args[8] == '='
                ):
                    print('Ошибка: некорректная форма записи команды\n')
                    continue

                tab_name = args[1]
                if tab_name not in data:
                    print(f'Ошибка: Таблицы {tab_name} в БД не обнаруженно!\n')
                    continue

                tab_data = load_table_data(
                    table_name=tab_name
                )

                result = update(
                        table_data=tab_data,
                        set_clause=" ".join(args[3:6]),
                        where_clause=" ".join(args[7:])
                    )
                if result is None:
                    continue

                ids, res_for_save = result
                if not ids:
                    print('Записи по заданному условию не найдены.\n')
                    continue

                save_table_data(tab_name, res_for_save)
                print(
                    f'Запись(и) с ID = {ids} в таблице "{tab_name}" '
                    'успешно обновлена(ы).\n'
                )

            case 'delete':
                if len(args) < 7:
                    print('Ошибка при вводе команды или параметров\n')
                    continue

                if not (
                    args[1] == 'from'
                    and args[3] == 'where'
                    and args[5] == '='
                ):
                    print('Ошибка: некорректная форма записи команды\n')
                    continue

                tab_name = args[2]
                if tab_name not in data:
                    print(f'Ошибка: Таблицы {tab_name} в БД не обнаруженно!\n')
                    continue

                tab_data = load_table_data(
                    table_name=tab_name
                )

                result = delete(
                    table_data=tab_data,
                    where_clause=" ".join(args[4:])
                )

                if result is None:
                    continue

                result_for_save, ids = result
                if not ids:
                    print('Записи по заданному условию не найдены.\n')
                    continue
                save_table_data(tab_name, result_for_save)

                print(
                    f'Запись(и) с ID = {ids} успешно удалена(ы) из таблицы '
                    f'"{tab_name}".\n'
                )

            case 'info':
                if len(args) < 2:
                    print('Ошибка при вводе команды или параметров\n')
                    continue

                tab_name = args[1]
                if tab_name not in data:
                    print(f'Ошибка: Таблицы {tab_name} в БД не обнаруженно!\n')
                    continue

                tab_data = load_table_data(
                    table_name=tab_name
                )

                print(f'Таблица: {tab_name}')
                print('Столбцы: ', end='')
                for key, value in data[tab_name].items():
                    print(f'{key}:{value}', end=', ')
                print(f'Количество записей: {len(tab_data)}\n')

            case 'exit':
                break

            case 'help':
                print_help()

            case _:
                print(f'Функции {args[0]} нет. Попробуйте снова.\n')
