from flask import Flask, render_template, Markup, session, request
from scripts.layout import Layout
from scripts.sbf import sbf
app = Flask(__name__)

app.secret_key = 'spacial bloom filter'

CELL_NUM = 10
HASH_FAMILY = ['md5', 'sha256', 'sha1']

format_layout = Layout(CELL_NUM)
app.my_sbf = sbf(CELL_NUM, HASH_FAMILY)


@app.route('/index')
@app.route('/')
def index():
    app.my_sbf = sbf(CELL_NUM, HASH_FAMILY)
    sbf_table = format_layout.load_table(app.my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(app.my_sbf.get_stats())
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
    app.my_sbf.insert_from_file()
    app.my_sbf.update_stats()
    sbf_table = format_layout.load_table(app.my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(app.my_sbf.get_stats())

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['incorrect_values'] = format_layout.incorrect_areas(app.my_sbf.incorrect_values())

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(session.get('check_result_table')),
                           check_result_conclusion=Markup(session.get('check_result_conclusion')))


@app.route('/check_sbf', methods=['POST'])
def check_sbf():
    if request.method == 'POST':
        result = request.form
        value = result['sbf_check']

        check_result_table, check_result_conclusion = format_layout.load_check_result(value, app.my_sbf.check(value),
                                                                                      app.my_sbf.incorrect_values())
        sbf_table = format_layout.highlight_table(app.my_sbf.get_filter(), app.my_sbf.check(value))

        return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(session.get('sbf_stats')),
                               check_result_table=Markup(check_result_table),
                               check_result_conclusion=Markup(check_result_conclusion))


@app.route('/clear_sbf', methods=['POST'])
def clear_sbf():
    app.my_sbf.clear_filter()
    sbf_table = format_layout.load_table(app.my_sbf.get_filter())
    sbf_stats = format_layout.load_stats(app.my_sbf.get_stats())

    session['sbf_table'] = sbf_table
    session['sbf_stats'] = sbf_stats
    session['incorrect_values'] = '<tr><td></td><td></td><td></td><td></td></tr>'

    return render_template('index.html', sbf_table=Markup(sbf_table), sbf_stats=Markup(sbf_stats),
                           check_result_table=Markup(session.get('check_result_table')),
                           check_result_conclusion=Markup(session.get('check_result_conclusion')))


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


@app.route('/edit_details')
def edit_details():
    hash_family, hf_options = _hash_functions(app.my_sbf.get_hash_family())
    return render_template('edit-details.html', hash_family=Markup(hash_family), hf_options=Markup(hf_options))


@app.route('/reset_hash_family', methods=['POST'])
def reset_hash_family():
    if request.method == 'POST':
        default_hash_family = ['md5', 'sha256', 'sha1']
        hash_family, hf_options = _hash_functions(default_hash_family)

        app.my_sbf.clear_filter()
        app.my_sbf = sbf(CELL_NUM, default_hash_family)
        sbf_table = format_layout.load_table(app.my_sbf.get_filter())
        sbf_stats = format_layout.load_stats(app.my_sbf.get_stats())
        check_result_table, check_result_conclusion = format_layout.no_check_result()

        session['sbf_table'] = sbf_table
        session['sbf_stats'] = sbf_stats
        session['check_result_table'] = check_result_table
        session['check_result_conclusion'] = check_result_conclusion
        session['incorrect_values'] = '<tr><td></td><td></td><td></td><td></td></tr>'

        return render_template('edit-details.html', hash_family=Markup(hash_family), hf_options=Markup(hf_options))


@app.route('/back')
def back():
    return render_template('index.html', sbf_table=Markup(session.get('sbf_table')),
                           sbf_stats=Markup(session.get('sbf_stats')),
                           check_result_table=Markup(session.get('check_result_table')),
                           check_result_conclusion=Markup(session.get('check_result_conclusion')))


def _hash_functions(hash_fam):
    hf = format_layout.edit_details(hash_fam)
    allowed_hash_functions = app.my_sbf.allowed_hashes()
    if 'sha' in allowed_hash_functions:
        allowed_hash_functions.remove('sha')
    hfo = format_layout.hash_family_options(allowed_hash_functions)
    return hf, hfo


if __name__ == '__main__':
    app.run()
