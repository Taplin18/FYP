from flask import Flask, render_template, Markup, session, request
from scripts.layout import Layout
from scripts.sbf import sbf
app = Flask(__name__)

app.secret_key = 'any random string'

format_layout = Layout()
my_sbf = sbf(4, 'sha1', 3)


@app.route('/')
def index():
    sbf_table, sbf_stats, check_result = "", "", ""
    sbf_table = format_layout.load_initial_table()
    sbf_stats = format_layout.load_initial_stats()

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['check_result'] = check_result

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result=Markup(check_result))


@app.route('/import_sbf', methods=['POST'])
def import_sbf():
    check_result = session.get('check_result')
    sbf_table = ""

    my_sbf.insert_from_file()
    sbf_table = format_layout.load_table(my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(my_sbf.get_stats())

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result=Markup(check_result))


@app.route('/check_sbf', methods=['POST'])
def check_sbf():
    if request.method == 'POST':
        result = request.form

        sbf_table = session.get('sbf_table')
        sbf_stats = session.get('sbf_stats')

        check_result = format_layout.load_check_result(result['sbf_check'], my_sbf.check(result['sbf_check']))

        return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                               check_result=Markup(check_result))


if __name__ == '__main__':
    app.run(debug=True)
