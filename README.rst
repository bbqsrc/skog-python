skog
====

A tool to generate human-readable trees of dependencies of a FreeBSD port.

Usage
-----

Command-line tool
~~~~~~~~~~~~~~~~~

::

    usage: skog [-h] [--version] [-p ports-dir] [-x exclude-port] port [port ...]

    positional arguments:
      port                  Ports to have a tree generated

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -p ports-dir, --ports-dir ports-dir
                            Path to ports directory
      -x exclude-port       Ports to be excluded from tree

License
-------

BSD 2-clause. See LICENSE.
