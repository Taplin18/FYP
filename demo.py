from flask import Flask, render_template, Markup, session, request
from scripts.layout import Layout
from scripts.sbf import sbf
app = Flask(__name__)

app.secret_key = 'spacial bloom filter'

HASH_FAMILY = ['md5', 'sha1', 'sha256']

format_layout = Layout(10)
app.my_sbf = sbf(HASH_FAMILY)


@app.route('/index')
@app.route('/')
def index():
    app.my_sbf = sbf(HASH_FAMILY)

    _set_session()

    return render_template('index.html', sbf_table=Markup(session.get('sbf_table')),
                           sbf_stats=Markup(session.get('sbf_stats')),
                           import_message=Markup(session.get('import_message')),
                           check_result_table=Markup(session.get('check_result_table')),
                           check_result_conclusion=Markup(session.get('check_result_conclusion')))


@app.route('/import_sbf', methods=['POST'])
def import_sbf():
    app.my_sbf.insert_from_file()
    app.my_sbf.update_stats()

    session['sbf_table'] = format_layout.load_table(app.my_sbf.get_filter())
    session['sbf_stats'] = format_layout.load_stats(app.my_sbf.get_stats())
    session['import_message'] = 'style="display: none"'
    session['fp_values'] = format_layout.false_positive_area(app.my_sbf.find_false_positives())
    session['incorrect_values'] = format_layout.incorrect_areas(app.my_sbf.incorrect_values())

    return render_template('index.html', sbf_table=Markup(session.get('sbf_table')),
                           sbf_stats=Markup(session.get('sbf_stats')),
                           import_message=Markup(session.get('import_message')),
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

        return render_template('index.html', sbf_table=Markup(sbf_table),
                               sbf_stats=Markup(session.get('sbf_stats')),
                               import_message=Markup(session.get('import_message')),
                               check_result_table=Markup(check_result_table),
                               check_result_conclusion=Markup(check_result_conclusion))


@app.route('/clear_sbf', methods=['POST'])
def clear_sbf():
    app.my_sbf.clear_filter()
    _set_session()

    return render_template('index.html', sbf_table=Markup(session.get('sbf_table')),
                           sbf_stats=Markup(session.get('sbf_stats')),
                           import_message=Markup(session.get('import_message')),
                           check_result_table=Markup(session.get('check_result_table')),
                           check_result_conclusion=Markup(session.get('check_result_conclusion')))


@app.route('/reset_hash_family', methods=['POST'])
def reset_hash_family():
    if request.method == 'POST':
        default_hash_family = ['md5', 'sha256', 'sha1']
        hash_family, hf_options = _hash_functions(default_hash_family)

        app.my_sbf.clear_filter()
        app.my_sbf = sbf(default_hash_family)
        _set_session()

        return render_template('edit-details.html', hash_family=Markup(hash_family), hf_options=Markup(hf_options))


@app.route('/update_hash_family', methods=['POST'])
def update_hash_family():
    if request.method == 'POST':
        hash_family, hf_options = _hash_functions(request.form.getlist('hf'))

        app.my_sbf.clear_filter()
        app.my_sbf = sbf(request.form.getlist('hf'))
        _set_session()

        return render_template('edit-details.html', hash_family=Markup(hash_family), hf_options=Markup(hf_options))


@app.route('/back')
def back():
    return render_template('index.html', sbf_table=Markup(session.get('sbf_table')),
                           sbf_stats=Markup(session.get('sbf_stats')),
                           import_message=Markup(session.get('import_message')),
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
    return render_template('values.html', incorrect_values=Markup(session.get('incorrect_values')),
                           import_message=Markup(session.get('import_message')),
                           fp_values=Markup(session.get('fp_values')))


@app.route('/edit_details')
def edit_details():
    hash_family, hf_options = _hash_functions(app.my_sbf.get_hash_family())
    return render_template('edit-details.html', hash_family=Markup(hash_family), hf_options=Markup(hf_options))


def _set_session():
    session['sbf_table'] = format_layout.load_table(app.my_sbf.get_filter())
    session['sbf_stats'] = format_layout.load_stats(app.my_sbf.get_stats())
    session['import_message'] = 'style="display: display"'

    check_result_table, check_result_conclusion = format_layout.no_check_result()

    session['check_result_table'] = check_result_table
    session['check_result_conclusion'] = check_result_conclusion
    session['incorrect_values'] = '<tr><td></td><td></td><td></td><td></td></tr>'
    session['fp_values'] = '<tr><td></td><td></td><td></td></tr>'


def _hash_functions(hash_fam):
    hf = format_layout.edit_details(hash_fam)
    allowed_hash_functions = app.my_sbf.allowed_hashes()
    hfo = format_layout.hash_family_options(allowed_hash_functions)
    return hf, hfo


if __name__ == '__main__':
    app.run()
