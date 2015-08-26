dereferer
===========

Stupid, simple, self-hostable, dereferer.

Why ?
-----
Using a dereferer is cool. A selfhosted one is better.



Installation from sources
--------------------------

   python setup.py install

Running in dev mode with manage.py
----------------------------------

    dereferer-manage runserver -p 8000


Running with gunicorn
----------------------

    gunicorn -w 4 dereferer:app


nginx setup examples
--------------------


In a sub location, with caching :

::

    location /d {
        rewrite ^/d/(.*)$ /$1 break;
        expires 1M;

        # with 'cache' a zone defined a nginx http level
        proxy_cache cache;

        proxy_cache_valid      200  15d;
        proxy_cache_use_stale  error timeout invalid_header updating http_500 http_502 http_503 http_504;

        proxy_pass  http://127.0.0.1:8000/;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /d;

    }


TODO
----
Fork, hack, PR welcomes.
