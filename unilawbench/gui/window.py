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
        
        # 转换类型选择
        self.convert_btn = QPushButton('选择转换文件')
        self.convert_btn.clicked.connect(self.select_convert_file)
        layout.addWidget(self.convert_btn)
        
        # TODO: 添加其他转换相关控件
        
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