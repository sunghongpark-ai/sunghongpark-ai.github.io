# 제작 검증 기록

검증일: 2026-10-22

## 수행한 점검

- Python 정적 빌드 완료: 7개 HTML 페이지.
- `node --check`: JavaScript 구문 오류 없음.
- 오프라인 검증: 로컬 파일/앵커 참조 158건, 중복 ID, h1 개수, 메타데이터,
  JSON-LD 파싱, 필수 리소스, 출판 논문/BibTeX 일치 검사 통과.
- Chromium UI 테스트: **98개 검사 통과**, JavaScript runtime exception 0건.
- 페이지별 320 / 390 / 768 / 1024 / 1440px 가로 폭에서 수평 넘침 없음.
- 13개 논문 초기 표시, 문자열 검색, 연도 조합, 분야 필터, 결과 없음, 초기화 확인.
- 인용창, BibTeX 전환, 복사 피드백, Escape 닫기와 포커스 복원 확인.
- 모바일 메뉴 열기/닫기와 Contact 항목 확인.
- 테마 전환, 개념적 그래프 모드 전환, 이메일 복사 피드백 확인.
- 52개 아카이브 기록, 특허 17건 / 학회 31건 필터 및 항목 펼치기 확인.
- JavaScript 비활성화 시 논문과 메뉴 접근 가능 여부 확인.
- 움직임 감소 설정 반영과 데스크톱 모바일 메뉴 숨김 확인.

세부 결과: `browser-test-results.json`.

## 중요한 시험 범위 제한

제작 환경의 브라우저 정책은 HTTP/file URL 탐색을 막았으므로 동일한 생성 HTML의
CSS/JS를 인라인으로 넣는 `--inline` 모드로 렌더링과 상호작용을 시험했습니다.
이 과정에서 스타일·기능 소스는 바꾸지 않았으나,
실제 HTTP 리소스 로딩·페이지 이동·localStorage 영속성의 종단간 검증은 아닙니다.
실제 파일/앵커 존재 여부는 별도 정적 검증으로 확인했습니다.

다음 사항은 완료된 것으로 간주하지 않습니다.

- 원격 GitHub Actions 실행 및 실제 Pages 배포.
- 도메인 구매/소유권, DNS 전파, SSL 인증서, www 리디렉션.
- 모든 DOI/학술지·Google Scholar·CV PDF 외부 링크의 최종 접근 가능성.
- Safari/Firefox, 실제 iOS/Android 장치, 스크린리더별 호환성 시험.
- Lighthouse 실측 점수나 공식 WCAG 적합성 인증.
- OS 클립보드 내용을 읽어 검증하는 시험. 복사 성공/수동 대안 피드백은 확인함.

배포 후 `DEPLOY_KO.md`의 최종 확인 목록을 적용하세요.

## 재현

```bash
python scripts/build.py
python scripts/validate.py
# 아래는 선택적 브라우저 테스트 환경 설치가 필요합니다.
pip install playwright
playwright install chromium
python scripts/browser_smoke.py
```

네트워크 탐색이 막힌 격리 환경에서만 `--inline`을 사용하세요.
