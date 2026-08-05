#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
import sys
import traceback

from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QHBoxLayout, QStyleFactory,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, QHeaderView, QMessageBox)
from PySide6.QtGui import QIcon, QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt
from pathlib import Path
import json
import re
# NOTE: it's seem many packages on pypi using root namespace `leveldb`
# I'm using `leveldb-py` https://pypi.org/project/leveldb-py
import leveldb
import functools
print = functools.partial(print, flush=True)

ROLE_RAW_KEY = Qt.UserRole + 1
ROLE_VALUE = Qt.UserRole


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []
        fmt_key = QTextCharFormat()
        fmt_key.setForeground(QColor('#9CDCFE'))
        self._rules.append((re.compile(r'"([^"\\]|\\.)*"\s*(?=:)'), fmt_key))
        fmt_str = QTextCharFormat()
        fmt_str.setForeground(QColor('#CE9178'))
        self._rules.append((re.compile(r'(?<=: )"([^"\\]|\\.)*"'), fmt_str))
        fmt_num = QTextCharFormat()
        fmt_num.setForeground(QColor('#B5CEA8'))
        self._rules.append((re.compile(r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b'), fmt_num))
        fmt_bool = QTextCharFormat()
        fmt_bool.setForeground(QColor('#569CD6'))
        self._rules.append((re.compile(r'\b(true|false|null)\b'), fmt_bool))
        fmt_brace = QTextCharFormat()
        fmt_brace.setForeground(QColor('#D4D4D4'))
        self._rules.append((re.compile(r'[\{\}\[\]]'), fmt_brace))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


class LevelDBViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LevelDB Viewer | Z U K O')
        self.setGeometry(100, 100, 1200, 700)
        self._db = None
        self._current_raw_key = None
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        controls_layout = QHBoxLayout()
        self.path_label = QLabel('No database selected')
        controls_layout.addWidget(self.path_label)
        self.select_button = QPushButton('Select LevelDB')
        self.select_button.clicked.connect(self.select_db)
        controls_layout.addWidget(self.select_button)
        main_layout.addLayout(controls_layout)
        splitter = QSplitter(Qt.Horizontal)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Key', 'Type', 'Value'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.currentCellChanged.connect(self._on_row_selected)
        splitter.addWidget(self.table)
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        self._key_label = QLabel('Select an entry')
        self._key_label.setStyleSheet('font-weight:bold; padding:4px;')
        detail_layout.addWidget(self._key_label)
        self._tabs = QTabWidget()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(['Key', 'Value', 'Type'])
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemDoubleClicked.connect(self._edit_tree_item)
        self._tabs.addTab(self._tree, 'Tree')
        self._raw_edit = QTextEdit()
        self._raw_edit.setReadOnly(False)
        self._raw_edit.setFont(QFont('Consolas', 10))
        self._raw_edit.setStyleSheet('background:#1E1E1E; color:#D4D4D4;')
        self._highlighter = JsonHighlighter(self._raw_edit.document())
        self._tabs.addTab(self._raw_edit, 'Raw')
        self._save_btn = QPushButton('Save Changes')
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._save_value)
        detail_layout.addWidget(self._tabs)
        detail_layout.addWidget(self._save_btn)
        splitter.addWidget(detail_widget)
        splitter.setSizes([400, 500])
        main_layout.addWidget(splitter)
        self.statusBar().showMessage('Ready - Using leveldb-py')

    def select_db(self):
        db_path = QFileDialog.getExistingDirectory(self, 'Select LevelDB Directory', '', QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if db_path:
            self.path_label.setText(db_path)
            self.load_db(db_path)

    def load_db(self, db_path):
        try:
            self.table.setRowCount(0)
            self.statusBar().showMessage('Loading database...')
            print(f'[DBG] Opening DB: {db_path}')
            self._db = leveldb.LevelDB(db_path, create_if_missing=False)
            print(f'[DBG] DB opened OK. Type: {type(self._db)}')
            data = []
            count = 0
            try:
                for raw_key, raw_value in self._db.items():
                    count += 1
                    print(f'[DBG] Entry {count}: key={raw_key[:30]!r} val={raw_value[:30]!r}')
                    try:
                        key_str = raw_key.decode('utf-8')
                    except:
                        key_str = raw_key.hex()
                    clean = self._decode_value(raw_value)
                    print(f'[DBG]   decoded: {clean[:80]!r}')
                    data.append((key_str, raw_key, clean))
            except Exception as e:
                print(f'[DBG] Iteration error: {e}')
                traceback.print_exc()
                self.statusBar().showMessage(f'Error iterating database: {str(e)}')
                return
            print(f'[DBG] Total raw entries: {count}, parsed: {len(data)}')
            self._populate_table(data)
        except Exception as e:
            print(f'[DBG] Open error: {e}')
            traceback.print_exc()
            self.statusBar().showMessage(f'Error opening database: {str(e)}')

    @staticmethod
    def _strip_prefix(s):
        return s.lstrip('\x00\x01')

    def _detect_type(self, value):
        try:
            parsed = json.loads(self._strip_prefix(str(value)))
            if isinstance(parsed, dict):
                return 'JSON Object'
            elif isinstance(parsed, list):
                return 'JSON Array'
            elif isinstance(parsed, bool):
                return 'Boolean'
            elif isinstance(parsed, int):
                return 'Number (int)'
            elif isinstance(parsed, float):
                return 'Number (float)'
            elif parsed is None:
                return 'Null'
            return 'JSON String'
        except (json.JSONDecodeError, TypeError, ValueError):
            return 'String'

    def _populate_table(self, data):
        self.table.setRowCount(len(data))
        type_colors = {
            'JSON Object': '#DCDCAA', 'JSON Array': '#C586C0',
            'Boolean': '#569CD6', 'Number (int)': '#B5CEA8',
            'Number (float)': '#B5CEA8', 'Null': '#569CD6',
        }
        for row, (key_str, raw_key, value) in enumerate(data):
            key_item = QTableWidgetItem(key_str)
            key_item.setData(ROLE_RAW_KEY, raw_key)
            val_type = self._detect_type(value)
            type_item = QTableWidgetItem(val_type)
            color = type_colors.get(val_type)
            if color:
                type_item.setForeground(QColor(color))
            preview = str(value)[:200] + ('...' if len(str(value)) > 200 else '')
            value_item = QTableWidgetItem(preview)
            for item in (key_item, type_item):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            value_item.setData(ROLE_VALUE, value)
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, type_item)
            self.table.setItem(row, 2, value_item)
        self.table.resizeColumnToContents(0)
        self.statusBar().showMessage(f'Loaded {len(data)} entries')

    def _on_row_selected(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        key_item = self.table.item(row, 0)
        value = self.table.item(row, 2).data(ROLE_VALUE)
        self._current_raw_key = key_item.data(ROLE_RAW_KEY)
        self._key_label.setText(f'Key: {key_item.text()}')
        clean = self._strip_prefix(str(value))
        self._raw_edit.setPlainText(clean)
        self._tree.clear()
        try:
            parsed = json.loads(clean)
            self._build_tree(self._tree.invisibleRootItem(), parsed)
            self._tree.expandAll()
            self._tabs.setCurrentIndex(0)
            self._save_btn.setEnabled(True)
        except (json.JSONDecodeError, TypeError, ValueError):
            item = QTreeWidgetItem(['(plain text)', clean, type(value).__name__])
            self._tree.addTopLevelItem(item)
            self._tabs.setCurrentIndex(1)
            self._save_btn.setEnabled(True)

    def _build_tree(self, parent, obj, key_name=''):
        if isinstance(obj, dict):
            node = QTreeWidgetItem([str(key_name), f'{{{len(obj)} keys}}', 'object'])
            node.setForeground(1, QColor('#888888'))
            parent.addChild(node)
            for k, v in obj.items():
                self._build_tree(node, v, k)
        elif isinstance(obj, list):
            node = QTreeWidgetItem([str(key_name), f'[{len(obj)} items]', 'array'])
            node.setForeground(1, QColor('#888888'))
            parent.addChild(node)
            for i, v in enumerate(obj):
                self._build_tree(node, v, f'[{i}]')
        else:
            type_name = type(obj).__name__
            display = str(obj) if not isinstance(obj, str) else f'"{obj}"'
            item = QTreeWidgetItem([str(key_name), display, type_name])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            if isinstance(obj, bool):
                item.setForeground(1, QColor('#569CD6'))
            elif isinstance(obj, (int, float)):
                item.setForeground(1, QColor('#B5CEA8'))
            elif isinstance(obj, str):
                item.setForeground(1, QColor('#CE9178'))
            elif obj is None:
                item.setForeground(1, QColor('#569CD6'))
            parent.addChild(item)

    def _edit_tree_item(self, item, column):
        if column == 1 and item.childCount() == 0:
            self._tree.editItem(item, 1)

    @staticmethod
    def _infer_value(text):
        if text in ('true', 'True'):
            return True
        if text in ('false', 'False'):
            return False
        if text in ('null', 'None', 'none'):
            return None
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            pass
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text

    def _tree_to_json(self, item):
        if item.childCount() == 0:
            return self._infer_value(item.text(1))
        type_label = item.text(2)
        if type_label == 'object':
            result = {}
            for i in range(item.childCount()):
                child = item.child(i)
                result[child.text(0)] = self._tree_to_json(child)
            return result
        else:
            result = []
            for i in range(item.childCount()):
                result.append(self._tree_to_json(item.child(i)))
            return result

    def _save_value(self):
        if not self._db or self._current_raw_key is None:
            return
        try:
            if self._tabs.currentIndex() == 1:
                new_value = self._raw_edit.toPlainText()
            else:
                root = self._tree.invisibleRootItem()
                if root.childCount() != 1:
                    return
                obj = self._tree_to_json(root.child(0))
                new_value = json.dumps(obj, ensure_ascii=False)
            self._db.put(self._current_raw_key, new_value.encode('utf-8'))
            try:
                parsed = json.loads(new_value)
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError, ValueError):
                pretty = new_value
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(ROLE_RAW_KEY) == self._current_raw_key:
                    preview = pretty[:200] + ('...' if len(pretty) > 200 else '')
                    self.table.item(row, 1).setText(self._detect_type(pretty))
                    self.table.item(row, 2).setText(preview)
                    self.table.item(row, 2).setData(ROLE_VALUE, pretty)
                    break
            self._raw_edit.setPlainText(pretty)
            self.statusBar().showMessage(f'Saved key: {self.table.item(row, 0).text()}')
        except Exception as e:
            QMessageBox.warning(self, 'Save Error', str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setWindowIcon(QIcon(str(Path('./assets/icon.png').resolve())))
    window = LevelDBViewer()
    window.show()
    # DEBUG: auto-load DB
    _test_db = r'D:/personal_git/bvauto2/data/profiles/gio/Default/Local Storage/leveldb'
    if Path(_test_db).exists():
        window.path_label.setText(_test_db)
        window.load_db(_test_db)
    sys.exit(app.exec())
