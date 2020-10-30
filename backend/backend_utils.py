from sanic.exceptions import InvalidUsage


def validate_required_params(param_list, *params):
    args = {}
    for param in list(params):
        if param not in param_list:
            raise InvalidUsage(f'Parameter "{param}" was missing from the request')

        arg = param_list[param]
        if len(arg) == 0:
            raise InvalidUsage(f'Parameter "{param}" had no data associated with it')

        args[param] = arg

    return args
