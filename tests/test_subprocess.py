# -*- Mode: Python -*-

import sys
import os
import unittest
import warnings

from gi.repository import GLib
from gi import PyGIDeprecationWarning


class TestProcess(unittest.TestCase):

    def test_deprecated_child_watch_no_data(self):
        def cb(pid, status):
            self.status = status
            self.loop.quit()

        self.status = None
        self.loop = GLib.MainLoop()
        argv = [sys.executable, '-c', 'import sys']
        pid, stdin, stdout, stderr = GLib.spawn_async(
            argv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
        pid.close()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            GLib.child_watch_add(pid, cb)
            self.assertTrue(issubclass(w[0].category, PyGIDeprecationWarning))
        self.loop.run()
        self.assertEqual(self.status, 0)

    def test_deprecated_child_watch_data_priority(self):
        def cb(pid, status, data):
            self.data = data
            self.status = status
            self.loop.quit()

        self.status = None
        self.data = None
        self.loop = GLib.MainLoop()
        argv = [sys.executable, '-c', 'import sys']
        pid, stdin, stdout, stderr = GLib.spawn_async(
            argv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
        pid.close()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            id = GLib.child_watch_add(pid, cb, 12345, GLib.PRIORITY_HIGH)
            self.assertTrue(issubclass(w[0].category, PyGIDeprecationWarning))
        self.assertEqual(self.loop.get_context().find_source_by_id(id).priority,
                         GLib.PRIORITY_HIGH)
        self.loop.run()
        self.assertEqual(self.data, 12345)
        self.assertEqual(self.status, 0)

    def test_deprecated_child_watch_data_priority_kwargs(self):
        def cb(pid, status, data):
            self.data = data
            self.status = status
            self.loop.quit()

        self.status = None
        self.data = None
        self.loop = GLib.MainLoop()
        argv = [sys.executable, '-c', 'import sys']
        pid, stdin, stdout, stderr = GLib.spawn_async(
            argv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
        pid.close()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            id = GLib.child_watch_add(pid, cb, priority=GLib.PRIORITY_HIGH, data=12345)
            self.assertTrue(issubclass(w[0].category, PyGIDeprecationWarning))
        self.assertEqual(self.loop.get_context().find_source_by_id(id).priority,
                         GLib.PRIORITY_HIGH)
        self.loop.run()
        self.assertEqual(self.data, 12345)
        self.assertEqual(self.status, 0)

    def test_child_watch_no_data(self):
        def cb(pid, status):
            self.status = status
            self.loop.quit()

        self.status = None
        self.loop = GLib.MainLoop()
        argv = [sys.executable, '-c', 'import sys']
        pid, stdin, stdout, stderr = GLib.spawn_async(
            argv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
        pid.close()
        id = GLib.child_watch_add(GLib.PRIORITY_HIGH, pid, cb)
        self.assertEqual(self.loop.get_context().find_source_by_id(id).priority,
                         GLib.PRIORITY_HIGH)
        self.loop.run()
        self.assertEqual(self.status, 0)

    def test_child_watch_with_data(self):
        def cb(pid, status, data):
            self.status = status
            self.data = data
            self.loop.quit()

        self.data = None
        self.status = None
        self.loop = GLib.MainLoop()
        argv = [sys.executable, '-c', 'import sys']
        pid, stdin, stdout, stderr = GLib.spawn_async(
            argv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
        self.assertEqual(stdin, None)
        self.assertEqual(stdout, None)
        self.assertEqual(stderr, None)
        pid.close()
        id = GLib.child_watch_add(GLib.PRIORITY_HIGH, pid, cb, 12345)
        self.assertEqual(self.loop.get_context().find_source_by_id(id).priority,
                         GLib.PRIORITY_HIGH)
        self.loop.run()
        self.assertEqual(self.data, 12345)
        self.assertEqual(self.status, 0)

    def test_spawn_async_fds(self):
        pid, stdin, stdout, stderr = GLib.spawn_async(
            ['cat'], flags=GLib.SpawnFlags.SEARCH_PATH, standard_input=True,
            standard_output=True, standard_error=True)
        os.write(stdin, b'hello world!\n')
        os.close(stdin)
        out = os.read(stdout, 50)
        os.close(stdout)
        err = os.read(stderr, 50)
        os.close(stderr)
        pid.close()
        self.assertEqual(out, b'hello world!\n')
        self.assertEqual(err, b'')

    def test_spawn_async_envp(self):
        pid, stdin, stdout, stderr = GLib.spawn_async(
            ['sh', '-c', 'echo $TEST_VAR'], ['TEST_VAR=moo!'],
            flags=GLib.SpawnFlags.SEARCH_PATH, standard_output=True)
        self.assertEqual(stdin, None)
        self.assertEqual(stderr, None)
        out = os.read(stdout, 50)
        os.close(stdout)
        pid.close()
        self.assertEqual(out, b'moo!\n')

    def test_backwards_compat_flags(self):
        self.assertEqual(GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                         GLib.SPAWN_DO_NOT_REAP_CHILD)
