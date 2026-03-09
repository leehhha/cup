"""Setup questions, bonus questions, and 6-month update questions."""

# Each question has:
# - key: unique identifier
# - text: the question to display
# - category: used for gift matching
# - type: "options" (select from list), "multi" (multi-select), "text" (free text), "scale" (1-5)
# - options: list of choices (for options/multi types)
# - section: display grouping header

# --- Core setup: 10 essential questions for fast onboarding ---
SETUP_QUESTIONS = [
    {
        "key": "partner_name",
        "text": "What is your wife's first name?",
        "category": "basic",
        "type": "text",
        "section": "Getting Started",
    },
    {
        "key": "hobbies",
        "text": "What are her main hobbies or interests? (Select all that apply)",
        "category": "interests",
        "type": "multi",
        "options": [
            "Reading",
            "Cooking",
            "Fitness/Wellness",
            "Art/Creative",
            "Music",
            "Nature/Outdoors",
            "Fashion/Style",
            "Technology",
            "Travel",
            "Home Decor",
            "Gardening",
            "Photography",
        ],
        "section": "Her Interests",
    },
    {
        "key": "food_treats",
        "text": "What treats or indulgences does she love?",
        "category": "food_pref",
        "type": "multi",
        "options": [
            "Chocolate",
            "Wine",
            "Coffee",
            "Tea",
            "Baked Goods",
            "Healthy Snacks",
            "Cheese/Charcuterie",
            "Ice Cream",
        ],
        "section": "Treats & Indulgences",
    },
    {
        "key": "dietary",
        "text": "Any dietary preferences or restrictions?",
        "category": "food_pref",
        "type": "multi",
        "options": [
            "No restrictions",
            "Vegetarian",
            "Vegan",
            "Gluten-free",
            "Dairy-free",
            "Nut allergy",
            "Other allergies",
        ],
        "section": "Treats & Indulgences",
    },
    {
        "key": "style",
        "text": "How would you describe her personal style?",
        "category": "style",
        "type": "options",
        "options": [
            "Classic & elegant",
            "Casual & comfortable",
            "Trendy & fashion-forward",
            "Bohemian & free-spirited",
            "Minimalist & clean",
            "Sporty & active",
        ],
        "section": "Style & Self-Care",
    },
    {
        "key": "jewelry_pref",
        "text": "What type of jewelry does she prefer?",
        "category": "style",
        "type": "multi",
        "options": [
            "Gold",
            "Silver",
            "Rose Gold",
            "Dainty/Minimal",
            "Bold/Statement",
            "Doesn't wear much jewelry",
        ],
        "section": "Style & Self-Care",
    },
    {
        "key": "self_care",
        "text": "What self-care does she enjoy?",
        "category": "self_care_pref",
        "type": "multi",
        "options": [
            "Spa/Massage",
            "Skincare",
            "Bath Products",
            "Aromatherapy",
            "Yoga/Meditation",
            "Nails/Manicure",
            "Hair treatments",
        ],
        "section": "Style & Self-Care",
    },
    {
        "key": "experience_pref",
        "text": "What kind of experiences does she enjoy most?",
        "category": "interests",
        "type": "multi",
        "options": [
            "Travel",
            "Dining Out",
            "Spa Days",
            "Concerts/Shows",
            "Classes/Workshops",
            "Outdoor Adventures",
            "Cultural Events",
            "Staycations",
        ],
        "section": "Gifts & Experiences",
    },
    {
        "key": "fav_colors",
        "text": "What colors does she gravitate toward? (clothes, decor, etc.)",
        "category": "style",
        "type": "text",
        "section": "Gifts & Experiences",
    },
    {
        "key": "dislikes",
        "text": "Anything she specifically DOESN'T like receiving as gifts?",
        "category": "dislikes",
        "type": "text",
        "section": "Gifts & Experiences",
    },

    # --- Special occasions: dates and holidays ---
    {
        "key": "partner_birthday",
        "text": "What is her birthday? (MM/DD, e.g. 05/15)",
        "category": "occasions",
        "type": "text",
        "section": "Special Occasions",
    },
    {
        "key": "anniversary_date",
        "text": "What is your anniversary? (MM/DD, e.g. 09/22)",
        "category": "occasions",
        "type": "text",
        "section": "Special Occasions",
    },
    {
        "key": "is_mother",
        "text": "Is she a mother?",
        "category": "occasions",
        "type": "options",
        "options": ["Yes", "No"],
        "section": "Special Occasions",
    },
    {
        "key": "holidays",
        "text": "Which holidays should we remind you about? (Select all that apply)",
        "category": "occasions",
        "type": "multi",
        "options": [
            "Valentine's Day (Feb 14)",
            "Mother's Day (May)",
            "Her Birthday",
            "Anniversary",
            "Christmas (Dec 25)",
        ],
        "section": "Special Occasions",
    },
    {
        "key": "custom_dates",
        "text": "What other special dates should we remember?",
        "category": "occasions",
        "type": "custom_dates",
        "section": "Important Dates",
        "preset_dates": [
            {"name": "Day we met", "emoji": "\U0001f495"},
            {"name": "First date", "emoji": "\U0001f339"},
            {"name": "Wedding anniversary", "emoji": "\U0001f48d"},
            {"name": "Dating anniversary", "emoji": "\u2764\ufe0f"},
            {"name": "When we got engaged", "emoji": "\U0001f48e"},
            {"name": "Moved in together", "emoji": "\U0001f3e0"},
            {"name": "First I love you", "emoji": "\U0001f497"},
        ],
    },

    # --- Giver profile: 8 questions about YOUR gift-giving style ---
    {
        "key": "giver_style",
        "text": "How would you describe your gift-giving style?",
        "category": "giver",
        "type": "options",
        "options": [
            "Planner — I like to think ahead",
            "Last-minute — I work best under pressure",
            "Spontaneous — I give when inspiration strikes",
            "Delegator — just tell me what to buy",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_time",
        "text": "How much time can you realistically spend on a gift each month?",
        "category": "giver",
        "type": "options",
        "options": [
            "5 minutes (quick online order)",
            "15 minutes (a little browsing)",
            "30+ minutes (I enjoy the hunt)",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_monthly_budget",
        "text": "What's your comfortable monthly gift budget?",
        "category": "giver",
        "type": "options",
        "options": [
            "Under $25",
            "$25 – $50",
            "$50 – $100",
            "$100+",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_quarterly_budget",
        "text": "What about for bigger quarterly surprises?",
        "category": "giver",
        "type": "options",
        "options": [
            "Under $50",
            "$50 – $100",
            "$100 – $200",
            "$200+",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_gift_type",
        "text": "What type of gifts are you most comfortable giving?",
        "category": "giver",
        "type": "options",
        "options": [
            "Physical products (delivered to door)",
            "Experiences (tickets, reservations, outings)",
            "Mix of both",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_experience_comfort",
        "text": "How comfortable are you planning an experience (booking, logistics)?",
        "category": "giver",
        "type": "options",
        "options": [
            "Very comfortable — I'll handle it all",
            "Somewhat — keep it simple",
            "Not really — just show me what to buy",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_diy_comfort",
        "text": "Would you ever make or personalize a gift yourself?",
        "category": "giver",
        "type": "options",
        "options": [
            "Absolutely — I'm crafty",
            "Maybe — if it's easy",
            "No way — I'll buy something",
        ],
        "section": "About Your Gift-Giving Style",
    },
    {
        "key": "giver_busy_handling",
        "text": "If life gets hectic and you miss a month, what should we do?",
        "category": "giver",
        "type": "options",
        "options": [
            "Send me a last-minute rescue idea",
            "Skip it and double up next month",
            "Just remind me — I'll figure it out",
        ],
        "section": "About Your Gift-Giving Style",
    },
]

# --- Bonus questions: 15 extra questions for engaged users ---
BONUS_QUESTIONS = [
    # Deeper personality & preferences
    {
        "key": "love_language",
        "text": "Which of these makes her feel most loved?",
        "category": "love_language",
        "type": "options",
        "options": [
            "Words of Affirmation",
            "Acts of Service",
            "Receiving Gifts",
            "Quality Time",
            "Physical Touch",
        ],
        "section": "Deeper Personality",
    },
    {
        "key": "personality",
        "text": "How would you describe her personality?",
        "category": "personality",
        "type": "multi",
        "options": [
            "Adventurous",
            "Creative",
            "Intellectual",
            "Social",
            "Homebody",
            "Practical",
            "Romantic",
            "Spontaneous",
        ],
        "section": "Deeper Personality",
    },
    {
        "key": "surprise_comfort",
        "text": "How does she feel about surprises?",
        "category": "preferences",
        "type": "options",
        "options": [
            "Loves surprises",
            "Likes small surprises",
            "Prefers to know what's coming",
            "Depends on the situation",
        ],
        "section": "Deeper Personality",
    },
    {
        "key": "gift_reaction",
        "text": "When she receives a gift she loves, she typically:",
        "category": "preferences",
        "type": "options",
        "options": [
            "Gets very emotional and expressive",
            "Quietly appreciates it deeply",
            "Immediately wants to use/wear it",
            "Shares it on social media or tells friends",
        ],
        "section": "Deeper Personality",
    },

    # More about interests
    {
        "key": "hobby_detail",
        "text": "What specific hobby or interest is she most passionate about right now?",
        "category": "interests",
        "type": "text",
        "section": "More About Interests",
    },
    {
        "key": "entertainment",
        "text": "What does she enjoy for entertainment?",
        "category": "interests",
        "type": "multi",
        "options": [
            "Movies",
            "TV Shows",
            "Podcasts",
            "Live Music/Concerts",
            "Theater",
            "Museums/Galleries",
            "Board Games",
            "Video Games",
        ],
        "section": "More About Interests",
    },
    {
        "key": "reading_pref",
        "text": "If she reads, what does she gravitate toward?",
        "category": "interests",
        "type": "multi",
        "options": [
            "Fiction/Novels",
            "Non-Fiction",
            "Self-Help",
            "Cookbooks",
            "Magazines",
            "Poetry",
            "Doesn't read much",
        ],
        "section": "More About Interests",
    },
    {
        "key": "music_taste",
        "text": "What kind of music does she enjoy?",
        "category": "interests",
        "type": "text",
        "section": "More About Interests",
    },

    # Food & dining details
    {
        "key": "dining_pref",
        "text": "What's her ideal dining experience?",
        "category": "food_pref",
        "type": "options",
        "options": [
            "Fine dining",
            "Casual & cozy restaurants",
            "Trendy new spots",
            "Home-cooked meals",
            "Takeout & comfort food",
        ],
        "section": "Food & Dining Details",
    },
    {
        "key": "fav_cuisine",
        "text": "What are her favorite cuisines? (e.g., Italian, Japanese, Mexican)",
        "category": "food_pref",
        "type": "text",
        "section": "Food & Dining Details",
    },

    # Style details
    {
        "key": "fragrance_pref",
        "text": "What type of scents/fragrances does she like?",
        "category": "style",
        "type": "multi",
        "options": [
            "Floral",
            "Fresh/Clean",
            "Warm/Vanilla",
            "Citrus",
            "Woody/Earthy",
            "No strong preference",
        ],
        "section": "Style Details",
    },

    # Experiences & sentimental
    {
        "key": "date_night",
        "text": "What's her ideal date night?",
        "category": "interests",
        "type": "options",
        "options": [
            "Nice dinner out",
            "Movie & cozy night in",
            "Live event (concert, show, game)",
            "Active adventure (hike, bike, explore)",
            "Something creative (painting, cooking class)",
        ],
        "section": "Experiences & Sentimental",
    },
    {
        "key": "sentimental_value",
        "text": "How important is sentimentality to her?",
        "category": "preferences",
        "type": "scale",
        "section": "Experiences & Sentimental",
    },
    {
        "key": "meaningful_gift",
        "text": "What's the most meaningful gift you've ever given her? What made it special?",
        "category": "preferences",
        "type": "text",
        "section": "Experiences & Sentimental",
    },
]

# 3-month check-in questions (quick pulse check)
CHECKIN_3_QUESTIONS = [
    {
        "key": "checkin3_hits",
        "text": "Which recent gifts were the biggest hits?",
        "type": "text",
    },
    {
        "key": "checkin3_misses",
        "text": "Any gifts that didn't land? What would have been better?",
        "type": "text",
    },
    {
        "key": "checkin3_budget",
        "text": "Is the current budget still working for you?",
        "type": "options",
        "options": [
            "Perfect",
            "I'd like to spend less",
            "I can spend more",
        ],
    },
]

# 6-month update questions (deeper refresh)
UPDATE_QUESTIONS = [
    {
        "key": "gift_feedback",
        "text": "Looking back at recent gifts, which ones did she love the most and why?",
        "type": "text",
    },
    {
        "key": "new_interests",
        "text": "Has she picked up any new hobbies or interests recently?",
        "type": "text",
    },
    {
        "key": "current_wishes",
        "text": "Has she mentioned wanting anything specific lately?",
        "type": "text",
    },
    {
        "key": "life_changes",
        "text": "Any life changes that might affect gift preferences? (new job, new hobby, health focus, etc.)",
        "type": "text",
    },
    {
        "key": "improvement",
        "text": "Is there anything you'd like to do differently with gifts going forward?",
        "type": "text",
    },
]
