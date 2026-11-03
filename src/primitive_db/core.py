def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.\n')
        return metadata

    table_names = [column.partition(':')[0].lower() for column in columns]
    table_types = [column.partition(':')[2] for column in columns]
    for i in range(len(columns)):
        if table_types[i] not in ['int', 'str', 'bool'] or not table_names[i]:
            print(f'Некорректное значение: {columns[i]}. Попробуйте снова.\n')
            return metadata

    if len(table_names) != len(set(table_names)):
        print('Ошибка. Столбцы должны иметь уникальные table_name\n')
        return metadata

    has_id = False
    for name, type_ in zip(table_names, table_types):
        if name.lower() == 'id' and type_ != 'int':
            print('Ошибка. ID может быть только типа integer\n')
            return metadata
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


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.\n')
        return metadata
    del metadata[table_name]

    return metadata


def list_tables(metadata):
    if not metadata:
        print('База данных не содержит таблиц.\n')
        return metadata
    for table_name in metadata:
        print(table_name)
