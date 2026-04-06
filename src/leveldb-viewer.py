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

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QHBoxLayout, QStyleFactory
from PySide6.QtGui import QIcon
from pathlib import Path
import json

# Chỉ sử dụng leveldb-py
import leveldb


class LevelDBViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LevelDB Viewer | Z U K O')
        self.setGeometry(100, 100, 800, 600)
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        # Controls
        controls_layout = QHBoxLayout()
        self.path_label = QLabel('No database selected')
        controls_layout.addWidget(self.path_label)
        self.select_button = QPushButton('Select LevelDB')
        self.select_button.clicked.connect(self.select_db)
        controls_layout.addWidget(self.select_button)
        main_layout.addLayout(controls_layout)
        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['Key', 'Value'])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)
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
            # Sử dụng leveldb
            db = leveldb.LevelDB(db_path, create_if_missing=False)
            data = []
            # Đọc tất cả các entry từ database
            try:
                for key, value in db.items():
                    try:
                        # Cố gắng decode key/value
                        key_str = key.decode('utf-8')
                        try:
                            # Cố gắng decode value
                            value_str = value.decode('utf-8')
                            # Kiểm tra xem có phải JSON không
                            try:
                                parsed = json.loads(value_str)
                                value_str = json.dumps(parsed, indent=2)
                            except:
                                pass
                            data.append((key_str, value_str))
                        except:
                            # Nếu không decode được value, hiển thị dưới dạng hex
                            data.append((key_str, value.hex()))
                    except:
                        # Nếu không decode được key, hiển thị cả key và value dưới dạng hex
                        data.append((key.hex(), value.hex()))
            except Exception as e:
                print(traceback.print_exc())
                self.statusBar().showMessage(f'Error iterating database: {str(e)}')
                return
            # Hiển thị dữ liệu trên bảng
            self._populate_table(data)
        except Exception as e:
            print(traceback.print_exc())
            self.statusBar().showMessage(f'Error opening database: {str(e)}')

    def _populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, (key, value) in enumerate(data):
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(value))
            # Đặt chế độ chỉ đọc
            key_item.setFlags(key_item.flags())
            value_item.setFlags(value_item.flags())
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, value_item)
        self.table.resizeColumnToContents(0)
        self.statusBar().showMessage(f'Loaded {len(data)} entries')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setWindowIcon(QIcon(str(Path('./assets/icon.png').resolve())))
    window = LevelDBViewer()
    window.show()
    sys.exit(app.exec())
