def get_param(request, param, default=None):
    try:
        if request.method == "POST":
            return request.data[param]
        if request.method == "PUT":
            return request.body[param]
        elif request.method == "GET":
            return request.query_params[param]
        else:
            return default
    except Exception:
        return default
