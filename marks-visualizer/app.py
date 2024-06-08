from flask import Flask, render_template_string
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
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

    # Creating an interactive plot using Plotly
    fig = px.line(df, x='DATE', y=['PHYSICS', 'CHEMISTRY', 'MATHS', 'ENGLISH', 'IP'], 
                  labels={'value': 'Marks', 'variable': 'Subjects'}, title='Marks in Different Subjects Over Time')
    fig.update_layout(legend_title_text='Subjects')
    graph_html = fig.to_html(full_html=False)

    # Render the HTML
    return render_template_string('''
        <html>
        <head>
            <title>Interactive Marks Visualization</title>
        </head>
        <body>
            <h1>Marks in Different Subjects Over Time</h1>
            <div>{{ graph_html | safe }}</div>
        </body>
        </html>
    ''', graph_html=graph_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
