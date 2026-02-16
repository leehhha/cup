"""Curated gift ideas database, categorized for easy matching."""

# Each gift has: name, category tags, effort_level (1-3, 1=easiest), gift_type
# price: estimated price range string
# buy_query: (optional) concise search term for Amazon; defaults to name if omitted
# buy_channel / buy_url: (optional) override retailer; defaults to Amazon search
# All gifts are designed to be low-effort, purchasable, or easy to arrange.

MONTHLY_GIFTS = [
    # Flowers & Plants
    {"name": "Fresh flower bouquet from a local florist", "tags": ["flowers", "romantic", "classic"], "effort": 1,
     "price": "$15-30", "buy_query": "fresh flower bouquet"},
    {"name": "A potted succulent or small plant", "tags": ["plants", "home", "lasting"], "effort": 1,
     "price": "$10-20", "buy_query": "potted succulent gift"},
    {"name": "Dried flower arrangement", "tags": ["flowers", "home", "decor"], "effort": 1,
     "price": "$15-30", "buy_query": "dried flower arrangement", "buy_channel": "Etsy",
     "buy_url": "https://www.etsy.com/search?q=dried+flower+arrangement"},

    # Food & Drink
    {"name": "Box of artisan chocolates", "tags": ["chocolate", "food", "treats"], "effort": 1,
     "price": "$15-30", "buy_query": "artisan chocolate gift box"},
    {"name": "Her favorite coffee or tea blend", "tags": ["coffee", "tea", "daily"], "effort": 1,
     "price": "$10-20", "buy_query": "gourmet coffee gift"},
    {"name": "A bottle of her favorite wine", "tags": ["wine", "drinks", "relaxation"], "effort": 1,
     "price": "$15-35", "buy_query": "wine gift"},
    {"name": "Gourmet cookies or pastries from a bakery", "tags": ["food", "treats", "bakery"], "effort": 1,
     "price": "$15-30", "buy_query": "gourmet cookies gift box"},
    {"name": "A specialty food item she's mentioned wanting to try", "tags": ["food", "adventurous", "thoughtful"], "effort": 1,
     "price": "$10-25", "buy_query": "specialty food gift"},
    {"name": "Fruit basket or seasonal fruit box", "tags": ["food", "healthy", "fresh"], "effort": 1,
     "price": "$25-45", "buy_query": "fruit basket gift"},
    {"name": "Fancy hot sauce or condiment set", "tags": ["food", "cooking", "adventurous"], "effort": 1,
     "price": "$15-30", "buy_query": "hot sauce gift set"},

    # Self-Care & Beauty
    {"name": "Luxury bath bomb set", "tags": ["self_care", "bath", "relaxation"], "effort": 1,
     "price": "$12-25", "buy_query": "luxury bath bomb gift set"},
    {"name": "High-quality hand cream or lotion", "tags": ["self_care", "skincare", "daily"], "effort": 1,
     "price": "$10-25", "buy_query": "luxury hand cream gift"},
    {"name": "Scented candle in her favorite fragrance", "tags": ["candles", "home", "relaxation"], "effort": 1,
     "price": "$15-30", "buy_query": "scented candle gift"},
    {"name": "Face mask or skincare sheet masks", "tags": ["self_care", "skincare", "pampering"], "effort": 1,
     "price": "$10-20", "buy_query": "face mask skincare gift set"},
    {"name": "Essential oil roller or aromatherapy set", "tags": ["self_care", "wellness", "relaxation"], "effort": 1,
     "price": "$12-25", "buy_query": "essential oil aromatherapy gift set"},
    {"name": "Lip balm or lipstick in a shade she loves", "tags": ["beauty", "makeup", "daily"], "effort": 1,
     "price": "$8-20", "buy_query": "lip balm gift set"},
    {"name": "Nail polish in a new color", "tags": ["beauty", "nails", "fun"], "effort": 1,
     "price": "$8-15", "buy_query": "nail polish gift set"},

    # Accessories & Small Items
    {"name": "A cute pair of socks or cozy slippers", "tags": ["clothing", "cozy", "comfort"], "effort": 1,
     "price": "$10-25", "buy_query": "cozy slippers women gift"},
    {"name": "Hair accessories (clips, scrunchies, headband)", "tags": ["accessories", "fashion", "daily"], "effort": 1,
     "price": "$8-18", "buy_query": "hair accessories gift set women"},
    {"name": "A small piece of costume jewelry", "tags": ["jewelry", "fashion", "accessories"], "effort": 1,
     "price": "$12-30", "buy_query": "costume jewelry gift women"},
    {"name": "Keychain or bag charm she'd like", "tags": ["accessories", "thoughtful", "daily"], "effort": 1,
     "price": "$8-20", "buy_query": "cute keychain bag charm women"},
    {"name": "Phone case in a design she'd love", "tags": ["tech", "accessories", "daily"], "effort": 1,
     "price": "$10-25", "buy_query": "cute phone case women"},

    # Books & Entertainment
    {"name": "A book by an author she loves", "tags": ["books", "reading", "entertainment"], "effort": 1,
     "price": "$10-20", "buy_query": "bestseller book gift"},
    {"name": "Magazine subscription issue", "tags": ["reading", "interests", "entertainment"], "effort": 1,
     "price": "$5-15", "buy_query": "magazine subscription gift"},
    {"name": "Audiobook credit or gift card", "tags": ["books", "reading", "digital"], "effort": 1,
     "price": "$15-15", "buy_query": "Audible gift card"},

    # Stationery & Home
    {"name": "A beautiful journal or notebook", "tags": ["stationery", "writing", "creative"], "effort": 1,
     "price": "$10-20", "buy_query": "beautiful journal notebook gift"},
    {"name": "Cute pens or markers set", "tags": ["stationery", "creative", "fun"], "effort": 1,
     "price": "$8-18", "buy_query": "cute pen set gift"},
    {"name": "A cozy throw blanket", "tags": ["home", "cozy", "comfort"], "effort": 1,
     "price": "$20-40", "buy_query": "cozy throw blanket gift"},
    {"name": "Decorative mug with a sweet message", "tags": ["home", "daily", "thoughtful"], "effort": 1,
     "price": "$10-20", "buy_query": "cute mug gift women"},

    # Experiences (small)
    {"name": "Her favorite takeout meal delivered", "tags": ["food", "experiences", "thoughtful"], "effort": 1,
     "price": "$20-40", "buy_query": "DoorDash gift card"},
    {"name": "A handwritten love note with a small treat", "tags": ["romantic", "sentimental", "personal"], "effort": 2,
     "price": "$5-15", "buy_query": "greeting card romantic"},
    {"name": "Playlist of songs that remind you of her", "tags": ["music", "romantic", "digital", "personal"], "effort": 2,
     "price": "Free", "buy_query": "Spotify gift card"},
    {"name": "Breakfast in bed (order from a restaurant)", "tags": ["food", "romantic", "experiences"], "effort": 1,
     "price": "$15-30", "buy_query": "Uber Eats gift card"},
]

QUARTERLY_GIFTS = [
    # Experiences
    {"name": "Spa day or massage gift certificate", "tags": ["self_care", "experiences", "pampering", "relaxation"], "effort": 1,
     "price": "$60-120", "buy_query": "spa massage gift certificate"},
    {"name": "Dinner reservation at a restaurant she's wanted to try", "tags": ["food", "experiences", "dining", "romantic"], "effort": 1,
     "price": "$50-120", "buy_query": "restaurant gift card"},
    {"name": "Concert or show tickets", "tags": ["music", "entertainment", "experiences", "date_night"], "effort": 1,
     "price": "$50-150", "buy_query": "concert tickets gift card"},
    {"name": "Cooking class for two", "tags": ["food", "experiences", "cooking", "date_night"], "effort": 1,
     "price": "$60-100", "buy_query": "couples cooking class gift"},
    {"name": "Wine or cocktail tasting experience", "tags": ["wine", "drinks", "experiences", "date_night"], "effort": 1,
     "price": "$40-80", "buy_query": "wine tasting experience gift"},
    {"name": "Museum or art gallery membership", "tags": ["art", "culture", "experiences", "intellectual"], "effort": 1,
     "price": "$50-100", "buy_query": "museum membership gift"},
    {"name": "Weekend brunch at a fancy spot", "tags": ["food", "experiences", "dining"], "effort": 1,
     "price": "$40-80", "buy_query": "restaurant gift card"},
    {"name": "Pottery or art class for two", "tags": ["creative", "experiences", "art", "date_night"], "effort": 1,
     "price": "$50-90", "buy_query": "pottery class couples gift"},
    {"name": "Movie night kit (streaming rental, gourmet popcorn, blanket)", "tags": ["entertainment", "cozy", "date_night"], "effort": 1,
     "price": "$30-50", "buy_query": "movie night gift basket"},
    {"name": "Botanical garden or zoo visit", "tags": ["nature", "experiences", "outdoors"], "effort": 1,
     "price": "$30-60", "buy_query": "botanical garden tickets gift"},
    {"name": "Escape room experience", "tags": ["experiences", "fun", "date_night", "adventurous"], "effort": 1,
     "price": "$30-60", "buy_query": "escape room gift card"},
    {"name": "Photo shoot session (couples or solo)", "tags": ["experiences", "romantic", "sentimental"], "effort": 1,
     "price": "$100-250", "buy_query": "couples photo shoot gift certificate"},

    # Bigger Items
    {"name": "Jewelry piece she's had her eye on", "tags": ["jewelry", "fashion", "lasting"], "effort": 1,
     "price": "$40-150", "buy_query": "women jewelry gift"},
    {"name": "Luxury skincare product or set", "tags": ["self_care", "skincare", "beauty", "pampering"], "effort": 1,
     "price": "$40-80", "buy_query": "luxury skincare gift set women"},
    {"name": "Designer accessory (wallet, scarf, sunglasses)", "tags": ["fashion", "accessories", "lasting"], "effort": 1,
     "price": "$50-150", "buy_query": "designer scarf women gift"},
    {"name": "Perfume or fragrance she loves", "tags": ["beauty", "fragrance", "lasting"], "effort": 1,
     "price": "$40-100", "buy_query": "women perfume gift set"},
    {"name": "Subscription box (beauty, books, snacks) - 3 months", "tags": ["subscription", "recurring", "surprise"], "effort": 1,
     "price": "$45-90", "buy_query": "subscription box gift women"},
    {"name": "Weighted blanket or luxury bedding item", "tags": ["home", "comfort", "cozy", "lasting"], "effort": 1,
     "price": "$40-80", "buy_query": "weighted blanket gift"},
    {"name": "Instant camera (like Fuji Instax)", "tags": ["tech", "creative", "fun", "lasting"], "effort": 1,
     "price": "$60-80", "buy_query": "Fujifilm Instax Mini camera"},
    {"name": "Kindle or e-reader loaded with books", "tags": ["books", "reading", "tech", "lasting"], "effort": 1,
     "price": "$100-150", "buy_query": "Kindle Paperwhite"},
    {"name": "Bluetooth speaker for the bath/shower", "tags": ["tech", "music", "relaxation"], "effort": 1,
     "price": "$20-50", "buy_query": "waterproof bluetooth shower speaker"},
    {"name": "Silk pillowcase or sleep mask set", "tags": ["self_care", "home", "comfort", "luxury"], "effort": 1,
     "price": "$20-50", "buy_query": "silk pillowcase sleep mask set"},
    {"name": "Personalized photo book (use an online service)", "tags": ["sentimental", "romantic", "personal"], "effort": 2,
     "price": "$30-60", "buy_query": "personalized photo book", "buy_channel": "Shutterfly",
     "buy_url": "https://www.shutterfly.com/photo-books"},
    {"name": "Custom piece of art or print she'd love", "tags": ["art", "home", "decor", "lasting"], "effort": 1,
     "price": "$30-80", "buy_query": "custom art print", "buy_channel": "Etsy",
     "buy_url": "https://www.etsy.com/search?q=custom+art+print"},

    # Surprise Gestures
    {"name": "Plan a surprise date night (restaurant + activity)", "tags": ["romantic", "experiences", "date_night", "surprise"], "effort": 2,
     "price": "$60-150", "buy_query": "date night gift card"},
    {"name": "Weekend getaway to a nearby town", "tags": ["travel", "experiences", "romantic", "adventure"], "effort": 2,
     "price": "$150-400", "buy_query": "weekend getaway gift card"},
    {"name": "Flower delivery subscription (weekly for a month)", "tags": ["flowers", "subscription", "romantic"], "effort": 1,
     "price": "$40-80", "buy_query": "flower delivery subscription"},
    {"name": "Star or constellation map of a meaningful date", "tags": ["sentimental", "romantic", "personal", "art"], "effort": 1,
     "price": "$25-50", "buy_query": "star map custom poster", "buy_channel": "Etsy",
     "buy_url": "https://www.etsy.com/search?q=custom+star+map+poster"},
]

# Categories used for matching answers to gift tags
CATEGORY_TAG_MAP = {
    "love_language": {
        "Words of Affirmation": ["romantic", "sentimental", "personal"],
        "Acts of Service": ["thoughtful", "daily", "comfort"],
        "Receiving Gifts": ["lasting", "luxury", "surprise"],
        "Quality Time": ["experiences", "date_night", "romantic"],
        "Physical Touch": ["cozy", "comfort", "relaxation"],
    },
    "interests": {
        "Reading": ["books", "reading"],
        "Cooking": ["food", "cooking"],
        "Fitness/Wellness": ["self_care", "wellness"],
        "Art/Creative": ["art", "creative"],
        "Music": ["music", "entertainment"],
        "Nature/Outdoors": ["nature", "outdoors", "plants"],
        "Fashion/Style": ["fashion", "accessories", "jewelry"],
        "Technology": ["tech", "digital"],
        "Travel": ["travel", "adventure", "adventurous"],
        "Home Decor": ["home", "decor"],
    },
    "self_care_pref": {
        "Spa/Massage": ["pampering", "relaxation", "self_care"],
        "Skincare": ["skincare", "beauty", "self_care"],
        "Bath Products": ["bath", "relaxation", "self_care"],
        "Aromatherapy": ["relaxation", "wellness"],
    },
    "food_pref": {
        "Chocolate": ["chocolate", "treats"],
        "Wine": ["wine", "drinks"],
        "Coffee": ["coffee", "daily"],
        "Tea": ["tea", "daily"],
        "Baked Goods": ["bakery", "treats"],
        "Healthy Snacks": ["healthy", "fresh"],
    },
}
