#!/usr/bin/env python3
"""
GitHub Wiki設定スクリプト
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

def generate_wiki_content(wiki_path: str = 'wiki'):
    """Wikiページのコンテンツを生成"""
    print("📚 Generating Wiki content...")
    
    # Wikiディレクトリの作成
    os.makedirs(wiki_path, exist_ok=True)
    
    # 1. HOMEページ
    home_content = f"""# イマココSNS Wiki

イマココSNS開発プロジェクトのWikiページです。

## 📋 ドキュメント一覧

- [[テーブル設計書]] - データベース設計の詳細
- [[ルール]] - チーム開発のルールとガイドライン
- [[キックオフ]] - プロジェクトキックオフ資料

## 🔗 関連リンク

- [GitHub リポジトリ](https://github.com/{GITHUB_REPOSITORY})
- [Issues](https://github.com/{GITHUB_REPOSITORY}/issues)
- [Projects](https://github.com/{GITHUB_REPOSITORY}/projects)
- [Discussions](https://github.com/{GITHUB_REPOSITORY}/discussions)

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
- [GitHub ベースリポジトリ](https://github.com/prum-jp/imakoko-base)

---

*このWikiは GitHub Actions により自動生成されています*  
*最終更新: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 2. テーブル設計書
    table_design_content = generate_table_design()
    
    # 3. ルールページ（空）
    rules_content = """# ルール

チーム開発のルールとガイドラインをここに記載します。

## 開発ルール

*ここに開発ルールを記載してください*

## コミットルール

*ここにコミットルールを記載してください*

## レビュールール

*ここにレビュールールを記載してください*

---

*最終更新: """ + time.strftime('%Y-%m-%d %H:%M:%S') + "*"
    
    # 4. キックオフページ（空）
    kickoff_content = """# キックオフ

プロジェクトキックオフの資料をここに記載します。

## プロジェクト概要

*ここにプロジェクト概要を記載してください*

## 開発スケジュール

*ここに開発スケジュールを記載してください*

## 役割分担

*ここに役割分担を記載してください*

---

*最終更新: """ + time.strftime('%Y-%m-%d %H:%M:%S') + "*"
    
    try:
        # ファイルに書き込み
        pages = {
            'Home.md': home_content,
            'テーブル設計書.md': table_design_content,
            'ルール.md': rules_content,
            'キックオフ.md': kickoff_content
        }
        
        for filename, content in pages.items():
            file_path = os.path.join(wiki_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Generated: {filename}")
        
        print(f"📂 Wiki content generated in: {wiki_path}")
        print("📌 Generated pages:")
        for filename in pages.keys():
            print(f"  • {filename}")
        
    except Exception as e:
        print(f"❌ Failed to generate wiki content: {str(e)}")
        return False
    
    return True

def main():
    """メイン処理"""
    print("📚 Setting up GitHub Wiki...")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    
    # Wikiコンテンツの生成
    success = generate_wiki_content()
    
    if success:
        print(f"\n✨ Wiki setup completed!")
        print(f"📌 Generated wiki pages ready for Git operations")
        print(f"\n💡 Note: Wiki pages will be committed and pushed by GitHub Actions workflow")
        print(f"\n🔗 Wiki will be available at:")
        print(f"  https://github.com/{GITHUB_REPOSITORY}/wiki")
        return 0
    else:
        print(f"\n❌ Wiki setup failed!")
        return 1

if __name__ == '__main__':
    exit(main())