#!/usr/bin/env python3
"""
KPT Issue作成スクリプト（並列実行最適化版）
"""

import os
import requests
import csv
import time
import math
import random
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

# 最適化されたRate Limit設定
REQUEST_DELAY = 0.8      # 0.8秒間隔（高速化）
BATCH_SIZE = 15          # バッチサイズ増加
BATCH_PAUSE = 8.0        # バッチ間休憩短縮
MAX_RETRIES = 10

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def load_kpt_data() -> List[Dict]:
    """KPT CSVデータを読み込み"""
    print("📊 Loading KPT data...")
    
    kpt_issues = []
    csv_path = 'data/kpt_for_issues.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            kpt_issues = [row for row in reader if row.get('title', '').strip()]
    
    print(f"📋 Loaded: {len(kpt_issues)} KPT issues")
    return kpt_issues

def create_single_issue(issue_data: Dict, index: int, total: int) -> Optional[Dict]:
    """単一のKPT Issueを作成"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    if index > 0:
        time.sleep(REQUEST_DELAY)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.post(
                f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue = response.json()
                print(f"  ✅ KPT ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
            
            elif response.status_code == 403:
                retry_after = response.headers.get('retry-after')
                wait_time = int(retry_after) if retry_after else (30 * (attempt + 1))
                print(f"  ⏳ Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"  ❌ KPT failed ({index + 1}/{total}): {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ Exception ({index + 1}/{total}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(30 * (attempt + 1))
                continue
    
    return None

def prepare_kpt_data(kpts: List[Dict]) -> List[Dict]:
    """KPT Issue作成用データを準備"""
    kpt_requests = []
    
    for row in kpts:
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
        
        # KPTはタイトルをそのまま使用（既に適切な形式）
        
        # ラベル処理
        labels_str = row.get('labels', '').strip()
        if labels_str.startswith('"') and labels_str.endswith('"'):
            labels_str = labels_str[1:-1]
        labels = [label.strip() for label in labels_str.split(',') if label.strip()]
        
        if 'kpt' not in labels:
            labels.append('kpt')
        
        issue_data = {
            'title': title,
            'body': body,
            'labels': labels
        }
        
        kpt_requests.append(issue_data)
    
    return kpt_requests

def create_kpt_issues_batch(issues_data: List[Dict], batch_num: int, total_batches: int) -> List[Dict]:
    """KPT Issuesをバッチ作成"""
    created_issues = []
    
    print(f"🚀 Processing KPT batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    for i, issue_data in enumerate(issues_data):
        issue = create_single_issue(issue_data, i, len(issues_data))
        if issue:
            created_issues.append(issue)
    
    print(f"📊 KPT batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created")
    return created_issues

def main():
    """メイン処理"""
    print("=" * 60)
    print("🎯 KPT ISSUE CREATOR (Parallel Optimized)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⚙️ Settings: delay={REQUEST_DELAY}s, batch_size={BATCH_SIZE}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # データ読み込み
        kpt_data = load_kpt_data()
        
        if not kpt_data:
            print("⚠️ No KPT issues found")
            return 0
        
        # データ準備
        kpt_requests = prepare_kpt_data(kpt_data)
        total_batches = math.ceil(len(kpt_requests) / BATCH_SIZE) if kpt_requests else 1
        
        print(f"📋 Processing {len(kpt_requests)} KPT issues in {total_batches} batches")
        
        # バッチ処理
        all_created = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(kpt_requests))
            batch_requests = kpt_requests[start_idx:end_idx]
            
            if not batch_requests:
                break
                
            batch_created = create_kpt_issues_batch(batch_requests, batch_num + 1, total_batches)
            all_created.extend(batch_created)
            
            # バッチ間休憩
            if batch_num < total_batches - 1:
                print(f"  ⏳ Batch pause ({BATCH_PAUSE}s)...")
                time.sleep(BATCH_PAUSE)
        
        # 結果保存
        with open('kpt_issues_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"KPT Issues Created: {len(all_created)}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution time: {time.time() - start_time:.1f}s\n")
            
            for issue in all_created:
                f.write(f"{issue['number']}: {issue['title']}\n")
        
        print(f"\n✅ KPT issues completed: {len(all_created)}/{len(kpt_requests)}")
        print(f"⏱️ Execution time: {time.time() - start_time:.1f}s")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())