from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import pandas as pd
import io
import base64
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the directory for the database file exists
db_dir = '/app/marks_data'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_dir}/marks.db'
db = SQLAlchemy(app)

# Marks model to store CBSE Score in Database
class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    physics = db.Column(db.Integer, nullable=False)
    chemistry = db.Column(db.Integer, nullable=False)
    maths = db.Column(db.Integer, nullable=False)
    english = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'DATE': self.date,
            'PHYSICS': self.physics,
            'CHEMISTRY': self.chemistry,
            'MATHS': self.maths,
            'ENGLISH': self.english,
            'IP': self.ip
        }
        
# Marks model to store JEE main/Advanced Score in Database
class JEEMarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    physics = db.Column(db.Integer, nullable=False)
    chemistry = db.Column(db.Integer, nullable=False)
    maths = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'DATE': self.date,
            'PHYSICS': self.physics,
            'CHEMISTRY': self.chemistry,
            'MATHS': self.maths,
            'TOTAL': self.total
        }
# Model to store daily updates 
class DailyUpdates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    general_notes = db.Column(db.String, nullable=True)
    physics = db.Column(db.String, nullable=True)
    chemistry = db.Column(db.String, nullable=True)
    maths = db.Column(db.String, nullable=True)
    english = db.Column(db.String, nullable=True)
    ip = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            'DATE': self.date,
            'PHYSICS': self.physics,
            'CHEMISTRY': self.chemistry,
            'MATHS': self.maths,
            'ENGLISH': self.english,
            'INFORMATICS PRACTICES': self.ip,
            'GENERAL NOTES': self.general_notes
        }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/plot', methods=['POST'])
def plot():
    plot_type = request.form['plot_type']
    theme = request.form['theme']
    
    # Fetch and sort school marks data
    school_marks = Marks.query.order_by(Marks.date.desc()).all()
    school_data = [mark.to_dict() for mark in school_marks]
    df_school = pd.DataFrame(school_data).sort_values(by='DATE', ascending=False) if school_data else pd.DataFrame()

    # Fetch and sort jee/main advance marks data
    jee_marks = JEEMarks.query.order_by(JEEMarks.date.desc()).all()
    jee_data = [mark.to_dict() for mark in jee_marks]
    df_jee = pd.DataFrame(jee_data).sort_values(by='DATE', ascending=False) if jee_data else pd.DataFrame()

    # Fetch and sort daily updates
    daily_updates = DailyUpdates.query.order_by(DailyUpdates.date.desc()).all()
    daily_data = [update.to_dict() for update in daily_updates]
    df_daily_updates = pd.DataFrame(daily_data).sort_values(by='DATE', ascending=False) if daily_data else pd.DataFrame()

    plot_html = ""
    school_plot_html = ""
    jee_plot_html = ""

    if plot_type == 'static':
        # Creating a static plot using Matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

        if not df_school.empty:
            # School marks plot
            ax1.plot(df_school['DATE'], df_school['PHYSICS'], marker='o', label='PHYSICS')
            ax1.plot(df_school['DATE'], df_school['CHEMISTRY'], marker='o', label='CHEMISTRY')
            ax1.plot(df_school['DATE'], df_school['MATHS'], marker='o', label='MATHS')
            ax1.plot(df_school['DATE'], df_school['ENGLISH'], marker='o', label='ENGLISH')
            ax1.plot(df_school['DATE'], df_school['IP'], marker='o', label='IP')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Marks')
            ax1.set_title('School Marks in Different Subjects Over Time')
            ax1.legend()
            ax1.grid(True)
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.set_title('No School Marks Data Available')
            ax1.axis('off')

        if not df_jee.empty:
            # JEE marks plot
            ax2.plot(df_jee['DATE'], df_jee['PHYSICS'], marker='o', label='PHYSICS')
            ax2.plot(df_jee['DATE'], df_jee['CHEMISTRY'], marker='o', label='CHEMISTRY')
            ax2.plot(df_jee['DATE'], df_jee['MATHS'], marker='o', label='MATHS')
            ax2.plot(df_jee['DATE'], df_jee['TOTAL'], marker='o', label='TOTAL')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Marks')
            ax2.set_title('JEE/Advance Test Marks Over Time')
            ax2.legend()
            ax2.grid(True)
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.set_title('No JEE/Advance Test Marks Data Available')
            ax2.axis('off')

        plt.tight_layout()

        # Save it to a temporary buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Embed the result in the html output.
        data_img = base64.b64encode(buf.read()).decode('ascii')
        plot_html = f'<img src="data:image/png;base64,{data_img}"/>'
    
    elif plot_type == 'interactive':
        # Setting the Plotly theme
        if theme == 'dark':
            pio.templates.default = "plotly_dark"
        else:
            pio.templates.default = "plotly_white"

        if not df_school.empty:
            # Creating an interactive plot using Plotly for school marks
            fig_school = px.line(df_school, x='DATE', y=['PHYSICS', 'CHEMISTRY', 'MATHS', 'ENGLISH', 'IP'], 
                                 labels={'value': 'Marks', 'variable': 'Subjects'}, title='School Marks in Different Subjects Over Time')
            fig_school.update_layout(legend_title_text='Subjects')
            school_plot_html = fig_school.to_html(full_html=False)

        if not df_jee.empty:
            # Creating an interactive plot using Plotly for JEE marks
            fig_jee = px.line(df_jee, x='DATE', y=['PHYSICS', 'CHEMISTRY', 'MATHS', 'TOTAL'], 
                              labels={'value': 'Marks', 'variable': 'Subjects'}, title='JEE/Advance Test Marks Over Time')
            fig_jee.update_layout(legend_title_text='Subjects')
            jee_plot_html = fig_jee.to_html(full_html=False)
        
        plot_html = school_plot_html + jee_plot_html
    
    return render_template('plot.html', plot_html=plot_html, school_plot_html=school_plot_html, jee_plot_html=jee_plot_html, school_data=df_school.to_dict('records'), jee_data=df_jee.to_dict('records'), daily_updates=df_daily_updates.to_dict('records'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check credentials (hardcoded for simplicity)
        if username == 'hanisntsolo' and password == 'zaq12wsx':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials"
    return render_template('login.html')
    
@app.route('/daily_update', methods=['GET', 'POST'])
def daily_update():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_physics = request.form['physics']
        new_chemistry = request.form['chemistry']
        new_maths = request.form['maths']
        new_english = request.form['english']
        new_ip = request.form['ip']
        new_general_notes = request.form['general_notes']

        mark = DailyUpdates.query.filter_by(date=new_date).first()
        if mark:
            if new_physics:
                mark.physics = new_physics
            if new_chemistry:
                mark.chemistry = new_chemistry
            if new_maths:
                mark.maths = new_maths
            if new_english:
                mark.english = new_english
            if new_ip:
                mark.ip = new_ip
            if new_general_notes:
                mark.general_notes = new_general_notes
        else:
            new_daily_update = DailyUpdates(
                date=new_date,
                physics=new_physics if new_physics else 'NA',
                chemistry=new_chemistry if new_chemistry else 'NA',
                maths=new_maths if new_maths else 'NA',
                english=new_english if new_english else 'NA',
                ip=new_ip if new_ip else 'NA',
                general_notes=new_general_notes if new_general_notes else 'NA'
            )
            db.session.add(new_daily_update)

        db.session.commit()
        return redirect(url_for('daily_update'))

    daily_updates = DailyUpdates.query.order_by(DailyUpdates.date.desc()).all()
    data = [update.to_dict() for update in daily_updates]
    if not data:
        data = None
    df = pd.DataFrame(data).sort_values(by='DATE', ascending=False) if data else pd.DataFrame()
    return render_template('daily_update.html', data=df.to_dict('records') if not df.empty else None)

  
@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_physics = int(request.form['physics'])
        new_chemistry = int(request.form['chemistry'])
        new_maths = int(request.form['maths'])
        new_english = int(request.form['english'])
        new_ip = int(request.form['ip'])

        mark = Marks.query.filter_by(date=new_date).first()
        if mark:
            mark.physics = new_physics
            mark.chemistry = new_chemistry
            mark.maths = new_maths
            mark.english = new_english
            mark.ip = new_ip
        else:
            new_mark = Marks(date=new_date, physics=new_physics, chemistry=new_chemistry, maths=new_maths, english=new_english, ip=new_ip)
            db.session.add(new_mark)
        
        db.session.commit()
        return redirect(url_for('update'))

    marks = Marks.query.order_by(Marks.date.desc()).all()
    data = [mark.to_dict() for mark in marks]
    if not data:
        data = None
    df = pd.DataFrame(data).sort_values(by='DATE', ascending=False) if data else pd.DataFrame()
    return render_template('update.html', data=df.to_dict('records') if not df.empty else None)

@app.route('/update_jee', methods=['GET', 'POST'])
def update_jee():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        new_physics = int(request.form['physics'])
        new_chemistry = int(request.form['chemistry'])
        new_maths = int(request.form['maths'])
        new_total = new_physics + new_chemistry + new_maths

        mark = JEEMarks.query.filter_by(date=new_date).first()
        if mark:
            mark.physics = new_physics
            mark.chemistry = new_chemistry
            mark.maths = new_maths
            mark.total = new_total
        else:
            new_mark = JEEMarks(date=new_date, physics=new_physics, chemistry=new_chemistry, maths=new_maths, total=new_total)
            db.session.add(new_mark)
        
        db.session.commit()
        return redirect(url_for('update_jee'))

    jee_marks = JEEMarks.query.order_by(JEEMarks.date.desc()).all()
    data = [mark.to_dict() for mark in jee_marks]
    if not data:
        data = None
    df = pd.DataFrame(data).sort_values(by='DATE', ascending=False) if data else pd.DataFrame()
    return render_template('update_jee.html', data=df.to_dict('records') if not df.empty else None)
    
@app.route('/delete', methods=['POST'])
def delete():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    date_to_delete = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    mark = Marks.query.filter_by(date=date_to_delete).first()
    if mark:
        db.session.delete(mark)
        db.session.commit()

    return redirect(url_for('update'))

@app.route('/delete_jee', methods=['POST'])
def delete_jee():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    date_to_delete = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    mark = JEEMarks.query.filter_by(date=date_to_delete).first()
    if mark:
        db.session.delete(mark)
        db.session.commit()

    return redirect(url_for('update_jee'))
    
@app.route('/delete_daily_status', methods=['POST'])
def delete_daily_status():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    date_to_delete = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    daily_status = DailyUpdates.query.filter_by(date=date_to_delete).first()
    if daily_status:
        db.session.delete(daily_status)
        db.session.commit()

    return redirect(url_for('daily_update'))
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5007)
