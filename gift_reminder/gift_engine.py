"""Gift suggestion engine that matches gifts to partner preferences."""

import random
import re
from collections import Counter
from gift_reminder.data.gifts import MONTHLY_GIFTS, QUARTERLY_GIFTS, CATEGORY_TAG_MAP

# Budget string → max dollar value for filtering
_BUDGET_CAPS = {
    "Under $25": 25,
    "$25 – $50": 50,
    "$50 – $100": 100,
    "$100+": 999,
    "Under $50": 50,
    "$100 – $200": 200,
    "$200+": 999,
}


def _parse_price_max(price_str: str) -> float:
    """Extract the upper-bound dollar amount from a price string like '$15-30' or '$60-120'."""
    nums = re.findall(r"\d+", price_str or "")
    if not nums:
        return 999.0
    return float(nums[-1])


class GiftEngine:
    def __init__(self, db):
        self.db = db

    def _get_giver_profile(self) -> dict:
        return self.db.get_giver_profile() or {}

    def _build_preference_tags(self) -> Counter:
        """Build a weighted tag set from setup answers and update history."""
        tag_weights = Counter()
        answers = self.db.get_setup_answers()

        for ans in answers:
            category = ans["category"]
            answer_text = ans["answer"]

            # Check if this answer maps to known tags
            if category in CATEGORY_TAG_MAP:
                for key, tags in CATEGORY_TAG_MAP[category].items():
                    if key.lower() in answer_text.lower():
                        for tag in tags:
                            tag_weights[tag] += 2

            # Also extract tags from freeform answers via keyword matching
            answer_lower = answer_text.lower()
            all_tags = set()
            for gift_list in [MONTHLY_GIFTS, QUARTERLY_GIFTS]:
                for gift in gift_list:
                    all_tags.update(gift["tags"])

            for tag in all_tags:
                if tag.replace("_", " ") in answer_lower:
                    tag_weights[tag] += 1

        # Boost tags from highly-rated past gifts
        gifts = self.db.get_all_gifts()
        for gift in gifts:
            if gift.get("rating") and gift["rating"] >= 4:
                # Find matching gift in our database and boost its tags
                for gift_entry in MONTHLY_GIFTS + QUARTERLY_GIFTS:
                    if gift_entry["name"] == gift["gift_name"]:
                        for tag in gift_entry["tags"]:
                            tag_weights[tag] += 3
                        break

        # Penalize tags from poorly-rated gifts
        for gift in gifts:
            if gift.get("rating") and gift["rating"] <= 2:
                for gift_entry in MONTHLY_GIFTS + QUARTERLY_GIFTS:
                    if gift_entry["name"] == gift["gift_name"]:
                        for tag in gift_entry["tags"]:
                            tag_weights[tag] -= 2
                        break

        return tag_weights

    def _score_gift(self, gift: dict, tag_weights: Counter, budget_cap: float = 999,
                     giver: dict | None = None) -> float:
        """Score a gift based on how well it matches preferences and giver constraints."""
        score = 0.0
        for tag in gift["tags"]:
            score += tag_weights.get(tag, 0)

        # Slight penalty for higher effort
        score -= (gift["effort"] - 1) * 2

        # Budget filter: heavy penalty if price exceeds cap
        price_max = _parse_price_max(gift.get("price", ""))
        if price_max > budget_cap:
            score -= 40

        if giver:
            # Time preference: penalize higher-effort gifts for time-constrained givers
            time_pref = giver.get("time_budget", "")
            if "5 minutes" in time_pref and gift["effort"] >= 2:
                score -= 15
            elif "15 minutes" in time_pref and gift["effort"] >= 3:
                score -= 10

            # Gift type preference: products vs experiences
            kind = gift.get("kind", "product")
            type_pref = giver.get("gift_type_pref", "")
            if "Physical products" in type_pref and kind == "experience":
                score -= 20
            elif "Experiences" in type_pref and kind == "product":
                score -= 15

            # Experience comfort: penalize experiences for uncomfortable givers
            exp_comfort = giver.get("experience_comfort", "")
            if "Not really" in exp_comfort and kind == "experience":
                score -= 25

            # DIY comfort: penalize craft/diy items for non-crafty givers
            diy_comfort = giver.get("diy_comfort", "")
            if "No way" in diy_comfort:
                for tag in gift["tags"]:
                    if tag in ("diy", "craft", "personalized", "creative"):
                        score -= 15
                        break

        # Avoid recently given gifts
        recent_gifts = self.db.get_recent_gifts(20)
        recent_names = {g["gift_name"] for g in recent_gifts}
        if gift["name"] in recent_names:
            score -= 50  # Strong penalty for repeats

        # Penalize frequently skipped gifts
        skipped = set(self.db.get_skipped_gifts(30))
        if gift["name"] in skipped:
            score -= 25

        return score

    def suggest_monthly_gifts(self, count: int = 3) -> list[dict]:
        """Suggest monthly gift ideas, ranked by preference match."""
        tag_weights = self._build_preference_tags()
        giver = self._get_giver_profile()
        budget_cap = _BUDGET_CAPS.get(giver.get("monthly_budget", ""), 999)

        scored = []
        for gift in MONTHLY_GIFTS:
            score = self._score_gift(gift, tag_weights, budget_cap, giver)
            scored.append((score, gift))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Pick from top candidates with some randomness
        top_pool = scored[: max(count * 3, 10)]
        if len(top_pool) <= count:
            return [g for _, g in top_pool]

        # Weighted random selection from top pool
        selected = []
        pool = list(top_pool)
        for _ in range(count):
            if not pool:
                break
            min_score = min(s for s, _ in pool)
            weights = [max(s - min_score + 1, 1) for s, _ in pool]
            chosen = random.choices(pool, weights=weights, k=1)[0]
            selected.append(chosen[1])
            pool.remove(chosen)

        return selected

    def suggest_quarterly_gifts(self, count: int = 3) -> list[dict]:
        """Suggest quarterly surprise gift ideas."""
        tag_weights = self._build_preference_tags()
        giver = self._get_giver_profile()
        budget_cap = _BUDGET_CAPS.get(giver.get("quarterly_budget", ""), 999)

        scored = []
        for gift in QUARTERLY_GIFTS:
            score = self._score_gift(gift, tag_weights, budget_cap, giver)
            scored.append((score, gift))

        scored.sort(key=lambda x: x[0], reverse=True)

        top_pool = scored[: max(count * 3, 10)]
        if len(top_pool) <= count:
            return [g for _, g in top_pool]

        selected = []
        pool = list(top_pool)
        for _ in range(count):
            if not pool:
                break
            min_score = min(s for s, _ in pool)
            weights = [max(s - min_score + 1, 1) for s, _ in pool]
            chosen = random.choices(pool, weights=weights, k=1)[0]
            selected.append(chosen[1])
            pool.remove(chosen)

        return selected

    def suggest_last_minute(self, count: int = 2) -> list[dict]:
        """Suggest easy, quick gifts for last-minute rescue."""
        tag_weights = self._build_preference_tags()
        # Only effort=1 gifts
        easy = [g for g in MONTHLY_GIFTS if g["effort"] <= 1]
        scored = [(self._score_gift(g, tag_weights), g) for g in easy]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [g for _, g in scored[:count]]

    def get_suggestion_for_reminder(self, reminder_type: str) -> list[dict]:
        """Get gift suggestions appropriate for the reminder type."""
        if reminder_type == "monthly":
            return self.suggest_monthly_gifts(3)
        elif reminder_type == "quarterly":
            return self.suggest_quarterly_gifts(3)
        return []
