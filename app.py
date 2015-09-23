from flask.ext.api import FlaskAPI
from flask.ext.api import status
from flask import redirect
from flask import request
from flask import url_for
import argparse
import re
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost')
parser.add_argument('--port', default=5000, type=int)
parser.add_argument(
    '--debug',
    default=False,
    action='store_true',
    help='Set the server in debug mode'
)

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


@app.route('/tabs', methods=['GET', 'POST'])
def tabs():
    """
    This view allows listing all Chrome tabs available and creating new ones.
    """
    if request.method == 'POST':
        url = request.data.get('url')

        if url is None:
            return {'message': 'No URL specified'}, status.HTTP_400_BAD_REQUEST

        args = ['chrome-cli', 'open', url.encode('utf-8')]
        subprocess.check_call(args)

        return {'message': 'Tab created successfully'}

    tabs = subprocess.check_output(
        ['chrome-cli', 'list', 'tabs']
    ).rstrip().split('\n')
    tabs = [_tab_list_str_to_dict(unicode(tab, 'utf-8'), request) for tab in tabs]
    return tabs


@app.route('/tabs/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tab_detail(id):
    """
    This view allows viewing the details of a specific tab, updating its URL
    or closing it.
    """
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
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
