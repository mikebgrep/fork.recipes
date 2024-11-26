import datetime


def format_date_joined(date_joined):
    date_obj = datetime.datetime.strptime(date_joined, "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_date = date_obj.strftime("%B %Y")

    return formatted_date