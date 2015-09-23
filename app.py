from flask.ext.api import FlaskAPI
from flask import redirect
from flask import request
from flask import url_for
import re
import subprocess


app = FlaskAPI(__name__)


def _tab_list_str_to_dict(tab_str, request):
    matches = re.search(
        r'^\[(?P<window_id>\d+):(?P<tab_id>\d+)\](?P<tab_title>.+)$', tab_str
    )
    if matches is None:
        return {}
    tab = {
        'id': matches.group('tab_id'),
        'title': matches.group('tab_title'),
        'window': matches.group('window_id'),
    }
    tab['tab_view_url'] = '%stabs/%s' % (request.url_root, tab['id'])
    tab['title'] = tab['title'].strip()
    return tab


def _tab_info_str_to_dict(tab_str, request):
    tab_lines = tab_str.rstrip().split('\n')
    tab = {}

    for line in tab_lines:
        matches = re.search(
            r'^(?P<key>\w+):(?P<value>.+)$', line
        )
        key = unicode(matches.group('key').lower(), 'utf-8')
        value = unicode(matches.group('value'), 'utf-8')
        tab[key] = value

    tab['id'] = int(tab['id'])
    tab['title'] = tab['title'].strip()
    tab['tab_view_url'] = '%stabs/%s' % (request.url_root, tab['id'])

    return tab


@app.route('/tabs')
def tab_list():
    tabs = subprocess.check_output(
        ['chrome-cli', 'list', 'tabs']
    ).rstrip().split('\n')
    tabs = [_tab_list_str_to_dict(unicode(tab, 'utf-8'), request) for tab in tabs]
    return tabs


@app.route('/tabs/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tab_detail(id):
    tab = _tab_info_str_to_dict(
        subprocess.check_output(['chrome-cli', 'info', '-t', str(id)]),
        request
    )

    if request.method == 'DELETE':
        subprocess.check_call(['chrome-cli', 'close', '-t', str(id)])
        return {'message': 'Tab closed successfully'}

    if request.method == 'PUT':
        url = request.data.get('url')
        args = ['chrome-cli', 'open', str(url), '-t', str(id)]
        subprocess.check_call(args)
        return redirect(url_for('tab_detail', id=tab['id']))

    return tab


@app.route('/tabs/current', methods=['GET', 'PUT', 'DELETE'])
def tab_current():
    if request.method == 'DELETE':
        subprocess.check_call(['chrome-cli', 'close', '-t', str(id)])
        return {'message': 'Tab closed successfully'}

    current_tab = _tab_info_str_to_dict(
        subprocess.check_output(['chrome-cli', 'info']),
        request
    )
    return redirect(url_for('tab_detail', id=current_tab['id']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
