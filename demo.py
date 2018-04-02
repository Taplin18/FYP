from flask import Flask, render_template, Markup, session, request
from scripts.layout import Layout
from scripts.sbf import sbf
app = Flask(__name__)

app.secret_key = 'any random string'

CELL_NUM = 10
HASH_FAM = ['md5', 'SHA256', 'sha1']

format_layout = Layout(CELL_NUM)
my_sbf = sbf(CELL_NUM, HASH_FAM)


@app.route('/index')
@app.route('/')
def index():
    my_sbf.clear_filter()
    sbf_table = format_layout.load_table(my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(my_sbf.get_stats())
    check_result_table, check_result_conclusion = format_layout.no_check_result()

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['check_result_table'] = check_result_table
    session['check_result_conclusion'] = check_result_conclusion
    session['incorrect_values'] = '<tr><td></td><td></td><td></td><td></td></tr>'

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(check_result_table),
                           check_result_conclusion=Markup(check_result_conclusion))


@app.route('/import_sbf', methods=['POST'])
def import_sbf():
    check_result_table = session.get('check_result_table')
    check_result_conclusion = session.get('check_result_conclusion')

    my_sbf.insert_from_file()
    my_sbf.update_stats()
    sbf_table = format_layout.load_table(my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(my_sbf.get_stats())

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['incorrect_values'] = format_layout.incorrect_areas(my_sbf.incorrect_values())

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(check_result_table),
                           check_result_conclusion=Markup(check_result_conclusion))


@app.route('/check_sbf', methods=['POST'])
def check_sbf():
    if request.method == 'POST':
        result = request.form
        value = result['sbf_check']

        sbf_stats = session.get('sbf_stats')
        check_result_table, check_result_conclusion = format_layout.load_check_result(value, my_sbf.check(value),
                                                                                      my_sbf.incorrect_values())
        sbf_table = format_layout.highlight_table(my_sbf.get_filter(), my_sbf.check(value))

        return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                               check_result_table=Markup(check_result_table),
                               check_result_conclusion=Markup(check_result_conclusion))


@app.route('/clear_sbf', methods=['POST'])
def clear_sbf():
    check_result_table = session.get('check_result_table')
    check_result_conclusion = session.get('check_result_conclusion')

    my_sbf.clear_filter()
    sbf_table = format_layout.load_table(my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(my_sbf.get_stats())

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['incorrect_values'] = '<tr><td></td><td></td><td></td><td></td></tr>'

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(check_result_table),
                           check_result_conclusion=Markup(check_result_conclusion))


@app.route('/cork_csv')
def cork_csv():
    csv_table = format_layout.csv_table()
    return render_template('cork-csv.html', csv_table=Markup(csv_table))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/values')
def values():
    incorrect_values = session.get('incorrect_values')
    return render_template('values.html', incorrect_values=Markup(incorrect_values))


@app.route('/back')
def back():
    sbf_table = session.get('sbf_table')
    sbf_stats = session.get('sbf_stats')
    check_result_table = session.get('check_result_table')
    check_result_conclusion = session.get('check_result_conclusion')

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(check_result_table),
                           check_result_conclusion=Markup(check_result_conclusion))


if __name__ == '__main__':
    app.run()
