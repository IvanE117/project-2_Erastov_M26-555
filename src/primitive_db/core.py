from primitive_db.parser import clause_parser
from primitive_db.utils import load_table_data


def check_table_existence(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.\n')
        return False
    return True


def check_data_absence(data):
    if not data:
        print('В БД отсутствуют записи.\n')
        return False
    return True


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.\n')
        return metadata, False

    table_names = [column.partition(':')[0].lower() for column in columns]
    table_types = [column.partition(':')[2] for column in columns]
    for i in range(len(columns)):
        if table_types[i] not in ['int', 'str', 'bool'] or not table_names[i]:
            print(f'Некорректное значение: {columns[i]}. Попробуйте снова.\n')
            return metadata, False

    if len(table_names) != len(set(table_names)):
        print('Ошибка. Столбцы должны иметь уникальные table_name\n')
        return metadata, False

    has_id = False
    for name, type_ in zip(table_names, table_types):
        if name.lower() == 'id' and type_ != 'int':
            print('Ошибка. ID может быть только типа integer\n')
            return metadata, False
        elif name == 'id' and type_ == 'int':
            has_id = True

    if has_id:
        copy_columns = columns
    else:
        copy_columns = ['ID:int'] + columns

    metadata.update(
        {
            table_name: {
                column.partition(':')[0]: column.partition(':')[2]
                for column in copy_columns
            }
        }
    )
    return metadata, True


def drop_table(metadata, table_name):
    if not check_table_existence(metadata, table_name):
        return metadata, False
    del metadata[table_name]

    return metadata, True


def list_tables(metadata):
    if not check_data_absence(metadata):
        return metadata
    for table_name in metadata:
        print(table_name)


def get_dict_values(dt):
    return dt.values()


def insert(metadata, table_name, values):
    if not check_data_absence(metadata):
        return None

    if not check_table_existence(metadata, table_name):
        return None

    if len(values) != len(metadata[table_name]) - 1:
        return None

    column_types = list(get_dict_values(metadata[table_name]))[1:]
    column_names = list(metadata[table_name].keys())[1:]
    type_mapping = {
        'int': int,
        'str': str,
        'bool': bool
    }
    converted_values = []
    for column, value in zip(column_types, values):
        expected_type = type_mapping[column]

        if expected_type is int:
            try:
                converted_values.append(int(value))
            except ValueError:
                print('Ошибка преобразования типа!\n')
                return None
        elif expected_type is bool:
            if value.lower() == 'true':
                converted_values.append(True)
            elif value.lower() == 'false':
                converted_values.append(False)
            else:
                print('Ошибка преобразования типа!\n')
                return None
        else:
            converted_values.append(str(value))
    updated_table = dict(zip(column_names, converted_values))

    data_table = load_table_data(table_name)
    max_id = max((table['ID'] for table in data_table), default=0)

    id_dict = dict()
    id_dict['ID'] = max_id + 1
    merged_dict = id_dict | updated_table
    data_table.append(merged_dict)

    return max_id + 1, data_table


def parse_and_check(table_data, clause):
    if not check_data_absence(table_data):
        return table_data

    parser = clause_parser(clause)
    column = next(parser)

    if column in table_data[0]:
        expected_type = type(table_data[0][column])
    else:
        print('Ошибка: такого столбца нет!\n')
        return None, None

    try:
        result = parser.send(expected_type)
    except ValueError:
        return None, None

    return next(iter(result.items()))


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    try:
        key, value = parse_and_check(table_data, where_clause)
    except ValueError:
        return table_data

    if key is None and value is None:
        return
    result = []
    for tuple_ in table_data:
        if key in tuple_ and tuple_[key] == value:
            result.append(tuple_)
    return result


def update(table_data, set_clause, where_clause):
    if not check_data_absence(table_data):
        return None

    set_key, new_set_value = parse_and_check(table_data, set_clause)
    if set_key is None and new_set_value is None:
        return None

    selected_tuples = select(table_data, where_clause)
    if selected_tuples is None:
        return None

    ids = []
    for tuple_ in selected_tuples:
        tuple_[set_key] = new_set_value
        ids += [tuple_['ID']]

    return ids, table_data


def delete(table_data, where_clause):
    if not check_data_absence(table_data):
        return table_data, []

    selected_tuples = select(table_data, where_clause)
    if selected_tuples is None:
        return

    ids = [tuple_['ID'] for tuple_ in table_data if tuple_ in selected_tuples]
    return [tuple_ for tuple_ in table_data if tuple_ not in selected_tuples], ids


table_data = [
    {'ID': 1, 'name': 'Sergei', 'age': 28, 'is_active': True},
    {'ID': 2, 'name': 'Ivan', 'age': 25, 'is_active': False},
    {'ID': 3, 'name': 'Alex', 'age': 28, 'is_active': True},
    {'ID': 4, 'name': 'Maria', 'age': 32, 'is_active': False}
]


if __name__ == '__main__':
    # data = where_clause_parser('age = 28')
    # print(next(data))
    # condition = data.send(int)

    # print(condition,'here')
    # key, value = list(condition.keys())[0], list(condition.values())[0]
    # for tuple_ in table_data:
    #     if key in tuple_ and tuple_[key] == value:
    #         print(tuple_)

    # print(select(table_data, 'age = 28'))
    # print(select(table_data, 'is_active = false'))
    # print(select(table_data, 'age = 100'))
    # print(select(table_data, 'is_active = hello'))
    # print(select(table_data, 'name = Sergei'))
    # print(select(table_data, 'name = Unknown'))
    print(update(table_data, 'age = 100', 'age = 28'))
    # print(delete(table_data, 'age=hello'))
