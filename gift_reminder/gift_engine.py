"""Gift suggestion engine that matches gifts to partner preferences."""

import random
from collections import Counter
from gift_reminder.data.gifts import MONTHLY_GIFTS, QUARTERLY_GIFTS, CATEGORY_TAG_MAP


class GiftEngine:
    def __init__(self, db):
        self.db = db

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

    def _score_gift(self, gift: dict, tag_weights: Counter) -> float:
        """Score a gift based on how well it matches preferences."""
        score = 0.0
        for tag in gift["tags"]:
            score += tag_weights.get(tag, 0)

        # Slight penalty for higher effort
        score -= (gift["effort"] - 1) * 2

        # Avoid recently given gifts
        recent_gifts = self.db.get_recent_gifts(20)
        recent_names = {g["gift_name"] for g in recent_gifts}
        if gift["name"] in recent_names:
            score -= 50  # Strong penalty for repeats

        return score

    def suggest_monthly_gifts(self, count: int = 3) -> list[dict]:
        """Suggest monthly gift ideas, ranked by preference match."""
        tag_weights = self._build_preference_tags()
        scored = []
        for gift in MONTHLY_GIFTS:
            score = self._score_gift(gift, tag_weights)
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
            # Shift scores to be positive for weighting
            min_score = min(s for s, _ in pool)
            weights = [max(s - min_score + 1, 1) for s, _ in pool]
            chosen = random.choices(pool, weights=weights, k=1)[0]
            selected.append(chosen[1])
            pool.remove(chosen)

        return selected

    def suggest_quarterly_gifts(self, count: int = 3) -> list[dict]:
        """Suggest quarterly surprise gift ideas."""
        tag_weights = self._build_preference_tags()
        scored = []
        for gift in QUARTERLY_GIFTS:
            score = self._score_gift(gift, tag_weights)
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

    def get_suggestion_for_reminder(self, reminder_type: str) -> list[dict]:
        """Get gift suggestions appropriate for the reminder type."""
        if reminder_type == "monthly":
            return self.suggest_monthly_gifts(3)
        elif reminder_type == "quarterly":
            return self.suggest_quarterly_gifts(3)
        return []
