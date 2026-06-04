from datetime import date, timedelta

# ─── ACTIVITY CATALOG ────────────────────────────────────────────
ACTIVITIES = {
    "public_transport": {
        "label": "Used Public Transport",
        "points": 10,
        "co2_saved": 2.1,       # kg CO2 per trip
        "plastic_avoided": 0,
        "emoji": "🚌"
    },
    "walking_cycling": {
        "label": "Walked or Cycled",
        "points": 15,
        "co2_saved": 1.5,
        "plastic_avoided": 0,
        "emoji": "🚲"
    },
    "reusable_bottle": {
        "label": "Used Reusable Bottle",
        "points": 5,
        "co2_saved": 0.1,
        "plastic_avoided": 25,  # grams
        "emoji": "🍶"
    },
    "no_plastic_bags": {
        "label": "Avoided Plastic Bags",
        "points": 5,
        "co2_saved": 0.05,
        "plastic_avoided": 8,
        "emoji": "♻️"
    },
    "cleanup_drive": {
        "label": "Participated in Clean-up Drive",
        "points": 40,
        "co2_saved": 0.5,
        "plastic_avoided": 500,
        "emoji": "🧹",
        "volunteer_hours": 2
    },
    "tree_planting": {
        "label": "Planted a Tree",
        "points": 50,
        "co2_saved": 22.0,       # lifetime estimate, symbolic
        "plastic_avoided": 0,
        "trees_planted": 1,
        "emoji": "🌳"
    },
    "waste_segregation": {
        "label": "Waste Segregation",
        "points": 10,
        "co2_saved": 0.3,
        "plastic_avoided": 0,
        "emoji": "🗂️"
    },
    "saved_electricity": {
        "label": "Saved Electricity",
        "points": 10,
        "co2_saved": 0.9,
        "plastic_avoided": 0,
        "emoji": "💡"
    },
    "environmental_event": {
        "label": "Attended Environmental Event",
        "points": 20,
        "co2_saved": 0.2,
        "plastic_avoided": 0,
        "emoji": "🌍",
        "volunteer_hours": 1
    },
}

# ─── LEVEL SYSTEM ────────────────────────────────────────────────
LEVELS = [
    {"level": 1, "name": "Eco Beginner",         "min_score": 0,    "emoji": "🌱"},
    {"level": 2, "name": "Green Explorer",        "min_score": 100,  "emoji": "🌿"},
    {"level": 3, "name": "Sustainability Advocate","min_score": 300,  "emoji": "🍃"},
    {"level": 4, "name": "Climate Warrior",       "min_score": 600,  "emoji": "⚔️"},
    {"level": 5, "name": "Ecosystem Guardian",    "min_score": 1000, "emoji": "🛡️"},
    {"level": 6, "name": "Climate Champion",      "min_score": 1500, "emoji": "🏆"},
    {"level": 7, "name": "Planet Protector",      "min_score": 2500, "emoji": "🌍"},
]

def get_level(score):
    """Returns the level dict for a given score."""
    current = LEVELS[0]
    for lvl in LEVELS:
        if score >= lvl["min_score"]:
            current = lvl
    return current

def get_next_level(score):
    """Returns the next level dict, or None if max."""
    for i, lvl in enumerate(LEVELS):
        if score < lvl["min_score"]:
            return lvl
    return None

def get_level_progress(score):
    """Returns (progress_percent, points_needed) to next level."""
    current = get_level(score)
    next_lvl = get_next_level(score)
    if not next_lvl:
        return 100, 0
    points_in_level = score - current["min_score"]
    level_range = next_lvl["min_score"] - current["min_score"]
    progress = int((points_in_level / level_range) * 100)
    points_needed = next_lvl["min_score"] - score
    return progress, points_needed

def update_streak(user, today=None):
    """Update the user's streak. Call this after logging an activity."""
    if today is None:
        today = date.today()
    if user.last_activity_date is None:
        user.streak_days = 1
    elif user.last_activity_date == today - timedelta(days=1):
        user.streak_days += 1
    elif user.last_activity_date == today:
        pass  # Already logged today, no change
    else:
        user.streak_days = 1  # Streak broken, restart
    user.last_activity_date = today

def check_and_award_badges(user, db):
    """Check if user has earned any new badges and award them."""
    from models import Badge, UserBadge
    all_badges = Badge.query.all()
    earned_ids = {ub.badge_id for ub in user.user_badges}
    newly_earned = []

    for badge in all_badges:
        if badge.id in earned_ids:
            continue
        earned = False
        if badge.requirement_type == 'score' and user.isr_score >= badge.requirement_value:
            earned = True
        elif badge.requirement_type == 'streak' and user.streak_days >= badge.requirement_value:
            earned = True
        elif badge.requirement_type == 'trees' and user.trees_planted >= badge.requirement_value:
            earned = True
        elif badge.requirement_type == 'activity_count':
            count = len(user.activities)
            if count >= badge.requirement_value:
                earned = True
        if earned:
            ub = UserBadge(user_id=user.id, badge_id=badge.id)
            db.session.add(ub)
            newly_earned.append(badge)

    db.session.commit()
    return newly_earned