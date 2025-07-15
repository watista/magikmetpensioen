import logging
from datetime import date, datetime
from django.shortcuts import render
from .usage_tracker import increment_usage
from .forms import BirthDateForm
from .calc import (
    retirement_age,
    retirement_date,
    time_left,
    working_time_left,
)

logger = logging.getLogger('retirement_app')

def index(request):
    result = error = warning = None
    work_stats = None
    can_retire = None

    if request.method == "POST":
        form = BirthDateForm(request.POST)
        if form.is_valid():
            raw_input = form.cleaned_data["birth_date"]
            increment_usage(raw_input)
            logger.info(f"Form submitted with birthdate: {raw_input}")

            try:
                birth = datetime.strptime(raw_input, "%d-%m-%Y").date()

                # ── core calculations ────────────────────────────────────
                r_age = retirement_age(birth)
                r_date, is_est1 = retirement_date(birth)
                left, is_est2 = time_left(birth)
                work_stats = working_time_left(birth)
                can_retire = (left.years <= 0 and left.months <= 0 and left.days <= 0)

                # build result dict
                result = {
                    "ret_age": str(r_age),
                    "ret_date": r_date,
                    "left": (
                        f"{left.years} jaar{'' if left.years != 1 else ''}, "
                        f"{left.months} maand{'en' if left.months != 1 else ''}, "
                        f"{left.days} dag{'en' if left.days != 1 else ''}"
                    ),
                    "work_time": work_stats,
                }

                today = date.today()
                total_span = (r_date - birth).days
                elapsed = (today - birth).days

                if total_span > 0:
                    percent_done = min(100, int(100 * (elapsed / total_span)))
                else:
                    percent_done = 100
                result["progress_percent"] = percent_done

                if r_age.estimated or is_est1 or is_est2:
                    warning = "De AOW-leeftijd is een schatting op basis van de verwachte levensverwachting (CBS-prognoses na 2040)."

            except ValueError as ve:
                logger.warning(f"Invalid birthdate input: {raw_input} - {ve}")
                error = "Voer een geldige datum in dd-mm-jjj-formaat in (bijv. 10-05-1995)."
            except Exception as exc:
                logger.exception(f"Unexpected error occurred during form submission: {exc}")
                error = str(exc)
    else:
        form = BirthDateForm()

    # ── render ───────────────────────────────────────────────────────────
    return render(
        request,
        "index.html",
        {
            "form": form,
            "result": result,
            "error": error,
            "warning": warning,
            "can_retire": can_retire,
        },
    )

def over(request):
    return render(request, "over.html")
