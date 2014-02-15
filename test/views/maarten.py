def get_messageList_data(session):
    if session.has("bekeken"):
        bekeken = session.bekeken + 1
    else:
        bekeken = 1

    session.bekeken = bekeken
    return { "messages": [{"name": "Pieter", "message": "Hoi!"}, {"name": "Maarten", "message": "Hallo!"}, {"name": "Meike", "message": "Bram!"}], "bekeken": str(bekeken) }