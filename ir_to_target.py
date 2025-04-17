import os
import argparse
import re
from openai import OpenAI

def sanitize_generated_code(output_text: str) -> str:
    patterns = [
        r"(?<=```python\n).*?(?=\n```)",
        r"(?<=### Python Code:\n).*",
        r"def .*?\n[\s\S]*?(?=\n\S|$)"
    ]
    for pattern in patterns:
        match = re.search(pattern, output_text, re.DOTALL)
        if match:
            return match.group().strip()
    return output_text.strip()

def ir_to_target_language(ir_code, target_language="python", model_type="gpt-4o"):
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("環境変数 'OPENAI_API_KEY' が設定されていません。")
    
    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "system", "content": f"You are a code translator that converts LLVM IR into clean {target_language} code."},
        {"role": "user", "content": f"### LLVM IR:\n{ir_code}\n\n### Convert this to {target_language} code:\n"}
    ]
    response = client.chat.completions.create(
        model=model_type,
        messages=messages,
        temperature=0.4,
        max_tokens=1024,
    )
    output_text = response.choices[0].message.content
    return sanitize_generated_code(output_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="使用するモデル (例: gpt-3.5-turbo, gpt-4, gpt-4o, o1 など)")
    args = parser.parse_args()

    # モデルの入力を対話形式にする（指定されていなければ）
    model = args.model
    if not model:
        print("使用するモデルを入力してください（例: gpt-4o, gpt-3.5-turbo, gpt-4, o1 など）:")
        model = input("モデル名: ").strip()

    # IRファイル読み込み
    with open("generated_code/generated_code.ll", "r") as f:
        ir_code = f.read()
        print(f"IR Code Length: {len(ir_code)} characters")

    # 翻訳処理
    translated_code = ir_to_target_language(ir_code, target_language="python", model_type=model)
    print("\n[Translated Python Code]:\n")
    print(translated_code)

    # コード保存
    output_path = os.path.join("generated_code", "translated_code.py")
    os.makedirs("generated_code", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated_code)
    print(f"\n[Saved to]: {output_path}")
