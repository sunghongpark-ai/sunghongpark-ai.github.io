# GitHub Pages 배포 및 sunghongpark.ai 연결

## 0. 범위와 안전한 기본값

이 패키지는 실제 서비스에 올릴 정적 파일과 GitHub Actions 워크플로를 포함합니다.
저장소 변경, 도메인 구입, DNS 수정, 실제 배포는 실행하지 않았습니다.
기본 주소는 `https://sunghongpark-ai.github.io`입니다.
도메인을 구입하기 전에도 기존 주소에서 사이트를 사용할 수 있습니다.

## 1. 기존 사이트 보존

현재 공개 저장소는 `sunghongpark-ai/sunghongpark-ai.github.io`이며 확인 당시 기본 브랜치는 `main`입니다.
기존 루트에는 `index.md`, `_config.yml`, `assets/css`, `IMG_SHP.jpg`가 있습니다.
새 워크플로는 **`site/`만 배포**하므로 기존 파일을 즉시 지울 필요가 없습니다.
특히 사진·이력 원본을 실수로 삭제하지 마세요.

로컬 Git을 사용할 경우:

```bash
git clone https://github.com/sunghongpark-ai/sunghongpark-ai.github.io.git
cd sunghongpark-ai.github.io
git switch -c redesign/research-ai-hybrid
```

다운로드한 전체 소스 ZIP을 풀고, 내부 파일을 이 저장소 루트에 복사합니다.
`.github`처럼 숨김 처리되는 폴더도 반드시 포함하세요.
이미 같은 이름의 파일이나 워크플로가 있으면 덮어쓰기 전에 차이를 검토하세요.

```bash
python scripts/build.py
python scripts/validate.py
git status
# 변경 목록을 확인한 뒤 필요한 파일만 추가합니다.
git add content design scripts site docs previews .github/workflows/pages.yml README.md .gitignore
git diff --cached --stat
git commit -m "Redesign research website with Research x AI Hybrid layout"
git push -u origin redesign/research-ai-hybrid
```

GitHub에서 이 브랜치의 Pull Request를 만들고 확인한 후 `main`으로 병합합니다.
Git 명령 없이 GitHub 웹 UI를 사용할 때도 최종 저장소 루트에 동일한 디렉터리 구조가 있어야 합니다.
ZIP 파일 자체를 올리는 것으로는 배포되지 않습니다.

## 2. GitHub Actions 배포 선택

1. 저장소 → **Settings → Pages**.
2. **Build and deployment → Source → GitHub Actions**.
3. `main` 병합 후 **Actions → Build and deploy research website** 실행 결과 확인.
4. 자동 실행이 없으면 **Run workflow**에서 `main`을 선택.
5. 배포 성공 뒤 기존 `https://sunghongpark-ai.github.io/`를 열고 확인.

워크플로는 Python 표준 라이브러리로 HTML을 생성하고 로컬 링크 검사 후 `site/`만 업로드합니다.
API 키나 Personal Access Token을 코드에 넣을 필요가 없습니다.
GitHub가 제공하는 워크플로 토큰에 `contents: read`, `pages: write`, `id-token: write`를 사용합니다.

기존에 별도의 Pages 배포 워크플로가 있다면 동시 배포 경쟁이 없도록 하나만 활성화하세요.
기본 브랜치 이름을 바꾸면 `.github/workflows/pages.yml`의 `branches: [main]`도 수정합니다.

## 3. 도메인 확보와 소유권 검증

`sunghongpark.ai`의 등록 가능 여부·소유권은 이 제작 작업에서 확인하거나 변경하지 않았습니다.
본인 계정으로 등록을 완료한 후 다음을 진행하세요.

GitHub **계정 설정 → Pages → Add a domain**에서 `sunghongpark.ai`를 추가합니다.
GitHub가 화면에 표시하는 TXT 호스트와 값을 DNS에 정확히 넣고 Verify를 실행하세요.
TXT 값은 계정별로 다르므로 이 문서에서 임의 값을 제공하지 않습니다.
검증 완료 후에도 TXT 레코드를 유지합니다.

## 4. Pages 사용자 지정 도메인과 DNS

먼저 해당 저장소 **Settings → Pages → Custom domain**에 `sunghongpark.ai`를 저장합니다.
이후 도메인 DNS 관리자에서 아래 GitHub Pages 권장 레코드를 설정합니다.

| 유형 | 이름/호스트 | 값 |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | sunghongpark-ai.github.io |

주의 사항:

- `www`의 CNAME은 저장소 이름이나 URL 경로가 아니라 **계정의 github.io 호스트**입니다.
- CNAME 값에 `https://`, `/`, `/site`를 붙이지 않습니다.
- 루트 `@`에서 다른 서비스로 향하는 기존 A/AAAA/CNAME 레코드가 있으면 충돌을 확인합니다.
- 메일용 MX/TXT, GitHub 소유권 검증 TXT는 무작정 삭제하지 않습니다.
- 와일드카드 `*` DNS는 사용하지 않습니다.
- Cloudflare의 프록시 사용 여부는 GitHub DNS 검사와 인증서 확인에 영향을 줄 수 있으므로
  초기 연결은 DNS-only로 확인하는 것이 운영상 단순합니다. 프록시를 별도로 사용할 경우 제공업체 문서를 확인하세요.
- SSL 인증서가 준비되면 GitHub Pages의 **Enforce HTTPS**를 활성화합니다.

## 5. 빌드 URL 전환

GitHub 저장소:

**Settings → Secrets and variables → Actions → Variables → New repository variable**

```text
Name:  SITE_URL
Value: https://sunghongpark.ai
```

그다음 Actions 워크플로를 다시 실행합니다.

새 빌드는 `site/CNAME`에 `sunghongpark.ai`를 기록하고 다음 항목도 함께 바꿉니다.
canonical, Open Graph URL/이미지 주소, Person JSON-LD URL, sitemap, robots.txt.

**CNAME 생성과 GitHub Pages Custom domain 설정은 서로 다릅니다.**
특히 GitHub Actions 배포에서는 CNAME 파일만 넣어서 GitHub 설정이 변경되었다고 간주하면 안 됩니다.

`www.sunghongpark.ai`는 별도 복제 사이트를 만들기보다 메인 도메인의 보조 진입점으로 사용하세요.
GitHub Pages의 사용자 지정 도메인 및 DNS 설정을 완료한 뒤 리디렉션을 직접 확인합니다.

## 6. 별도 제공된 도메인용 정적 ZIP

`sunghongpark-ai-static.zip`은 `sunghongpark.ai` canonical과 CNAME이 포함된 정적 배포본입니다.
도메인을 구입·검증·연결한 뒤 사용하는 패키지입니다.

가장 단순한 branch 배포를 사용할 때는 ZIP **안의 파일**을 배포 브랜치 루트에 넣고
Settings → Pages → Deploy from a branch → 해당 브랜치 → `/ (root)`를 선택합니다.
`.nojekyll`과 `CNAME`을 빠뜨리지 마세요.
기존 Jekyll `index.md`를 같은 배포 루트에서 함께 사용하지 말고, 백업 후 충돌을 해소하세요.
소스 패키지의 Actions 방식과 branch 방식을 동시에 운영하지 않습니다.

장기적으로는 논문 추가 시 자동 빌드되는 **소스 + Actions 방식**을 권장합니다.

## 7. 최종 확인

- 메인 주소와 www 주소가 의도한 사이트로 연결되는지 확인.
- HTTPS 및 인증서 확인, 혼합 콘텐츠 경고 확인.
- Home / Research / Publications / Projects / About / Archive 페이지 확인.
- 실제 DOI 클릭, 외부 CV 다운로드, Google Scholar, GitHub 링크 확인.
- 메일 앱이 설정된 장치에서 연락처 mailto 동작 확인.
- Publications 검색, 연도/분야 필터, 인용문/BibTeX 복사 확인.
- 모바일 메뉴, 키보드 Tab/Escape, 라이트/다크 모드 확인.
- sitemap의 도메인이 실제 메인 주소와 일치하는지 확인.
- 필요 시 본인 계정으로 검색엔진 소유권 등록. 이 패키지가 자동 등록하지는 않습니다.

## 8. 되돌리기

사이트 개편 자체를 되돌릴 때는 이전 커밋/브랜치 또는 PR revert를 사용합니다.
원래 Jekyll branch 배포로 돌아갈 때는 Settings → Pages의 Source도 원래 방식으로 복원합니다.
도메인 연결을 해제할 때는 Pages의 Custom domain과 DNS를 함께 검토하세요.
DNS만 GitHub를 계속 가리키게 남겨 두거나, 소유권 검증 TXT를 임의로 삭제하지 마세요.

## 공식 문서

확인 기준: 2026-10-22. UI와 정책은 변경될 수 있습니다.

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
- https://github.com/actions/upload-pages-artifact/releases
- https://github.com/actions/deploy-pages/releases
