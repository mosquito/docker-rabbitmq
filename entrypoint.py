#!/usr/bin/env python
# encoding: utf-8
import sys
import os
from pwd import getpwnam
from StringIO import StringIO
from subprocess import Popen
import re
import signal

ENV = dict(os.environ)
ENV['RABBITMQ_LOG_BASE'] = '/data/log'
ENV['RABBITMQ_MNESIA_BASE'] = '/data/mnesia'
ENV['HOME'] = '/data'
ENV['LANG'] = 'en_US.UTF-8'

BINARY = '/usr/sbin/rabbitmq-server'
PREFIX = os.path.dirname(BINARY)
USER = 'rabbitmq'


def run(cmd, args, env=None, chdir=None, fork=False, user='root'):
    def su():
        n = getpwnam(user)
        os.setgid(n.pw_uid)
        os.setuid(n.pw_gid)

    if isinstance(args, (type(''), type(u''))):
        args = (args, )
    elif isinstance(args, list):
        args = tuple(args)

    if not env:
        env = dict(os.environ)

    if not chdir:
        chdir = os.path.dirname(cmd)

    os.chdir(chdir)

    print ('Trying to run %s %s' % (cmd, args))
    if fork:
        su()
        return os.execve(cmd, (cmd,) + tuple(args), env)
    else:
        return Popen((cmd,) + args, env=env, preexec_fn=su, cwd=chdir)


def ensure_line(fname, rexp, value):
    out = StringIO()
    exp = re.compile(rexp)
    with open(fname, 'r+') as f:
        c = 0
        for line in f:
            if exp.match(line) is not None:
                c += 1
                out.write("%s\n" % value)
            else:
                out.write("%s\n" % line)

        if not c:
            out.write("%s\n" % value)

    out.seek(0)
    with open(fname, 'w+') as f:
        f.write(out.read())


def main(command, *args):
    ensure_line('/etc/rabbitmq/rabbitmq.config', r"^\[\{rabbit", "[{rabbit, [{loopback_users, []}]}].")
    run('/usr/bin/mkdir', ('-p', '/data/mnesia', '/data/log')).wait()
    run('/usr/bin/chown', ('-R', 'rabbitmq:rabbitmq', '/data')).wait()

    nodes = filter(lambda x: bool(x), ENV.get('RABBITMQ_NODES', '').split(','))
    cluster_cookie = ENV.get('RABBITMQ_COOKIE', '')
    if cluster_cookie:
        with open(os.path.join('/data', '.erlang.cookie'), 'w+') as f:
            f.write('%s\n' % cluster_cookie)
        run('/usr/bin/chmod', ('600', os.path.join('/', 'data', '.erlang.cookie'))).wait()

    if nodes:
        for node in nodes:
            args = ['join_cluster']
            host = node.split('/', 1)
            if len(host) > 1:
                args.append('--%s' % host.pop())
            args.append(host.pop())
            run('/usr/sbin/rabbitmqctl', args, user=USER, env=ENV).wait()

    print ("Running server")
    return run('/usr/sbin/rabbitmq-server', args, fork=True, env=ENV, user=USER)


if __name__ == "__main__":
    exit(main(sys.argv[1:]))