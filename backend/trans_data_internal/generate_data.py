import csv, random, math
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict

# ----------------------------
# Config
# ----------------------------
RANDOM_SEED = 42
NUM_MONTHS_PAD = 7  # ~6 months window; we’ll compute from dates below
END_DATE = datetime.today().date()
START_DATE = END_DATE - timedelta(days=365)  # ~6+ months
OUT_PATH = Path("./trans_data_internal/sample_transactions_balanced.csv")

random.seed(RANDOM_SEED)

CATEGORIES = [
    "Groceries","Restaurants","Rent","Utilities","Entertainment",
    "Transportation","Shopping","Healthcare","Salary","Misc"
]

MERCHANTS = {
    "Groceries": ["Safeway","Trader Joe's","Whole Foods","Walmart","Costco"],
    "Restaurants": ["Starbucks","Chipotle","McDonald's","Olive Garden","Subway","Local Deli","Taco Truck"],
    "Rent": ["Landlord LLC","Property Mgmt Co"],
    "Utilities": ["PG&E","Comcast","AT&T","Water Utility"],
    "Entertainment": ["Netflix","Spotify","Hulu","Disney+"],
    "Transportation": ["Uber","Lyft","Shell Gas","Chevron","Exxon"],
    "Shopping": ["Amazon","Target","Best Buy","Ikea","Home Depot","Etsy"],
    "Healthcare": ["CVS Pharmacy","Walgreens","Kaiser"],
    "Salary": ["Company Payroll"],
    "Misc": ["Venmo","PayPal","Apple Cash"]
}

# Subscriptions (monthly with slight jitter; fixed amounts)
SUBSCRIPTIONS = [
    {"merchant": "Netflix",  "category": "Entertainment", "amount": -15.49, "dom": 7,  "jitter": 2},
    {"merchant": "Spotify",  "category": "Entertainment", "amount": -10.99, "dom": 15, "jitter": 2},
    {"merchant": "iCloud",   "category": "Entertainment", "amount": -2.99,  "dom": 22, "jitter": 1},
    {"merchant": "City Gym", "category": "Healthcare",    "amount": -39.99, "dom": 3,  "jitter": 2},
]

# Utility bills (monthly)
UTILITY_BILLS = [
    {"merchant":"PG&E",    "category":"Utilities", "dom": 5,  "rng": (60,190)},
    {"merchant":"Comcast", "category":"Utilities", "dom": 12, "rng": (60,120)},
    {"merchant":"AT&T",    "category":"Utilities", "dom": 25, "rng": (50,110)},
]

RENT_RANGE = (1500, 2600)        # monthly rent
GROCERY_RANGE = (25, 140)        # per trip
RESTAURANT_RANGE = (8, 35)
GAS_RANGE = (30, 85)
RIDE_RANGE = (8, 40)
SHOP_SMALL = (10, 120)
SHOP_BIG   = (150, 600)          # rare
HEALTHCARE_RANGE = (15, 180)
MISC_RANGE = (5, 120)

# Discretionary target as % of income after fixed (will sample this per month)
DISC_PCT_RANGE = (0.75, 0.90)    # spend 75–90% of income (leaves 10–25% net savings)

# ----------------------------
# Helpers
# ----------------------------
def month_iter(start_d: date, end_d: date):
    cur = date(start_d.year, start_d.month, 1)
    while cur <= end_d:
        yield cur
        # jump to next month 1st
        cur = (cur.replace(day=28) + timedelta(days=4)).replace(day=1)

def days_in_month(d: date) -> int:
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    return (nxt - d).days

def clamp_dom(year: int, month: int, dom: int) -> date:
    return date(year, month, min(dom, days_in_month(date(year, month, 1))))

def pick_pay_schedule(start_m: date, end_m: date):
    """Return list of paycheck dates within [start_m, end_m] across months.
       Either semi-monthly (1st/15th) or biweekly, but guarantee a paycheck within 7 days of START_DATE.
    """
    mode = random.choice(["semi-monthly","biweekly"])
    dates = []
    months = list(month_iter(start_m, end_m))
    if mode == "semi-monthly":
        for m0 in months:
            for dom in (1, 15):
                d = clamp_dom(m0.year, m0.month, dom)
                # shift weekends to next Monday
                if d.weekday() >= 5:
                    d = d + timedelta(days=(7 - d.weekday()))
                dates.append(d)
    else:
        # start biweekly no later than 7 days after START_DATE
        first = START_DATE + timedelta(days=random.randint(0, 7))
        pay = first
        while pay <= end_m:
            # shift weekends to Monday
            if pay.weekday() >= 5:
                pay = pay + timedelta(days=(7 - pay.weekday()))
            dates.append(pay)
            pay = pay + timedelta(days=14)

    # guarantee first income in first 7 days
    if all((abs((d - START_DATE).days) > 7 or d < START_DATE) for d in dates):
        forced = START_DATE + timedelta(days=random.randint(0, 7))
        if forced.weekday() >= 5:
            forced = forced + timedelta(days=(7 - forced.weekday()))
        dates.append(forced)

    return sorted(d for d in dates if START_DATE <= d <= END_DATE)

def add_tx(rows, d: date, desc: str, cat: str, amt: float, acct: str="Checking"):
    rows.append({
        "date": d.strftime("%Y-%m-%d"),
        "description": desc,
        "category": cat,
        "amount": round(amt, 2),
        "account": acct
    })

def rand_amount(lo, hi): return -round(random.uniform(lo, hi), 2)

# ----------------------------
# Build per-month plan
# ----------------------------
rows = []

# Income plan: per-month net income -> split across paychecks
pay_dates = pick_pay_schedule(START_DATE, END_DATE)
# Group pay dates by month
pay_by_month = defaultdict(list)
for d in pay_dates:
    pay_by_month[(d.year, d.month)].append(d)

# For each month in window, sample a net income target and split over pay dates
monthly_targets = {}  # (year,month) -> income_total
for m0 in month_iter(START_DATE, END_DATE):
    ym = (m0.year, m0.month)
    # Partial first/last months: scale income proportionally to days covered
    month_days = days_in_month(m0)
    covered_start = max(m0, START_DATE)
    covered_end = min((m0.replace(day=month_days)), END_DATE)
    covered_days = (covered_end - covered_start).days + 1
    coverage = max(0.3, covered_days / month_days)  # don't go too low
    base_income = random.uniform(3800, 5200) * coverage
    monthly_targets[ym] = base_income

# Emit paychecks (split the month target across paydates proportionally)
for ym, dates in pay_by_month.items():
    total = monthly_targets.get(ym, 0.0)
    if total <= 0 or not dates:
        continue
    # split roughly evenly with small noise
    parts = []
    remain = total
    for i, d in enumerate(dates):
        if i == len(dates) - 1:
            parts.append(remain)
        else:
            piece = total / len(dates) * random.uniform(0.9, 1.1)
            parts.append(piece)
            remain -= piece
    # ensure positive
    parts = [max(100.0, p) for p in parts]
    scale = total / sum(parts)
    parts = [p * scale for p in parts]

    for d, amt in zip(dates, parts):
        add_tx(rows, d, random.choice(MERCHANTS["Salary"]), "Salary", +abs(amt))

# Fixed monthly: Rent + Utilities + Subscriptions
for m0 in month_iter(START_DATE, END_DATE):
    ym = (m0.year, m0.month)

    # Rent on 1st–5th
    rent_dom = random.randint(1, 5)
    rent_date = clamp_dom(m0.year, m0.month, rent_dom)
    add_tx(rows, rent_date, random.choice(MERCHANTS["Rent"]), "Rent", -random.uniform(*RENT_RANGE))

    # Utilities
    for bill in UTILITY_BILLS:
        dom = max(1, min(28, bill["dom"] + random.randint(-2, 2)))
        bill_date = clamp_dom(m0.year, m0.month, dom)
        lo, hi = bill["rng"]
        add_tx(rows, bill_date, bill["merchant"], "Utilities", -random.uniform(lo, hi))

    # Subscriptions
    for sub in SUBSCRIPTIONS:
        dom = max(1, min(28, sub["dom"] + random.randint(-sub["jitter"], sub["jitter"])))
        sub_date = clamp_dom(m0.year, m0.month, dom)
        add_tx(rows, sub_date, sub["merchant"], sub["category"], sub["amount"])

# Discretionary budget per month = income * pct - fixed_costs
# First, compute fixed spend per month
def month_key(d: date): return (d.year, d.month)

income_by_m = defaultdict(float)
spend_fixed_by_m = defaultdict(float)
for r in rows:
    ym = tuple(map(int, r["date"].split("-")[:2]))
    if r["category"] == "Salary":
        income_by_m[ym] += r["amount"]
    elif r["category"] in ("Rent","Utilities","Entertainment","Healthcare"):
        # subscriptions are under Entertainment/Healthcare; treat as fixed-ish
        if r["amount"] < 0:
            spend_fixed_by_m[ym] += -r["amount"]

# Now generate discretionary transactions to hit target share without exceeding income
for m0 in month_iter(START_DATE, END_DATE):
    ym = (m0.year, m0.month)
    income = income_by_m.get(ym, 0.0)
    if income <= 0:
        continue
    # choose discretionary percentage this month
    disc_pct = random.uniform(*DISC_PCT_RANGE)
    fixed = spend_fixed_by_m.get(ym, 0.0)
    target_disc = max(0.0, income * disc_pct - fixed)

    # allocate across categories (weights)
    weights = {
        "Groceries": 0.32,
        "Restaurants": 0.22,
        "Transportation": 0.14,
        "Shopping": 0.16,
        "Healthcare": 0.06,  # additional discretionary (OTC, copays)
        "Misc": 0.10,
    }
    # normalize (just in case)
    wsum = sum(weights.values())
    weights = {k: v / wsum for k, v in weights.items()}

    # produce transactions until hitting each category bucket
    days_in_m = days_in_month(m0)
    start_day = max(m0, START_DATE)
    end_day = min(m0.replace(day=days_in_m), END_DATE)
    span_days = (end_day - start_day).days + 1

    for cat, pct in weights.items():
        bucket = target_disc * pct
        spent = 0.0
        tries = 0
        # keep sampling small realistic purchases until we roughly hit the bucket
        while spent < bucket * random.uniform(0.90, 1.05) and tries < 200:
            tries += 1
            # pick a random day in the covered part of this month
            day = start_day + timedelta(days=random.randint(0, max(0, span_days - 1)))
            if cat == "Groceries":
                amt = rand_amount(*GROCERY_RANGE)
                merchant = random.choice(MERCHANTS["Groceries"])
            elif cat == "Restaurants":
                amt = rand_amount(*RESTAURANT_RANGE)
                merchant = random.choice(MERCHANTS["Restaurants"])
            elif cat == "Transportation":
                if random.random() < 0.45:
                    amt = rand_amount(*GAS_RANGE); merchant = random.choice(["Shell Gas","Chevron","Exxon"])
                else:
                    amt = rand_amount(*RIDE_RANGE); merchant = random.choice(["Uber","Lyft"])
            elif cat == "Shopping":
                if random.random() < 0.07:  # occasional bigger cart
                    amt = rand_amount(*SHOP_BIG); merchant = random.choice(["Amazon","Target","Best Buy","Ikea","Home Depot"])
                else:
                    amt = rand_amount(*SHOP_SMALL); merchant = random.choice(MERCHANTS["Shopping"])
            elif cat == "Healthcare":
                amt = rand_amount(*HEALTHCARE_RANGE); merchant = random.choice(MERCHANTS["Healthcare"])
            else:
                amt = rand_amount(*MISC_RANGE); merchant = random.choice(MERCHANTS["Misc"])

            add_tx(rows, day, merchant, cat, amt)
            spent += -amt  # amt is negative
        # done category

# Shuffle and write
random.shuffle(rows)

with OUT_PATH.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date","description","category","amount","account"])
    writer.writeheader()
    writer.writerows(rows)

# Quick sanity print
total_income = sum(r["amount"] for r in rows if r["category"]=="Salary")
total_spend  = -sum(r["amount"] for r in rows if r["amount"]<0)
net = total_income - total_spend
print(f"✅ Wrote {len(rows)} rows → {OUT_PATH.resolve()}")
print(f"   Income: ${total_income:,.2f}  Spend: ${total_spend:,.2f}  Net: ${net:,.2f}")
