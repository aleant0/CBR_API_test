import pytest
import requests
import xmlschema
from xml.etree import ElementTree as ET
from src.daily_currency_quotes import get_daily_currency, xml_schema, gdc_certain_date, currency_list


def isfloat(n):
    try:
        float(n)
        return True
    except ValueError:
        return False


# Проверка сатус-кодов (На невалидый URL по факту приходит редирект, но сюда прилетает 200. Не разобрался, как решить)
@pytest.mark.parametrize("func", [get_daily_currency(), gdc_certain_date('01/01/2021')])
def test_status_code(func):
    assert func.status_code == 200
    assert requests.get("https://www.cbr.ru/scripts/XML_da").status_code == 200


# Сверка выдачи с XSD-схемой
@pytest.mark.parametrize("func", [get_daily_currency(), gdc_certain_date('01/01/2021')])
def test_schema_validation(func):
    daily_currency = func.text
    schema = xmlschema.XMLSchema(xml_schema())
    assert xmlschema.is_valid(daily_currency, schema)


# Проверка Value в выдаче на числа
@pytest.mark.parametrize("func", [get_daily_currency(), gdc_certain_date('01/01/2021')])
def test_value_is_num(func):
    count = 0
    daily = ET.fromstring(func.text)
    for value in daily.iter("Value"):
        v = value.text.replace(",", ".")
        if isfloat(v):
            count += 1
    assert count == len(daily.findall("Valute"))


# Сверка кодов валют в выдаче с ISO кодами валют(Список с ISO кодами валют неполный, в нём нет старых валют)
@pytest.mark.parametrize("func", [get_daily_currency(), gdc_certain_date('01/01/2021')])
def test_quotes_code_validation(func):
    count = 0
    clist = ET.fromstring(currency_list())
    daily = ET.fromstring(func.text)
    for item in clist.iter("Item"):
        item_id = item.attrib['ID']
        if daily.find(f"Valute[@ID='{item_id}']") is None:
            continue
        daily_num_code = daily.find(f"Valute[@ID='{item_id}']/NumCode")
        daily_char_code = daily.find(f"Valute[@ID='{item_id}']/CharCode")
        list_num_code = item.find("./ISO_Num_Code")
        list_char_code = item.find("./ISO_Char_Code")
        a = int(list_num_code.text) == int(daily_num_code.text)
        b = list_char_code.text == daily_char_code.text
        if a and b:
            count += 1
    assert len(daily.findall("Valute")) == count


# Проверка невалидных дат(Количество символов в году не ограничено на проде)
@pytest.mark.parametrize("date", ['29/02/2001',
                                  '01/13/2001',
                                  '01/01/1990',
                                  '29/02/2001',
                                  '011/01/2001',
                                  '01/022/2001'
                                  '2001/01/01'])
def test_invalid_date(date):
    daily = gdc_certain_date(f"{date}").text
    assert "Error in parameters" in daily
