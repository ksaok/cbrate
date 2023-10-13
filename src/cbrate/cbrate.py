"""
Using API https://cbr.ru/development/SXML/
"""


from datetime import datetime
import requests
import xml.etree.ElementTree as ET

from typing import Optional

from .data_types import ReferenceRecord, RateRecord


class CBRate:
    REFERENCE_URL = 'https://www.cbr.ru/scripts/XML_valFull.asp'
    RATES_URL = 'https://cbr.ru/scripts/XML_daily_eng.asp'
   
    def __init__(self, year: int = None, month: int = None, day: int = None):
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        if day is None:
            day = datetime.now().day
        self.date = f'{day}/{month}/{year}'  # dd/mm/yyyy

        self._daily_reference = self._get_reference()
        self._monthly_reference = self._get_reference(monthly=True)
        self._daily_char_codes = {rec.char_code: rec.code for rec in self._daily_reference if rec.char_code}
        self._daily_num_codes = {rec.num_code: rec.code for rec in self._daily_reference if rec.num_code}
        self._monthly_char_codes = {rec.char_code: rec.code for rec in self._monthly_reference if rec.char_code}
        self._monthly_num_codes = {int(rec.num_code): rec.code for rec in self._monthly_reference if rec.num_code}

        self._rates = self._get_rates(self.date)
        self._rates_by_char_code = {rec.char_code: rec.vunit_rate for rec in self._rates if rec.char_code}
        self._rates_by_num_code = {int(rec.num_code): rec.vunit_rate for rec in self._rates if rec.num_code}


    def _request(self, url: str, params: dict = None):
        response = requests.get(url, params=params)
        return ET.fromstring(response.text) if response.status_code == 200 else None

    def _get_reference(self, monthly: bool = False):
        params = {'d': 1} if monthly else {'d': 0}
        root = self._request(self.REFERENCE_URL, params=params)
        return [
            ReferenceRecord(
                code=rec.attrib['ID'],
                name=rec.find('Name').text,
                nominal=int(rec.find('Nominal').text),
                parent_code=rec.find('ParentCode').text,
                char_code=rec.find('ISO_Char_Code').text,
                num_code=rec.find('ISO_Num_Code').text,
            ) for rec in root
        ]

    def _get_rates(self, date: str):
        params = {'date_req': date}
        root = self._request(self.RATES_URL, params=params)
        response_date = root.attrib['Date']
        return [
            RateRecord(
            date=response_date,
            code=rec.attrib['ID'],
            name=rec.find('Name').text,
            char_code=rec.find('CharCode').text,
            num_code=rec.find('NumCode').text,
            nominal=int(rec.find('Nominal').text),
            value=float(rec.find('Value').text.replace(',', '.')),
            vunit_rate=float(rec.find('VunitRate').text.replace(',', '.')),
            ) for rec in root
        ]

    def _get_cbr_code(self, iso_code: str | int) -> Optional[str]:
        if isinstance(iso_code, str):
            daily = self._daily_char_codes
            monthly = self._monthly_char_codes
        elif isinstance(iso_code, int):
            daily = self._daily_num_codes
            monthly = self._monthly_num_codes
        else:
            return None

        return daily.get(iso_code) or monthly.get(iso_code)

    def __getitem__(self, index: str | int) -> float:
        return self._rates_by_char_code.get(index) or self._rates_by_num_code.get(index)

