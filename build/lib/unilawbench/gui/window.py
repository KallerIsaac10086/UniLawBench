from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QComboBox, QLabel, QLineEdit, QCheckBox, QMessageBox, QGroupBox
from PyQt5.QtCore import Qt
import os
import sys
from pathlib import Path
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UniLawBench 法律评估工具')
        self.setMinimumSize(900, 700)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #d4d4d4;
                background: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # 保存路径
        self.model_path = ""
        self.dataset_path = ""
        self.output_path = ""
        self.input_file_path = ""
        self.output_file_path = ""
        
        # 创建主选项卡
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 评估选项卡
        self.create_eval_tab()
        # 转换选项卡
        self.create_convert_tab()
        # EvalScope选项卡
        self.create_evalscope_tab()

    def create_eval_tab(self):
        eval_tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 模型选择
        model_layout = QHBoxLayout()
        self.model_edit = QLineEdit()
        self.model_edit.setReadOnly(True)
        self.model_edit.setPlaceholderText('选择模型路径...')
        self.model_btn = QPushButton('浏览...')
        self.model_btn.clicked.connect(self.select_model)
        model_layout.addWidget(self.model_edit, 3)
        model_layout.addWidget(self.model_btn, 1)
        layout.addWidget(QLabel('模型路径:'))
        layout.addLayout(model_layout)
        
        # 评估模式选择
        layout.addWidget(QLabel('评估模式:'))
        self.eval_mode = QComboBox()
        self.eval_mode.addItems(['问答题(qa)', '选择题(mcq)'])
        self.eval_mode.currentIndexChanged.connect(self.update_eval_params)
        layout.addWidget(self.eval_mode)
        
        # 数据集选择组
        dataset_group = QGroupBox("数据集选择")
        dataset_layout = QVBoxLayout()
        
        # 运行所有数据集选项
        self.run_all_check = QCheckBox('运行所有数据集')
        self.run_all_check.stateChanged.connect(self.toggle_dataset_id)
        dataset_layout.addWidget(self.run_all_check)
        
        # 数据集ID输入
        self.dataset_id_label = QLabel('数据集ID (空格分隔):')
        dataset_layout.addWidget(self.dataset_id_label)
        self.dataset_id_edit = QLineEdit()
        dataset_layout.addWidget(self.dataset_id_edit)
        
        # 或者选择特定数据集文件
        self.dataset_file_label = QLabel('或选择特定数据集文件:')
        dataset_layout.addWidget(self.dataset_file_label)
        dataset_file_layout = QHBoxLayout()
        self.dataset_file_edit = QLineEdit()
        self.dataset_file_edit.setReadOnly(True)
        self.dataset_file_btn = QPushButton('浏览...')
        self.dataset_file_btn.clicked.connect(self.select_dataset)
        dataset_file_layout.addWidget(self.dataset_file_edit, 3)
        dataset_file_layout.addWidget(self.dataset_file_btn, 1)
        dataset_layout.addLayout(dataset_file_layout)
        
        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText('选择输出目录...')
        self.output_btn = QPushButton('浏览...')
        self.output_btn.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.output_edit, 3)
        output_layout.addWidget(self.output_btn, 1)
        layout.addWidget(QLabel('输出目录:'))
        layout.addLayout(output_layout)
        
        # 评估参数
        layout.addWidget(QLabel('评估参数:'))
        self.eval_params = QLineEdit()
        self.eval_params.setPlaceholderText('输入评估参数，用空格分隔')
        layout.addWidget(self.eval_params)
        
        # 运行评估按钮
        buttons_layout = QHBoxLayout()
        self.run_eval_btn = QPushButton('开始评估')
        self.run_eval_btn.setStyleSheet("background-color: #2196F3;")
        self.run_eval_btn.clicked.connect(self.run_evaluation)
        buttons_layout.addWidget(self.run_eval_btn)
        
        # 一键运行所有问答题
        self.run_all_qa_btn = QPushButton('运行所有问答题')
        self.run_all_qa_btn.setStyleSheet("background-color: #009688;")
        self.run_all_qa_btn.clicked.connect(self.run_all_qa)
        buttons_layout.addWidget(self.run_all_qa_btn)
        
        # 一键运行所有选择题
        self.run_all_mcq_btn = QPushButton('运行所有选择题')
        self.run_all_mcq_btn.setStyleSheet("background-color: #FF5722;")
        self.run_all_mcq_btn.clicked.connect(self.run_all_mcq)
        buttons_layout.addWidget(self.run_all_mcq_btn)
        
        layout.addLayout(buttons_layout)
        
        eval_tab.setLayout(layout)
        self.tabs.addTab(eval_tab, "评估")

    def create_convert_tab(self):
        convert_tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 转换类型选择
        self.convert_type = QComboBox()
        self.convert_type.addItems(['mcq', 'qa', 'focus', 'dynamic-choice', 'evalscope'])
        layout.addWidget(QLabel('转换类型:'))
        layout.addWidget(self.convert_type)
        
        # 输入文件选择
        input_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setReadOnly(True)
        self.input_file_edit.setPlaceholderText('选择输入文件...')
        self.input_file_btn = QPushButton('浏览...')
        self.input_file_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_file_edit, 3)
        input_layout.addWidget(self.input_file_btn, 1)
        layout.addWidget(QLabel('输入文件:'))
        layout.addLayout(input_layout)
        
        # 输出文件选择
        output_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setReadOnly(True)
        self.output_file_edit.setPlaceholderText('选择输出文件...')
        self.output_file_btn = QPushButton('浏览...')
        self.output_file_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.output_file_edit, 3)
        output_layout.addWidget(self.output_file_btn, 1)
        layout.addWidget(QLabel('输出文件:'))
        layout.addLayout(output_layout)
        
        # 转换按钮
        self.convert_btn = QPushButton('开始转换')
        self.convert_btn.setStyleSheet("background-color: #2196F3;")
        self.convert_btn.clicked.connect(self.run_convert)
        layout.addWidget(self.convert_btn)
        
        convert_tab.setLayout(layout)
        self.tabs.addTab(convert_tab, "转换")
    
    def create_evalscope_tab(self):
        evalscope_tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 评估部分
        eval_group = QGroupBox("EvalScope评估")
        eval_layout = QVBoxLayout()
        
        # 模型选择
        self.evalscope_model_combo = QComboBox()
        self.evalscope_model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "qwen", "baichuan", "llama"])
        eval_layout.addWidget(QLabel('模型:'))
        eval_layout.addWidget(self.evalscope_model_combo)
        
        # 数据集选择
        dataset_layout = QHBoxLayout()
        self.evalscope_dataset_edit = QLineEdit()
        self.evalscope_dataset_edit.setReadOnly(True)
        self.evalscope_dataset_edit.setPlaceholderText('选择EvalScope格式数据集...')
        self.evalscope_dataset_btn = QPushButton('浏览...')
        self.evalscope_dataset_btn.clicked.connect(self.select_evalscope_dataset)
        dataset_layout.addWidget(self.evalscope_dataset_edit, 3)
        dataset_layout.addWidget(self.evalscope_dataset_btn, 1)
        eval_layout.addWidget(QLabel('数据集:'))
        eval_layout.addLayout(dataset_layout)
        
        # 输出目录选择
        output_layout = QHBoxLayout()
        self.evalscope_output_edit = QLineEdit()
        self.evalscope_output_edit.setReadOnly(True)
        self.evalscope_output_edit.setPlaceholderText('选择输出目录...')
        self.evalscope_output_btn = QPushButton('浏览...')
        self.evalscope_output_btn.clicked.connect(self.select_evalscope_output)
        output_layout.addWidget(self.evalscope_output_edit, 3)
        output_layout.addWidget(self.evalscope_output_btn, 1)
        eval_layout.addWidget(QLabel('输出目录:'))
        eval_layout.addLayout(output_layout)
        
        # 评估按钮
        self.evalscope_eval_btn = QPushButton('开始评估')
        self.evalscope_eval_btn.setStyleSheet("background-color: #2196F3;")
        self.evalscope_eval_btn.clicked.connect(self.run_evalscope_eval)
        eval_layout.addWidget(self.evalscope_eval_btn)
        
        eval_group.setLayout(eval_layout)
        layout.addWidget(eval_group)
        
        # 可视化部分
        viz_group = QGroupBox("结果可视化")
        viz_layout = QVBoxLayout()
        
        # 结果文件选择
        results_layout = QHBoxLayout()
        self.evalscope_results_edit = QLineEdit()
        self.evalscope_results_edit.setReadOnly(True)
        self.evalscope_results_edit.setPlaceholderText('选择结果文件...')
        self.evalscope_results_btn = QPushButton('浏览...')
        self.evalscope_results_btn.clicked.connect(self.select_evalscope_results)
        results_layout.addWidget(self.evalscope_results_edit, 3)
        results_layout.addWidget(self.evalscope_results_btn, 1)
        viz_layout.addWidget(QLabel('结果文件:'))
        viz_layout.addLayout(results_layout)
        
        # 可视化按钮
        self.evalscope_viz_btn = QPushButton('开始可视化')
        self.evalscope_viz_btn.setStyleSheet("background-color: #FF9800;")
        self.evalscope_viz_btn.clicked.connect(self.run_evalscope_viz)
        viz_layout.addWidget(self.evalscope_viz_btn)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        evalscope_tab.setLayout(layout)
        self.tabs.addTab(evalscope_tab, "EvalScope")

    def select_model(self):
        path = QFileDialog.getExistingDirectory(self, '选择模型目录')
        if path:
            self.model_path = path
            self.model_edit.setText(path)
            print(f'Selected model path: {path}')

    def select_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择输入文件', filter="所有文件 (*.*);;JSONL文件 (*.jsonl);;CSV文件 (*.csv);;JSON文件 (*.json)")
        if path:
            self.input_file_path = path
            self.input_file_edit.setText(path)
            print(f'Selected input file: {path}')
            
    def select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, '选择输出文件', filter="所有文件 (*.*);;JSONL文件 (*.jsonl);;CSV文件 (*.csv)")
        if path:
            self.output_file_path = path
            self.output_file_edit.setText(path)
            print(f'Selected output file: {path}')
            
    def select_output_path(self):
        path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if path:
            self.output_path = path
            self.output_edit.setText(path)
            print(f'Selected output path: {path}')
    
    def select_evalscope_dataset(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择EvalScope数据集', filter="JSONL文件 (*.jsonl)")
        if path:
            self.evalscope_dataset_edit.setText(path)
            print(f'Selected EvalScope dataset: {path}')
    
    def select_evalscope_output(self):
        path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if path:
            self.evalscope_output_edit.setText(path)
            print(f'Selected EvalScope output directory: {path}')
    
    def select_evalscope_results(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择结果文件', filter="JSON文件 (*.json)")
        if path:
            self.evalscope_results_edit.setText(path)
            print(f'Selected EvalScope results file: {path}')
            
    def update_eval_params(self):
        mode = self.eval_mode.currentText()
        if 'qa' in mode:
            self.eval_params.setPlaceholderText('输入评估参数，如: batch_size temperature')
        else:
            self.eval_params.setPlaceholderText('输入评估参数，如: num_choices correct_index')
            
    def select_dataset(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择数据集文件', filter="所有文件 (*.*);;JSONL文件 (*.jsonl);;CSV文件 (*.csv)")
        if path:
            self.dataset_path = path
            self.dataset_file_edit.setText(path)
            print(f'Selected dataset path: {path}')
            
    def select_output_path(self):
        path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if path:
            self.output_path = path
            self.output_edit.setText(path)
            print(f'Selected output path: {path}')
    
    def run_convert(self):
        if not self.input_file_path or not self.output_file_path:
            QMessageBox.warning(self, "警告", "请选择输入文件和输出文件")
            return
        
        convert_type = self.convert_type.currentText()
        try:
            # 构建命令
            cmd = [sys.executable, "-m", "unilawbench", "convert", "--type", convert_type, 
                   str(self.input_file_path), str(self.output_file_path)]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", f"转换完成: {self.output_file_path}")
            else:
                QMessageBox.critical(self, "错误", f"转换失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"转换过程中出错: {str(e)}")
    
    def run_evalscope_eval(self):
        model = self.evalscope_model_combo.currentText()
        dataset = self.evalscope_dataset_edit.text()
        output = self.evalscope_output_edit.text()
        
        if not dataset:
            QMessageBox.warning(self, "警告", "请选择数据集文件")
            return
        
        try:
            # 构建命令
            cmd = [sys.executable, "-m", "unilawbench", "evalscope", "-model", model, "-dataset", dataset]
            if output:
                cmd.extend(["-output", output])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "EvalScope评估完成")
            else:
                QMessageBox.critical(self, "错误", f"评估失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"评估过程中出错: {str(e)}")
    
    def run_evalscope_viz(self):
        results = self.evalscope_results_edit.text()
        
        if not results:
            QMessageBox.warning(self, "警告", "请选择结果文件")
            return
        
        try:
            # 构建命令
            cmd = [sys.executable, "-m", "unilawbench", "visualize", results]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "可视化完成")
            else:
                QMessageBox.critical(self, "错误", f"可视化失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化过程中出错: {str(e)}")

    def toggle_dataset_id(self, state):
        """切换数据集ID输入框的启用状态"""
        is_checked = state == Qt.Checked
        self.dataset_id_edit.setEnabled(not is_checked)
        self.dataset_id_label.setEnabled(not is_checked)
        self.dataset_file_edit.setEnabled(not is_checked)
        self.dataset_file_label.setEnabled(not is_checked)
        self.dataset_file_btn.setEnabled(not is_checked)
    
    def run_evaluation(self):
        """运行评估"""
        if not self.model_path:
            QMessageBox.warning(self, "警告", "请选择模型路径")
            return
        
        # 获取评估模式
        mode = "qa" if "qa" in self.eval_mode.currentText().lower() else "mcq"
        
        # 构建命令
        cmd = [sys.executable, "-m", "unilawbench"]
        
        if self.run_all_check.isChecked():
            # 运行所有数据集
            cmd.extend(["eval", "-form", mode, "-model", self.model_path, "--run-all"])
        elif self.dataset_file_edit.text():
            # 使用特定数据集文件
            dataset_path = self.dataset_file_edit.text()
            cmd.extend(["-form", mode, "-model", self.model_path, "-set", dataset_path])
        elif self.dataset_id_edit.text():
            # 使用数据集ID
            dataset_ids = self.dataset_id_edit.text().split()
            cmd.extend(["eval", "-form", mode, "-model", self.model_path, "-set"] + dataset_ids)
        else:
            QMessageBox.warning(self, "警告", "请选择数据集或输入数据集ID")
            return
        
        # 添加输出目录
        if self.output_edit.text():
            cmd.extend(["-output", self.output_edit.text()])
        
        try:
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "评估完成")
            else:
                QMessageBox.critical(self, "错误", f"评估失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"评估过程中出错: {str(e)}")
    
    def run_all_qa(self):
        """一键运行所有问答题"""
        if not self.model_path:
            QMessageBox.warning(self, "警告", "请选择模型路径")
            return
        
        try:
            # 构建命令
            cmd = [sys.executable, "-m", "unilawbench", "-run-all-qa", "-model", self.model_path]
            
            # 添加输出目录
            if self.output_edit.text():
                cmd.extend(["-output", self.output_edit.text()])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "所有问答题评估完成")
            else:
                QMessageBox.critical(self, "错误", f"评估失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"评估过程中出错: {str(e)}")
    
    def run_all_mcq(self):
        """一键运行所有选择题"""
        if not self.model_path:
            QMessageBox.warning(self, "警告", "请选择模型路径")
            return
        
        try:
            # 构建命令
            cmd = [sys.executable, "-m", "unilawbench", "-run-all-mcq", "-model", self.model_path]
            
            # 添加输出目录
            if self.output_edit.text():
                cmd.extend(["-output", self.output_edit.text()])
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "成功", "所有选择题评估完成")
            else:
                QMessageBox.critical(self, "错误", f"评估失败: {result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"评估过程中出错: {str(e)}")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())