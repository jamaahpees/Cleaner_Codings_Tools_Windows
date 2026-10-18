"""Real Tk regressions in subprocesses; no discovery, catalog, or system jobs."""
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


BOOTSTRAP = '''
from contextlib import ExitStack
from unittest.mock import patch, Mock
from types import SimpleNamespace
import dev_cleaner as ui
stack = ExitStack()
for name in ('auto_initial_scan', '_load_native_catalog', '_init_storage_sense_state',
             'scan_startup_async', 'scan_services_async', 'refresh_restore_list'):
    if hasattr(ui.DevAICleanerApp, name):
        stack.enter_context(patch.object(ui.DevAICleanerApp, name))
stack.enter_context(patch.object(ui, 'load_startup_scan_preference', return_value=False))
stack.enter_context(patch.object(ui, 'discover_python_environments', return_value={'Fixture': 'python'}))
stack.enter_context(patch.object(ui, 'get_target_drive_options', return_value=[]))
stack.enter_context(patch.object(ui.psutil, 'disk_usage', return_value=SimpleNamespace(free=10**10, total=10**11)))
stack.enter_context(patch.object(ui.ThreadPoolExecutor, 'submit', side_effect=AssertionError('Unexpected system job')))
app = ui.DevAICleanerApp()
app.update()
'''


class BootstrapLayoutTests(unittest.TestCase):
    def run_tk(self, code):
        result = subprocess.run(
            [sys.executable, '-c', BOOTSTRAP + textwrap.dedent(code) +
             '\napp.executor.shutdown(wait=False)\napp.destroy()\nstack.close()\n'],
            cwd=Path(__file__).resolve().parents[1], capture_output=True,
            text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pixel_widths_and_scan_summary_fit(self):
        self.run_tk('''
            assert int(app.btn_smart_scan.cget('width')) < 40
            assert app.lbl_smart_summary.master != app.btn_smart_scan.master
            for widget in (app.cmb_target_drive, app.cmb_py_env, app.ent_lib_search):
                assert int(widget.cget('width')) < 40, widget
            frame = ui.ctk.CTkFrame(app, width=200)
            assert int(frame.cget('width')) == 200
            label = ui.ctk.CTkLabel(frame, text='status', width=200)
            assert int(label.cget('width')) < 40
            label.configure(width=100, fg_color=ui.UI_COLORS['warning'], text_color='#FFFFFF')
            assert str(label.cget('background')) == ui.UI_COLORS['warning']
            assert str(label.cget('foreground')) == ui.UI_COLORS['ink']
            label.configure(fg_color='transparent', text_color='#38BDF8')
            assert str(label.cget('background')) == str(frame.cget('background'))
            assert str(label.cget('foreground')) == ui.UI_COLORS['primary']
            assert app.cmb_target_drive.get() in app.target_paths_map
            assert app.native_app_cat.get() == 'Semua Kategori'
            frame.destroy()
        ''')

    def test_all_toolbars_and_subviews_fit(self):
        self.run_tk('''
            def visible_inside(widget):
                assert widget.winfo_ismapped(), str(widget)
                parent = widget.master
                assert widget.winfo_x() >= 0
                assert widget.winfo_x() + widget.winfo_width() <= parent.winfo_width() + 1, (str(widget), widget.winfo_x(), widget.winfo_width(), parent.winfo_width())
            for size in ('1050x720', '1260x840', '1440x900'):
                app.geometry(size)
                app.update()
                for key, view in app.views.items():
                    app.switch_view(key)
                    app.update()
                    toolbar = view.winfo_children()[0]
                    for widget in toolbar.winfo_children():
                        visible_inside(widget)
                    assert app.log_box.winfo_ismapped()
                    assert app.log_box.winfo_rooty() + app.log_box.winfo_height() <= app.winfo_rooty() + app.winfo_height()
                for value in app.seg_ghost.values:
                    app.seg_ghost.set(value, invoke_command=True)
                    app.update()
                    assert any(frame.winfo_ismapped() for frame in app.ghost_frames.values()), value
                app.seg_ghost.set(app.seg_ghost.values[0], invoke_command=True)
                app.update()
                for widget in app.native_app_search.master.winfo_children():
                    visible_inside(widget)
                app.switch_view('smart_cleaner')
                app.update()
                for widget in (app.lbl_smart_summary, app.btn_clean_smart, app.chk_startup_scan):
                    visible_inside(widget)
        ''')

    def test_summary_known_bytes_selection_and_columns(self):
        self.run_tk('''
            app.geometry('1050x720')
            for child in app.smart_scroll.winfo_children():
                child.destroy()
            sizes = (7, 2048, 1048576, 1073741824)
            app.smart_findings = [dict(name='Fixture', path='C:/fixture/' + 'long/'*20,
                                      badge='SAFE', size_bytes=size) for size in sizes]
            for item in app.smart_findings:
                app._render_smart_row(item)
            app.update_smart_summary()
            app.update()
            text = app.lbl_smart_summary.cget('text')
            assert '1.00 GB (4 items)' in text, text
            for item, expected in zip(app.smart_findings, ('7 B', '2.0 KB', '1.0 MB', '1.00 GB')):
                labels = {int(w.grid_info()['column']): w for w in item['row_widget'].winfo_children()}
                assert labels[3].cget('text') == expected
                assert labels[3].winfo_ismapped()
                assert abs(labels[3].winfo_rootx() - app.smart_table_header.grid_slaves(row=0, column=3)[0].winfo_rootx()) <= 20
            app.smart_findings[-1]['var'].set(False)
            app.update_smart_summary()
            assert 'Terpilih untuk dibersihkan: 1.0 MB (3 items)' in app.lbl_smart_summary.cget('text')
            app.var_smart_master.set(False)
            app.toggle_all_smart_rows()
            assert '0 B (0 items)' in app.lbl_smart_summary.cget('text')
            app.var_smart_master.set(True)
            app.toggle_all_smart_rows()
            assert app.lbl_smart_summary.cget('text').count('1.00 GB (4 items)') == 2
            assert app.lbl_smart_summary.winfo_width() >= app.lbl_smart_summary.winfo_reqwidth()
        ''')

    def test_optionmenu_user_callback_once_programmatic_set_silent(self):
        self.run_tk('''
            calls = []
            menu = ui.ctk.CTkOptionMenu(app, values=['first', 'second'], command=calls.append, width=190)
            menu.set('second')
            assert calls == []
            menu.menu.invoke(0)
            assert calls == ['first'] and menu.get() == 'first'
            menu.configure(values=['third'])
            menu.menu.invoke(0)
            assert calls == ['first', 'third']
            selected = Mock()
            app.opt_dup_auto.command = selected
            app.opt_dup_auto.set('Kosongkan Pilihan')
            selected.assert_not_called()
            app.opt_dup_auto.menu.invoke(1)
            selected.assert_called_once_with('Pilih Duplikat Terlama')
            menu.destroy()
        ''')
