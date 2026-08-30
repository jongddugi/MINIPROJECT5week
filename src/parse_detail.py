from __future__ import annotations
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
HTML_DIR = RAW_DIR / 'html'
LIST_CSV = RAW_DIR / 'policy_list.csv'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

FIELD_LABELS = [
    '정책 유형', 
    '주관 기관', 
    '정책 소개', 
    '지원 내용',
    '사업운영기간', 
    '사업신청기간', 
    '지원규모', 
    '관련 사이트',
    '연령', 
    '학력', 
    '전공요건', 
    '취업상태', 
    '특화분야 요건',
    '추가단서 사항', 
    '참여제한 대상',
    '신청절차', 
    '심사 및 발표', 
    '제출서류', 
    '신청 사이트',
    '기타사항', 
    '운영기관', 
    '참고 사이트 Ⅰ', 
    '참고 사이트 Ⅱ',
]

LINK_LABELS = {'관련 사이트', '신청 사이트', '참고 사이트 Ⅰ', '참고 사이트 Ⅱ'}

def read_cell(cell, label:str) -> str:
    if label in LINK_LABELS:
        link = cell.select_one('a[href]')

        return link['href'] if link else ''

    return cell.get_text('\n', strip=True)

def extract_fields(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, 'html.parser')    
    values : dict[str, str] = {}

    for table in soup.select('table.form-table') :
        for row in table.select('tr'):
            label = None

            for cell in row.find_all(['th','td']):
                if cell.name =='th' :
                    label = cell.get_text(' ', strip=True)
                elif label is not None:
                    values[label] = read_cell(cell, label)
                    label = None

    return values

def parse_one(policy_id: str) -> dict[str, str] | None : 
    target = HTML_DIR / f'{policy_id}.html'

    if not target.exists():
        return None

    values = extract_fields(target.read_text(encoding='utf-8'))
    parsed = {'policy_id' : policy_id}

    for label in FIELD_LABELS:
        parsed[label] = values.get(label, '')

    return parsed

def main() -> None : 
    dataframe = pd.read_csv(LIST_CSV, dtype={'policy_id':str})
    parsed_rows: list[dict[str, str]] = []
    missing_ids: list[str] = []

    for policy_id in dataframe['policy_id']:
        parsed = parse_one(policy_id)

        if parsed is None:
            missing_ids.append(policy_id)
            continue

        parsed_rows.append(parsed)

    detail = pd.DataFrame(parsed_rows)
    merged = dataframe.merge(detail, on='policy_id', how='left')

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_csv(
        PROCESSED_DIR/'policy_detail.csv',
        index=False,
        encoding='utf-8-sig'
    )

    print(f'파싱 {len(detail)}건 / HTML 없음 {len(missing_ids)}건')
    print('\n---빈 값 건수 ---')
    print((detail[FIELD_LABELS] =='').sum().to_string())

    if missing_ids:
        print('\nHTML 없음 : ', ', '.join(missing_ids))

if __name__ =='__main__':
    main()