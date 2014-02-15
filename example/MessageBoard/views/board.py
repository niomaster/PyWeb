def get_body_data(data):
    messages = data.storage.messages
    userMessages = filter(lambda message: message["recipient"] == data.session.user or message["sender"] == data.session.user, messages)
    newMessages = sorted(filter(lambda message: message["new"][data.session.user], userMessages), key=lambda message: message["sent"])[::-1]
    oldMessages = sorted(filter(lambda message: not message["new"][data.session.user], userMessages), key=lambda message: message["sent"])[::-1]

    for message in newMessages:
        message["new"][data.session.user] = False

    if data.session.get("error", "") != "":
        message = data.session.error
        data.session.error = ""
    else:
        message = ""

    return { "errorMessage": message, "newMessages": newMessages, "oldMessages": oldMessages }