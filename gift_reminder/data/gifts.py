"""Curated gift ideas database, categorized for easy matching."""

# Each gift has: name, category tags, effort_level (1-3, 1=easiest), gift_type
# All gifts are designed to be low-effort, purchasable, or easy to arrange.

MONTHLY_GIFTS = [
    # Flowers & Plants
    {"name": "Fresh flower bouquet from a local florist", "tags": ["flowers", "romantic", "classic"], "effort": 1},
    {"name": "A potted succulent or small plant", "tags": ["plants", "home", "lasting"], "effort": 1},
    {"name": "Dried flower arrangement", "tags": ["flowers", "home", "decor"], "effort": 1},

    # Food & Drink
    {"name": "Box of artisan chocolates", "tags": ["chocolate", "food", "treats"], "effort": 1},
    {"name": "Her favorite coffee or tea blend", "tags": ["coffee", "tea", "daily"], "effort": 1},
    {"name": "A bottle of her favorite wine", "tags": ["wine", "drinks", "relaxation"], "effort": 1},
    {"name": "Gourmet cookies or pastries from a bakery", "tags": ["food", "treats", "bakery"], "effort": 1},
    {"name": "A specialty food item she's mentioned wanting to try", "tags": ["food", "adventurous", "thoughtful"], "effort": 1},
    {"name": "Fruit basket or seasonal fruit box", "tags": ["food", "healthy", "fresh"], "effort": 1},
    {"name": "Fancy hot sauce or condiment set", "tags": ["food", "cooking", "adventurous"], "effort": 1},

    # Self-Care & Beauty
    {"name": "Luxury bath bomb set", "tags": ["self_care", "bath", "relaxation"], "effort": 1},
    {"name": "High-quality hand cream or lotion", "tags": ["self_care", "skincare", "daily"], "effort": 1},
    {"name": "Scented candle in her favorite fragrance", "tags": ["candles", "home", "relaxation"], "effort": 1},
    {"name": "Face mask or skincare sheet masks", "tags": ["self_care", "skincare", "pampering"], "effort": 1},
    {"name": "Essential oil roller or aromatherapy set", "tags": ["self_care", "wellness", "relaxation"], "effort": 1},
    {"name": "Lip balm or lipstick in a shade she loves", "tags": ["beauty", "makeup", "daily"], "effort": 1},
    {"name": "Nail polish in a new color", "tags": ["beauty", "nails", "fun"], "effort": 1},

    # Accessories & Small Items
    {"name": "A cute pair of socks or cozy slippers", "tags": ["clothing", "cozy", "comfort"], "effort": 1},
    {"name": "Hair accessories (clips, scrunchies, headband)", "tags": ["accessories", "fashion", "daily"], "effort": 1},
    {"name": "A small piece of costume jewelry", "tags": ["jewelry", "fashion", "accessories"], "effort": 1},
    {"name": "Keychain or bag charm she'd like", "tags": ["accessories", "thoughtful", "daily"], "effort": 1},
    {"name": "Phone case in a design she'd love", "tags": ["tech", "accessories", "daily"], "effort": 1},

    # Books & Entertainment
    {"name": "A book by an author she loves", "tags": ["books", "reading", "entertainment"], "effort": 1},
    {"name": "Magazine subscription issue", "tags": ["reading", "interests", "entertainment"], "effort": 1},
    {"name": "Audiobook credit or gift card", "tags": ["books", "reading", "digital"], "effort": 1},

    # Stationery & Home
    {"name": "A beautiful journal or notebook", "tags": ["stationery", "writing", "creative"], "effort": 1},
    {"name": "Cute pens or markers set", "tags": ["stationery", "creative", "fun"], "effort": 1},
    {"name": "A cozy throw blanket", "tags": ["home", "cozy", "comfort"], "effort": 1},
    {"name": "Decorative mug with a sweet message", "tags": ["home", "daily", "thoughtful"], "effort": 1},

    # Experiences (small)
    {"name": "Her favorite takeout meal delivered", "tags": ["food", "experiences", "thoughtful"], "effort": 1},
    {"name": "A handwritten love note with a small treat", "tags": ["romantic", "sentimental", "personal"], "effort": 2},
    {"name": "Playlist of songs that remind you of her", "tags": ["music", "romantic", "digital", "personal"], "effort": 2},
    {"name": "Breakfast in bed (order from a restaurant)", "tags": ["food", "romantic", "experiences"], "effort": 1},
]

QUARTERLY_GIFTS = [
    # Experiences
    {"name": "Spa day or massage gift certificate", "tags": ["self_care", "experiences", "pampering", "relaxation"], "effort": 1},
    {"name": "Dinner reservation at a restaurant she's wanted to try", "tags": ["food", "experiences", "dining", "romantic"], "effort": 1},
    {"name": "Concert or show tickets", "tags": ["music", "entertainment", "experiences", "date_night"], "effort": 1},
    {"name": "Cooking class for two", "tags": ["food", "experiences", "cooking", "date_night"], "effort": 1},
    {"name": "Wine or cocktail tasting experience", "tags": ["wine", "drinks", "experiences", "date_night"], "effort": 1},
    {"name": "Museum or art gallery membership", "tags": ["art", "culture", "experiences", "intellectual"], "effort": 1},
    {"name": "Weekend brunch at a fancy spot", "tags": ["food", "experiences", "dining"], "effort": 1},
    {"name": "Pottery or art class for two", "tags": ["creative", "experiences", "art", "date_night"], "effort": 1},
    {"name": "Movie night kit (streaming rental, gourmet popcorn, blanket)", "tags": ["entertainment", "cozy", "date_night"], "effort": 1},
    {"name": "Botanical garden or zoo visit", "tags": ["nature", "experiences", "outdoors"], "effort": 1},
    {"name": "Escape room experience", "tags": ["experiences", "fun", "date_night", "adventurous"], "effort": 1},
    {"name": "Photo shoot session (couples or solo)", "tags": ["experiences", "romantic", "sentimental"], "effort": 1},

    # Bigger Items
    {"name": "Jewelry piece she's had her eye on", "tags": ["jewelry", "fashion", "lasting"], "effort": 1},
    {"name": "Luxury skincare product or set", "tags": ["self_care", "skincare", "beauty", "pampering"], "effort": 1},
    {"name": "Designer accessory (wallet, scarf, sunglasses)", "tags": ["fashion", "accessories", "lasting"], "effort": 1},
    {"name": "Perfume or fragrance she loves", "tags": ["beauty", "fragrance", "lasting"], "effort": 1},
    {"name": "Subscription box (beauty, books, snacks) - 3 months", "tags": ["subscription", "recurring", "surprise"], "effort": 1},
    {"name": "Weighted blanket or luxury bedding item", "tags": ["home", "comfort", "cozy", "lasting"], "effort": 1},
    {"name": "Instant camera (like Fuji Instax)", "tags": ["tech", "creative", "fun", "lasting"], "effort": 1},
    {"name": "Kindle or e-reader loaded with books", "tags": ["books", "reading", "tech", "lasting"], "effort": 1},
    {"name": "Bluetooth speaker for the bath/shower", "tags": ["tech", "music", "relaxation"], "effort": 1},
    {"name": "Silk pillowcase or sleep mask set", "tags": ["self_care", "home", "comfort", "luxury"], "effort": 1},
    {"name": "Personalized photo book (use an online service)", "tags": ["sentimental", "romantic", "personal"], "effort": 2},
    {"name": "Custom piece of art or print she'd love", "tags": ["art", "home", "decor", "lasting"], "effort": 1},

    # Surprise Gestures
    {"name": "Plan a surprise date night (restaurant + activity)", "tags": ["romantic", "experiences", "date_night", "surprise"], "effort": 2},
    {"name": "Weekend getaway to a nearby town", "tags": ["travel", "experiences", "romantic", "adventure"], "effort": 2},
    {"name": "Flower delivery subscription (weekly for a month)", "tags": ["flowers", "subscription", "romantic"], "effort": 1},
    {"name": "Star or constellation map of a meaningful date", "tags": ["sentimental", "romantic", "personal", "art"], "effort": 1},
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
