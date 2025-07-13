from datetime import date, datetime
from django.shortcuts import render
from .forms import BirthDateForm
from .calc import (
    retirement_age,
    retirement_date,
    time_left,
    working_time_left,
)


def index(request):
    result = error = warning = None
    work_stats = None
    can_retire = None

    if request.method == "POST":
        form = BirthDateForm(request.POST)
        if form.is_valid():
            raw_input = form.cleaned_data["birth_date"]

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
                    "ret_date": r_date.strftime("%d %b %Y"),
                    "left": (
                        f"{left.years} year{'s' if left.years != 1 else ''}, "
                        f"{left.months} month{'s' if left.months != 1 else ''}, "
                        f"{left.days} day{'s' if left.days != 1 else ''}"
                    ),
                    "work_time": work_stats,
                }

                if r_age.estimated or is_est1 or is_est2:
                    warning = (
                        "The AOW age shown is an estimate based on projected "
                        "life-expectancy figures (CBS projections beyond 2040)."
                    )

            except ValueError:
                error = "Please enter a valid date in dd-mm-yyyy format (e.g. 10-05-1995)."
            except Exception as exc:
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
