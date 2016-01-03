# Copyright (c) 2016  Brendan Molloy <brendan+freebsd@bbqsrc.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
import locale
import logging
import multiprocessing
import os
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('skog')

__version__ = "0.1.0"

_glyphs = namedtuple('Glyphs', ['leaf', 'leaf_end', 'leaf_arm', 'pipe'])(
    *("├└─│" if (locale.getlocale()[1] or '').upper() == "UTF-8" else "|`-|")
)

def extend_env(**kwargs):
    env = os.environ.copy()
    env.update(kwargs)
    return env

class TreeGenerator:
    def __init__(self, path, excludes=None, portsdir=None, cmd=None, max_depth=None):
        self.excludes = set(excludes or [])
        self.cache = {}
        self.mnt = path
        self.mnt_len = len(self.mnt) + 1
        self.cmd = ['make', '%s-depends-list' % (cmd or 'all')]
        self.env = extend_env(PORTSDIR=portsdir or path)
        self.pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.max_depth = max_depth or 2

    def strip_mount(self, path):
        if path.startswith(self.mnt):
            return path[self.mnt_len:]
        return path

    def _run_pool(self, port_path, depth=None):
        if depth is None:
            depth = 0
        elif depth == self.max_depth:
            return [('[+]', [])]
        path = os.path.join(self.mnt, port_path)
        data = subprocess.check_output(self.cmd, cwd=path, env=self.env)
        ports = data.decode().strip()

        if ports == '':
            return []

        ports = [port for port in \
                (self.strip_mount(port) for port in ports.split('\n')) \
                if port not in self.excludes]

        root = []
        for port in ports:
            if port in self.cache:
                logger.debug("Cache hit: %s -> %s" % (port_path, port))
                root.append((port, self.cache[port]))
            else:
                future = self.pool.submit(self._run_pool, port, depth+1)
                root.append((port, future))

        self.cache[port_path] = root
        return root

    def run(self, port_path):
        if port_path in self.cache:
            root = self.cache[port_path]
        else:
            root = self._run_pool(port_path)
        return root

def resolve_future(future):
    if not isinstance(future, list):
        return future.result()
    return future

def print_tree(nodes, depth=-1, prefix=None, max_depth=2):
    if depth == max_depth:
        print("%s %s%s[+]" % (''.join(prefix), _glyphs.leaf_end,
            _glyphs.leaf_arm))
        return
    nodes = resolve_future(nodes)

    if prefix is None:
        prefix = []

    last = len(nodes) - 1
    for i, node in enumerate(nodes):
        p = prefix[:]
        if depth == -1:
            print(node[0])
        elif i == last:
            print('%s %s%s%s' % (''.join(prefix), _glyphs.leaf_end,
                _glyphs.leaf_arm, node[0]))
            p.append('   ')
        else:
            print('%s %s%s%s' % (''.join(prefix), _glyphs.leaf,
                _glyphs.leaf_arm, node[0]))
            p.append(' %s ' % _glyphs.pipe)

        print_tree(node[1], depth + 1, p, max_depth)
