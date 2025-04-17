import subprocess

def convert_to_llvm_ir(c_code_filename,ir_output_filename):
    command = [
        "clang",
        "-S",
        "-emit-llvm",
        "-O3",
        "-fno-discard-value-names",
        "-g0",
        c_code_filename,
        "-o",ir_output_filename
    ] #出力ファイルを最適化してLLMに読み込ませやすく
    result = subprocess.run(command,capture_output=True)
    if result.returncode == 0:
        print(f"LLVM IRが生成されました: {ir_output_filename}")
    else:
        print(f"エラー発生: {result.stderr.decode()}")