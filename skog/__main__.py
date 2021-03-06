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

import argparse

import skog

def print_ports(ports, portsdir, excludes=None, max_depth=None, cmd=None):
    if excludes is not None and len(excludes) > 0:
        print("The following ports were not included in the tree:")
        print("  %s" % "\n  ".join(excludes))
        print()

    treegen = skog.TreeGenerator(portsdir, excludes,
        max_depth=max_depth, cmd=cmd)
    out = []
    for port in ports:
        try:
            tree = treegen.run(port)
        except KeyboardInterrupt:
            treegen.pool.shutdown(wait=False)
            return
        out.append((port, tree))

    skog.print_tree(out, max_depth=max_depth)

def main():
    p = argparse.ArgumentParser(prog='skog')
    p.add_argument('--version', action='version',
        version='%(prog)s {}'.format(skog.__version__))
    p.add_argument('-c', '--command', choices=['all', 'build', 'run', 'test'],
        default='all', help='Dependency list command to use'),
    p.add_argument('-d', '--depth', metavar='max-depth', dest='max_depth',
        default=2, type=int, help="Maximum tree depth")
    p.add_argument('-p', '--ports-dir', metavar='ports-dir', dest='portsdir',
        default='/usr/ports', help='Path to ports directory')
    p.add_argument('-x', action='append', metavar='exclude-port', default=[],
        dest='excludes', help='Ports to be excluded from tree')
    p.add_argument('ports', nargs='+', metavar='port',
        help='Ports to have a tree generated')

    args = p.parse_args()
    try:
        print_ports(args.ports, args.portsdir, args.excludes,
            max_depth=args.max_depth, cmd=args.command)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
