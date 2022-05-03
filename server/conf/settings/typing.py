readonly = object()


def convert(value, annotation):
    # readonly
    if annotation is readonly:
        raise ConvertError('It is readonly.')

    # bool
    if annotation is bool:
        return _convert_bool(value)


def _convert_bool(value):
    try:
        return bool(int(value))
    except ValueError:
        if value in ("True", "true"):
            return True
        if value in ("False", "false"):
            return False
        raise ConvertError("Supported values for boolean settings "
                           "are 0/1, True/False, '0'/'1', "
                           "'True'/'False' and 'true'/'false'.")


class ConvertError(Exception):
    pass
