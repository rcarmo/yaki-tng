yaki-tng
========

A modern, revamped implementation of [Yaki][y].

## Main goals

* Move to a standard WSGI app model, using [Bottle][b] as both routing and templating engine
* Streamline the markup rendering pipeline
* Move all the cache management to an external process (Redis, Memcache, etc. - your choice)
* Split the indexer from the main body of code
* Get it running at insanely high speeds inside `uWSGI+gevent` or `Gunicorn+gevent` (and PyPy)

## Secondary Goals

* Refactor all the configuration to use JSON
* Refactor all the inline logic according to MVC patterns
* Provide a set of APIs for gathering data
* Increase resiliency (lower RAM footprint, better horizontal scaling, better fault tolerance, etc.)
* Python 3 support (eventually, I'm actually aiming for PyPy)

## Target Feature Set

* Support for (Multi)Markdown, Textile, raw HTML, etc.
* Flexible set of plugins
* Pygments integration (for technical documentation)
* Full-text indexing

## Batteries included

Yaki has always been designed around three simple rules:

* Pure Python
* No external dependencies - _everything_ is included
* No databases

All of these are, of course, applied within reason.


# Dev Notes

Before starting work, make sure you run:

    python tools/msgfmt.py lib/yaki/locale/en/LC_MESSAGES/yaki.po
    
...to create the translation file(s).

[b]: http://bottlepy.org
[y]: https://github.com/rcarmo/yaki