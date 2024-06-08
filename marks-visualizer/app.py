from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import pandas as pd
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample data
data = {
    'DATE': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01']),
    'PHYSICS': [85, 90, 78],
    'CHEMISTRY': [88, 85, 80],
    'MATHS': [95, 89, 92],
    'ENGLISH': [75, 80, 78],
    'IP': [80, 82, 85]
}
df = pd.DataFrame(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    plot_type = request.form['plot_type']
    theme = request.form['theme']

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
        new_date = pd.to_datetime(request.form['date'])
        new_physics = int(request.form['physics'])
        new_chemistry = int(request.form['chemistry'])
        new_maths = int(request.form['maths'])
        new_english = int(request.form['english'])
        new_ip = int(request.form['ip'])

        # Check if the date already exists
        if new_date in df['DATE'].values:
            df.loc[df['DATE'] == new_date, ['PHYSICS', 'CHEMISTRY', 'MATHS', 'ENGLISH', 'IP']] = [new_physics, new_chemistry, new_maths, new_english, new_ip]
        else:
            # Add new data
            new_data = {'DATE': new_date,
                        'PHYSICS': new_physics,
                        'CHEMISTRY': new_chemistry,
                        'MATHS': new_maths,
                        'ENGLISH': new_english,
                        'IP': new_ip}
            df = pd.concat([df, pd.DataFrame([new_data])]).sort_values(by='DATE')

        return redirect(url_for('index'))

    return render_template('update.html', data=df.to_dict('records'))

@app.route('/delete', methods=['POST'])
def delete():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    date_to_delete = pd.to_datetime(request.form['date'])
    global df
    df = df[df['DATE'] != date_to_delete]

    return redirect(url_for('update'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
