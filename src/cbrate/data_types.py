from dataclasses import dataclass
import datetime


@dataclass
class ReferenceRecord:
    code: str  # ID
    name: str  # EngName
    nominal: int  # Nominal
    parent_code: str  # ParentCode
    char_code: str  # ISO_Char_Code
    num_code: int  # ISO_Num_Code


@dataclass
class RateRecord:
    date: datetime.date  # Date
    code: str  # ID
    name: str  # Name
    char_code: str  # CharCode
    num_code: int  # NumCode
    nominal: int  # Nominal
    value: float  # Value
    vunit_rate: float  # VunitRate

