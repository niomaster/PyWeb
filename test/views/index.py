def get_head_data(data):
    return "Ons gezin"

def get_body_data(data):
    session = data.session

    if session.has("visits"):
        visits = session.get("visits") + 1
    else:
        visits = 1

    session.set("visits", visits)

    return { "visits": str(visits), "gezinsleden": [{ "naam": "Pieter", "leeftijd": "16" }, { "naam": "Meike", "leeftijd": "14"}
        , { "naam": "Willemijn", "leeftijd": "42"}, { "naam": "Teun", "leeftijd": "35"}
        , { "naam": "Bram", "leeftijd": "4"}]}

