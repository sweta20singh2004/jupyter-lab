from flask import Flask, render_template_string, request
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    # Render the HTML with a form to choose between static and interactive
    return render_template_string('''
        <html>
        <head>
            <title>Marks Visualization</title>
        </head>
        <body>
            <h1>Marks in Different Subjects Over Time</h1>
            <form action="/plot" method="post">
                <label for="plot_type">Choose plot type:</label>
                <select id="plot_type" name="plot_type">
                    <option value="static">Static</option>
                    <option value="interactive">Interactive</option>
                </select>
                <input type="submit" value="Generate Plot">
            </form>
        </body>
        </html>
    ''')

@app.route('/plot', methods=['POST'])
def plot():
    plot_type = request.form['plot_type']
    
    # Manually provided data
    dates = ['2023-01-01', '2023-02-01', '2023-03-01']
    physics = [85, 90, 78]
    chemistry = [88, 85, 80]
    maths = [95, 89, 92]
    english = [75, 80, 78]
    ip = [80, 82, 85]

    # Creating a dataframe with the provided data
    data = {
        'DATE': pd.to_datetime(dates),
        'PHYSICS': physics,
        'CHEMISTRY': chemistry,
        'MATHS': maths,
        'ENGLISH': english,
        'IP': ip
    }
    df = pd.DataFrame(data)

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
        data = base64.b64encode(buf.read()).decode('ascii')
        plot_html = f'<img src="data:image/png;base64,{data}"/>'
    
    elif plot_type == 'interactive':
        # Creating an interactive plot using Plotly
        fig = px.line(df, x='DATE', y=['PHYSICS', 'CHEMISTRY', 'MATHS', 'ENGLISH', 'IP'], 
                      labels={'value': 'Marks', 'variable': 'Subjects'}, title='Marks in Different Subjects Over Time')
        fig.update_layout(legend_title_text='Subjects')
        plot_html = fig.to_html(full_html=False)
    
    return render_template_string('''
        <html>
        <head>
            <title>Marks Visualization</title>
        </head>
        <body>
            <h1>Marks in Different Subjects Over Time</h1>
            <div>{{ plot_html | safe }}</div>
            <a href="/">Back to Choose Plot Type</a>
        </body>
        </html>
    ''', plot_html=plot_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
