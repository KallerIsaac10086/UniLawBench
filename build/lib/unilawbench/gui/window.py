from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UniLawBench 法律评估工具')
        self.setMinimumSize(800, 600)
        
        # 创建主选项卡
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 评估选项卡
        self.create_eval_tab()
        # 转换选项卡
        self.create_convert_tab()

    def create_eval_tab(self):
        eval_tab = QWidget()
        layout = QVBoxLayout()
        
        # 模型选择
        self.model_btn = QPushButton('选择模型路径')
        self.model_btn.clicked.connect(self.select_model)
        layout.addWidget(self.model_btn)
        
        # TODO: 添加其他评估相关控件
        
        eval_tab.setLayout(layout)
        self.tabs.addTab(eval_tab, "评估")

    def create_convert_tab(self):
        convert_tab = QWidget()
        layout = QVBoxLayout()
        
        # 评估形式选择
        self.form_combo = QComboBox()
        self.form_combo.addItems(['qa', 'mcq'])
        layout.addWidget(QLabel('评估形式:'))
        layout.addWidget(self.form_combo)

        # 运行所有数据集
        self.run_all_check = QCheckBox('运行所有数据集')
        layout.addWidget(self.run_all_check)

        # 数据集ID输入
        self.dataset_edit = QLineEdit()
        layout.addWidget(QLabel('数据集ID (空格分隔):'))
        layout.addWidget(self.dataset_edit)

        # 转换类型选择
        self.convert_type = QComboBox()
        self.convert_type.addItems(['mcq', 'qa', 'focus'])
        layout.addWidget(QLabel('转换类型:'))
        layout.addWidget(self.convert_type)

        # 输出路径选择
        self.output_btn = QPushButton('选择输出路径')
        self.output_btn.clicked.connect(self.select_output_path)
        layout.addWidget(self.output_btn)
        
        convert_tab.setLayout(layout)
        self.tabs.addTab(convert_tab, "转换")

    def select_model(self):
        path = QFileDialog.getExistingDirectory(self, '选择模型目录')
        if path:
            print(f'Selected model path: {path}')

    def select_convert_file(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择输入文件')
        if path:
            print(f'Selected input file: {path}')

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())