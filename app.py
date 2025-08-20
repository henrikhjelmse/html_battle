from flask_login import current_user, LoginManager, UserMixin, login_required,logout_user
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import os
import random
import difflib

import json


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Ändra till en säker nyckel

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for flask_login
class User(UserMixin):
    def __init__(self, username, rank):
        self.id = username
        self.username = username
        self.rank = rank
    @property
    def is_superadmin(self):
        return self.rank == 'superadmin'

@login_manager.user_loader
def load_user(user_id):
    admins = load_admins()
    user = next((a for a in admins if a.get('username') == user_id), None)
    if user:
        return User(user['username'], user.get('rank', 'admin'))
    return None

# Make current_user available in all templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Admins loaded from admins.json
ADMINS_JSON = os.path.join(os.path.dirname(__file__), 'admins.json')

#check if admins.json exists, if not create an empty one
if not os.path.exists(ADMINS_JSON):
    with open(ADMINS_JSON, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    #create admin/admin123 and superadmin
    with open(ADMINS_JSON, 'r+', encoding='utf-8') as f:
        admins = json.load(f)
        if not any(a['username'] == 'admin' for a in admins):
            admins.append({
                'username': 'admin',
                'password_hash': generate_password_hash('admin123'),
                'rank': 'admin'
            })
        if not any(a['username'] == 'superadmin' for a in admins):
            admins.append({
                'username': 'superadmin',
                'password_hash': generate_password_hash('superadmin123'),
                'rank': 'superadmin'
            })
        f.seek(0)
        json.dump(admins, f, ensure_ascii=False, indent=2)
        f.truncate()

def load_admins():
    if not os.path.exists(ADMINS_JSON):
        return []
    with open(ADMINS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/admin', methods=['GET'])
@login_required
def admin_panel():
    layout_ids = get_available_layouts()
    layout_dict = get_layout_dict()
    # Skicka även hints till admin.html
    layouts = load_layouts()
    hint_dict = {l['id']: l.get('hint', '') for l in layouts}
    return render_template('admin.html', layouts=layout_ids, correct_html=layout_dict, correct_hint=hint_dict, all_layouts=layouts)

@app.route('/admin/delete', methods=['POST'])
@login_required
def admin_delete():
    layout_id = request.form.get('layout_id')
    try:
        layout_id = int(layout_id)
    except (TypeError, ValueError):
        return redirect(url_for('admin_panel'))
    # Ta bort bildfil
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{layout_id}.jpg")
    if os.path.exists(img_path):
        os.remove(img_path)
    # Ta bort från layouts.json
    layouts = load_layouts()
    layouts = [l for l in layouts if l['id'] != layout_id]
    save_layouts(layouts)
    layout_ids = get_available_layouts()
    layout_dict = get_layout_dict()
    layouts = load_layouts()
    hint_dict = {l['id']: l.get('hint', '') for l in layouts}
    return render_template('admin.html', layouts=layout_ids, correct_html=layout_dict, correct_hint=hint_dict, all_layouts=load_layouts(), success=f"Layout {layout_id} borttagen!")

# Konfiguration
UPLOAD_FOLDER = 'static/layouts'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Skapa upload-mappen om den inte existerar
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Layout-data hanteras i layouts.json
LAYOUTS_JSON = os.path.join(os.path.dirname(__file__), 'layouts.json')

def load_layouts():
    if not os.path.exists(LAYOUTS_JSON):
        return []
    with open(LAYOUTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_layouts(layouts):
    with open(LAYOUTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(layouts, f, ensure_ascii=False, indent=2)

def get_layout_dict():
    """Returnerar dict med layout_id som key och html som value"""
    layouts = load_layouts()
    return {l['id']: l['html'] for l in layouts}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_available_layouts():
    """Returnerar en lista över tillgängliga layouter"""
    layouts = []
    for i in range(1, 21):  # Kontrollera för 1.jpg till 20.jpg
        if os.path.exists(os.path.join(UPLOAD_FOLDER, f"{i}.jpg")):
            layouts.append(i)
    return layouts

def calculate_similarity(user_html, correct_html):
    """Beräknar likhet mellan användarens HTML och rätt svar"""
    # Ta bort ALL whitespace (mellanslag, radbrytningar, tabbar)
    import re
    user_clean = re.sub(r'\s+', '', user_html)
    correct_clean = re.sub(r'\s+', '', correct_html)
    similarity = difflib.SequenceMatcher(None, user_clean.lower(), correct_clean.lower()).ratio()
    return round(similarity * 100, 1)

@app.route('/')
def index():
    available_layouts = get_available_layouts()
    return render_template('index.html', layouts=available_layouts)

# API-endpoint för att hämta taggstatistik för en layout
@app.route('/api/layout_tags/<int:layout_id>')
def api_layout_tags(layout_id):
    layouts = load_layouts()
    html = ''
    for l in layouts:
        if l['id'] == layout_id:
            html = l.get('html', '')
            break
    import re
    from collections import Counter
    tags = re.findall(r'<([a-zA-Z0-9]+)', html)
    tag_counts = Counter(tags)
    # Returnera som {"tags": {tag: antal, ...}}
    return jsonify({'tags': dict(tag_counts)})

# API-endpoint för att hämta rätt textinnehåll (utan taggar) för en layout
@app.route('/api/layout_text/<int:layout_id>')
def api_layout_text(layout_id):
    layouts = load_layouts()
    html = ''
    for l in layouts:
        if l['id'] == layout_id:
            html = l.get('html', '')
            break
    # Ta bort alla taggar och returnera endast texten
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text("\n")
    return text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/layout/<int:layout_id>')
def show_layout(layout_id):
    # Kontrollera om layouten existerar
    layout_path = os.path.join(UPLOAD_FOLDER, f"{layout_id}.jpg")
    if not os.path.exists(layout_path):
        return "Layout inte hittad", 404

    available_layouts = get_available_layouts()
    session['current_layout'] = layout_id
    # Hämta hint för denna layout
    layouts = load_layouts()
    hint = ''
    correct_html = ''
    for l in layouts:
        if l['id'] == layout_id:
            hint = l.get('hint', '')
            correct_html = l.get('html', '')
            break
    return render_template('layout.html', layout_id=layout_id, available_layouts=available_layouts, hint=hint, correct_html=correct_html)

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    data = request.get_json()
    user_html = data.get('html', '').strip()
    layout_id = session.get('current_layout')
    layout_dict = get_layout_dict()
    if not layout_id or layout_id not in layout_dict:
        return jsonify({'error': 'Ingen giltig layout vald'}), 400
    correct_html = layout_dict[layout_id]
    similarity = calculate_similarity(user_html, correct_html)
    # Bestäm feedback baserat på likhet
    if similarity == 100:
        feedback = "Fantastiskt! Din HTML är identisk med den korrekta. 🎉"
        status = 'perfect'
    elif similarity >= 90:
        feedback = f"Bra jobbat! Din HTML är mycket lik den korrekta.{' ' if similarity < 100 else ''} "
        status = 'correct'
    elif similarity >= 70:
        feedback = f"Bra försök! Din HTML är ganska lik den korrekta. "
        status = 'almost_correct'
    elif similarity >= 50:
        feedback = f"Du är på rätt spår... 🤔 "
        status = 'partially_correct'
    elif similarity >= 30:
        feedback = f"Du behöver jobba mer på detta."
        status = 'somewhat_correct'
    else:
        feedback = f"Försök igen! 💪"
        status = f"try_again_{similarity}"

    return jsonify({
        'similarity': similarity,
        'feedback': feedback,
        'status': status,
        'correct_html': correct_html if similarity < 90 else None
    })

@app.route('/admin/edit', methods=['POST'])
@login_required
def admin_edit():
    layout_id = request.form.get('layout_id')
    new_html = request.form.get('new_html', '').strip()
    new_hint = request.form.get('new_hint', '').strip()
    try:
        layout_id = int(layout_id)
    except (TypeError, ValueError):
        return redirect(url_for('admin_panel'))
    layouts = load_layouts()
    updated = False
    for l in layouts:
        if l['id'] == layout_id:
            # Only superadmin or the creator can edit
            if session.get('admin_rank') == 'superadmin' or l.get('made_by') == session.get('admin_username'):
                l['html'] = new_html
                l['hint'] = new_hint
                updated = True
            else:
                success = 'Du har inte behörighet att ändra denna layout.'
            break
    if updated:
        save_layouts(layouts)
        success = f"HTML för layout {layout_id} uppdaterad!"
    else:
        success = f"Layout {layout_id} hittades inte."
    layout_ids = get_available_layouts()
    layout_dict = get_layout_dict()
    hint_dict = {l['id']: l.get('hint', '') for l in layouts}
    return render_template('admin.html', layouts=layout_ids, correct_html=layout_dict, correct_hint=hint_dict, all_layouts=load_layouts(), success=success)


@app.route('/random')
def random_layout():
    available_layouts = get_available_layouts()
    if not available_layouts:
        return "Inga layouter tillgängliga", 404
    
    random_id = random.choice(available_layouts)
    return redirect(url_for('show_layout', layout_id=random_id))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # Endast admin får ladda upp
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    # Hitta nästa lediga layout-nummer
    # Hitta minsta lediga layout-nummer
    existing = sorted(get_available_layouts())
    next_layout_number = 1
    for i, num in enumerate(existing, start=1):
        if num != i:
            next_layout_number = i
            break
    else:
        next_layout_number = (existing[-1] + 1) if existing else 1

    
    

    if request.method == 'POST':
        layouts = load_layouts()
        if 'file' not in request.files:
            return render_template('upload.html', error='Ingen fil vald', next_layout_number=next_layout_number)

        file = request.files['file']
        correct_html = request.form.get('correct_html', '').strip()
        hint = request.form.get('hint', '').strip()

        if file.filename == '':
            return render_template('upload.html', error='Ingen fil vald', next_layout_number=next_layout_number)

        if not correct_html:
            return render_template('upload.html', error='Rätt HTML-kod krävs', next_layout_number=next_layout_number)

        layout_number = next_layout_number
        if file and allowed_file(file.filename):
            filename = f"{layout_number}.jpg"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Spara till layouts.json
            layouts.append({'id': layout_number, 'html': correct_html, 'hint': hint})
            save_layouts(layouts)
            return render_template('upload.html', success=f'Layout {layout_number} uppladdad!', next_layout_number=layout_number+1)

    return render_template('upload.html', next_layout_number=next_layout_number)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask_login import login_user, current_user
    if current_user.is_authenticated:
        return render_template('login.html', error=None, already_logged_in=True)

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admins = load_admins()
        user = next((a for a in admins if a.get('username') == username), None)
        if user and check_password_hash(user.get('password_hash', ''), password):
            login_user(User(user['username'], user.get('rank', 'admin')))
            session['admin_logged_in'] = True
            session['admin_username'] = user['username']
            session['admin_rank'] = user.get('rank', 'admin')
            return redirect(url_for('upload_file'))
        else:
            error = 'Fel användarnamn eller lösenord.'
    return render_template('login.html', error=error)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    # Only superadmin can manage users
    if not (hasattr(current_user, 'rank') and current_user.rank == 'superadmin'):
        return redirect(url_for('login'))

    admins = load_admins()
    error = None
    success = None

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username', '').strip()
        rank = request.form.get('rank', 'admin')
        admins = load_admins()
        if action == 'add':
            password = request.form.get('password', '').strip()
            if not username or not password:
                error = 'Användarnamn och lösenord krävs.'
            elif any(a['username'] == username for a in admins):
                error = 'Användarnamnet finns redan.'
            else:
                admins.append({
                    'username': username,
                    'password_hash': generate_password_hash(password),
                    'rank': rank
                })
                with open(ADMINS_JSON, 'w', encoding='utf-8') as f:
                    json.dump(admins, f, ensure_ascii=False, indent=2)
                success = f'Användare {username} tillagd.'
        elif action == 'edit':
            for a in admins:
                if a['username'] == username:
                    a['rank'] = rank
                    if request.form.get('password'):
                        a['password_hash'] = generate_password_hash(request.form.get('password'))
                    with open(ADMINS_JSON, 'w', encoding='utf-8') as f:
                        json.dump(admins, f, ensure_ascii=False, indent=2)
                    success = f'Användare {username} uppdaterad.'
                    break
            else:
                error = 'Användaren hittades inte.'
    admins = load_admins()
    return render_template('admin_users.html', admins=admins, error=error, success=success)

@app.route('/logout')
def logout():

    logout_user()
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    session.pop('admin_rank', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=5000)  # Exponera appen på alla IP-adresser