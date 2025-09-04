from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import math
import pandas as pd
from datetime import date
from calendar import monthrange

def _monthly_rate(apr_pct: float) -> float:
    """Convert annual percent rate to effective monthly rate."""
    return (1.0 + apr_pct / 100.0) ** (1.0 / 12.0) - 1.0

@dataclass
class WealthInputs:
    # --- Assets (starting balances) ---
    real_estate: float = 0.0          # home + other properties (market value)
    checking: float = 0.0
    savings_hysa: float = 0.0         # HYSA balance
    retirement_invest: float = 0.0    # 401k/IRA/brokerage
    cars_value: float = 0.0
    other_assets: float = 0.0

    # --- Debts (starting balances, totals owed) ---
    real_estate_loans: float = 0.0    # mortgage total owed
    credit_card_debt: float = 0.0
    personal_loans: float = 0.0
    student_loans: float = 0.0
    car_loans: float = 0.0
    other_debt: float = 0.0

@dataclass
class Assumptions:
    # Annual growth / depreciation / interest (percent)
    real_estate_apr: float = 3.5       # appreciation
    hysa_apr: float = 2.0              # HYSA interest
    retirement_apr: float = 10.0       # stocks/bonds return
    cars_apr: float = -10.0            # depreciation (negative)
    other_assets_apr: float = 0.0      # usually 0

    mortgage_apr: float = 3.5
    cc_apr: float = 22.0               # credit card interest
    personal_apr: float = 12.0
    student_apr: float = 7.0
    car_apr: float = 9.0
    other_debt_apr: float = 0.0

@dataclass
class MonthlyFlows:
    # Contributions (added each month before growth on that bucket)
    contrib_checking: float = 0.0
    contrib_hysa: float = 0.0
    contrib_retirement: float = 0.0

    # Optional one-time rebalancing into investments from checking (kept simple: monthly)
    move_checking_to_invest: float = 0.0  # e.g., auto-invest

    # Debt payments (subtracted after interest; capped at outstanding)
    pay_mortgage: float = 0.0
    pay_cc: float = 0.0
    pay_personal: float = 0.0
    pay_student: float = 0.0
    pay_car: float = 0.0
    pay_other_debt: float = 0.0

def simulate_future_wealth(
    start: WealthInputs,
    months: int = 60,
    assumptions: Assumptions = Assumptions(),
    flows: MonthlyFlows = MonthlyFlows(),
    start_year_month: Optional[tuple[int, int]] = None,  # (YYYY, MM)
) -> pd.DataFrame:
    """
    Project assets, liabilities, and net worth by month.

    • Assets compound monthly: real estate, HYSA, retirement; cars depreciate; other assets as configured.
    • Debts accrue interest monthly, then payments are applied and capped at zero.
    • Contributions are added before growth each month; payments are taken after interest.
    • Returns a DataFrame with one row per month (including month 0 as the starting point).

    Parameters
    ----------
    start : WealthInputs
        Starting balances for assets and debts.
    months : int
        Projection horizon in months (default 60).
    assumptions : Assumptions
        APRs used for compounding/depreciation/interest.
    flows : MonthlyFlows
        Monthly contributions and payments.
    start_year_month : (YYYY, MM) optional
        If provided, the first row will use this calendar month; otherwise uses current month.

    Returns
    -------
    pd.DataFrame with columns:
        month, assets_total, liabilities_total, net_worth,
        real_estate, checking, savings_hysa, retirement_invest, cars_value, other_assets,
        real_estate_loans, credit_card_debt, personal_loans, student_loans, car_loans, other_debt
    """
    # Copy balances
    re_val   = float(start.real_estate)
    chk      = float(start.checking)
    hysa     = float(start.savings_hysa)
    invest   = float(start.retirement_invest)
    cars     = float(start.cars_value)
    other_a  = float(start.other_assets)

    mort     = float(start.real_estate_loans)
    cc       = float(start.credit_card_debt)
    pers     = float(start.personal_loans)
    stud     = float(start.student_loans)
    carl     = float(start.car_loans)
    other_d  = float(start.other_debt)

    # Monthly rates
    r_re     = _monthly_rate(assumptions.real_estate_apr)
    r_hysa   = _monthly_rate(assumptions.hysa_apr)
    r_inv    = _monthly_rate(assumptions.retirement_apr)
    r_cars   = _monthly_rate(assumptions.cars_apr)
    r_othera = _monthly_rate(assumptions.other_assets_apr)

    r_mort   = _monthly_rate(assumptions.mortgage_apr)
    r_cc     = _monthly_rate(assumptions.cc_apr)
    r_pers   = _monthly_rate(assumptions.personal_apr)
    r_stud   = _monthly_rate(assumptions.student_apr)
    r_carl   = _monthly_rate(assumptions.car_apr)
    r_otherd = _monthly_rate(assumptions.other_debt_apr)

    # Calendar start
    if start_year_month is None:
        from datetime import datetime
        y, m = datetime.today().year, datetime.today().month
    else:
        y, m = start_year_month

    rows: List[Dict] = []

    def record_row(year: int, month: int):
        assets_total = re_val + chk + hysa + invest + cars + other_a
        liabilities_total = mort + cc + pers + stud + carl + other_d
        rows.append({
            "month": f"{year:04d}-{month:02d}",
            "assets_total": round(assets_total, 2),
            "liabilities_total": round(liabilities_total, 2),
            "net_worth": round(assets_total - liabilities_total, 2),

            "real_estate": round(re_val, 2),
            "checking": round(chk, 2),
            "savings_hysa": round(hysa, 2),
            "retirement_invest": round(invest, 2),
            "cars_value": round(cars, 2),
            "other_assets": round(other_a, 2),

            "real_estate_loans": round(mort, 2),
            "credit_card_debt": round(cc, 2),
            "personal_loans": round(pers, 2),
            "student_loans": round(stud, 2),
            "car_loans": round(carl, 2),
            "other_debt": round(other_d, 2),
        })

    # Record starting month (month 0)
    record_row(y, m)

    # Iterate months
    for _ in range(months):
        # Advance month
        m += 1
        if m > 12:
            y += 1
            m = 1

        # ---- Contributions (before growth) ----
        chk += flows.contrib_checking
        hysa += flows.contrib_hysa
        invest += flows.contrib_retirement

        # Optional auto-move from checking to investments
        move_amt = min(flows.move_checking_to_invest, max(0.0, chk))
        chk -= move_amt
        invest += move_amt

        # ---- Asset growth / depreciation ----
        re_val *= (1.0 + r_re)
        hysa   *= (1.0 + r_hysa)
        invest *= (1.0 + r_inv)
        cars   *= (1.0 + r_cars)     # r_cars is negative for depreciation
        other_a*= (1.0 + r_othera)

        # Prevent tiny negative due to rounding
        cars = max(0.0, cars)

        # ---- Debt interest accrual ----
        mort *= (1.0 + r_mort)
        cc   *= (1.0 + r_cc)
        pers *= (1.0 + r_pers)
        stud *= (1.0 + r_stud)
        carl *= (1.0 + r_carl)
        other_d *= (1.0 + r_otherd)

        # ---- Payments (cap at outstanding) ----
        def pay(balance: float, payment: float) -> float:
            if balance <= 0.0 or payment <= 0.0:
                return balance
            return max(0.0, balance - payment)

        mort = pay(mort, flows.pay_mortgage)
        cc   = pay(cc, flows.pay_cc)
        pers = pay(pers, flows.pay_personal)
        stud = pay(stud, flows.pay_student)
        carl = pay(carl, flows.pay_car)
        other_d = pay(other_d, flows.pay_other_debt)

        # Record
        record_row(y, m)

    return pd.DataFrame(rows)
