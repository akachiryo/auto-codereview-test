#!/usr/bin/env python3
"""
Marp形式のスライドをGitHub Wiki用のMarkdownに変換
"""

import re
import os

def convert_marp_to_wiki(input_file, output_file):
    """Marp MarkdownをWiki形式に変換"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Marp frontmatterを削除
    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    
    # スライド区切り(---)をセクション区切りに変換
    sections = content.split('\n---\n')
    
    wiki_content = []
    
    # タイトルページ
    wiki_content.append("# PRUMアカデミー チーム開発キックオフ資料\n")
    wiki_content.append("このページはチーム開発のキックオフ説明資料です。\n")
    wiki_content.append("---\n")
    
    # 目次を作成
    wiki_content.append("## 📚 目次\n")
    toc_items = [
        "1. [アジェンダ](#アジェンダ)",
        "2. [目的](#目的)",
        "3. [開発スケジュール](#開発スケジュール)",
        "4. [1週間スケジュール](#1週間スケジュール)",
        "5. [プロダクト説明](#プロダクト説明)",
        "6. [成果物](#成果物)",
        "7. [ルールと評価](#ルールと評価)",
        "8. [リーダー決め](#リーダー決め)",
        "9. [評価基準](#評価基準)",
        "10. [その他ツール・リンク](#その他ツール・リンク)"
    ]
    wiki_content.extend([f"{item}\n" for item in toc_items])
    wiki_content.append("\n---\n")
    
    # 各セクションを処理
    for i, section in enumerate(sections):
        if i == 0:
            # タイトルスライドはスキップ（既に処理済み）
            continue
        
        # HTMLコメントやクラス指定を削除
        section = re.sub(r'<!--.*?-->', '', section, flags=re.DOTALL)
        section = re.sub(r'<div.*?>|</div>', '', section)
        
        # # を ## に変換（Wikiでは1つ深くする）
        section = re.sub(r'^# ', '## ', section, flags=re.MULTILINE)
        section = re.sub(r'^## ', '### ', section, flags=re.MULTILINE)
        
        # 特定のセクションタイトルは維持
        section = re.sub(r'^### アジェンダ', '## アジェンダ', section, flags=re.MULTILINE)
        section = re.sub(r'^### 目的', '## 目的', section, flags=re.MULTILINE)
        section = re.sub(r'^### 開発スケジュール', '## 開発スケジュール', section, flags=re.MULTILINE)
        section = re.sub(r'^### 1週間スケジュール', '## 1週間スケジュール', section, flags=re.MULTILINE)
        section = re.sub(r'^### プロダクト説明', '## プロダクト説明', section, flags=re.MULTILINE)
        section = re.sub(r'^### 成果物', '## 成果物', section, flags=re.MULTILINE)
        section = re.sub(r'^### ルールと評価', '## ルールと評価', section, flags=re.MULTILINE)
        section = re.sub(r'^### リーダー決め', '## リーダー決め', section, flags=re.MULTILINE)
        section = re.sub(r'^### 評価基準', '## 評価基準', section, flags=re.MULTILINE)
        section = re.sub(r'^### その他ツール・リンク', '## その他ツール・リンク', section, flags=re.MULTILINE)
        
        wiki_content.append(section.strip())
        wiki_content.append("\n\n---\n\n")
    
    # フッターを追加
    wiki_content.append("## 📚 関連ページ\n\n")
    wiki_content.append("- [Home](Home) - Wikiトップページ\n")
    wiki_content.append("- [テーブル設計](Table-Design) - データベース設計\n")
    wiki_content.append("- [開発ルール](Development-Rules) - 開発規約\n")
    wiki_content.append("- [キックオフ](Kickoff) - プロジェクト開始情報\n")
    
    # ファイルに書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(wiki_content))
    
    print(f"✅ Converted {input_file} to {output_file}")

if __name__ == '__main__':
    input_path = 'data/チーム開発説明資料.md'
    output_path = 'wiki/Team-Development-Presentation.md'
    
    # wiki ディレクトリが存在しない場合は作成
    os.makedirs('wiki', exist_ok=True)
    
    if os.path.exists(input_path):
        convert_marp_to_wiki(input_path, output_path)
    else:
        print(f"❌ Input file not found: {input_path}")