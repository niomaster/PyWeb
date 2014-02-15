def get_body_data(data):
    if data.session.get("error", "") != "":
        message = data.session.error
        data.session.error = ""
    else:
        message = ""

    return { "errorMessage": message }