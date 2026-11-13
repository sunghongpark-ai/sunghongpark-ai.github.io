# 제작 검증 기록

검증일: 2026-11-13 ("Signal Graph" 디자인 적용 후 다시 검증)
이전 검증: 2026-10-22 (개편 전 디자인)

이번 변경 범위는 `design/styles.css`, `scripts/build.py`(마크업·SVG·파비콘·글꼴 복사),
`design/og-card.html`·`og-card.png`, `design/fonts/` 추가입니다.
`content/*.json`, `design/site.js`, `design/theme.js`, `scripts/validate.py`,
`scripts/browser_smoke.py`는 수정하지 않았습니다.

## 수행한 점검

- Python 정적 빌드 완료: 7개 HTML 페이지.
  Python 3.11 / 3.12 / 3.13에서 생성 결과가 바이트 단위로 같았습니다.
  (검증 환경에 3.10이 없어 3.10에서는 실행하지 못했습니다.)
- `--base-url https://sunghongpark.ai` 빌드도 검증 통과: CNAME, canonical, og:image 주소 확인.
- `design/fonts/`를 제거한 사본에서도 빌드·검증 통과(시스템 글꼴로 대체되는 경로).
- `node --check`: `site.js`, `theme.js` 구문 오류 없음.
- 오프라인 검증(`validate.py`): 로컬 파일/앵커 참조 177건, 중복 ID, h1 개수, 메타데이터,
  JSON-LD 파싱, 필수 리소스, 출판 논문/BibTeX 일치 검사 통과.
  (참조 수는 글꼴 preload 링크 14건과 페이지 안 이동 링크 5건이 추가되어 158건에서 늘었습니다.)
- Chromium UI 테스트(`browser_smoke.py --inline`): **98개 검사 통과**, JavaScript runtime exception 0건.
  - 페이지별 320 / 390 / 768 / 1024 / 1440px 가로 폭에서 수평 넘침 없음.
  - 13개 논문 초기 표시, 문자열 검색, 연도 조합, 분야 필터, 결과 없음, 초기화 확인.
  - 인용창, BibTeX 전환, 복사 피드백, Escape 닫기와 포커스 복원 확인.
  - 모바일 메뉴 열기/닫기와 Contact 항목 확인.
  - 테마 전환, 개념적 그래프 모드 전환, 이메일 복사 피드백 확인.
  - 52개 아카이브 기록, 특허 17건 / 학회 31건 필터 및 항목 펼치기 확인.
  - JavaScript 비활성화 시 논문과 메뉴 접근 가능 여부 확인.
  - 움직임 감소 설정 반영과 데스크톱 모바일 메뉴 숨김 확인.
- 로컬 HTTP 서버 렌더링 점검(별도 스크립트, 실제 글꼴 3종이 로드된 상태):
  7개 페이지 × 23개 폭(320–1920px, 라이트) + 7개 페이지 × 5개 폭(다크) = **196회 렌더링**에서
  수평 넘침 0건, 화면 밖으로 나간 요소 0건, 실패한 요청 0건, JavaScript 오류 0건.
- 스크린샷 육안 확인: 7개 페이지의 1440px 화면, 390·320px 모바일, 768·1024px,
  다크 테마, 모바일 메뉴, 인용창, 검색 결과 없음, 아카이브 펼침, 복사 알림,
  JavaScript 비활성 화면, 키보드 포커스 표시, 인쇄 미디어(CV·논문·홈).
- 색상 점검: `styles.css`의 색상 값이 지정된 6색과 Ink/Paper의 투명도 혼합뿐임을 스크립트로 확인.
- 명도 대비: 색상 값으로 계산한 비율을 `DESIGN_SYSTEM.md`에 기록.

세부 결과: `browser-test-results.json` (`--inline` 실행 결과).

## 로컬 HTTP 모드의 `browser_smoke.py`에 대하여

옵션 없이 실행하면 "Citation copy feedback" 검사에서 중단됩니다.
127.0.0.1은 보안 컨텍스트라 `navigator.clipboard`가 비동기로 처리되는데,
테스트가 그 완료를 기다리지 않고 문구를 바로 읽기 때문입니다.
같은 이유로 "Email copy feedback" 검사도 영향을 받습니다.
개편 전 디자인에서도 같은 지점에서 중단되는 것을 확인했으므로 이번 변경으로 생긴 문제가 아닙니다.

저장소의 테스트 스크립트는 고치지 않았습니다. 작업용 사본에서 이 두 검사에만 대기를 추가해
로컬 HTTP 모드로 실행했을 때는 **98개 검사를 모두 통과**했습니다.
실제 화면에서는 인용 복사 문구와 이메일 복사 알림이 정상적으로 나타납니다.

## 중요한 시험 범위 제한

`--inline` 모드는 생성된 HTML에 CSS/JS를 인라인으로 넣어 렌더링과 상호작용을 시험합니다.
스타일·기능 소스는 바꾸지 않지만, 실제 HTTP 리소스 로딩·페이지 이동·localStorage 영속성의
종단간 검증은 아니며, 이 모드에서는 글꼴 파일이 로드되지 않아 대체 글꼴로 렌더링됩니다.
그래서 실제 글꼴을 쓰는 화면은 위의 로컬 HTTP 렌더링 점검으로 따로 확인했습니다.

다음 사항은 완료된 것으로 간주하지 않습니다.

- 원격 GitHub Actions 실행 및 실제 Pages 배포. 이번 변경은 로컬 파일에만 반영되었습니다.
- 도메인 구매/소유권, DNS 전파, SSL 인증서, www 리디렉션.
- 모든 DOI/학술지·Google Scholar·CV PDF 외부 링크의 최종 접근 가능성.
- Safari/Firefox, 실제 iOS/Android 장치, 스크린리더별 호환성 시험.
- Windows·macOS의 한글 시스템 글꼴 렌더링. 검증은 Linux의 Chromium에서 했고,
  한글 특허명은 각 운영체제의 시스템 글꼴로 표시됩니다.
- 실제 프린터 출력과 PDF 페이지 나눔. 인쇄 스타일은 print 미디어 화면으로만 확인했습니다.
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
python scripts/browser_smoke.py --inline
```

`--inline`을 빼면 로컬 HTTP 서버로 실제 리소스 로딩까지 시험하지만,
위에 적은 복사 피드백 검사 때문에 중단될 수 있습니다.
