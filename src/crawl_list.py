from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'

BASE_URL = 'https://youth.seoul.go.kr'
LIST_SOURCE = {
    '서울시': '/infoData/plcyInfo/ctList.do',
    '자치구': '/infoData/plcyInfo/guList.do',
}
DETAIL_PATH = '/infoData/plcyInfo/view.do'

HEADERS = {
    'User-Agent': 'YouthPolicyStudyBot/1.0'
    '(study project; jongddugi)'
    }
SLEEP_SECONDS = 1.0
MAX_PAGE = 50

POLICY_ID_PATTERN = re.compile(r"goView\('([^']+)'\)")

def fetch_html(url: str, params: dict | None = None) -> str :
    response=requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=10
    )
    response.raise_for_status()
    response.encoding='utf-8-sig'

    return response.text

def extract_policy_id(onclick: str) -> str | None:
    matched = POLICY_ID_PATTERN.search(onclick)

    return matched.group(1) if matched else None

def build_detail_url(policy_id : str) -> str:

    return(
        f'{BASE_URL}{DETAIL_PATH}'
        f'?plcyBizId={policy_id}&tabKind=001'
    )

def parse_list_page(html: str, source: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    rows: list[dict[str, str]] = []

    for item in soup.select('ul.policy-list > li'):
        title_tag = item.select_one('a.tit')

        if title_tag is None : 
            continue

        policy_id = extract_policy_id(title_tag.get('onclick',''))

        if policy_id is None : 
            continue

        summary_tag = item.select_one('em')
        district_tag = item.select_one('span.bg-purple')

        rows.append({
            'policy_id' : policy_id,
            'policy_name' : title_tag.get_text(' ', strip=True),
            'summary' : (
                summary_tag.get_text(' ', strip=True)
                if summary_tag else ''
            ),
            'district' : (
                district_tag.get_text(' ', strip=True)
                if district_tag else ''
            ),
            'source' : source,
            'detail_url' : build_detail_url(policy_id),
        })

    return rows

def crawl_list(source: str, path: str)-> list[dict[str, str]]:
    url=f'{BASE_URL}{path}'
    collected: list[dict[str, str]] = []

    for page_index in range(1, MAX_PAGE +1):
        html = fetch_html(url, {
            'pageIndex' : page_index,
            'tabKind' : '001',
            'blueWorksYn' : 'N',
        })
        rows = parse_list_page(html, source)

        print(f'[{source}] {page_index}페이지 -> {len(rows)}건')

        if not rows:
            break

        collected.extend(rows)
        time.sleep(SLEEP_SECONDS)

    return collected

def main() -> None : 
    all_rows: list[dict[str, str]] =[]

    for source, path in LIST_SOURCE.items() : 
        all_rows.extend(crawl_list(source, path))

    dataframe = pd.DataFrame(all_rows)
    before = len(dataframe)
    dataframe = dataframe.drop_duplicates(subset='policy_id')

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(
        RAW_DIR/'policy_list.csv',
        index=False,
        encoding='utf-8-sig',
    )

    print(f'\n수집 {before}건 -> 중복 제거 후 {len(dataframe)}')
    print(dataframe['source'].value_counts().to_string())
    print(dataframe.head(3).to_string(index=False))

if __name__ =='__main__' : 
    main()

