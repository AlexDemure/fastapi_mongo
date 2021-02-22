from decimal import Decimal, ROUND_DOWN
from typing import Union


def convert_number_to_decimal(num: Union[int, float, Decimal]) -> Decimal:
    """
    Конвертация всех числовых значений в Decimal с округлением вниз.

    На выходе получаем Decimal в формате 0.00
    """
    return Decimal(num).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
