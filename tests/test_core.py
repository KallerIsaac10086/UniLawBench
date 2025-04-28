import unittest
from unilawbench.cli import main
from evalscope_integration import convert_to_evalscope_format, evaluate_with_evalscope

class TestCoreFunctions(unittest.TestCase):
    def test_data_conversion(self):
        """测试数据转换功能"""
        # 测试JSONL到EvalScope格式的转换
        input_file = "test_data.jsonl"
        output_file = "test_output.jsonl"
        convert_to_evalscope_format(input_file, output_file)
        
        # 验证输出文件是否存在
        self.assertTrue(os.path.exists(output_file))
    
    def test_model_evaluation(self):
        """测试模型评估功能"""
        # 测试使用EvalScope评估模型
        result = evaluate_with_evalscope("gpt-3.5-turbo", "test_dataset.jsonl")
        self.assertIsNotNone(result)
        
    def test_cli_commands(self):
        """测试CLI命令"""
        # 测试version命令
        with self.assertRaises(SystemExit):
            main(["version"])
            
        # 测试eval命令
        with self.assertRaises(SystemExit):
            main(["eval", "-form", "qa", "-model", "test_model"])

if __name__ == "__main__":
    unittest.main()