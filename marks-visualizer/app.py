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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    plot_type = request.form['plot_type']
    theme = request.form['theme']

    marks = Marks.query.order_by(Marks.date).all()
    data = [mark.to_dict() for mark in marks]
    df = pd.DataFrame(data).sort_values(by='DATE')

    if plot_type == 'static':
        # Creating a static plot using Matplotlib
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(df['DATE'], df['PHYSICS'], marker='o', label='PHYSICS')
        ax.plot(df['DATE'], df['CHEMISTRY'], marker='o', label='CHEMISTRY')
        ax.plot(df['DATE'], df['MATHS'], marker='o', label='MATHS')
        ax.plot(df['DATE'], df['ENGLISH'], marker='o', label='ENGLISH')
        ax.plot(df['DATE'], df['IP'], marker='o', label='IP')

        ax.set_xlabel('Date')
        ax.set_ylabel('Marks')
        ax.set_title('Marks in Different Subjects Over Time')
        ax.legend()
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
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

        # Creating an interactive plot using Plotly
        fig = px.line(df, x='DATE', y=['PHYSICS', 'CHEMISTRY', 'MATHS', 'ENGLISH', 'IP'], 
                      labels={'value': 'Marks', 'variable': 'Subjects'}, title='Marks in Different Subjects Over Time')
        fig.update_layout(legend_title_text='Subjects')
        plot_html = fig.to_html(full_html=False)
    
    return render_template('plot.html', plot_html=plot_html, data=df.to_html(index=False))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check credentials (hardcoded for simplicity)
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('update'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

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
        return redirect(url_for('index'))

    marks = Marks.query.order_by(Marks.date).all()
    data = [mark.to_dict() for mark in marks]
    df = pd.DataFrame(data).sort_values(by='DATE')
    return render_template('update.html', data=df.to_dict('records'))

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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5007)
