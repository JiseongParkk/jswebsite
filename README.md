# 박지성 · 바이오메디컬공학 의료영상 포트폴리오

- 공개 사이트: https://jiseongparkk.github.io/jswebsite/
- 저장소: https://github.com/JiseongParkk/jswebsite
- 테마: [Toha](https://github.com/hugo-toha/toha), MIT. 원본 `LICENSE` 유지.
- 주 언어: 한국어. 소개·관심 분야·MRI/CT·활동 기록·학습 계획을 담은 단일 페이지.

## 실행 환경

Windows에서 소스를 편집하며, 실제 배포 빌드는 GitHub Actions의 Ubuntu에서 실행한다.
`mise.toml`에 Hugo **0.167.0 Extended**, Node.js **26.11.1**, Go **1.27.2**를 고정한다.
`mise`가 설치된 환경에서 저장소 루트 기준으로 실행한다.

```sh
git clone https://github.com/JiseongParkk/jswebsite.git
cd jswebsite
mise install
mise run build
```

`mise run build`는 루트 npm 의존성 설치 → exampleSite Hugo module/npm 의존성 설치 → Hugo production 빌드 순서로 실행한다.
결과는 `exampleSite/public/`에 생성된다. 빌드 결과와 node_modules는 커밋하지 않는다.

로컬 확인:

```sh
mise run example-site
```

터미널에 나온 localhost 주소를 연다. 프로젝트 배포 경로는 `/jswebsite/`이며 운영 `baseURL`을 임의로 도메인 루트로 바꾸지 않는다.
Python 3는 배포 버전 JSON 작성과 선택적인 커밋 집계 도구에 사용한다. 사이트 자체는 서버·데이터베이스 없이 동작한다.

## 어디를 수정하나요?

| 대상 | 경로 |
| --- | --- |
| 이름·GitHub·소개 | `exampleSite/data/portfolio/identity.json`, `hero.json`, `about.json` |
| 관심 분야·학습 계획 | `exampleSite/data/portfolio/interests.json`, `roadmap.json` |
| 실제 활동 기록 | `exampleSite/data/portfolio/activity.json` |
| MRI·CT와 출처 | `exampleSite/data/portfolio/gallery.json`, `sources.json` |
| 메뉴 | `exampleSite/data/portfolio/navigation.json` |
| 한국어 공통 조작명 | `exampleSite/i18n/ko.yaml` |
| 운영 설정 | `exampleSite/hugo.yaml` |
| 개인 화면 템플릿 | `exampleSite/layouts/partials/portfolio/` |
| 스타일·조작 | `exampleSite/assets/styles/portfolio/`, `exampleSite/assets/scripts/portfolio/` |
| 이미지 원본 | `exampleSite/static/images/portfolio/` |

이후 본인 프로젝트를 추가할 때는 실제 수행 시기·역할·목적·과정·산출물·한계·다음 개선을 함께 작성한다.
`params.medicalPortfolio.animation`을 false로 바꾸면 CT 개념도 섹션을 끈다.

## 커밋과 재배포

```sh
git status
git add .
git diff --cached
git commit -m "실제 변경 내용을 설명하는 메시지"
git push origin main
```

GitHub Settings → Pages → Source는 **GitHub Actions**를 사용한다.
main push가 `.github/workflows/deploy-pages.yml`의 build와 deploy를 실행한다.
[Actions](https://github.com/JiseongParkk/jswebsite/actions)에서 두 작업이 성공했는지 확인한 뒤 공개 사이트를 새로고침한다.
공개 [배포 버전 JSON](https://jiseongparkk.github.io/jswebsite/build-info.json)의 commit과 해당 main SHA가 일치해야 한다.

## 확인할 동작

소개·활동 앵커 이동, MRI/CT 이미지, CT 밝기·초기화, CT 개념도 재생·정지·초기화, 390/768/1440px 배치, Tab/Enter/Escape 조작을 확인한다.
JavaScript 없이도 모든 소개와 출처를 읽을 수 있다. CT 조작은 JavaScript가 로드되면 나타난다. 자동 재생은 없다.

## 기록과 출처

- [외부 자료·직접 제작 범위](docs/SOURCES.md)
- [AI 활용 기록 초안](docs/AI-USAGE.md)
- [제출 전 점검표](docs/SUBMISSION-CHECKLIST.md)
- `scripts/audit-commits.py`: 최종 main의 커밋 집계 근거 작성용. 각 diff의 유효성은 직접 확인한다.

과제 최종 PDF와 LMS 제출은 사이트 변경 후 SHA·Actions·화면 증빙을 맞춰 별도로 완료한다.
