import json

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.parser import clause_parser
from primitive_db.utils import load_table_data
from primitive_db.constants import VALID_TYPES

cacher = create_cacher()


def check_table_existence(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(f'Ошибка: Таблица "{table_name}" не существует.')


def check_data_absence(data):
    if not data:
        print('В БД отсутствуют записи.\n')
        return False
    return True


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise KeyError(f'Ошибка: Таблица "{table_name}" уже существует.')

    table_names = [column.partition(':')[0].lower() for column in columns]
    table_types = [column.partition(':')[2] for column in columns]
    for i in range(len(columns)):
        if table_types[i] not in VALID_TYPES or not table_names[i]:
            raise ValueError(f'Некорректное значение: {columns[i]}. Попробуйте снова.')

    if len(table_names) != len(set(table_names)):
        raise ValueError('Ошибка: Столбцы должны иметь уникальные table_name')

    has_id = False
    for name, type_ in zip(table_names, table_types):
        if name.lower() == 'id' and type_ != 'int':
            raise ValueError('Ошибка: ID может быть только типа integer')
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
    return metadata


@confirm_action('удаление таблицы')
@handle_db_errors
def drop_table(metadata, table_name):
    check_table_existence(metadata, table_name)
    del metadata[table_name]

    return metadata, True


def list_tables(metadata):
    if not check_data_absence(metadata):
        return metadata
    for table_name in metadata:
        print(table_name)


def get_dict_values(dt):
    return dt.values()


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if not check_data_absence(metadata):
        return None

    check_table_existence(metadata, table_name)

    if len(values) != len(metadata[table_name]) - 1:
        raise ValueError('Неверное число переданных параметров!')

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
                raise ValueError(
                    f'Ошибка преобразования типа: "{value}" '
                    'не является целым числом.'
                )
        elif expected_type is bool:
            if value.lower() == 'true':
                converted_values.append(True)
            elif value.lower() == 'false':
                converted_values.append(False)
            else:
                raise ValueError(
                    f'Ошибка преобразования типа: "{value}" '
                    'не является типом bool'
                )
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
        return None

    parser = clause_parser(clause)
    column = next(parser)

    if column in table_data[0]:
        expected_type = type(table_data[0][column])
    else:
        raise KeyError(f'Ошибка: столбец {column} отсутствует!')

    result = parser.send(expected_type)

    return next(iter(result.items()))


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    key_and_value = parse_and_check(table_data, where_clause)

    if key_and_value is None:
        return None
    key, value = key_and_value

    def compute():
        result = []
        for tuple_ in table_data:
            if key in tuple_ and tuple_[key] == value:
                result.append(dict(tuple_))
        return result

    cache_key = (where_clause, json.dumps(table_data, sort_keys=True))
    return cacher(cache_key, compute)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    if not check_data_absence(table_data):
        return None

    result = parse_and_check(table_data, set_clause)

    if result is None:
        return None
    set_key, new_set_value = result

    selected_tuples = select(table_data, where_clause)
    if selected_tuples is None:
        return None

    selected_ids = {tuple_['ID'] for tuple_ in selected_tuples}

    ids = []
    for tuple_ in table_data:
        if tuple_['ID'] in selected_ids:
            tuple_[set_key] = new_set_value
            ids.append(tuple_['ID'])

    return ids, table_data


@confirm_action('удаление записи')
@handle_db_errors
def delete(table_data, where_clause):
    if not check_data_absence(table_data):
        return table_data, []

    selected_tuples = select(table_data, where_clause)
    if selected_tuples is None:
        return None

    ids = [tuple_['ID'] for tuple_ in table_data if tuple_ in selected_tuples]
    return [tuple_ for tuple_ in table_data if tuple_ not in selected_tuples], ids
