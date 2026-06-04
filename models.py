from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default='')
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    isr_score = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    level = db.Column(db.Integer, default=1)
    co2_saved = db.Column(db.Float, default=0.0)       # kg
    plastic_avoided = db.Column(db.Float, default=0.0) # grams
    trees_planted = db.Column(db.Integer, default=0)
    volunteer_hours = db.Column(db.Float, default=0.0)
    activities = db.relationship('Activity', backref='user', lazy=True)
    user_badges = db.relationship('UserBadge', backref='user', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    co2_impact = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, default='')

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    emoji = db.Column(db.String(10))
    requirement_type = db.Column(db.String(50))  # e.g. 'score', 'streak', 'activity_count'
    requirement_value = db.Column(db.Integer)

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    badge = db.relationship('Badge')

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    challenge_type = db.Column(db.String(20))  # 'daily' or 'weekly'
    points_reward = db.Column(db.Integer, default=20)
    activity_target = db.Column(db.String(100))  # matches activity_type
    is_active = db.Column(db.Boolean, default=True)

class UserChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    challenge = db.relationship('Challenge')