from __future__ import unicode_literals

import logging
import logging.config

import os

from flask import Flask
from flask import request


try:
    from urllib.parse import urlparse, unquote, parse_qsl, urlencode
except:
    from urlparse import urlparse, parse_qsl
    from urllib import unquote, urlencode


import requests


class ReverseProxied(object):

    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application

    snippet from http://flask.pocoo.org/snippets/35/
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

logging_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')

logging.config.fileConfig(logging_conf)

index_tpl = """
<html>
<head>
<title>dereferer</title>
</head>

<body>
  <h1>What is it?</h1>
  <p>This application let you remove http referer for links you visit.</p>
  <h1>How?</h1>
  <p>Simply use '{host_url}?' or '{host_url}?u=' in front of your url.</p>
  <p>Example : <a href='{host_url}?http://www.whatismyreferer.com/'>{host_url}?http://www.whatismyreferer.com/</a></p>
  <h1>Test it</h1>
  <p>
    <form action='{host_url}?'>
        <label for='u'>Enter an url : <label/>
        <input name='u' type='text' size='31' value='http://www.whatismyreferer.com'/>
        <input type='submit' value='Go'/>
    </form>
  </p>
</body>
</html>
"""

redirect_tpl = """
<html>
<head>
<title>redirecting...</title>
<meta http-equiv="refresh" content="0; URL={url}" />
</head>

<body>
<p>you are being redirected to<br />
  <a id="autoclick" rel="noreferrer" href="{url}">{url}</a></p>
</body>
<script language="JavaScript" type="text/javascript">
    window.setTimeout( document.getElementById('autoclick').click() , 1000 * 0.5);
</script>
</html>
"""


KNOWN_SHORTNERZ = (
    'goo.gl',
    'bit.ly',
    't.co',
    'ow.li',
    'tr.im',
    'is.gd',
    'tiny.cc',
    'tinyurl.com',
    'bit.do',
    'fb.me',
)


def _follow(url):
    """ Follows 301 and 302 redirect and extract location for url matches known
    shortners """
    try:
        urlp = urlparse(url)
    except Exception:
        app.logger.exception("Could not parse %s", url)
    else:
        if urlp.netloc not in ('localhost', '127.0.0.1', request.host)\
            and urlp.netloc in KNOWN_SHORTNERZ\
                and urlp.scheme:
            try:
                app.logger.info("Following %s", url)
                resp = requests.head(url, allow_redirects=False, timeout=1)
                if resp.ok and resp.status_code in (301, 302):
                    url = resp.headers.get('Location')
                    if not url:
                        # could not get location with 'L', try lowercase
                        # and fallback to original url
                        url = resp.headers.get('location', url)
                    app.logger.info("URL is a redirection. Next url %s", url)
            except Exception:
                app.logger.exception("Could not get head at url %s", url)
    return url


ANNOYING_PARAMS = (
    'utm_',
    'action_object_map', 'action_ref_map', 'action_type_map', 'fb_',
    '__scoop',
    'xtor',
)


def cleanup(url):
    url = _follow(url)
    # remove trackers params
    try:
        urlp = urlparse(url)
        # cleanup query param
        query = parse_qsl(urlp.query)
        # only if query is non empty and we manage to parse fragment as
        # key/value
        if urlp.query and query:
            for annoying in ANNOYING_PARAMS:
                query = [(x, y) for x, y in query if not x.startswith(annoying)]
            urlp = urlp._replace(
                query=urlencode(query),
            )

        # cleanup fragment param
        fragment = parse_qsl(urlp.fragment)
        # only if fragments is non empty and we manage to parse fragment as
        # key/value
        if urlp.fragment and fragment:
            for annoying in ANNOYING_PARAMS:
                fragment = [(x, y) for x, y in fragment if not x.startswith(annoying)]
            urlp = urlp._replace(
                fragment=urlencode(fragment),
            )
        url = urlp.geturl()
    except Exception:
        app.logger.exception("Problem cleaning url %s", url)

    app.logger.info("Final url %s", url)
    return url


@app.route("/", methods=['GET', ])
def index():
    if len(request.args):
        url = unquote(
            request.args.get('u', request.url.split('?')[-1])
        )
        return redirect_tpl.format(url=cleanup(url))
    return index_tpl.format(host_url=request.url)

app.logger.info("Up and running")

if __name__ == "__main__":
    app.run(debug=True)
