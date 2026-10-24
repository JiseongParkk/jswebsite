# 공개 사이트 동작 확인 · 2026-10-24

- URL: https://jiseongparkk.github.io/jswebsite/
- 확인 버전: `b8a256e478ce5ac553da45d9c1d1abb8f5b8f033`.
- Actions: https://github.com/JiseongParkk/jswebsite/actions/runs/40086230205 / build·deploy 성공.
- 검사 시각: 2026-10-24 19:32–19:36 KST.
- 브라우저: Microsoft Edge, 브라우저 연결에서 정확한 버전 미표시.
- 화면 폭: 브라우저 viewport 1440 / 768 / 390px. 세로 스크롤바를 제외한 본문 폭은 각각 1425 / 753 / 375px.

| 영역·기준 | 동작과 예상 | 확인한 실제 결과 | 근거 |
| --- | --- | --- | --- |
| 배포 P01–P06 | main push → Hugo build → Pages deploy; 실제 SHA 일치 | build와 deploy 성공, 공개 HTTPS 200, build-info.json의 SHA 일치 | 위 Actions, `evidence/live-assets.json` |
| 자산·경로 P11–P20 | 하위 경로에서 CSS·JS·이미지 요청 | 스타일 1개·스크립트 4개·이미지 3개 모두 HTTP 200. 본문 갤러리 lazy 이미지도 화면 이동 후 로드 확인 | `evidence/live-assets.json` |
| 메뉴·링크 P21–P30 | 소개/활동 등 앵커 이동, 404에서 홈 복귀 링크 | 누락 앵커·중복 ID 0개, 메뉴에서 #imaging·#activity 이동, 404.html에 /jswebsite/ 복귀 링크 존재 | DOM 검사와 공개 HTML 검사 |
| 반응형 P31–P39 | 1440/768/390에서 가로 넘침 없음, 메뉴 이동, 폭 변경 후 복귀 | 가로 넘침 요소 없음. 390 메뉴 선택 후 닫힘. #activity 상단 약 99.6px, 헤더 하단 81px로 제목 가림 없음. 1440 복귀 시 메뉴 링크 6개 표시 | 그림 1–3과 DOM 크기 검사 |
| 키보드 P41–P44 | Tab 도달, Enter 실행, Escape 메뉴 탈출, 초점 표시 | 브랜드에서 Tab으로 소개 링크 도달·solid 초점 표시·Enter로 #about 이동. 모바일 Enter로 메뉴 열림, Escape로 닫힘과 메뉴 버튼 초점 복귀 | 실제 브라우저 키 입력 |
| 미디어 조작 P12·P50 | 밝기 변경·초기화와 CT 재생·정지·초기화 | 키보드 ArrowRight: 100→105%, CSS brightness(1.05). 초기화 100%. 재생 후 17→20° 변화, 정지 false, 초기화 0°. 자동 재생 없음 | 그림 4, 조작 후 DOM |
| 개인화 P48·P59·P80 | 한국어 문서와 실제 이름, 가상 경력 제거 | lang=ko, 박지성 소개 확인, 공개 HTML에 John 및 보류한 실습 프로젝트 이름 없음 | `evidence/live-assets.json` |

## 화면 증빙

- 그림 1: `evidence/desktop-1440.png`, 홈 첫 화면, 위 URL, 1440×1000 viewport.
- 그림 2: `evidence/mobile-390.png`, 홈 첫 화면, 위 URL, 390×844 viewport.
- 그림 3: `evidence/tablet-768-activity.png`, 활동 영역, 위 URL의 #activity, 768×1024 viewport.
- 그림 4: `evidence/ct-animation-1440.png`, CT 개념도 조작 영역, 위 URL, 1440×1000 viewport.
- 모든 그림은 위 검사 시간대에 저장한 브라우저 화면이며, 수정·합성하지 않았다.

## 문제 해결과 재확인

첫 빌드 https://github.com/JiseongParkk/jswebsite/actions/runs/40086113848 에서 about 템플릿의 문자열 줄바꿈으로 parse 오류가 발생했다. 제목을 `titleLines` 배열로 바꾸고 템플릿에서 순회하도록 수정했다. 배포 버전 기록 스크립트의 줄바꿈도 수정했으며, 위 두 번째 run에서 build·deploy 성공과 공개 화면 반영을 확인했다.

## 확인 범위와 남은 점검

- 실제 브라우저의 200% 확대는 이번 연결에서 확대 적용을 확인하지 못했다. viewport 변경 검사로 대체했다고 주장하지 않으며 제출 전 별도로 확인한다.
- 독립된 다른 브라우저 및 로그인하지 않은 새 창의 재접속은 제출 전 직접 확인한다. HTTP 검사는 인증 없이 실행했다.
- 화면은 현재 구현 버전의 증빙이다. 디자인 개편 후에는 새 버전 화면과 링크로 갱신한다.
- 최종 보고서 PDF·LMS 제출은 별도 진행한다. 현재 기록은 사이트 제작 단계의 근거이다.
