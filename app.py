from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Activity, Badge, UserBadge, Challenge, UserChallenge
from gamification import (ACTIVITIES, LEVELS, get_level, get_next_level,
                          get_level_progress, update_streak, check_and_award_badges)
from datetime import datetime, date
import os

# ─── APP CONFIG ──────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'isr-green-marshal-secret-2024')

# Use DATABASE_URL env var if set (PostgreSQL on Railway), else SQLite locally
database_url = os.environ.get('DATABASE_URL', 'sqlite:///isr.db')
# Fix for Railway's postgres:// prefix (SQLAlchemy needs postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the Command Center.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── DATABASE SEED (badges + challenges) ─────────────────────────
def seed_database():
    if Badge.query.count() == 0:
        badges = [
            Badge(name="First Green Step",  description="Complete your first activity",  emoji="🌱", requirement_type="activity_count", requirement_value=1),
            Badge(name="Green Starter",     description="Earn 100 ISR points",           emoji="🌿", requirement_type="score",          requirement_value=100),
            Badge(name="Streak Keeper",     description="Maintain a 7-day streak",       emoji="🔥", requirement_type="streak",         requirement_value=7),
            Badge(name="Tree Guardian",     description="Plant 5 trees",                 emoji="🌳", requirement_type="trees",          requirement_value=5),
            Badge(name="Plastic-Free Hero", description="Earn 500 ISR points",           emoji="♻️", requirement_type="score",          requirement_value=500),
            Badge(name="Carbon Saver",      description="Complete 50 activities",        emoji="🚲", requirement_type="activity_count", requirement_value=50),
            Badge(name="Climate Champion",  description="Reach 1500 ISR points",         emoji="🏆", requirement_type="score",          requirement_value=1500),
            Badge(name="Planet Protector",  description="Reach 2500 ISR points",         emoji="🌍", requirement_type="score",          requirement_value=2500),
        ]
        db.session.add_all(badges)

    if Challenge.query.count() == 0:
        challenges = [
            Challenge(title="Reusable Bottle Day",  description="Carry a reusable water bottle all day.",         challenge_type="daily",  points_reward=15, activity_target="reusable_bottle"),
            Challenge(title="Unplug & Save",         description="Switch off all unnecessary appliances today.",   challenge_type="daily",  points_reward=15, activity_target="saved_electricity"),
            Challenge(title="Zero Plastic Day",      description="Go an entire day without single-use plastic.",  challenge_type="daily",  points_reward=20, activity_target="no_plastic_bags"),
            Challenge(title="Green Commute Week",    description="Use public transport or cycle for 3 days.",     challenge_type="weekly", points_reward=50, activity_target="public_transport"),
            Challenge(title="Community Cleanup",     description="Join or organize a local cleanup drive.",       challenge_type="weekly", points_reward=80, activity_target="cleanup_drive"),
            Challenge(title="Energy Saver Week",     description="Reduce household energy use for 5 days.",      challenge_type="weekly", points_reward=60, activity_target="saved_electricity"),
        ]
        db.session.add_all(challenges)

    db.session.commit()

# ─── ROUTES ──────────────────────────────────────────────────────

@app.route('/')
def index():
    top_users = User.query.order_by(User.isr_score.desc()).limit(5).all()
    total_users = User.query.count()
    total_activities = Activity.query.count()
    total_trees = db.session.query(db.func.sum(User.trees_planted)).scalar() or 0
    total_co2 = db.session.query(db.func.sum(User.co2_saved)).scalar() or 0
    stats = {
        "total_users": total_users,
        "total_activities": total_activities,
        "total_trees": total_trees,
        "total_co2": round(total_co2, 1)
    }
    return render_template('index.html', top_users=top_users, stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username  = request.form['username'].strip()
        email     = request.form['email'].strip()
        full_name = request.form['full_name'].strip()
        password  = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Choose another.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        user = User(username=username, email=email,
                    full_name=full_name, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Welcome to ISR Command Center.', 'success')
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password   = request.form['password']
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username/email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    level_info    = get_level(current_user.isr_score)
    next_level    = get_next_level(current_user.isr_score)
    progress, needed = get_level_progress(current_user.isr_score)
    recent_activities = Activity.query.filter_by(user_id=current_user.id)\
                                      .order_by(Activity.timestamp.desc()).limit(5).all()
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    rank = User.query.filter(User.isr_score > current_user.isr_score).count() + 1
    return render_template('dashboard.html',
        level_info=level_info, next_level=next_level,
        progress=progress, needed=needed,
        recent_activities=recent_activities,
        user_badges=user_badges, rank=rank,
        activities_catalog=ACTIVITIES,
        get_next_level=get_next_level)

@app.route('/log_activity', methods=['GET', 'POST'])
@login_required
def log_activity():
    if request.method == 'POST':
        activity_key = request.form['activity_type']
        notes = request.form.get('notes', '')

        if activity_key not in ACTIVITIES:
            flash('Invalid activity selected.', 'error')
            return redirect(url_for('log_activity'))

        info = ACTIVITIES[activity_key]
        activity = Activity(
            user_id=current_user.id,
            activity_type=activity_key,
            points_earned=info['points'],
            co2_impact=info.get('co2_saved', 0),
            notes=notes
        )
        db.session.add(activity)

        current_user.isr_score       += info['points']
        current_user.co2_saved       += info.get('co2_saved', 0)
        current_user.plastic_avoided += info.get('plastic_avoided', 0)
        current_user.trees_planted   += info.get('trees_planted', 0)
        current_user.volunteer_hours += info.get('volunteer_hours', 0)

        update_streak(current_user, date.today())
        current_user.level = get_level(current_user.isr_score)['level']
        db.session.commit()

        new_badges = check_and_award_badges(current_user, db)
        if new_badges:
            for b in new_badges:
                flash(f'New Badge Unlocked: {b.name}!', 'badge')

        flash(f'Logged "{info["label"]}" — +{info["points"]} points!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('log_activity.html', activities=ACTIVITIES)

@app.route('/challenges')
@login_required
def challenges():
    all_challenges = Challenge.query.filter_by(is_active=True).all()
    completed_ids = {uc.challenge_id for uc in
                     UserChallenge.query.filter_by(user_id=current_user.id, completed=True).all()}
    return render_template('challenges.html',
                           challenges=all_challenges,
                           completed_ids=completed_ids)

@app.route('/complete_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    already = UserChallenge.query.filter_by(
        user_id=current_user.id, challenge_id=challenge_id, completed=True).first()
    if already:
        flash('Challenge already completed!', 'info')
    else:
        uc = UserChallenge(user_id=current_user.id, challenge_id=challenge_id,
                           completed=True, completed_date=datetime.utcnow())
        db.session.add(uc)
        current_user.isr_score += challenge.points_reward
        db.session.commit()
        flash(f'Challenge completed! +{challenge.points_reward} points', 'success')
    return redirect(url_for('challenges'))

@app.route('/leaderboard')
def leaderboard():
    period = request.args.get('period', 'alltime')
    users = User.query.order_by(User.isr_score.desc()).limit(20).all()
    return render_template('leaderboard.html', users=users, period=period,
                           get_level=get_level)

@app.route('/badges')
@login_required
def badges():
    all_badges = Badge.query.all()
    earned_ids = {ub.badge_id for ub in current_user.user_badges}
    return render_template('badges.html', all_badges=all_badges, earned_ids=earned_ids)

@app.route('/profile')
@login_required
def profile():
    level_info = get_level(current_user.isr_score)
    progress, needed = get_level_progress(current_user.isr_score)
    all_activities = Activity.query.filter_by(user_id=current_user.id)\
                                   .order_by(Activity.timestamp.desc()).all()
    rank = User.query.filter(User.isr_score > current_user.isr_score).count() + 1
    return render_template('profile.html',
                           level_info=level_info, progress=progress,
                           all_activities=all_activities, rank=rank,
                           activities_catalog=ACTIVITIES)

# ─── INIT & ENTRY POINT ──────────────────────────────────────────
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
