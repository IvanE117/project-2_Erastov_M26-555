# Primitive DB

Консольная база данных с поддержкой создания, просмотра и удаления таблиц.

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/IvanE117/project-2_Erastov_M26-555.git
cd project-2_Erastov_M26-555
```

Установите зависимости и синхронизируйте виртуальное окружение:

```bash
uv sync
```

## Запуск

```bash
uv run database
```

## Управление таблицами

Поддерживаются следующие команды:

- `create_table` — создание таблицы;
- `list_tables` — вывод списка всех таблиц;
- `drop_table` — удаление таблицы;
- `help` — вывод справки по командам;
- `exit` — выход из программы.

### Поддерживаемые типы данных

- `int` — целое число;
- `str` — строка;
- `bool` — логическое значение.

## Пример использования

Создание таблицы:

```text
create_table users name:str age:int
```

Просмотр списка таблиц:

```text
list_tables
```

Удаление таблицы:

```text
drop_table users
```

Завершение работы:

```text
exit
```

## Демонстрация

[![asciicast](https://asciinema.org/a/E49SOALxzntdYQeC.svg)](https://asciinema.org/a/E49SOALxzntdYQeC)