# calculator/calc.py
from __future__ import annotations
from datetime import date, timedelta
from functools import lru_cache
from dateutil.relativedelta import relativedelta


class UnknownRetirementAge(Exception):
    """Raised when no AOW-leeftijd can be calculated (e.g., very old dates)."""
    pass


class RetirementResult:
    """Stores statutory age and whether that figure is an estimate."""
    def __init__(self, years: int, months: int, estimated: bool):
        self.years = years
        self.months = months
        self.estimated = estimated

    def __str__(self) -> str:
        y = f"{self.years} jaar{'' if self.years != 1 else ''}" if self.years else ""
        m = f"{self.months} maand{'en' if self.months != 1 else ''}" if self.months else ""
        return " en ".join(part for part in (y, m) if part)


# ────────────────────────────────────────────────────────────────────────────────
#  Life-expectancy projections used in the legal formula  (article 7a AOW)
#  Sources: CBS news releases 2020-2024 (one per year) ▶︎ see footnotes.
# ────────────────────────────────────────────────────────────────────────────────
_LIFE_EXP_AT_65: dict[int, float] = {
    2024: 20.64,
    2025: 20.75,
    2026: 20.82,
    2027: 20.93,
    2028: 21.05,
    2029: 20.89,
    2030: 20.96,
    2031: 21.12,
    2032: 21.24,
    2033: 21.35,
    2034: 21.47,
    2035: 21.59,
    2036: 21.71,
    2037: 21.82,
    2038: 21.94,
    2039: 22.06,
    2040: 22.17,
}

BASE_EXPECTANCY   = 20.64   #   fixed in the Act
BASE_AGE          = 67.0    # → statutory AOW age for calendar-year 2025
TREND_LE_PER_YEAR = 0.1    #   long-term CBS trend (≈ +11 days / year)


# ───────────────────────────────────────────────────────────────────────
#  Build a calendar-year → (age, is_estimate) table.
#  Caches the result so we do the math only once per server run.
# ───────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def _age_schedule(upto_year: int = 2150) -> dict[int, tuple[float, bool]]:
    ages: dict[int, tuple[float, bool]] = {2025: (BASE_AGE, False)}
    life_exp = _LIFE_EXP_AT_65.copy()

    last_official_year = max(life_exp)
    last_official_le   = life_exp[last_official_year]

    for year in range(2026, upto_year + 1):
        prev_age, _ = ages[year - 1]

        # Obtain life expectancy value
        if year in life_exp:
            le = life_exp[year]
            is_estimate = False
        else:
            # Extrapolate linearly from last official point
            years_after_last = year - last_official_year
            le = last_official_le + TREND_LE_PER_YEAR * years_after_last
            is_estimate = True

        # Formula from AOW art. 7a
        V = (2 / 3) * (le - BASE_EXPECTANCY) - (prev_age - 67)
        delta = 0.25 if V >= 0.25 else 0.0          # +3 months step if warranted

        age_float = round(prev_age + delta, 2)      # keep two decimals ≈ months
        ages[year] = (age_float, is_estimate or delta == 0.25 and is_estimate)

    return ages


# ───────────────────────────────────────────────────────────────────────
#  Public helpers
# ───────────────────────────────────────────────────────────────────────
def retirement_age(birth: date) -> RetirementResult:
    """
    Returns statutory AOW age for a person *born on `birth`*.

    • Exact (estimated=False) if CBS projection for retirement year exists.
    • Estimated=True when relying on extrapolated life-expectancy figures.
    """
    if birth.year < 1900:
        raise UnknownRetirementAge("Geboortejaren voor 1900 worden niet ondersteund.")
    if birth.year > 2100:
        raise UnknownRetirementAge("Geboortejaren na 2100 worden niet ondersteund.")
    if birth.year < 1953:
        return RetirementResult(65, 0, estimated=True)

    schedule = _age_schedule()

    # Scan through the calendar years in which retirement could fall.
    for year, (age_float, est_flag) in schedule.items():
        yrs  = int(age_float)
        mos  = round((age_float - yrs) * 12)
        try:
            date_at_age = birth + relativedelta(years=yrs, months=mos)
        except ValueError:
            raise UnknownRetirementAge("Pensioendatum overschrijdt maximum ondersteunde jaar.")
        if date_at_age.year == year:
            return RetirementResult(yrs, mos, est_flag)

    # Even beyond 2150 we very rarely end up here, but if so keep extrapolating
    # year-by-year until we hit the candidate year.
    current_year = max(schedule) + 1
    current_age, _ = schedule[max(schedule)]
    while True:
        current_age = round(current_age + 0.25, 2)   # assume a rise every year
        yrs, mos = int(current_age), round((current_age - int(current_age)) * 12)
        date_at_age = birth + relativedelta(years=yrs, months=mos)
        if date_at_age.year == current_year:
            return RetirementResult(yrs, mos, True)
        current_year += 1


def retirement_date(birth: date) -> tuple[date, bool]:
    r = retirement_age(birth)
    return birth + relativedelta(years=r.years, months=r.months), r.estimated


def time_left(birth: date, today: date | None = None) -> tuple[relativedelta, bool]:
    if today is None:
        today = date.today()
    r_date, est = retirement_date(birth)
    return relativedelta(r_date, today), est


def working_time_left(
    birth: date,
    today: date | None = None,
    vacation_days_per_year: int = 25,
    public_holidays_per_year: int = 11,
) -> dict[str, int]:
    if today is None:
        today = date.today()

    # Get retirement date from your existing logic
    r_date, _ = retirement_date(birth)

    # 1. Count total weekdays (Mon–Fri) between today and retirement
    total_days = (r_date - today).days
    total_weekdays = sum(
        1 for i in range(total_days)
        if (today + relativedelta(days=i)).weekday() < 5
    )

    # 2. Estimate how many years (fractional) are left
    delta = relativedelta(r_date, today)
    approx_years = delta.years + (delta.months / 12) + (delta.days / 365.25)

    estimated_vacation_days = round(vacation_days_per_year * approx_years)
    estimated_holidays = round(public_holidays_per_year * approx_years)

    # 3. Calculate effective working days and hours
    effective_working_days = max(
        total_weekdays - estimated_vacation_days - estimated_holidays,
        0
    )
    total_work_hours = effective_working_days * 8

    # 4. Normalize to work years, months, weeks, days, hours
    work_years = total_work_hours // 2080
    work_months = total_work_hours // 173
    work_weeks = total_work_hours // 40
    work_days = total_work_hours // 8

    return {
        "work_years": int(work_years),
        "work_months": int(work_months),
        "work_weeks": int(work_weeks),
        "work_days": int(work_days),
        "work_hours": int(total_work_hours),
    }
