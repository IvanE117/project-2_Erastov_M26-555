def clause_parser(condition):
    column_name, _, value = condition.partition('=')
    value = value.strip()
    column_name = column_name.strip()

    expected_type = yield column_name
    if expected_type is bool:
        if value.lower() == 'true':
            yield {
                column_name: True
            }
        elif value.lower() == 'false':
            yield {
                column_name: False
            }
        else:
            raise ValueError('Ошибка. Некорректное значение bool!')
    else:
        yield {
            column_name: expected_type(value)
        }
