def track_variable_access(variable_name):
    def decorator(func):
        access_count = 0

        def wrapper(*args, **kwargs):
            nonlocal access_count
            access_count += 1
            return func(*args, **kwargs)

        wrapper.access_count = lambda: access_count
        return wrapper

    return decorator
