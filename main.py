import re
import os
from llm_module import generate_c_code
from llvm_module import convert_to_llvm_ir
from ir_to_target import ir_to_target_language


# IRコード分割処理
def split_ir_code(ir_code, max_lines=200):
    functions = re.split(r'\n(?=define)', ir_code)
    return '\n'.join(functions[:max_lines])


def save_code(code, filename):
    os.makedirs("generated_code", exist_ok=True)  # ディレクトリがなければ作成
    with open(f"generated_code/{filename}", "w") as f:
        f.write(code)

def extract_c_code(llm_output):
    # ```c または ``` で囲まれた部分を抽出
    code_blocks = re.findall(r'```(?:c|cpp)?\n(.*?)```', llm_output, re.DOTALL)
    return code_blocks[-1].strip() if code_blocks else llm_output  # 最後のブロックを選択
    
def extract_explanation(llm_output):
    # ```c ~ ```を除いた部分（説明）
    return re.sub(r"```c.*?```","",llm_output,flags=re.DOTALL).strip()

def sanitize_c_code(code):
    """コメント＆不要部分除去"""
    # ブロックコメント削除
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # ラインコメント削除
    code = re.sub(r'//.*', '', code)
    # 空白行の削除
    return '\n'.join([line for line in code.split('\n') if line.strip()])

def remove_duplicate_lines(code):
    """重複行除去ロジックの実装"""
    seen = set()
    cleaned = []
    for line in code.split('\n'):
        simplified = line.strip().split('//')[0]  # コメント除去後の比較
        if simplified and simplified not in seen:
            seen.add(simplified)
            cleaned.append(line)
    return '\n'.join(cleaned)

def main():
    # 使用するモデルを指定可能にする
    print("使用するモデルを選択してください（例: gpt-4o, codellama）:")
    model = input("モデル名: ").strip()

    # 1. 自然言語からC言語コードを精製
    user_input = input("行いたい処理内容を自然言語で入力してください: ")
    c_code = generate_c_code(user_input,model=model)
    print("\n生成されたCコード:\n",c_code)

    # Cコード部分だけ抽出（Markdownの```c ```ブロック対応）
    match = re.search(r"```c(.*?)```",c_code, re.DOTALL)
    pure_c_code = match.group(1).strip() if match else c_code # fallback: 全体を使う

    # Cコード以外（説明文やコメントなど）を抽出
    explanation_text = re.sub(r"```c.*?```","",c_code,flags=re.DOTALL).strip()

    # コード加工パイプラインの改良
    processing_flow = [
        extract_c_code,        # 最終コードブロック抽出
        sanitize_c_code,       # コメント除去
        remove_duplicate_lines # 重複行削除
    ]
    
    processed_code = pure_c_code
    for step in processing_flow:
        processed_code = step(processed_code)

    os.makedirs("generated_code", exist_ok=True)

    # Cコードをファイルに保存
    with open("generated_code/generated_code.c","w",encoding="utf-8") as file:
        file.write(processed_code)

    # 説明文などを保存
    with open("generated_code/generated_code_info.txt","w",encoding="utf-8") as info_file:
        info_file.write(explanation_text.strip())
        info_file.write("\n\n" + "-" * 80 + "\n")
        info_file.write(pure_c_code.strip())

    print("\n保存完了: 'generated_code/generated_code.c' と 'generated_code/generated_code_info.txt'")

    # 2. CコードをLLVM IRに変換
    convert_to_llvm_ir("generated_code/generated_code.c","generated_code/generated_code.ll")

    # 3. LLVM IRをターゲット言語に変換
    with open("generated_code/generated_code.ll","r") as ir_file:
        ir_code = ir_file.read()
    target_code = ir_to_target_language(ir_code, target_language="python")

    # 最後にIRからPythonコードを生成
    print("IRからPythonコードを生成しています...")
    os.system("python ir_to_target.py")


    print("\nターゲット言語のコード:\n",target_code)

if __name__ == "__main__":
    main()