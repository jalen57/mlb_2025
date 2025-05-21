import warnings
from fractions import Fraction
from typing import Union

import numpy as np
import numpy.typing as npt
import pandas as pd


def convert_odds(
    american: float = None,
    decimal: float = None,
    fractional: Union[float, str] = None,
    implied_probability: float = None,
    rounded: bool = False
) -> dict:
    """Convert any odds to the other three types.
    References:https://www.aceodds.com/bet-calculator/odds-converter.html.

    Odds types:
    - American/Moneyline:
        - Positive figures: The odds state the winnings on a £100 bet
            e.g. american odds of 110 would win £110 on a £100 bet.
        - Negative figures: The odds state how much must be bet to win £100 profit
            e.g. american odds of -120 would win £100 on a £120 bet.
    - Decimals/European:
        Decimals quote the potential return should the bet succeed relative to the stake.
        For example, if £5 is bet at odds of 3 the total returned is £15 (£5 * 3)
        the potential profit is £10 (£5 * 3 minus the £5 stake).
    - Fractions:
        Used primarily in the UK and Ireland, fractions quote the potential profit should
        the bet succeed relative to the stake. For example, if £5 is bet at odds of 2/1
        the potential profit is £10 (£5 * 2) and the total returned is £15 (£10 plus the £5 stake).
    - Implied probability:
        Odds correlate to probability e.g a 3/1 bet is expected to win one in every 4 attempts.
        Hence, the probability is 25%.
    """
    non_nulls = pd.notna([fractional, decimal, american,
                          implied_probability]).sum()

    if non_nulls != 1:
        implied_probability = np.nan
        warnings.warn(
            'Please input exactly ONE type of odds, now returning with nulls.'
        )

    # convert fractional from string to number
    if isinstance(fractional, str):
        fractional = float(Fraction(fractional))

    # convert all types of odds to implied probabilities
    if not pd.isna(american):
        # convert -100 to 100 which is the same but avoiding zero denominator
        american = 100 if american == -100 else american

        # positive american odds
        if american >= 0:
            implied_probability = 100 / (american + 100)

        # negative american odds
        else:
            implied_probability = -american / (100 - american)

    # valid decimal odds >= 1
    elif (not pd.isna(decimal)) and (decimal >= 1):
        implied_probability = 1 / decimal

    # valid fractional odds > 0
    elif (not pd.isna(fractional)) and (fractional > 0):
        implied_probability = 1 / (fractional + 1)

    # if it is an invalid odds value and implied_probability not given, return null
    elif pd.isna(implied_probability):
        implied_probability = np.nan

    # only process valid probabilities
    if 0 <= implied_probability <= 1:

        # to avoid zero division by assigning close values to prob of 0 and 1
        if implied_probability == 0:
            implied_probability = 1e-5
        elif implied_probability == 1:
            implied_probability = 1 - 1e-5

        decimal = 1 / implied_probability
        fractional = 1 / implied_probability - 1

        # convert implied probabilities to all types of odds
        american_positive = (100 / implied_probability) - 100
        american_negative = -implied_probability * 100 / (
            1 - implied_probability
        )

        if rounded:
            american_positive = round(american_positive)
            american_negative = round(american_negative)

        american = american_positive if abs(american_positive) >= abs(
            american_negative
        ) else american_negative

    else:
        warnings.warn(
            f'Invalid {implied_probability=}, now returning with nulls.'
        )
        decimal = np.nan
        fractional = np.nan
        american, american_positive, american_negative = np.nan, np.nan, np.nan

    # do the roundings
    if rounded:
        decimal = round(decimal, 2)
        fractional = round(fractional, 2)

    # get fractional odds as string fraction
    try:
        fractional_str = str(Fraction(str(fractional)))
    except ValueError:
        fractional_str = ''

    return {
        'decimal': decimal,
        'fractional': fractional,
        'fractional_str': fractional_str,
        'implied_probability': implied_probability,
        'american': american,
        'american_positive': american_positive,
        'american_negative': american_negative,
    }


def calculate_margin(decimal_odds: npt.ArrayLike) -> np.array:
    """Calculates the individual margin/hold of betting props giving all the
    odds.

    Args:
        decimal_odds: the matrix containing odds, rows being each betting props
            while columns being odds regarding the prop.

    Returns:
        the calculated margin per props.
    """

    return np.sum(1 / decimal_odds, axis=1) - 1
