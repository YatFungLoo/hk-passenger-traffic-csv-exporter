from flask import Flask, send_file, render_template, request, redirect, url_for
from grapher import flaskOutput
from datetime import datetime
from io import BytesIO

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve the input value (even though we're not doing anything with it)
        date_input = request.form.get('date')
        return redirect(url_for('download_csv', date=date_input))

    return render_template('index.html')


@app.route('/download')
def download_csv():
    # Get the date from the query parameter
    date_input = request.args.get('date')

    temp = flaskOutput(date_input)
    csv_buffer = BytesIO()
    temp.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)  # Reset buffer position to the beginning
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=str(date_input + '_HKPT')
    )


if __name__ == '__main__':
    app.run(debug=False)
