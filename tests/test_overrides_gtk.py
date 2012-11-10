# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import unittest
import ctypes
import sys

from compathelper import _unicode, _bytes

import gi.overrides
import gi.types
from gi.repository import GLib, GObject

try:
    from gi.repository import GdkPixbuf, Gdk, Gtk
    Gtk  # pyflakes
except ImportError:
    Gtk = None


class RawTreeIter(ctypes.Structure):
    """Class used for testing Gtk.TreeIter raw data."""
    _fields_ = [('stamp', ctypes.c_int),
                ('user_data', ctypes.c_void_p),
                ('user_data2', ctypes.c_void_p),
                ('user_data3', ctypes.c_void_p)]

    @classmethod
    def from_iter(cls, iter):
        offset = sys.getsizeof(object())  # size of PyObject_HEAD
        return ctypes.POINTER(cls).from_address(id(iter) + offset)


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestGtk(unittest.TestCase):
    def test_container(self):
        box = Gtk.Box()
        self.assertTrue(isinstance(box, Gtk.Box))
        self.assertTrue(isinstance(box, Gtk.Container))
        self.assertTrue(isinstance(box, Gtk.Widget))
        self.assertTrue(box)
        label = Gtk.Label()
        label2 = Gtk.Label()
        box.add(label)
        box.add(label2)
        self.assertTrue(label in box)
        self.assertTrue(label2 in box)
        self.assertEqual(len(box), 2)
        self.assertTrue(box)
        l = [x for x in box]
        self.assertEqual(l, [label, label2])

    def test_actions(self):
        self.assertEqual(Gtk.Action, gi.overrides.Gtk.Action)
        self.assertRaises(TypeError, Gtk.Action)
        action = Gtk.Action("test", "Test", "Test Action", Gtk.STOCK_COPY)
        self.assertEqual(action.get_name(), "test")
        self.assertEqual(action.get_label(), "Test")
        self.assertEqual(action.get_tooltip(), "Test Action")
        self.assertEqual(action.get_stock_id(), Gtk.STOCK_COPY)

        self.assertEqual(Gtk.RadioAction, gi.overrides.Gtk.RadioAction)
        self.assertRaises(TypeError, Gtk.RadioAction)
        action = Gtk.RadioAction("test", "Test", "Test Action", Gtk.STOCK_COPY, 1)
        self.assertEqual(action.get_name(), "test")
        self.assertEqual(action.get_label(), "Test")
        self.assertEqual(action.get_tooltip(), "Test Action")
        self.assertEqual(action.get_stock_id(), Gtk.STOCK_COPY)
        self.assertEqual(action.get_current_value(), 1)

    def test_actiongroup(self):
        self.assertEqual(Gtk.ActionGroup, gi.overrides.Gtk.ActionGroup)
        self.assertRaises(TypeError, Gtk.ActionGroup)

        action_group = Gtk.ActionGroup(name='TestActionGroup')
        callback_data = "callback data"

        def test_action_callback_data(action, user_data):
            self.assertEqual(user_data, callback_data)

        def test_radio_action_callback_data(action, current, user_data):
            self.assertEqual(user_data, callback_data)

        action_group.add_actions([
            ('test-action1', None, 'Test Action 1',
             None, None, test_action_callback_data),
            ('test-action2', Gtk.STOCK_COPY, 'Test Action 2',
             None, None, test_action_callback_data)], callback_data)
        action_group.add_toggle_actions([
            ('test-toggle-action1', None, 'Test Toggle Action 1',
             None, None, test_action_callback_data, False),
            ('test-toggle-action2', Gtk.STOCK_COPY, 'Test Toggle Action 2',
             None, None, test_action_callback_data, True)], callback_data)
        action_group.add_radio_actions([
            ('test-radio-action1', None, 'Test Radio Action 1'),
            ('test-radio-action2', Gtk.STOCK_COPY, 'Test Radio Action 2')], 1,
            test_radio_action_callback_data,
            callback_data)

        expected_results = [('test-action1', Gtk.Action),
                            ('test-action2', Gtk.Action),
                            ('test-toggle-action1', Gtk.ToggleAction),
                            ('test-toggle-action2', Gtk.ToggleAction),
                            ('test-radio-action1', Gtk.RadioAction),
                            ('test-radio-action2', Gtk.RadioAction)]

        for action in action_group.list_actions():
            a = (action.get_name(), type(action))
            self.assertTrue(a in expected_results)
            expected_results.remove(a)
            action.activate()

    def test_uimanager(self):
        self.assertEqual(Gtk.UIManager, gi.overrides.Gtk.UIManager)
        ui = Gtk.UIManager()
        ui.add_ui_from_string("""<ui>
    <menubar name="menubar1"></menubar>
</ui>
"""
)
        menubar = ui.get_widget("/menubar1")
        self.assertEqual(type(menubar), Gtk.MenuBar)

        ag = Gtk.ActionGroup(name="ag1")
        ui.insert_action_group(ag)
        ag2 = Gtk.ActionGroup(name="ag2")
        ui.insert_action_group(ag2)
        groups = ui.get_action_groups()
        self.assertEqual(ag, groups[-2])
        self.assertEqual(ag2, groups[-1])

    def test_builder(self):
        self.assertEqual(Gtk.Builder, gi.overrides.Gtk.Builder)

        class SignalTest(GObject.GObject):
            __gtype_name__ = "GIOverrideSignalTest"
            __gsignals__ = {
                "test-signal": (GObject.SignalFlags.RUN_FIRST,
                                None,
                                []),
            }

        class SignalCheck:
            def __init__(self):
                self.sentinel = 0
                self.after_sentinel = 0

            def on_signal_1(self, *args):
                self.sentinel += 1
                self.after_sentinel += 1

            def on_signal_3(self, *args):
                self.sentinel += 3

            def on_signal_after(self, *args):
                if self.after_sentinel == 1:
                    self.after_sentinel += 1

        signal_checker = SignalCheck()
        builder = Gtk.Builder()

        # add object1 to the builder
        builder.add_from_string("""
<interface>
  <object class="GIOverrideSignalTest" id="object1">
      <signal name="test-signal" after="yes" handler="on_signal_after" />
      <signal name="test-signal" handler="on_signal_1" />
  </object>
</interface>
""")

        # only add object3 to the builder
        builder.add_objects_from_string("""
<interface>
  <object class="GIOverrideSignalTest" id="object2">
      <signal name="test-signal" handler="on_signal_2" />
  </object>
  <object class="GIOverrideSignalTest" id="object3">
      <signal name="test-signal" handler="on_signal_3" />
  </object>
  <object class="GIOverrideSignalTest" id="object4">
      <signal name="test-signal" handler="on_signal_4" />
  </object>
</interface>
""", ['object3'])

        # hook up signals
        builder.connect_signals(signal_checker)

        # call their notify signals and check sentinel
        objects = builder.get_objects()
        self.assertEqual(len(objects), 2)
        for obj in objects:
            obj.emit('test-signal')

        self.assertEqual(signal_checker.sentinel, 4)
        self.assertEqual(signal_checker.after_sentinel, 2)

    def test_window(self):
        # standard Window
        w = Gtk.Window()
        self.assertEqual(w.get_property('type'), Gtk.WindowType.TOPLEVEL)

        # type works as keyword argument
        w = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.assertEqual(w.get_property('type'), Gtk.WindowType.POPUP)

        # pygtk compatible positional argument
        w = Gtk.Window(Gtk.WindowType.POPUP)
        self.assertEqual(w.get_property('type'), Gtk.WindowType.POPUP)

        class TestWindow(Gtk.Window):
            __gtype_name__ = "TestWindow"

        # works from builder
        builder = Gtk.Builder()
        builder.add_from_string('''
<interface>
  <object class="GtkWindow" id="win">
    <property name="type">popup</property>
  </object>
  <object class="TestWindow" id="testwin">
  </object>
  <object class="TestWindow" id="testpop">
    <property name="type">popup</property>
  </object>
</interface>''')
        self.assertEqual(builder.get_object('win').get_property('type'),
                         Gtk.WindowType.POPUP)
        self.assertEqual(builder.get_object('testwin').get_property('type'),
                         Gtk.WindowType.TOPLEVEL)
        self.assertEqual(builder.get_object('testpop').get_property('type'),
                         Gtk.WindowType.POPUP)

    def test_dialogs(self):
        self.assertEqual(Gtk.Dialog, gi.overrides.Gtk.Dialog)
        self.assertEqual(Gtk.AboutDialog, gi.overrides.Gtk.AboutDialog)
        self.assertEqual(Gtk.MessageDialog, gi.overrides.Gtk.MessageDialog)
        self.assertEqual(Gtk.ColorSelectionDialog, gi.overrides.Gtk.ColorSelectionDialog)
        self.assertEqual(Gtk.FileChooserDialog, gi.overrides.Gtk.FileChooserDialog)
        self.assertEqual(Gtk.FontSelectionDialog, gi.overrides.Gtk.FontSelectionDialog)
        self.assertEqual(Gtk.RecentChooserDialog, gi.overrides.Gtk.RecentChooserDialog)

        # Gtk.Dialog
        dialog = Gtk.Dialog(title='Foo',
                            flags=Gtk.DialogFlags.MODAL,
                            buttons=('test-button1', 1))
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))

        dialog.add_buttons('test-button2', 2, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        self.assertEqual('Foo', dialog.get_title())
        self.assertTrue(dialog.get_modal())
        button = dialog.get_widget_for_response(1)
        self.assertEqual('test-button1', button.get_label())
        button = dialog.get_widget_for_response(2)
        self.assertEqual('test-button2', button.get_label())
        button = dialog.get_widget_for_response(Gtk.ResponseType.CLOSE)
        self.assertEqual(Gtk.STOCK_CLOSE, button.get_label())

        # Gtk.AboutDialog
        dialog = Gtk.AboutDialog()
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))

        # Gtk.MessageDialog
        dialog = Gtk.MessageDialog(title='message dialog test',
                                   flags=Gtk.DialogFlags.MODAL,
                                   buttons=Gtk.ButtonsType.OK,
                                   message_format='dude!')
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))

        self.assertEqual('message dialog test', dialog.get_title())
        self.assertTrue(dialog.get_modal())
        text = dialog.get_property('text')
        self.assertEqual('dude!', text)

        dialog.format_secondary_text('2nd text')
        self.assertEqual(dialog.get_property('secondary-text'), '2nd text')
        self.assertFalse(dialog.get_property('secondary-use-markup'))

        dialog.format_secondary_markup('2nd markup')
        self.assertEqual(dialog.get_property('secondary-text'), '2nd markup')
        self.assertTrue(dialog.get_property('secondary-use-markup'))

        # Gtk.ColorSelectionDialog
        dialog = Gtk.ColorSelectionDialog("color selection dialog test")
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))
        self.assertEqual('color selection dialog test', dialog.get_title())

        # Gtk.FileChooserDialog
        dialog = Gtk.FileChooserDialog(title='file chooser dialog test',
                                       buttons=('test-button1', 1),
                                       action=Gtk.FileChooserAction.SAVE)
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))

        dialog.add_buttons('test-button2', 2, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.assertEqual('file chooser dialog test', dialog.get_title())
        button = dialog.get_widget_for_response(1)
        self.assertEqual('test-button1', button.get_label())
        button = dialog.get_widget_for_response(2)
        self.assertEqual('test-button2', button.get_label())
        button = dialog.get_widget_for_response(Gtk.ResponseType.CLOSE)
        self.assertEqual(Gtk.STOCK_CLOSE, button.get_label())
        action = dialog.get_property('action')
        self.assertEqual(Gtk.FileChooserAction.SAVE, action)

        # Gtk.FontSelectionDialog
        dialog = Gtk.ColorSelectionDialog("font selection dialog test")
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))
        self.assertEqual('font selection dialog test', dialog.get_title())

        # Gtk.RecentChooserDialog
        test_manager = Gtk.RecentManager()
        dialog = Gtk.RecentChooserDialog(title='recent chooser dialog test',
                                         buttons=('test-button1', 1),
                                         manager=test_manager)
        self.assertTrue(isinstance(dialog, Gtk.Dialog))
        self.assertTrue(isinstance(dialog, Gtk.Window))

        dialog.add_buttons('test-button2', 2, Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.assertEqual('recent chooser dialog test', dialog.get_title())
        button = dialog.get_widget_for_response(1)
        self.assertEqual('test-button1', button.get_label())
        button = dialog.get_widget_for_response(2)
        self.assertEqual('test-button2', button.get_label())
        button = dialog.get_widget_for_response(Gtk.ResponseType.CLOSE)
        self.assertEqual(Gtk.STOCK_CLOSE, button.get_label())

    class TestClass(GObject.GObject):
        __gtype_name__ = "GIOverrideTreeAPITest"

        def __init__(self, tester, int_value, string_value):
            super(TestGtk.TestClass, self).__init__()
            self.tester = tester
            self.int_value = int_value
            self.string_value = string_value

        def check(self, int_value, string_value):
            self.tester.assertEqual(int_value, self.int_value)
            self.tester.assertEqual(string_value, self.string_value)

    def test_buttons(self):
        self.assertEqual(Gtk.Button, gi.overrides.Gtk.Button)

        # test Gtk.Button
        button = Gtk.Button()
        self.assertTrue(isinstance(button, Gtk.Button))
        self.assertTrue(isinstance(button, Gtk.Container))
        self.assertTrue(isinstance(button, Gtk.Widget))
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        self.assertEqual(Gtk.STOCK_CLOSE, button.get_label())
        self.assertTrue(button.get_use_stock())
        self.assertTrue(button.get_use_underline())

        # test Gtk.Button use_stock
        button = Gtk.Button(label=Gtk.STOCK_CLOSE, use_stock=True, use_underline=True)
        self.assertEqual(Gtk.STOCK_CLOSE, button.get_label())
        self.assertTrue(button.get_use_stock())
        self.assertTrue(button.get_use_underline())

        # test Gtk.LinkButton
        self.assertRaises(TypeError, Gtk.LinkButton)
        button = Gtk.LinkButton('http://www.Gtk.org', 'Gtk')
        self.assertTrue(isinstance(button, Gtk.Button))
        self.assertTrue(isinstance(button, Gtk.Container))
        self.assertTrue(isinstance(button, Gtk.Widget))
        self.assertEqual('http://www.Gtk.org', button.get_uri())
        self.assertEqual('Gtk', button.get_label())

    def test_inheritance(self):
        for name in gi.overrides.Gtk.__all__:
            over = getattr(gi.overrides.Gtk, name)
            for element in dir(Gtk):
                try:
                    klass = getattr(Gtk, element)
                    info = klass.__info__
                except (NotImplementedError, AttributeError):
                    continue

                # Get all parent classes and interfaces klass inherits from
                if isinstance(info, gi.types.ObjectInfo):
                    classes = list(info.get_interfaces())
                    parent = info.get_parent()
                    while parent.get_name() != "Object":
                        classes.append(parent)
                        parent = parent.get_parent()
                    classes = [kl for kl in classes if kl.get_namespace() == "Gtk"]
                else:
                    continue

                for kl in classes:
                    if kl.get_name() == name:
                        self.assertTrue(issubclass(klass, over,),
                                        "%r does not inherit from override %r" % (klass, over,))

    def test_editable(self):
        self.assertEqual(Gtk.Editable, gi.overrides.Gtk.Editable)

        # need to use Gtk.Entry because Editable is an interface
        entry = Gtk.Entry()
        pos = entry.insert_text('HeWorld', 0)
        self.assertEqual(pos, 7)
        pos = entry.insert_text('llo ', 2)
        self.assertEqual(pos, 6)
        text = entry.get_chars(0, 11)
        self.assertEqual('Hello World', text)

    def test_label(self):
        label = Gtk.Label(label='Hello')
        self.assertTrue(isinstance(label, Gtk.Widget))
        self.assertEqual(label.get_text(), 'Hello')

    def adjustment_check(self, adjustment, value=0.0, lower=0.0, upper=0.0,
                         step_increment=0.0, page_increment=0.0, page_size=0.0):
        self.assertEqual(adjustment.get_value(), value)
        self.assertEqual(adjustment.get_lower(), lower)
        self.assertEqual(adjustment.get_upper(), upper)
        self.assertEqual(adjustment.get_step_increment(), step_increment)
        self.assertEqual(adjustment.get_page_increment(), page_increment)
        self.assertEqual(adjustment.get_page_size(), page_size)

    def test_adjustment(self):
        adjustment = Gtk.Adjustment(1, 0, 6, 4, 5, 3)
        self.adjustment_check(adjustment, 1, 0, 6, 4, 5, 3)

        adjustment = Gtk.Adjustment(1, 0, 6, 4, 5)
        self.adjustment_check(adjustment, 1, 0, 6, 4, 5)

        adjustment = Gtk.Adjustment(1, 0, 6, 4)
        self.adjustment_check(adjustment, 1, 0, 6, 4)

        adjustment = Gtk.Adjustment(1, 0, 6)
        self.adjustment_check(adjustment, 1, 0, 6)

        adjustment = Gtk.Adjustment()
        self.adjustment_check(adjustment)

        adjustment = Gtk.Adjustment(value=1, lower=0, upper=6,
                                    step_increment=4, page_increment=5, page_size=3)
        self.adjustment_check(adjustment, 1, 0, 6, 4, 5, 3)

    def test_table(self):
        table = Gtk.Table()
        self.assertTrue(isinstance(table, Gtk.Table))
        self.assertTrue(isinstance(table, Gtk.Container))
        self.assertTrue(isinstance(table, Gtk.Widget))
        self.assertEqual(table.get_size(), (1, 1))
        self.assertEqual(table.get_homogeneous(), False)
        table = Gtk.Table(2, 3)
        self.assertEqual(table.get_size(), (2, 3))
        self.assertEqual(table.get_homogeneous(), False)
        table = Gtk.Table(2, 3, True)
        self.assertEqual(table.get_size(), (2, 3))
        self.assertEqual(table.get_homogeneous(), True)

        # Test PyGTK interface
        table = Gtk.Table(rows=3, columns=2)
        self.assertEqual(table.get_size(), (3, 2))
        # Test using the actual property names
        table = Gtk.Table(n_rows=2, n_columns=3, homogeneous=True)
        self.assertEqual(table.get_size(), (2, 3))
        self.assertEqual(table.get_homogeneous(), True)

        label = Gtk.Label(label='Hello')
        self.assertTrue(isinstance(label, Gtk.Widget))
        table.attach(label, 0, 1, 0, 1)
        self.assertEqual(label, table.get_children()[0])

    def test_scrolledwindow(self):
        sw = Gtk.ScrolledWindow()
        self.assertTrue(isinstance(sw, Gtk.ScrolledWindow))
        self.assertTrue(isinstance(sw, Gtk.Container))
        self.assertTrue(isinstance(sw, Gtk.Widget))
        sb = sw.get_hscrollbar()
        self.assertEqual(sw.get_hadjustment(), sb.get_adjustment())
        sb = sw.get_vscrollbar()
        self.assertEqual(sw.get_vadjustment(), sb.get_adjustment())

    def test_widget_drag_methods(self):
        widget = Gtk.Button()

        # here we are not checking functionality, only that the methods exist
        # and except the right number of arguments

        widget.drag_check_threshold(0, 0, 0, 0)

        # drag_dest_ methods
        widget.drag_dest_set(Gtk.DestDefaults.DROP, None, Gdk.DragAction.COPY)
        widget.drag_dest_add_image_targets()
        widget.drag_dest_add_text_targets()
        widget.drag_dest_add_uri_targets()
        widget.drag_dest_get_track_motion()
        widget.drag_dest_set_track_motion(True)
        widget.drag_dest_get_target_list()
        widget.drag_dest_set_target_list(Gtk.TargetList.new([Gtk.TargetEntry.new('test', 0, 0)]))
        widget.drag_dest_unset()

        widget.drag_highlight()
        widget.drag_unhighlight()

        # drag_source_ methods
        widget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, None, Gdk.DragAction.MOVE)
        widget.drag_source_add_image_targets()
        widget.drag_source_add_text_targets()
        widget.drag_source_add_uri_targets()
        widget.drag_source_set_icon_name("")
        widget.drag_source_set_icon_pixbuf(GdkPixbuf.Pixbuf())
        widget.drag_source_set_icon_stock("")
        widget.drag_source_get_target_list()
        widget.drag_source_set_target_list(Gtk.TargetList.new([Gtk.TargetEntry.new('test', 0, 0)]))
        widget.drag_source_unset()

        # these methods cannot be called because they require a valid drag on
        # a real GdkWindow. So we only check that they exist and are callable.
        self.assertTrue(hasattr(widget.drag_dest_set_proxy, '__call__'))
        self.assertTrue(hasattr(widget.drag_get_data, '__call__'))

    def test_scrollbar(self):
        # PyGTK compat
        adjustment = Gtk.Adjustment()

        hscrollbar = Gtk.HScrollbar()
        vscrollbar = Gtk.VScrollbar()
        self.assertNotEqual(hscrollbar.props.adjustment, adjustment)
        self.assertNotEqual(vscrollbar.props.adjustment, adjustment)

        hscrollbar = Gtk.HScrollbar(adjustment)
        vscrollbar = Gtk.VScrollbar(adjustment)
        self.assertEqual(hscrollbar.props.adjustment, adjustment)
        self.assertEqual(vscrollbar.props.adjustment, adjustment)

    def test_iconview(self):
        # PyGTK compat
        iconview = Gtk.IconView()
        self.assertEqual(iconview.props.model, None)

        model = Gtk.ListStore(str)
        iconview = Gtk.IconView(model)
        self.assertEqual(iconview.props.model, model)

    def test_toolbutton(self):
        # PyGTK compat
        button = Gtk.ToolButton()
        self.assertEqual(button.props.stock_id, None)

        button = Gtk.ToolButton('gtk-new')
        self.assertEqual(button.props.stock_id, 'gtk-new')

        icon = Gtk.Image.new_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.SMALL_TOOLBAR)

        button = Gtk.ToolButton(label='mylabel', icon_widget=icon)
        self.assertEqual(button.props.label, 'mylabel')
        self.assertEqual(button.props.icon_widget, icon)

    def test_iconset(self):
        # PyGTK compat
        Gtk.IconSet()
        pixbuf = GdkPixbuf.Pixbuf()
        Gtk.IconSet(pixbuf)

    def test_viewport(self):
        # PyGTK compat
        vadjustment = Gtk.Adjustment()
        hadjustment = Gtk.Adjustment()

        viewport = Gtk.Viewport(hadjustment=hadjustment,
                                vadjustment=vadjustment)

        self.assertEqual(viewport.props.vadjustment, vadjustment)
        self.assertEqual(viewport.props.hadjustment, hadjustment)


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestTreeModel(unittest.TestCase):
    def test_tree_model_sort(self):
        self.assertEqual(Gtk.TreeModelSort, gi.overrides.Gtk.TreeModelSort)
        self.assertRaises(TypeError, Gtk.TreeModelSort)
        model = Gtk.TreeStore(int, bool)
        model_sort = Gtk.TreeModelSort(model)
        self.assertEqual(model_sort.get_model(), model)

    def test_tree_store(self):
        self.assertEqual(Gtk.TreeStore, gi.overrides.Gtk.TreeStore)
        self.assertEqual(Gtk.ListStore, gi.overrides.Gtk.ListStore)
        self.assertEqual(Gtk.TreeModel, gi.overrides.Gtk.TreeModel)
        self.assertEqual(Gtk.TreeViewColumn, gi.overrides.Gtk.TreeViewColumn)

        class TestPyObject(object):
            pass

        test_pyobj = TestPyObject()
        test_pydict = {1: 1, "2": 2, "3": "3"}
        test_pylist = [1, "2", "3"]
        tree_store = Gtk.TreeStore(int,
                                   'gchararray',
                                   TestGtk.TestClass,
                                   GObject.TYPE_PYOBJECT,
                                   object,
                                   object,
                                   object,
                                   bool,
                                   bool,
                                   GObject.TYPE_UINT,
                                   GObject.TYPE_ULONG,
                                   GObject.TYPE_INT64,
                                   GObject.TYPE_UINT64,
                                   GObject.TYPE_UCHAR,
                                   GObject.TYPE_CHAR)

        parent = None
        for i in range(97):
            label = 'this is child #%d' % i
            testobj = TestGtk.TestClass(self, i, label)
            parent = tree_store.append(parent, (i,
                                                label,
                                                testobj,
                                                testobj,
                                                test_pyobj,
                                                test_pydict,
                                                test_pylist,
                                                i % 2,
                                                bool(i % 2),
                                                i,
                                                GObject.G_MAXULONG,
                                                GObject.G_MININT64,
                                                0xffffffffffffffff,
                                                254,
                                                _bytes('a')
                                                ))
        # test set
        parent = tree_store.append(parent)
        i = 97
        label = 'this is child #%d' % i
        testobj = TestGtk.TestClass(self, i, label)
        tree_store.set(parent,
                       0, i,
                       2, testobj,
                       1, label,
                       3, testobj,
                       4, test_pyobj,
                       5, test_pydict,
                       6, test_pylist,
                       7, i % 2,
                       8, bool(i % 2),
                       9, i,
                       10, GObject.G_MAXULONG,
                       11, GObject.G_MININT64,
                       12, 0xffffffffffffffff,
                       13, 254,
                       14, _bytes('a'))

        parent = tree_store.append(parent)
        i = 98
        label = 'this is child #%d' % i
        testobj = TestGtk.TestClass(self, i, label)
        tree_store.set(parent, {0: i,
                                2: testobj,
                                1: label,
                                3: testobj,
                                4: test_pyobj,
                                5: test_pydict,
                                6: test_pylist,
                                7: i % 2,
                                8: bool(i % 2),
                                9: i,
                                10: GObject.G_MAXULONG,
                                11: GObject.G_MININT64,
                                12: 0xffffffffffffffff,
                                13: 254,
                                14: _bytes('a')})

        parent = tree_store.append(parent)
        i = 99
        label = 'this is child #%d' % i
        testobj = TestGtk.TestClass(self, i, label)
        tree_store.set(parent, (0, 2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
                               (i,
                                testobj,
                                label,
                                testobj,
                                test_pyobj,
                                test_pydict,
                                test_pylist,
                                i % 2,
                                bool(i % 2),
                                i,
                                GObject.G_MAXULONG,
                                GObject.G_MININT64,
                                0xffffffffffffffff,
                                254,
                                _bytes('a')))

        # len gets the number of children in the root node
        # since we kept appending to the previous node
        # there should only be one child of the root
        self.assertEqual(len(tree_store), 1)

        # walk the tree to see if the values were stored correctly
        parent = None
        i = 0

        treeiter = tree_store.iter_children(parent)
        while treeiter:
            i = tree_store.get_value(treeiter, 0)
            s = tree_store.get_value(treeiter, 1)
            obj = tree_store.get_value(treeiter, 2)
            obj.check(i, s)
            obj2 = tree_store.get_value(treeiter, 3)
            self.assertEqual(obj, obj2)

            pyobj = tree_store.get_value(treeiter, 4)
            self.assertEqual(pyobj, test_pyobj)
            pydict = tree_store.get_value(treeiter, 5)
            self.assertEqual(pydict, test_pydict)
            pylist = tree_store.get_value(treeiter, 6)
            self.assertEqual(pylist, test_pylist)

            bool_1 = tree_store.get_value(treeiter, 7)
            bool_2 = tree_store.get_value(treeiter, 8)
            self.assertEqual(bool_1, bool_2)
            self.assertTrue(isinstance(bool_1, bool))
            self.assertTrue(isinstance(bool_2, bool))

            uint_ = tree_store.get_value(treeiter, 9)
            self.assertEqual(uint_, i)
            ulong_ = tree_store.get_value(treeiter, 10)
            self.assertEqual(ulong_, GObject.G_MAXULONG)
            int64_ = tree_store.get_value(treeiter, 11)
            self.assertEqual(int64_, GObject.G_MININT64)
            uint64_ = tree_store.get_value(treeiter, 12)
            self.assertEqual(uint64_, 0xffffffffffffffff)
            uchar_ = tree_store.get_value(treeiter, 13)
            self.assertEqual(ord(uchar_), 254)
            char_ = tree_store.get_value(treeiter, 14)
            self.assertEqual(char_, 'a')

            parent = treeiter
            treeiter = tree_store.iter_children(parent)

        self.assertEqual(i, 99)

    def test_tree_store_signals(self):
        tree_store = Gtk.TreeStore(int, bool)

        def on_row_inserted(tree_store, tree_path, tree_iter, signal_list):
            signal_list.append('row-inserted')

        def on_row_changed(tree_store, tree_path, tree_iter, signal_list):
            signal_list.append('row-changed')

        signals = []
        tree_store.connect('row-inserted', on_row_inserted, signals)
        tree_store.connect('row-changed', on_row_changed, signals)

        # adding rows with and without data should only call one signal
        tree_store.append(None, (0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        tree_store.append(None)
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        tree_store.prepend(None, (0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        tree_store.prepend(None)
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        tree_store.insert(None, 1, (0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        tree_store.insert(None, 1)
        self.assertEqual(signals, ['row-inserted'])

    def test_list_store(self):
        class TestPyObject(object):
            pass

        test_pyobj = TestPyObject()
        test_pydict = {1: 1, "2": 2, "3": "3"}
        test_pylist = [1, "2", "3"]

        list_store = Gtk.ListStore(int, str, 'GIOverrideTreeAPITest', object, object, object, bool, bool)
        for i in range(1, 93):
            label = 'this is row #%d' % i
            testobj = TestGtk.TestClass(self, i, label)
            list_store.append((i,
                               label,
                               testobj,
                               test_pyobj,
                               test_pydict,
                               test_pylist,
                               i % 2,
                               bool(i % 2)))

        i = 93
        label = _unicode('this is row #93')
        treeiter = list_store.append()
        list_store.set_value(treeiter, 0, i)
        list_store.set_value(treeiter, 1, label)
        list_store.set_value(treeiter, 2, TestGtk.TestClass(self, i, label))
        list_store.set_value(treeiter, 3, test_pyobj)
        list_store.set_value(treeiter, 4, test_pydict)
        list_store.set_value(treeiter, 5, test_pylist)
        list_store.set_value(treeiter, 6, 1)
        list_store.set_value(treeiter, 7, True)

        # test prepend
        label = 'this is row #0'
        list_store.prepend((0,
                            label,
                            TestGtk.TestClass(self, 0, label),
                            test_pyobj,
                            test_pydict,
                            test_pylist,
                            0,
                            False))

        # test automatic unicode->str conversion
        i = 94
        label = _unicode('this is row #94')
        treeiter = list_store.append((i,
                                      label,
                                      TestGtk.TestClass(self, i, label),
                                      test_pyobj,
                                      test_pydict,
                                      test_pylist,
                                      0,
                                      False))

        # add sorted items out of order to test insert* apis
        # also test sending in None to not set a column
        i = 97
        label = 'this is row #97'
        treeiter = list_store.append((None,
                                      None,
                                      None,
                                      test_pyobj,
                                      None,
                                      test_pylist,
                                      1,
                                      None))

        list_store.set_value(treeiter, 0, i)
        list_store.set_value(treeiter, 1, label)
        list_store.set_value(treeiter, 2, TestGtk.TestClass(self, i, label))
        list_store.set_value(treeiter, 4, test_pydict)
        list_store.set_value(treeiter, 7, True)

        # this should append
        i = 99
        label = 'this is row #99'
        list_store.insert(9999, (i,
                                 label,
                                 TestGtk.TestClass(self, i, label),
                                 test_pyobj,
                                 test_pydict,
                                 test_pylist,
                                 1,
                                 True))

        i = 96
        label = 'this is row #96'
        list_store.insert_before(treeiter, (i,
                                            label,
                                            TestGtk.TestClass(self, i, label),
                                            test_pyobj,
                                            test_pydict,
                                            test_pylist,
                                            0,
                                            False))

        i = 98
        label = 'this is row #98'
        list_store.insert_after(treeiter, (i,
                                           label,
                                           TestGtk.TestClass(self, i, label),
                                           test_pyobj,
                                           test_pydict,
                                           test_pylist,
                                           0,
                                           False))

        i = 95
        label = 'this is row #95'
        list_store.insert(95, (i,
                               label,
                               TestGtk.TestClass(self, i, label),
                               test_pyobj,
                               test_pydict,
                               test_pylist,
                               1,
                               True))

        i = 100
        label = 'this is row #100'
        treeiter = list_store.append()
        list_store.set(treeiter,
                       1, label,
                       0, i,
                       2, TestGtk.TestClass(self, i, label),
                       3, test_pyobj,
                       4, test_pydict,
                       5, test_pylist,
                       6, 0,
                       7, False)
        i = 101
        label = 'this is row #101'
        treeiter = list_store.append()
        list_store.set(treeiter, {1: label,
                                  0: i,
                                  2: TestGtk.TestClass(self, i, label),
                                  3: test_pyobj,
                                  4: test_pydict,
                                  5: test_pylist,
                                  6: 1,
                                  7: True})
        i = 102
        label = 'this is row #102'
        treeiter = list_store.append()
        list_store.set(treeiter, (1, 0, 2, 3, 4, 5, 6, 7),
                                 (label,
                                  i,
                                  TestGtk.TestClass(self, i, label),
                                  test_pyobj,
                                  test_pydict,
                                  test_pylist,
                                  0,
                                  False))

        self.assertEqual(len(list_store), 103)

        # walk the list to see if the values were stored correctly
        i = 0
        treeiter = list_store.get_iter_first()

        counter = 0
        while treeiter:
            i = list_store.get_value(treeiter, 0)
            self.assertEqual(i, counter)
            s = list_store.get_value(treeiter, 1)
            obj = list_store.get_value(treeiter, 2)
            obj.check(i, s)

            pyobj = list_store.get_value(treeiter, 3)
            self.assertEqual(pyobj, test_pyobj)
            pydict = list_store.get_value(treeiter, 4)
            self.assertEqual(pydict, test_pydict)
            pylist = list_store.get_value(treeiter, 5)
            self.assertEqual(pylist, test_pylist)

            bool_1 = list_store.get_value(treeiter, 6)
            bool_2 = list_store.get_value(treeiter, 7)
            self.assertEqual(bool_1, bool_2)
            self.assertTrue(isinstance(bool_1, bool))
            self.assertTrue(isinstance(bool_2, bool))

            treeiter = list_store.iter_next(treeiter)

            counter += 1

        self.assertEqual(i, 102)

    def test_list_store_sort(self):
        def comp1(model, row1, row2, user_data):
            v1 = model[row1][1]
            v2 = model[row2][1]

            # make "m" smaller than anything else
            if v1.startswith('m') and not v2.startswith('m'):
                return -1
            if v2.startswith('m') and not v1.startswith('m'):
                return 1
            return (v1 > v2) - (v1 < v2)

        list_store = Gtk.ListStore(int, str)
        list_store.set_sort_func(2, comp1, None)
        list_store.append((1, 'apples'))
        list_store.append((3, 'oranges'))
        list_store.append((2, 'mango'))

        # not sorted yet, should be original order
        self.assertEqual([list(i) for i in list_store],
                         [[1, 'apples'], [3, 'oranges'], [2, 'mango']])

        # sort with our custom function
        list_store.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        self.assertEqual([list(i) for i in list_store],
                         [[2, 'mango'], [1, 'apples'], [3, 'oranges']])

        list_store.set_sort_column_id(2, Gtk.SortType.DESCENDING)
        self.assertEqual([list(i) for i in list_store],
                         [[3, 'oranges'], [1, 'apples'], [2, 'mango']])

    def test_list_store_signals(self):
        list_store = Gtk.ListStore(int, bool)

        def on_row_inserted(list_store, tree_path, tree_iter, signal_list):
            signal_list.append('row-inserted')

        def on_row_changed(list_store, tree_path, tree_iter, signal_list):
            signal_list.append('row-changed')

        signals = []
        list_store.connect('row-inserted', on_row_inserted, signals)
        list_store.connect('row-changed', on_row_changed, signals)

        # adding rows with and without data should only call one signal
        list_store.append((0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        list_store.append()
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        list_store.prepend((0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        list_store.prepend()
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        list_store.insert(1, (0, False))
        self.assertEqual(signals, ['row-inserted'])

        signals.pop()
        list_store.insert(1)
        self.assertEqual(signals, ['row-inserted'])

    def test_tree_path(self):
        p1 = Gtk.TreePath()
        p2 = Gtk.TreePath.new_first()
        self.assertEqual(p1, p2)
        self.assertEqual(str(p1), '0')
        self.assertEqual(len(p1), 1)
        p1 = Gtk.TreePath(2)
        p2 = Gtk.TreePath.new_from_string('2')
        self.assertEqual(p1, p2)
        self.assertEqual(str(p1), '2')
        self.assertEqual(len(p1), 1)
        p1 = Gtk.TreePath('1:2:3')
        p2 = Gtk.TreePath.new_from_string('1:2:3')
        self.assertEqual(p1, p2)
        self.assertEqual(str(p1), '1:2:3')
        self.assertEqual(len(p1), 3)
        p1 = Gtk.TreePath((1, 2, 3))
        p2 = Gtk.TreePath.new_from_string('1:2:3')
        self.assertEqual(p1, p2)
        self.assertEqual(str(p1), '1:2:3')
        self.assertEqual(len(p1), 3)
        self.assertNotEqual(p1, None)
        self.assertTrue(p1 > None)
        self.assertTrue(p1 >= None)
        self.assertFalse(p1 < None)
        self.assertFalse(p1 <= None)

        self.assertEqual(tuple(p1), (1, 2, 3))
        self.assertEqual(p1[0], 1)
        self.assertEqual(p1[1], 2)
        self.assertEqual(p1[2], 3)
        self.assertRaises(IndexError, p1.__getitem__, 3)

    def test_tree_model(self):
        tree_store = Gtk.TreeStore(int, str)

        self.assertTrue(tree_store)
        self.assertEqual(len(tree_store), 0)
        self.assertEqual(tree_store.get_iter_first(), None)

        def get_by_index(row, col=None):
            if col:
                return tree_store[row][col]
            else:
                return tree_store[row]

        self.assertRaises(TypeError, get_by_index, None)
        self.assertRaises(TypeError, get_by_index, "")
        self.assertRaises(TypeError, get_by_index, ())

        self.assertRaises(IndexError, get_by_index, "0")
        self.assertRaises(IndexError, get_by_index, 0)
        self.assertRaises(IndexError, get_by_index, (0,))

        self.assertRaises(ValueError, tree_store.get_iter, "0")
        self.assertRaises(ValueError, tree_store.get_iter, 0)
        self.assertRaises(ValueError, tree_store.get_iter, (0,))

        self.assertRaises(ValueError, tree_store.get_iter_from_string, "0")

        for row in tree_store:
            self.fail("Should not be reached")

        class DerivedIntType(int):
            pass

        class DerivedStrType(str):
            pass

        for i in range(100):
            label = 'this is row #%d' % i
            parent = tree_store.append(None, (DerivedIntType(i), DerivedStrType(label),))
            self.assertNotEqual(parent, None)
            for j in range(20):
                label = 'this is child #%d of node #%d' % (j, i)
                child = tree_store.append(parent, (j, label,))
                self.assertNotEqual(child, None)

        self.assertTrue(tree_store)
        self.assertEqual(len(tree_store), 100)

        self.assertEqual(tree_store.iter_previous(tree_store.get_iter(0)), None)

        for i, row in enumerate(tree_store):
            self.assertEqual(row.model, tree_store)
            self.assertEqual(row.parent, None)

            self.assertEqual(tree_store[i].path, row.path)
            self.assertEqual(tree_store[str(i)].path, row.path)
            self.assertEqual(tree_store[(i,)].path, row.path)

            self.assertEqual(tree_store[i][0], i)
            self.assertEqual(tree_store[i][1], "this is row #%d" % i)

            aiter = tree_store.get_iter(i)
            self.assertEqual(tree_store.get_path(aiter), row.path)

            aiter = tree_store.get_iter(str(i))
            self.assertEqual(tree_store.get_path(aiter), row.path)

            aiter = tree_store.get_iter((i,))
            self.assertEqual(tree_store.get_path(aiter), row.path)

            self.assertEqual(tree_store.iter_parent(aiter), row.parent)

            next = tree_store.iter_next(aiter)
            if i < len(tree_store) - 1:
                self.assertEqual(tree_store.get_path(next), row.next.path)
                self.assertEqual(tree_store.get_path(tree_store.iter_previous(next)),
                                 tree_store.get_path(aiter))
            else:
                self.assertEqual(next, None)

            self.assertEqual(tree_store.iter_n_children(row.iter), 20)

            child = tree_store.iter_children(row.iter)
            for j, childrow in enumerate(row.iterchildren()):
                child_path = tree_store.get_path(child)
                self.assertEqual(childrow.path, child_path)
                self.assertEqual(childrow.parent.path, row.path)
                self.assertEqual(childrow.path, tree_store[child].path)
                self.assertEqual(childrow.path, tree_store[child_path].path)

                self.assertEqual(childrow[0], tree_store[child][0])
                self.assertEqual(childrow[0], j)
                self.assertEqual(childrow[1], tree_store[child][1])
                self.assertEqual(childrow[1], 'this is child #%d of node #%d' % (j, i))

                self.assertRaises(IndexError, get_by_index, child, 2)

                tree_store[child][1] = 'this was child #%d of node #%d' % (j, i)
                self.assertEqual(childrow[1], 'this was child #%d of node #%d' % (j, i))

                nth_child = tree_store.iter_nth_child(row.iter, j)
                self.assertEqual(childrow.path, tree_store.get_path(nth_child))

                childrow2 = tree_store["%d:%d" % (i, j)]
                self.assertEqual(childrow.path, childrow2.path)

                childrow2 = tree_store[(i, j,)]
                self.assertEqual(childrow.path, childrow2.path)

                child = tree_store.iter_next(child)
                if j < 19:
                    self.assertEqual(childrow.next.path, tree_store.get_path(child))
                else:
                    self.assertEqual(child, childrow.next)
                    self.assertEqual(child, None)

            self.assertEqual(j, 19)

        self.assertEqual(i, 99)

        # negative indices
        for i in range(-1, -100, -1):
            i_real = i + 100
            self.assertEqual(tree_store[i][0], i_real)

            row = tree_store[i]
            for j in range(-1, -20, -1):
                j_real = j + 20
                path = (i_real, j_real,)

                self.assertEqual(tree_store[path][-2], j_real)

                label = 'this was child #%d of node #%d' % (j_real, i_real)
                self.assertEqual(tree_store[path][-1], label)

                new_label = 'this still is child #%d of node #%d' % (j_real, i_real)
                tree_store[path][-1] = new_label
                self.assertEqual(tree_store[path][-1], new_label)

                self.assertRaises(IndexError, get_by_index, path, -3)

        self.assertRaises(IndexError, get_by_index, -101)

        last_row = tree_store[99]
        self.assertNotEqual(last_row, None)

        for i, childrow in enumerate(last_row.iterchildren()):
            if i < 19:
                self.assertTrue(tree_store.remove(childrow.iter))
            else:
                self.assertFalse(tree_store.remove(childrow.iter))

        self.assertEqual(i, 19)

        self.assertEqual(tree_store.iter_n_children(last_row.iter), 0)
        for childrow in last_row.iterchildren():
            self.fail("Should not be reached")

        aiter = tree_store.get_iter(10)
        self.assertRaises(TypeError, tree_store.get, aiter, 1, 'a')
        self.assertRaises(ValueError, tree_store.get, aiter, 1, -1)
        self.assertRaises(ValueError, tree_store.get, aiter, 1, 100)
        self.assertEqual(tree_store.get(aiter, 0, 1), (10, 'this is row #10'))

        # check __delitem__
        self.assertEqual(len(tree_store), 100)
        aiter = tree_store.get_iter(10)
        del tree_store[aiter]
        self.assertEqual(len(tree_store), 99)
        self.assertRaises(TypeError, tree_store.__delitem__, None)
        self.assertRaises(IndexError, tree_store.__delitem__, -101)
        self.assertRaises(IndexError, tree_store.__delitem__, 101)

    def test_tree_model_get_iter_fail(self):
        # TreeModel class with a failing get_iter()
        class MyTreeModel(GObject.GObject, Gtk.TreeModel):
            def do_get_iter(self, iter):
                return (False, None)

        tm = MyTreeModel()
        self.assertEqual(tm.get_iter_first(), None)

    def test_tree_model_edit(self):
        model = Gtk.ListStore(int, str, float)
        model.append([1, "one", -0.1])
        model.append([2, "two", -0.2])

        def set_row(value):
            model[1] = value

        self.assertRaises(TypeError, set_row, 3)
        self.assertRaises(TypeError, set_row, "three")
        self.assertRaises(ValueError, set_row, [])
        self.assertRaises(ValueError, set_row, [3, "three"])

        model[0] = (3, "three", -0.3)

    def test_tree_row_slice(self):
        model = Gtk.ListStore(int, str, float)
        model.append([1, "one", -0.1])

        self.assertEqual([1, "one", -0.1], model[0][:])
        self.assertEqual([1, "one"], model[0][:2])
        self.assertEqual(["one", -0.1], model[0][1:])
        self.assertEqual(["one"], model[0][1:-1])
        self.assertEqual([1], model[0][:-2])
        self.assertEqual([], model[0][5:])
        self.assertEqual([1, -0.1], model[0][0:3:2])

        model[0][:] = (2, "two", -0.2)
        self.assertEqual([2, "two", -0.2], model[0][:])

        model[0][:2] = (3, "three")
        self.assertEqual([3, "three", -0.2], model[0][:])

        model[0][1:] = ("four", -0.4)
        self.assertEqual([3, "four", -0.4], model[0][:])

        model[0][1:-1] = ("five",)
        self.assertEqual([3, "five", -0.4], model[0][:])

        model[0][0:3:2] = (6, -0.6)
        self.assertEqual([6, "five", -0.6], model[0][:])

        def set_row1():
            model[0][5:] = ("doesn't", "matter",)

        self.assertRaises(ValueError, set_row1)

        def set_row2():
            model[0][:1] = (0, "zero", 0)

        self.assertRaises(ValueError, set_row2)

        def set_row3():
            model[0][:2] = ("0", 0)

        self.assertRaises(ValueError, set_row3)


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestTreeView(unittest.TestCase):
    def test_tree_view(self):
        store = Gtk.ListStore(int, str)
        store.append((0, "foo"))
        store.append((1, "bar"))
        view = Gtk.TreeView()
        # FIXME: We can't easily call get_cursor() to make sure this works as
        # expected as we need to realize and focus the column; the following
        # will raise a Gtk-CRITICAL which we ignore for now
        old_mask = GLib.log_set_always_fatal(
            GLib.LogLevelFlags.LEVEL_WARNING | GLib.LogLevelFlags.LEVEL_ERROR)
        view.set_cursor(store[1].path)
        view.set_cursor(str(store[1].path))

        view.get_cell_area(store[1].path)
        view.get_cell_area(str(store[1].path))

        GLib.log_set_always_fatal(old_mask)

    def test_tree_view_column(self):
        cell = Gtk.CellRendererText()
        Gtk.TreeViewColumn(title='This is just a test',
                           cell_renderer=cell,
                           text=0,
                           style=2)

    def test_tree_view_add_column_with_attributes(self):
        model = Gtk.ListStore(str, str, str)
        # deliberately use out-of-order sorting here; we assign column 0 to
        # model index 2, etc.
        model.append(['cell13', 'cell11', 'cell12'])
        model.append(['cell23', 'cell21', 'cell22'])

        tree = Gtk.TreeView(model)
        cell1 = Gtk.CellRendererText()
        cell2 = Gtk.CellRendererText()
        cell3 = Gtk.CellRendererText()
        cell4 = Gtk.CellRendererText()

        tree.insert_column_with_attributes(0, 'Head2', cell2, text=2)
        tree.insert_column_with_attributes(0, 'Head1', cell1, text=1)
        tree.insert_column_with_attributes(-1, 'Head3', cell3, text=0)
        # unconnected
        tree.insert_column_with_attributes(-1, 'Head4', cell4)

        # might cause a Pango warning, do not break on this
        old_mask = GLib.log_set_always_fatal(
            GLib.LogLevelFlags.LEVEL_CRITICAL | GLib.LogLevelFlags.LEVEL_ERROR)
        # causes the widget to get realized and cellN.props.text receive a
        # value, otherwise it will be None.
        tree.get_preferred_size()
        GLib.log_set_always_fatal(old_mask)

        self.assertEqual(tree.get_column(0).get_title(), 'Head1')
        self.assertEqual(tree.get_column(1).get_title(), 'Head2')
        self.assertEqual(tree.get_column(2).get_title(), 'Head3')
        self.assertEqual(tree.get_column(3).get_title(), 'Head4')

        # cursor should be at the first row
        self.assertEqual(cell1.props.text, 'cell11')
        self.assertEqual(cell2.props.text, 'cell12')
        self.assertEqual(cell3.props.text, 'cell13')
        self.assertEqual(cell4.props.text, None)

    def test_tree_view_column_set_attributes(self):
        store = Gtk.ListStore(int, str)
        directors = ['Fellini', 'Tarantino', 'Tarkovskiy']
        for i, director in enumerate(directors):
            store.append([i, director])

        treeview = Gtk.TreeView()
        treeview.set_model(store)

        column = Gtk.TreeViewColumn()
        treeview.append_column(column)

        cell = Gtk.CellRendererText()
        column.pack_start(cell, expand=True)
        column.set_attributes(cell, text=1)

        # might cause a Pango warning, do not break on this
        old_mask = GLib.log_set_always_fatal(
            GLib.LogLevelFlags.LEVEL_CRITICAL | GLib.LogLevelFlags.LEVEL_ERROR)
        # This will make cell.props.text receive a value, otherwise it
        # will be None.
        treeview.get_preferred_size()
        GLib.log_set_always_fatal(old_mask)

        self.assertTrue(cell.props.text in directors)

    def test_tree_selection(self):
        store = Gtk.ListStore(int, str)
        for i in range(10):
            store.append((i, "foo"))
        view = Gtk.TreeView()
        view.set_model(store)
        firstpath = store.get_path(store.get_iter_first())
        sel = view.get_selection()

        sel.select_path(firstpath)
        (m, s) = sel.get_selected()
        self.assertEqual(m, store)
        self.assertEqual(store.get_path(s), firstpath)

        sel.select_path(0)
        (m, s) = sel.get_selected()
        self.assertEqual(m, store)
        self.assertEqual(store.get_path(s), firstpath)

        sel.select_path("0:0")
        (m, s) = sel.get_selected()
        self.assertEqual(m, store)
        self.assertEqual(store.get_path(s), firstpath)

        sel.select_path((0, 0))
        (m, s) = sel.get_selected()
        self.assertEqual(m, store)
        self.assertEqual(store.get_path(s), firstpath)

    def test_tree_iter_user_data_int(self):
        pyiter = Gtk.TreeIter()
        rawiter = RawTreeIter.from_iter(pyiter)

        initial_ref_count = sys.getrefcount(1)
        pyiter.user_data = 1

        # verify setting int value increases refcount of the "1" object
        self.assertEqual(sys.getrefcount(1), initial_ref_count + 1)
        # verify the address of the '1' object is what user_data is actually set to.
        self.assertEqual(id(1), rawiter.contents.user_data)

    def test_tree_iter_user_data_null(self):
        pyiter = Gtk.TreeIter()
        rawiter = RawTreeIter.from_iter(pyiter)

        self.assertEqual(pyiter.user_data, None)
        self.assertEqual(rawiter.contents.user_data, None)

        # Setting user_data to None should not increase None's ref count.
        # and the raw iters user_data should also come back as None/NULL.
        initial_ref_count = sys.getrefcount(None)
        pyiter.user_data = None
        self.assertEqual(sys.getrefcount(None), initial_ref_count)
        self.assertEqual(rawiter.contents.user_data, None)


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestTextBuffer(unittest.TestCase):
    def test_text_buffer(self):
        self.assertEqual(Gtk.TextBuffer, gi.overrides.Gtk.TextBuffer)
        buffer = Gtk.TextBuffer()
        tag = buffer.create_tag('title', font='Sans 18')

        self.assertEqual(tag.props.name, 'title')
        self.assertEqual(tag.props.font, 'Sans 18')

        (start, end) = buffer.get_bounds()

        mark = buffer.create_mark(None, start)
        self.assertFalse(mark.get_left_gravity())

        buffer.set_text('Hello Jane Hello Bob')
        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.assertEqual(text, 'Hello Jane Hello Bob')

        buffer.set_text('')
        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.assertEqual(text, '')

        buffer.insert(end, 'HelloHello')
        buffer.insert(end, ' Bob')

        cursor_iter = end.copy()
        cursor_iter.backward_chars(9)
        buffer.place_cursor(cursor_iter)
        buffer.insert_at_cursor(' Jane ')

        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.assertEqual(text, 'Hello Jane Hello Bob')

        sel = buffer.get_selection_bounds()
        self.assertEqual(sel, ())
        buffer.select_range(start, end)
        sel = buffer.get_selection_bounds()
        self.assertTrue(sel[0].equal(start))
        self.assertTrue(sel[1].equal(end))

        buffer.set_text('')
        buffer.insert_with_tags(buffer.get_start_iter(), 'HelloHello', tag)
        (start, end) = buffer.get_bounds()
        self.assertTrue(start.begins_tag(tag))
        self.assertTrue(start.has_tag(tag))

        buffer.set_text('')
        buffer.insert_with_tags_by_name(buffer.get_start_iter(), 'HelloHello', 'title')
        (start, end) = buffer.get_bounds()
        self.assertTrue(start.begins_tag(tag))
        self.assertTrue(start.has_tag(tag))

        self.assertRaises(ValueError, buffer.insert_with_tags_by_name,
                          buffer.get_start_iter(), 'HelloHello', 'unknowntag')

    def test_text_iter(self):
        self.assertEqual(Gtk.TextIter, gi.overrides.Gtk.TextIter)
        buffer = Gtk.TextBuffer()
        buffer.set_text('Hello Jane Hello Bob')
        tag = buffer.create_tag('title', font='Sans 18')
        (start, end) = buffer.get_bounds()
        start.forward_chars(10)
        buffer.apply_tag(tag, start, end)
        self.assertTrue(start.begins_tag())
        self.assertTrue(end.ends_tag())
        self.assertTrue(start.toggles_tag())
        self.assertTrue(end.toggles_tag())
        start.backward_chars(1)
        self.assertFalse(start.begins_tag())
        self.assertFalse(start.ends_tag())
        self.assertFalse(start.toggles_tag())

    def test_text_buffer_search(self):
        buffer = Gtk.TextBuffer()
        buffer.set_text('Hello World Hello GNOME')

        i = buffer.get_iter_at_offset(0)
        self.assertTrue(isinstance(i, Gtk.TextIter))

        self.assertEqual(i.forward_search('world', 0, None), None)

        (start, end) = i.forward_search('World', 0, None)
        self.assertEqual(start.get_offset(), 6)
        self.assertEqual(end.get_offset(), 11)

        (start, end) = i.forward_search('world',
                                        Gtk.TextSearchFlags.CASE_INSENSITIVE,
                                        None)
        self.assertEqual(start.get_offset(), 6)
        self.assertEqual(end.get_offset(), 11)
