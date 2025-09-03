import pandas as pd
import random
import re

random.seed(42)

categories = [
    "Restaurants",
    "Bars",
    "Grocery",
    "Transport",
    "Shopping",
    "Entertainment",
    "Coffee",
    "Utilities",
    "Rent",
    "Health",
    "Travel",
    "P2P",
    "Fees",
    "Gas",
    "Other",
]

# Base merchant seeds per category
seeds = {
    "Restaurants": [
        "CHIPOTLE", "MCDONALD'S", "SUBWAY", "TACO BELL", "PANERA BREAD",
        "SHAKE SHACK", "NOODLES & CO", "CHILI'S", "DOMINO'S PIZZA", "PANDA EXPRESS",
        "OLIVE GARDEN", "CHEESECAKE FACTORY", "SWEETGREEN", "WINGSTOP", "IHOP",
        "DENNY'S", "P.F. CHANG'S", "RED LOBSTER", "BUFFALO WILD WINGS", "APPLEBEE'S",
        "RAISING CANE'S", "JERSEY MIKE'S", "FIVE GUYS", "CULVER'S", "PORTILLO'S",
        "ZAXBY'S", "QDOBA", "JACK IN THE BOX", "IN-N-OUT", "WHATABURGER",
        "SONIC DRIVE-IN", "WHITE CASTLE", "CHECKERS", "HARDEE'S", "BOJANGLES",
        "EL POLLO LOCO", "WENDY'S", "ARBY'S"
    ],
    "Bars": [
        "THE LOCAL PUB", "DIVE BAR", "THE ALEHOUSE", "WHISKEY BAR", "HAPPY HOUR LOUNGE",
        "IRISH PUB", "COCKTAIL CLUB", "ROOFTOP BAR", "BREWHOUSE", "SPORTS BAR",
        "SPEAKEASY", "WINE BAR", "BEER GARDEN", "TAPROOM", "CIDER HOUSE",
        "YARD HOUSE", "BUFFALO WILD WINGS BAR", "CHILI'S BAR", "APPLEBEE'S BAR",
        "BREWER'S TAPROOM", "MICROBREWERY", "TAPHOUSE", "DISTILLERY BAR", "BARCADE"
    ],
    "Grocery": [
        "SAFEWAY", "TRADER JOE'S", "WHOLE FOODS", "KROGER", "RALPHS",
        "GELSON'S", "SPROUTS", "ALDI", "FOOD 4 LESS", "COSTCO",
        "FRESH MARKET", "VONS", "H-E-B", "PAVILIONS", "FOOD LION",
        "GIANT FOOD", "STOP & SHOP", "SHOPRITE", "PUBLIX", "WINCO",
        "GIANT EAGLE", "MEIJER", "WEGMANS", "HARRIS TEETER", "KING SOOPERS",
        "FRED MEYER", "ACME MARKETS", "MARKET BASKET", "SAVE MART", "NOB HILL FOODS"
    ],
    "Transport": [
        "UBER TRIP", "LYFT RIDE", "BART CLIPPER", "MUNI METRO", "AMTRAK",
        "CALTRAIN", "GREYHOUND", "MEGABUS", "SCOOTER RENTAL", "BIRD SCOOTERS",
        "LIME BIKE", "PARKING METER", "CITY PARKING", "TOLL BRIDGE", "AIRPORT SHUTTLE",
        "ZIPCAR", "ENTERPRISE RENTAL", "HERTZ", "AVIS RENTAL", "BUDGET RENTAL",
        "DELTA SHUTTLE", "UBERPOOL", "LYFT XL", "TAXI SERVICE"
    ],
    "Shopping": [
        "AMAZON", "TARGET", "WALMART", "BEST BUY", "IKEA",
        "ETSY", "EBAY", "NIKE STORE", "APPLE STORE", "H&M",
        "ZARA", "UNIQLO", "NORDSTROM", "MACY'S", "BATH & BODY WORKS",
        "SEPHORA", "ULTA", "KOHL'S", "TJ MAXX", "MARSHALLS",
        "HOME DEPOT", "LOWE'S", "OFFICE DEPOT", "STAPLES", "BARNES & NOBLE",
        "GAMESTOP", "COSTCO WHOLESALE", "SAM'S CLUB"
    ],
    "Entertainment": [
        "NETFLIX", "SPOTIFY", "HULU", "DISNEY+", "PARAMOUNT+",
        "AMC THEATRES", "REGAL CINEMAS", "STEAM GAMES", "PLAYSTATION STORE", "XBOX LIVE",
        "PEACOCK", "TICKETMASTER", "LIVE NATION", "BANDCAMP", "PATREON",
        "YOUTUBE PREMIUM", "SIRIUSXM", "AUDIBLE", "CRUNCHYROLL", "FUNIMATION",
        "NFL GAMEPASS", "NBA LEAGUE PASS", "FANDANGO"
    ],
    "Coffee": [
        "STARBUCKS", "PEET'S COFFEE", "BLUE BOTTLE", "PHILZ COFFEE", "DUTCH BROS",
        "DUNKIN", "STUMPTOWN", "COFFEE BEAN & TEA LEAF", "LAVAZZA CAFE", "TIM HORTONS",
        "INTELLIGENTSIA", "LA COLOMBE", "CAFE NERO", "SEATTLE'S BEST", "GLORIA JEAN'S",
        "BIGGBY COFFEE", "CARIBOU COFFEE", "JAVAHOUSE", "SECOND CUP", "COFFEE REPUBLIC"
    ],
    "Utilities": [
        "PG&E", "COMCAST", "XFINITY", "AT&T INTERNET", "T-MOBILE", "VERIZON",
        "WATER BILL", "CITY GARBAGE", "ELECTRIC CO-OP", "GAS COMPANY", "SMUD ENERGY",
        "SPECTRUM", "DIRECTV", "ADT SECURITY", "SONIC INTERNET", "WOW INTERNET",
        "FRONTIER COMMUNICATIONS", "CINCINNATI BELL", "COX COMMUNICATIONS", "METRONET", "AT&T"
    ],
    "Rent": [
        "RENT PAYMENT PORTAL", "APARTMENT RENT", "PROPERTY MANAGEMENT", "LANDLORD TRANSFER", "RENTCAFE",
        "ZILLOW RENT", "AVAIL.CO", "PAYLEASE", "TENANT WEB", "REALPAGE PAYMENTS",
        "BUILDINGLINK", "YARDI RENT", "APARTMENTS LLC", "LEASE DEPOSIT", "ONLINE RENT PAYMENT"
    ],
    "Health": [
        "CVS PHARMACY", "WALGREENS", "KAISER", "DENTAL CLINIC", "OPTOMETRY CENTER",
        "URGENT CARE", "RITE AID", "LABCORP", "QUEST DIAGNOSTICS", "GYM MEMBERSHIP",
        "PHYSICAL THERAPY", "ORTHO CLINIC", "PRIMARY CARE", "DERMATOLOGY", "MENTAL HEALTH",
        "WELLNESS CENTER", "CHIROPRACTOR", "HOSPITAL BILL", "EMERGENCY ROOM", "CANCER CENTER"
    ],
    "Travel": [
        "UNITED AIRLINES", "DELTA AIR LINES", "AMERICAN AIRLINES", "SOUTHWEST", "JETBLUE",
        "ALASKA AIR", "SPIRIT AIRLINES", "FRONTIER AIRLINES", "AIRBNB", "BOOKING.COM",
        "HOTELS.COM", "MARRIOTT", "HILTON", "EXPEDIA", "TSA PRECHECK",
        "UBER AIRPORT", "LYFT AIRPORT", "AIRPORT PARKING", "DELTA VACATIONS", "PRICELINE"
    ],
    "P2P": [
        "VENMO", "ZELLE", "CASH APP", "REVOLUT", "PAYPAL FRIENDS",
        "APPLE CASH", "GOOGLE PAY", "ZELLE REQUEST", "VENMO REQUEST", "PAYPAL TRANSFER",
        "SQUARE CASH", "CHIME TRANSFER", "WISE TRANSFER", "REMITLY", "STRIPE PAYOUT"
    ],
    "Fees": [
        "BANK FEE", "OVERDRAFT FEE", "MONTHLY SERVICE FEE", "FOREIGN TRANSACTION FEE", "ATM FEE",
        "LATE FEE", "CARD REPLACEMENT FEE", "WIRE FEE", "MAINTENANCE FEE", "NSF FEE",
        "ANNUAL FEE", "CASH ADVANCE FEE", "TRANSFER FEE", "STATEMENT FEE", "SERVICE CHARGE"
    ],
    "Gas": [
        "SHELL", "CHEVRON", "BP", "ARCO", "EXXONMOBIL",
        "VALERO", "CIRCLE K", "COSTCO FUEL", "SPEEDWAY", "PHILLIPS 66",
        "MOBIL", "SUNOCO", "76 STATION", "TEXACO", "GETTY",
        "ESSO", "GULF OIL", "HOLIDAY STATION", "EXXONMOBIL", "EXXON", "GAS BUDDY"
    ],
    "Other": [
        "MISC CHARGE", "GENERAL MERCHANT", "LOCAL MARKET", "STREET VENDOR", "COMMUNITY CENTER",
        "DONATION", "POST OFFICE", "HARDWARE STORE", "HOME IMPROVEMENT", "LAUNDROMAT",
        "PET STORE", "CAR WASH", "DRY CLEANING", "THRIFT STORE", "FARMERS MARKET",
        "DOLLAR TREE", "DOLLAR GENERAL", "FAMILY DOLLAR", "BIG LOTS", "GOODWILL",
        "SALVATION ARMY", "ACE HARDWARE", "TRUE VALUE", "HARBOR FREIGHT"
    ],
}


cities = ["BERKELEY CA", "OAKLAND CA", "SAN JOSE CA", "SAN FRANCISCO CA", "LOS ANGELES CA", "SEATTLE WA", "AUSTIN TX", "NEW YORK NY"]
prefixes = [
    "POS {num} ", "AUTH {num} ", "CARD {num} ", "PURCHASE ", "PAYMENT ", "WEB {num} ",
    "", "", ""
]
suffixes = [
    "", "", "", " #{num}", " - {city}", " *{num}", " /ONLINE", " STORE {num}", " {city}"
]

def synthesize(desc):
    num = random.randint(1000, 9999)
    city = random.choice(cities)
    pre = random.choice(prefixes).format(num=num)
    suf = random.choice(suffixes).format(num=num, city=city)
    return f"{pre}{desc}{suf}".strip()

rows = []
per_cat = 1000  # ~24 examples per category -> 24 * 15 = 360 rows
for cat in categories:
    options = seeds[cat]
    for _ in range(per_cat):
        desc = synthesize(random.choice(options))
        rows.append({"description": desc, "category": cat})

df = pd.DataFrame(rows)
# Shuffle rows
df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

csv_path = "./training_data/category_training_data.csv"
df.to_csv(csv_path, index=False)
