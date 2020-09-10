def validate_params(param_list, *params):
    for param in list(params):
        if param not in param_list:
            return False

    return True