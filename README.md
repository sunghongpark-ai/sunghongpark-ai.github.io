# Sunghong Park — Research × AI Hybrid

실제 공개 홈페이지의 연구 내용을 바탕으로 제작한 개인 연구자 웹사이트입니다.
**가벼운 HTML + CSS + JavaScript**, **Python 표준 라이브러리 빌드**, **GitHub Pages 배포**로 구성됩니다.
Node.js, npm, 유료 테마, 외부 웹폰트, 데이터베이스, API 키가 필요하지 않습니다.

- 현재 주소: https://sunghongpark-ai.github.io/
- 목표 주소: https://sunghongpark.ai/
- 콘텐츠 확인 기준: 2026-10-22
- 기본 언어: 영어. 기존 한국어 특허명은 원문 유지.
- 사이트 소스와 배포 파일은 제작되었으며, 실제 GitHub 저장소·DNS·도메인 등록은 변경하지 않았습니다.

## 1. 바로 열어 보기

압축을 해제하고 **`site/index.html`을 브라우저에서 여세요.**
콘텐츠가 HTML에 포함되어 있어 `fetch()`나 서버 없이도 기본 페이지와 검색을 사용할 수 있습니다.
브라우저 보안 설정에 따라 클립보드·테마 저장이 제한될 때는 아래 로컬 서버를 사용하세요.

```bash
# 프로젝트 최상위 폴더에서 실행. Python 3.10 이상 권장.
python -m http.server 8000 --directory site
```

브라우저에서 http://localhost:8000 에 접속합니다.
Windows에서 `python` 명령을 찾지 못하면 `py`를 사용하세요.

## 2. 권장 배포 방식

**소스 패키지 전체를 기존 `sunghongpark-ai.github.io` 저장소 루트에 넣고 GitHub Actions로 배포합니다.**
저장소 루트 바로 아래에 `.github`, `content`, `design`, `scripts`, `site`가 있어야 합니다.
다운로드한 ZIP 자체나 `sunghongpark-research-site` 상위 폴더를 통째로 한 단계 깊게 올리지 마세요.

1. 기존 사이트를 백업하거나 새 브랜치에서 작업합니다.
2. 패키지를 저장소 루트에 넣습니다. 기존 `index.md`, `_config.yml`, 사진은 지워야 할 필요가 없습니다.
3. GitHub → 저장소 → **Settings → Pages → Source → GitHub Actions**를 선택합니다.
4. `main` 브랜치에 병합하거나 `.github/workflows/pages.yml`을 수동 실행합니다.
5. 워크플로는 `content/*.json`을 읽고 사이트를 빌드한 다음 **`site/` 폴더만** 공개합니다.

자세한 절차, Git 명령, 롤백, DNS 설정: **[docs/DEPLOY_KO.md](docs/DEPLOY_KO.md)**

## 3. sunghongpark.ai 연결

도메인 소유권과 DNS가 확인되지 않은 상태에서 주소를 강제로 바꾸지 않도록,
기본 패키지는 기존 `github.io` 주소를 사용합니다. 도메인을 확보한 뒤:

- GitHub 계정 설정에서 도메인 소유권을 확인합니다.
- 저장소 Pages 설정의 Custom domain과 DNS를 설정합니다.
- 저장소의 **Settings → Secrets and variables → Actions → Variables**에서
  `SITE_URL`을 `https://sunghongpark.ai`로 지정합니다. Secret이 아니라 Variable입니다.
- 워크플로를 다시 실행합니다.

`CNAME`, canonical URL, Open Graph 주소, sitemap, robots.txt가 새 주소에 맞춰 생성됩니다.
**GitHub Actions 방식에서는 CNAME 파일만으로 GitHub의 Custom domain 설정이 바뀌지 않습니다.**

로컬에서 같은 결과를 만들려면:

```bash
python scripts/build.py --base-url https://sunghongpark.ai
python scripts/validate.py
```

기존 주소로 다시 빌드하려면:

```bash
python scripts/build.py --base-url https://sunghongpark-ai.github.io
```

## 4. 파일 구조

```text
sunghongpark-research-site/
├── .github/workflows/pages.yml  # 빌드·검사·배포
├── content/
│   ├── profile.json            # 프로필, 경력, 연구 방향, 과제, 소식
│   ├── publications.json       # 게재 논문 13편
│   ├── ongoing.json            # 심사 중 원고 1편, 진행 연구 8건
│   └── archive.json            # 특허 출원 17건, 발표 31건, 수상 4건
├── design/
│   ├── styles.css              # 색상, 타이포그래피, 반응형, 인쇄
│   ├── site.js                 # 메뉴, 필터, 인용, 테마, 이메일 복사
│   ├── theme.js                # 저장된 테마를 초기 로딩 전에 적용
│   ├── og-card.html            # 링크 공유 이미지의 편집 원본
│   └── og-card.png             # 1200 × 630 공유 이미지
├── scripts/
│   ├── build.py                # 외부 패키지가 필요 없는 정적 빌드
│   ├── validate.py             # 로컬 링크·메타데이터 검사
│   └── browser_smoke.py        # 선택 사항: Playwright UI 점검
├── site/                       # 생성된 배포 파일; 바로 열어 볼 수 있음
│   ├── index.html
│   ├── research.html
│   ├── publications.html
│   ├── projects.html
│   ├── cv.html
│   ├── archive.html
│   ├── 404.html
│   ├── publications.bib
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── .nojekyll
│   └── assets/
├── previews/                   # 실제 브라우저 렌더링 미리보기
└── docs/                       # 한글 배포·콘텐츠 점검·테스트 기록
```

## 5. 내용 수정

일반적인 수정은 HTML보다 **`content/*.json`**에서 하는 것이 좋습니다.
JSON은 마지막 항목 뒤에 쉼표를 둘 수 없으며, 문자열 안의 큰따옴표는 `\"`로 씁니다.
수정 후:

```bash
python scripts/build.py
python scripts/validate.py
```

GitHub Actions를 사용하면 콘텐츠 JSON을 커밋할 때 자동으로 재빌드됩니다.
배포가 Actions 방식일 때 `site/*.html`만 직접 고치면 다음 빌드에서 덮어써집니다.

### 논문 추가 예시

`content/publications.json`의 배열에 같은 형식의 객체를 추가합니다.
아래는 형식 설명이며 실제 연구 실적으로 입력하지 마세요.

```json
{
  "id": "unique-slug-2027",
  "title": "실제 게재 논문 제목",
  "authors": "실제 저자 목록",
  "year": 2027,
  "journal": "실제 학술지명",
  "volume": "실제 권",
  "pages": "실제 페이지 또는 논문번호",
  "doi": "10.1234/actual-doi",
  "tags": ["Graph learning", "Biomedical AI"],
  "featured": false,
  "summary": "논문에 근거한 짧은 설명",
  "label": "짧은 주제명"
}
```

`featured: true`인 논문이 홈의 Selected publications에 표시됩니다.
기본 분야명은 `Graph learning`, `Biomedical AI`, `Domain adaptation`, `Other applications`입니다.
새 분야를 만들면 `scripts/build.py`의 필터 목록도 함께 수정하세요.
홈의 논문·특허·과제 수는 데이터 항목 수에서 자동 계산됩니다.
심사 중 원고는 `ongoing.json`에 별도로 관리하며 게재 논문 수·BibTeX에 포함되지 않습니다.

### CV와 연락처

현재 CV 버튼은 기존 홈페이지에 연결되어 있던 **외부 GitHub 첨부 PDF**를 엽니다.
PDF 자체를 새로 작성하거나 변경한 것이 아니며, 패키지 안에 복사하지 않았습니다.
본인 PDF를 `design/cv.pdf`에 보관하는 것만으로는 자동 배포되지 않습니다.
로컬 CV를 쓰려면 `scripts/build.py`에 복사 단계를 추가해 `site/assets/cv.pdf`에 넣고,
`profile.json`의 `cv_url`을 실제 공개 HTTPS 주소로 바꾸세요.
기존 외부 CV의 업데이트 표시는 `cv_updated`에서 수정할 수 있습니다.

메일은 기존 공개 KAIST 주소를 사용합니다. `contact@sunghongpark.ai` 같은 메일박스를
도메인 구입만으로 생성하지 않습니다. 새 이메일 서비스 설정 후 `profile.json`을 바꾸세요.
연락처는 mailto 링크이며, 서버 없는 가짜 전송 폼은 넣지 않았습니다.

## 6. 구현 기능

- 반응형 6개 콘텐츠 페이지 + 404 페이지
- 밝은 학술·에디토리얼 화면과 네이비/청록색 그래프 시각화
- 라이트/다크 테마, 모바일 내비게이션, 키보드 포커스와 건너뛰기 링크
- 논문 검색, 연도·분야 필터, 검색 결과 수, 초기화, 검색 조건 URL 반영
- 인용문/BibTeX 모달, 복사·수동 복사 fallback, 전체 BibTeX 다운로드
- 특허·발표·수상 기록 검색 및 상세 펼치기
- 개념적 연구 맵 전환; 실제 실험 성능을 나타내는 그래프가 아님
- JavaScript 없이도 주요 콘텐츠와 메뉴 접근 가능
- 움직임 감소 설정 반영, CV 인쇄 스타일
- canonical, Open Graph, Person JSON-LD, favicon, sitemap, robots.txt
- 구 홈페이지의 주요 `#section` 북마크를 새 페이지로 연결
- 외부 분석 추적 코드, 외부 폰트 요청, 광고, API 키 없음

## 7. 검증 및 확인해야 할 내용

기본 검증: `python scripts/validate.py`
선택적 UI 테스트:

```bash
pip install playwright
playwright install chromium
python scripts/browser_smoke.py
```

제작 환경에서는 외부/로컬 URL 탐색이 제한되어 `--inline` 모드로 동일 HTML/CSS/JS를
Chromium에 넣어 **98개 렌더링·상호작용 검사를 수행**했습니다.
원격 GitHub 배포, DNS·SSL, 외부 PDF와 모든 DOI의 도달 가능성까지 통과했다고 주장하지 않습니다.
자세한 범위: [docs/TEST_REPORT_KO.md](docs/TEST_REPORT_KO.md).

기존 콘텐츠의 숫자 불일치, 오기 수정, 상태 확인 사항은
**[docs/CONTENT_REVIEW_KO.md](docs/CONTENT_REVIEW_KO.md)**를 확인하세요.
