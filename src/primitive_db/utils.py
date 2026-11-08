import json
from pathlib import Path


def load_metadata(filepath):
    """Загружает JSON-данные; если файл не найден, возвращает {}."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return


def load_table_data(table_name):
    filepath = f'data/{table_name}.json'
    data = load_metadata(filepath)
    if not data:
        return []
    return data


def save_table_data(table_name, data):
    Path('data').mkdir(exist_ok=True)
    filepath = f'data/{table_name}.json'
    save_metadata(filepath, data)


def delete_table_data(table_name):
    Path(f'data/{table_name}.json').unlink(missing_ok=True)
