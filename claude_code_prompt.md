# 프로젝트: 청년몽땅정보통 기반 서울 청년 취업·주거 지원사업 탐색기

## 내 상황
- 비전공자, 파이썬 초보
- 이 프로젝트는 복습 목적으로 진행 중 — **코드는 내가 직접 판단해서 작성할 거야**
- 너(Claude)는 **전체 코드를 통째로 작성해주지 마.** 대신 아래 역할로 도와줘:
  - 각 단계에서 무엇을 해야 하는지 개념/체크리스트로 안내
  - 내가 막히면 질문·힌트로 스스로 풀도록 유도 (바로 정답 코드부터 주지 말기)
  - 내가 작성한 코드를 보여주면 리뷰/디버깅은 적극적으로 도와줘도 됨
  - 함수 시그니처나 3~5줄 이내의 짧은 예시 스니펫 정도는 괜찮지만, 파일 전체를 대신 완성해주지는 마

## 서비스 개요
사용자가 지역·나이·취업 상태·관심 분야를 입력하면, 신청 가능성이 있는 청년 지원사업을 찾아
지원 내용과 신청 절차를 근거 문서와 함께 설명해주는 서비스.

- 지역 범위: 서울시 + 서울 자치구 정책
- 분야: 취업 / 주거 / 교육
- 상태: 모집 중 또는 상시 모집
- 수집량 목표: 50~150개

### 수집 대상 (3종)
1. 서울시 청년정책 상세 페이지 (예: https://youth.seoul.go.kr/infoData/plcyInfo/view.do?blueWorksYn=N&key=2309150002&orderBy=regYmd+desc&pageIndex=1&plcyBizId=V202600008&tabKind=001)
   - 정책 유형, 기관, 지원 내용, 신청 기간, 신청 자격, 신청 절차
2. 자치구 정책 목록: https://youth.seoul.go.kr/infoData/plcyInfo/guList.do (플러스알파, 거주 구 맞춤 추천용)
3. 정책 공지사항: https://youth.seoul.go.kr/bbs/list.do?key=2303300002 (모집 공고/변경 공고 확인용)

## 데이터 구조

**구조화 데이터 (JSON 또는 SQLite):** 나이 / 지역 / 자치구 / 취업 상태 / 분야 / 신청 시작일 / 신청 종료일

**ChromaDB (정책당 문서):** 정책명 / 정책 소개 / 지원 내용 / 상세 자격 / 제외 조건 / 신청 방법 / 제출 서류

**임베딩 청크 아이디어 (Step 3에서 최종 결정 예정):**
- 청크 1: 정책 개요 + 지원 내용
- 청크 2: 신청 자격 + 제외 조건
- 청크 3: 신청 방법 + 제출 서류
- 청크 4: 최신 모집·변경 공고

> ⚠️ "정책당 문서 1개"(ChromaDB)와 "청크 1~4개"(임베딩)가 서로 다른 단위야. 청크별로 나눠 담을지,
> 합쳐서 정책당 1개로 담을지는 Step 3에서 내가 직접 정할 거니까, 그때 옵션별 장단점을 물어보면서 판단 도와줘.

## Retrieval 파이프라인 (6단계)
1. 지역·자치구 조건 필터
2. 나이 조건 필터
3. 취업 상태·관심 분야 필터
4. 모집 중·상시 정책 필터
5. 남은 정책에서 의미 기반 검색
6. 유사도 기준을 통과한 정책만 채택

## 응답 출력 예시 포맷
```
서울 청년 월세 지원

신청 가능성: 확인 필요

일치 조건:
- 서울 거주
- 연령 조건 충족
- 주거 지원 관심 분야 일치

추가 확인:
- 가구소득 기준
- 임차보증금과 월세 기준
- 주택 소유 여부

근거 문서:
- 서울시 청년 월세 지원 신청 자격
- 2026년 참여자 모집 공고
```

## 개발 순서 (8단계)
1. Crawling + 데이터 문서
2. Data Processing
3. Embedding
4. ChromaDB
5. Retrieval
6. Gemini 이용
7. Function Calling
8. Streamlit

각 단계는 이전 단계 결과물이 있어야 다음으로 넘어갈 수 있어. 한 단계씩 진행하고,
그 단계의 결과물이 완료 기준을 통과했다고 판단되면 다음 단계로 넘어가자.

## 참고할 로컬 강의 자료 (읽기 전용 — 절대 수정·삭제 금지)
`/Users/gimjongha/Desktop/PS` 아래에 내가 들은 강의 실습 코드가 있어. 이 프로젝트 코드를 작성할 폴더와는
별개니까 건드리지 말고 참고만 해:

- 크롤링: `수업자료/data_lec3/day3/static_crawler.py`, `수업자료/data_lec3/quiz2/quiz_local_event_crawling.py`
- 문자열/정규식: `수업교재/문자열 조작과 정규식.pdf`, `수업교재/정규식.pdf`
- 데이터 처리: `수업교재/2. 데이터 처리를 위한 pandas.pdf`, `수업교재/5. 데이터 변형 및 치환.pdf`
- 프롬프트 설계(CO-STAR, RISEN): `AI_LEC/llm_use/day1`
- Gemini 구조화 출력/툴 사용: `AI_LEC/llm_use2/day1/geminiToolEx1~4.py`
- Embedding/ChromaDB: `AI_LEC/llm_use2/day4` (vectorDBEx1~4.py, `Embedding & VectorDB.pdf`, `vectorDB_정리.md`)
- Retrieval(유사도 threshold, 청크 검색): `AI_LEC/llm_use2/day5` (vectorDBEx5~6.py)
- Function Calling: `AI_LEC/llm_use2/day2~3` (functionCallEx1~8.py, functionCallEx8.md)
- Streamlit: `수업교재/Streamlit_문법_가이드.pdf`

## 지금 시작할 단계
STEP 0 (환경 준비)부터 시작할 거야. 프로젝트 폴더/가상환경 구조 잡는 것부터 체크리스트로 안내해줘.
