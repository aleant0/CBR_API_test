import requests


# gdc
def get_daily_currency():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    daily = requests.get(url)
    return daily


# Дату вводить строкой в формате "dd/mm/yyyy"
def gdc_certain_date(date):
    date_req = f'date_req={date}'
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    daily = requests.get(url, params=date_req)
    return daily


def xml_schema():
    url = "http://www.cbr.ru/StaticHtml/File/92172/ValCurs.xsd"
    xmlschema = requests.get(url).text
    return xmlschema


def currency_list():
    url = "http://www.cbr.ru/scripts/XML_valFull.asp"
    cl = requests.get(url).text
    return cl
