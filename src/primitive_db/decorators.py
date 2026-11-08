import time
from functools import wraps


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                'Ошибка: Файл данных не найден. Возможно, база данных '
                'не инициализирована.\n'
            )
            return None
        except ValueError as e:
            print(f'{e}\n')
            return None
        except KeyError as e:
            print(f'{e.args[0]}\n')
            return None
        except Exception as e:
            print(f'Произошла непредвиденная ошибка: {e}\n')
            return None
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if response.strip().lower() == 'y':
                return func(*args, **kwargs)
            else:
                print('Операция отменена\n')
                return None
        return wrapper
    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f'Функция {func.__name__} выполнилась за {elapsed:.3f} секунд')
        return result
    return wrapper


def create_cacher():
    cache_dt = dict()

    def cache_result(key, value_func):
        if key in cache_dt:
            return cache_dt[key]
        cache_dt[key] = value_func()
        return cache_dt[key]
    return cache_result
