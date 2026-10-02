# 영화 호프 네이버 리뷰 EDA

영화 ‘호프’ 네이버 리뷰 58,659건을 분석한 인터랙티브 HTML 슬라이드 덱입니다.

## 보기

정적 파일로 배포되며, `index.html`을 열거나 로컬 서버에서 실행할 수 있습니다.

```bash
python -m http.server 8000
```

슬라이드는 `←` `→` 방향키, 스페이스, 터치 스와이프로 이동합니다.

## 구성

- `index.html`: 발표용 HTML deck
- `deck_assets/`: matplotlib로 생성한 차트
- `deck_plan.md`: 구성·시각화·검증 계획
- `eda/호프_EDA_인사이트.md`: 상세 분석 보고서
- `eda/metrics.json`: 재현 가능한 분석 지표
- `eda_hope.py`, `build_visuals.py`: 분석·시각화 코드
