yaki-tng
========

A modern, revamped implementation of [Yaki][y].

## Main goals

* Move to a standard WSGI app model, using [Bottle][b] as both routing and templating engine
* Streamline the markup rendering pipeline
* Move all the cache management to an external process (Redis)
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
* No external dependencies - everything _ought_ to be included
* No databases

All of these are, of course, applied within reason.

Regrettably, and due to the various licensing requirements and the need to push development forward, most third-party dependencies were removed.

Yaki now provides an explicit `requirements.txt` file that makes it easy to install everything else you need, and a `Vagrantfile` to easily reproduce the development environment anywhere.


# Dev Notes

Yaki now requires Redis (since it's the only sensible way to share state among worker processes and saves a _lot_ of time in metadata housekeeping). A "mini" Redis server is included in the source tree, but it's a work in progress and only useful for basic testing. 

## Using Vagrant

The `Vagrantfile` that ships with Yaki assumes an Ubuntu (precise64) target, but should work fine with most modern Debian-based distros. At the time of this writing, it works with Vagrant 1.4 and the `vagrant-lxc` plugin, and sets up the following for you:

* Redis
* `mkvirtualenv` and a supporting `virtualenv` containing:
  * Celery
  * uWSGI
  * Whoosh
  * All the other miscellaneous dependencies listed in `requirements.txt`

If you decide to use `vagrant-lxc`, you can fetch a compatible box [from here](https://github.com/fgrehm/vagrant-lxc/wiki/Base-boxes#available-boxes).

## Coding

If you use the provided `Vagrantfile`, make sure you start your session with `workon yaki` to use the `virtualenv` it builds.

Before starting the development daemon, make sure you run:

    python tools/msgfmt.py lib/yaki/locale/en/LC_MESSAGES/yaki.po
    
...to create the translation file(s).

[b]: http://bottlepy.org
[y]: https://github.com/rcarmo/yaki
