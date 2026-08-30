from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

from crawl_list import SLEEP_SECONDS, fetch_html

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
HTML_DIR = RAW_DIR / 'html'
LIST_CSV = RAW_DIR / 'policy_list.csv'

def save_detail_html(policy_id: str, detail_url: str) -> str :
    target = HTML_DIR / f'{policy_id}.html'

    if target.exists():
        return 'skipped'

    try : 
        html = fetch_html(detail_url)
    except requests.RequestException as error : 
        print(f'실패 {policy_id} : {error}')
        return 'failed'

    target.write_text(html, encoding='utf-8')

    return 'saved'

def main() -> None : 
    dataframe = pd.read_csv(LIST_CSV)
    HTML_DIR.mkdir(parents=True, exist_ok=True)

    counts = {'saved' : 0, 'skipped' : 0, 'failed' : 0}
    failed_ids: list[str] = []
    total = len(dataframe)

    for order, row in enumerate(dataframe.itertuples(index=False), start=1):
        result = save_detail_html(row.policy_id, row.detail_url)
        counts[result]+=1

        if result =='failed' : 
            failed_ids.append(row.policy_id)

        print(f'[{order}/{total}] {row.policy_id} -> {result}')

        if result =='saved' : 
            time.sleep(SLEEP_SECONDS)

    print(
        f'\n저장 {counts['saved']}건 /'
        f' 건너뜀 {counts['skipped']}건 /'
        f' 실패 {counts['failed']}건'
    )

    if failed_ids :
        print('실패 목록 :', ', '.join(failed_ids))

if __name__ =='__main__' : 
    main()
