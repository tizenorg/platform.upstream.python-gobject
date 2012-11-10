# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import unittest

import gi.overrides
from gi.repository import GLib, Gio


class TestGio(unittest.TestCase):
    def test_file_enumerator(self):
        self.assertEqual(Gio.FileEnumerator, gi.overrides.Gio.FileEnumerator)
        f = Gio.file_new_for_path("./")

        iter_info = []
        for info in f.enumerate_children("standard::*", 0, None):
            iter_info.append(info.get_name())

        next_info = []
        enumerator = f.enumerate_children("standard::*", 0, None)
        while True:
            info = enumerator.next_file(None)
            if info is None:
                break
            next_info.append(info.get_name())

        self.assertEqual(iter_info, next_info)

    def test_menu_item(self):
        menu = Gio.Menu()
        item = Gio.MenuItem()
        item.set_attribute([("label", "s", "Test"),
                            ("action", "s", "app.test")])
        menu.append_item(item)
        value = menu.get_item_attribute_value(0, "label", GLib.VariantType.new("s"))
        self.assertEqual("Test", value.unpack())
        value = menu.get_item_attribute_value(0, "action", GLib.VariantType.new("s"))
        self.assertEqual("app.test", value.unpack())


class TestGSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Gio.Settings('org.gnome.test')
        # we change the values in the tests, so set them to predictable start
        # value
        self.settings.reset('test-string')
        self.settings.reset('test-array')

    def test_native(self):
        self.assertTrue('test-array' in self.settings.list_keys())

        # get various types
        v = self.settings.get_value('test-boolean')
        self.assertEqual(v.get_boolean(), True)
        self.assertEqual(self.settings.get_boolean('test-boolean'), True)

        v = self.settings.get_value('test-string')
        self.assertEqual(v.get_string(), 'Hello')
        self.assertEqual(self.settings.get_string('test-string'), 'Hello')

        v = self.settings.get_value('test-array')
        self.assertEqual(v.unpack(), [1, 2])

        v = self.settings.get_value('test-tuple')
        self.assertEqual(v.unpack(), (1, 2))

        # set a value
        self.settings.set_string('test-string', 'World')
        self.assertEqual(self.settings.get_string('test-string'), 'World')

        self.settings.set_value('test-string', GLib.Variant('s', 'Goodbye'))
        self.assertEqual(self.settings.get_string('test-string'), 'Goodbye')

    def test_constructor(self):
        # default constructor uses path from schema
        self.assertEqual(self.settings.get_property('path'), '/tests/')

        # optional constructor arguments
        with_path = Gio.Settings('org.gnome.nopathtest', path='/mypath/')
        self.assertEqual(with_path.get_property('path'), '/mypath/')
        self.assertEqual(with_path['np-int'], 42)

    def test_override(self):
        # dictionary interface
        self.assertEqual(len(self.settings), 4)
        self.assertTrue('test-array' in self.settings)
        self.assertTrue('test-array' in self.settings.keys())
        self.assertFalse('nonexisting' in self.settings)
        self.assertFalse(4 in self.settings)
        self.assertEqual(bool(self.settings), True)

        # get various types
        self.assertEqual(self.settings['test-boolean'], True)
        self.assertEqual(self.settings['test-string'], 'Hello')
        self.assertEqual(self.settings['test-array'], [1, 2])
        self.assertEqual(self.settings['test-tuple'], (1, 2))

        self.assertRaises(KeyError, self.settings.__getitem__, 'unknown')
        self.assertRaises(KeyError, self.settings.__getitem__, 2)

        # set a value
        self.settings['test-string'] = 'Goodbye'
        self.assertEqual(self.settings['test-string'], 'Goodbye')
        self.settings['test-array'] = [3, 4, 5]
        self.assertEqual(self.settings['test-array'], [3, 4, 5])

        self.assertRaises(TypeError, self.settings.__setitem__, 'test-string', 1)
        self.assertRaises(KeyError, self.settings.__setitem__, 'unknown', 'moo')

    def test_empty(self):
        empty = Gio.Settings('org.gnome.empty', path='/tests/')
        self.assertEqual(len(empty), 0)
        self.assertEqual(bool(empty), True)
        self.assertEqual(empty.keys(), [])
