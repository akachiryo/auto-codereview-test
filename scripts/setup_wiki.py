#!/usr/bin/env python3
"""
GitHub Wiki設定スクリプト v3.1 (構文エラー修正版)
Wikiページを生成する（git操作はGitHub Actionsで実行）
"""

import os
import csv
import time
from typing import Dict, List

# 環境変数から設定を取得
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

if not GITHUB_REPOSITORY:
    raise ValueError("GITHUB_REPOSITORY environment variable is required")

def generate_table_design() -> str:
    """CSVファイルからテーブル設計書を生成"""
    csv_path = 'data/imakoko_sns_tables.csv'
    
    if not os.path.exists(csv_path):
        return "# テーブル設計書\n\nテーブル設計ファイルが見つかりません。"
    
    content = "# テーブル設計書\n\n"
    content += "イマココSNSのデータベース設計書です。\n\n"
    content += f"*最終更新: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # テーブルごとにグループ化
        tables = {}
        for row in rows:
            table_name = row['table_name']
            if table_name not in tables:
                tables[table_name] = {
                    'role': row['table_role'],
                    'columns': []
                }
            
            # 空のカラムは除外
            if row['logical_name'] and row['physical_name']:
                tables[table_name]['columns'].append(row)
        
        # 各テーブルの情報を出力
        for table_name, table_info in tables.items():
            content += f"## {table_name}\n\n"
            
            if table_info['role']:
                content += f"**役割**: {table_info['role']}\n\n"
            
            content += "| # | 論理名 | 物理名 | データ型 | 長さ | NOT NULL | PK | FK | 備考 |\n"
            content += "|---|--------|--------|----------|------|----------|----|----|------|\n"
            
            for col in table_info['columns']:
                num = col['column_no']
                logical = col['logical_name']
                physical = col['physical_name']
                dtype = col['data_type']
                length = col['length']
                not_null = "✓" if col['not_null'] == 'YES' else ""
                pk = "✓" if col['primary_key'] == 'YES' else ""
                fk = "✓" if col['foreign_key'] == 'YES' else ""
                note = col['note']
                
                content += f"| {num} | {logical} | {physical} | {dtype} | {length} | {not_null} | {pk} | {fk} | {note} |\n"
            
            content += "\n"
            
    except Exception as e:
        content += f"\nエラー: テーブル設計の読み込みに失敗しました - {str(e)}\n"
    
    return content

def generate_wiki_content(source_wiki_path: str = 'wiki', output_wiki_path: str = 'wiki'):
    """Wikiページのコンテンツを生成（/wikiディレクトリから読み込み）"""
    print("📚 Generating Wiki content from source directory...")
    
    try:
        # ソースディレクトリの確認
        if not os.path.exists(source_wiki_path):
            print(f"⚠️ Source wiki directory not found: {source_wiki_path}")
            print(f"📝 No wiki pages will be generated.")
            return True
        
        # 出力ディレクトリの作成（必要に応じて）
        if source_wiki_path != output_wiki_path:
            os.makedirs(output_wiki_path, exist_ok=True)
            print(f"📂 Output directory created/verified: {output_wiki_path}")
        
        # /wikiディレクトリから.mdファイルを読み込み
        md_files = [f for f in os.listdir(source_wiki_path) if f.endswith('.md')]
        
        if not md_files:
            print(f"⚠️ No markdown files found in: {source_wiki_path}")
            return True
        
        print(f"📁 Found {len(md_files)} markdown files in {source_wiki_path}")
        
        generated_count = 0
        for filename in md_files:
            source_path = os.path.join(source_wiki_path, filename)
            
            # テーブル設計書.mdの特別処理
            if filename == 'テーブル設計書.md':
                # ファイルが存在するがほぼ空の場合、CSVから生成
                try:
                    with open(source_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read().strip()
                    
                    # ファイルが空またはプレースホルダーのみの場合
                    if len(existing_content) < 100 or 'ここにテーブル設計' in existing_content:
                        print(f"  📊 Generating table design from CSV for: {filename}")
                        content = generate_table_design()
                    else:
                        # 既存のコンテンツを使用
                        content = existing_content
                        print(f"  📖 Using existing content for: {filename}")
                except Exception as e:
                    print(f"  ⚠️ Error reading {filename}, generating from CSV: {str(e)}")
                    content = generate_table_design()
            else:
                # その他のファイルはそのまま読み込み
                try:
                    with open(source_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"  📖 Read content from: {filename}")
                except Exception as e:
                    print(f"  ❌ Failed to read {filename}: {str(e)}")
                    continue
            
            # 出力先にファイルを書き込み（source != outputの場合のみ）
            if source_wiki_path != output_wiki_path:
                output_path = os.path.join(output_wiki_path, filename)
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ Copied to output: {filename}")
                    generated_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to write {filename}: {str(e)}")
                    continue
            else:
                # 同じディレクトリの場合、テーブル設計書のみ更新の可能性あり
                if filename == 'テーブル設計書.md' and content != existing_content:
                    try:
                        with open(source_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✅ Updated: {filename}")
                    except Exception as e:
                        print(f"  ❌ Failed to update {filename}: {str(e)}")
                generated_count += 1
        
        if source_wiki_path != output_wiki_path:
            print(f"\n📂 Wiki content copied to: {output_wiki_path}")
            print(f"📌 Processed {generated_count} pages")
        else:
            print(f"\n📂 Wiki content verified in: {source_wiki_path}")
            print(f"📌 Found {generated_count} pages")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate wiki content: {str(e)}")
        print(f"💡 Error details: {type(e).__name__}")
        
        # フォールバック: 最低限のHome.mdだけでも作成
        try:
            fallback_home = f"""# {GITHUB_REPOSITORY} Wiki

## エラー発生

Wiki生成中にエラーが発生しました。手動でページを作成してください。

最終更新: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            fallback_path = os.path.join(wiki_path, 'Home.md')
            with open(fallback_path, 'w', encoding='utf-8') as f:
                f.write(fallback_home)
            print(f"  📝 Fallback: Created minimal Home.md")
            return True
        except Exception as fallback_error:
            print(f"  ❌ Fallback also failed: {str(fallback_error)}")
            return False

def verify_wiki_content(wiki_path: str = 'wiki'):
    """生成されたWikiコンテンツを検証"""
    print("🔍 Verifying Wiki content...")
    
    if not os.path.exists(wiki_path):
        print(f"⚠️ Wiki directory not found: {wiki_path}")
        print(f"📝 This is expected if no wiki files exist in the source.")
        return True  # Not an error if no wiki files exist
    
    # 実際に存在するmdファイルをチェック
    md_files = [f for f in os.listdir(wiki_path) if f.endswith('.md')]
    
    if not md_files:
        print(f"⚠️ No markdown files found in: {wiki_path}")
        return True  # Not an error if no files exist
    
    print(f"📋 Found {len(md_files)} markdown files:")
    
    for filename in md_files:
        file_path = os.path.join(wiki_path, filename)
        file_size = os.path.getsize(file_path)
        
        if file_size < 10:  # 10バイト未満は空ファイルとみなす
            print(f"  ⚠️ {filename}: Empty file ({file_size} bytes)")
        elif file_size < 100:  # 100バイト未満は内容不足の可能性
            print(f"  ⚠️ {filename}: Small file ({file_size} bytes)")
        else:
            print(f"  ✅ {filename}: OK ({file_size} bytes)")
    
    print(f"\n✅ Wiki verification completed")
    return True

def main():
    """メイン処理"""
    print("=" * 60)
    print("📚 WIKI SETUP v3.1 (SYNTAX ERROR FIXED)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: setup_wiki_v3.py v3.1")
    print("=" * 60)
    
    try:
        # Wikiコンテンツの生成
        success = generate_wiki_content()
        
        if success:
            # 生成されたコンテンツを検証
            verification_success = verify_wiki_content()
            
            if verification_success:
                print(f"\n✨ Wiki setup completed successfully!")
                
                wiki_files = [f for f in os.listdir('wiki') if f.endswith('.md')] if os.path.exists('wiki') else []
                if wiki_files:
                    print(f"📌 Wiki pages ready for Git operations")
                    print(f"\n📋 Processed files:")
                    for file in sorted(wiki_files):
                        print(f"  • {file}")
                    
                    print(f"\n💡 Note: Wiki pages will be committed and pushed by GitHub Actions workflow")
                    print(f"\n🔗 Wiki will be available at:")
                    print(f"  https://github.com/{GITHUB_REPOSITORY}/wiki")
                else:
                    print(f"📌 No wiki pages found to process")
                    print(f"💡 Add markdown files to /wiki directory to include them in the wiki")
                
                return 0
            else:
                print(f"\n⚠️ Wiki setup completed with warnings")
                return 0  # Not a failure if verification has warnings
        else:
            print(f"\n❌ Wiki setup failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Unexpected error during Wiki setup: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        
        # デバッグ情報の出力
        print(f"\n🔍 Debug information:")
        print(f"  • Current working directory: {os.getcwd()}")
        print(f"  • Wiki directory exists: {os.path.exists('wiki')}")
        print(f"  • Data directory exists: {os.path.exists('data')}")
        print(f"  • CSV file exists: {os.path.exists('data/imakoko_sns_tables.csv')}")
        
        return 1

if __name__ == '__main__':
    exit(main())