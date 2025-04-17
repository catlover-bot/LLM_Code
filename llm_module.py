import os
import re
import openai
import subprocess

# 環境変数からAPIキーを読み込み
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。")

client = openai.OpenAI(api_key=api_key)

def generate_c_code(prompt, model="gpt-4o"):
    if model.lower() == "codellama":
        return generate_with_codellama(prompt)

    # プロンプト構築
    messages = [
        {"role": "system", "content": "You are a helpful assistant that writes clean and efficient C code."},
        {"role": "user", "content": prompt}
    ]

    # モデルに応じたトークンパラメータの分岐
    if model in ["gpt-4o", "gpt-4-turbo", "o1"]:  # 新API対応
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=1024,
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,
            max_tokens=1024,
        )

    return response.choices[0].message.content.strip()

def generate_with_codellama(prompt):
    try: #例外処理追加
        with open("prompt.txt","w",encoding="utf-8", errors="ignore") as f:
            # プロンプトの指示文を明確化 
            f.write(f"/* 以下の処理をC言語で実装してください */\n{prompt}")
        result = subprocess.run(
            ["run_codellama.bat","prompt.txt"],
            capture_output=True,
            shell=True,
            timeout=30,
            text=True
        )

        # エラーチェック追加
        if result.returncode != 0:
            print(f"CodeLlama実行エラー:{result.stderr}")
            return "コード生成に失敗しました"
        
        # 出力からコードブロックを抽出
        code_blocks = re.findall(r"```(?:c|cpp)?\n(.*?)```", result.stdout, re.DOTALL)
        return code_blocks[-1].strip() if code_blocks else ""
    
    except Exception as e:
        print(f"実行時エラー:{str(e)}")
        return "エラーが発生しました"

def generate_description(prompt):
    description_prompt = f"次のコードを説明してください:\n{prompt}\n説明文を作成してください。"
    return generate_c_code(description_prompt)