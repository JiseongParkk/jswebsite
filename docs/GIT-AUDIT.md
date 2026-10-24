# 커밋 집계 근거 · 사이트 제작

- 집계 시작 기준: `a8b1a30fc0e50caa9eb2513e4cc3781cec6e8d88` **제외**.
- 이 기록의 포함 종료 SHA: `261a571b2a185538bbbbb3630702f94a8a718c0a`.
- 후보 커밋 수: **56**. 구간 내 제외: **0**. 실제 파일 변경이 있는 작업 커밋: **56**.
- 이전 커밋 6개는 원본 등록·기존 설정·이전 배포 작업이 섞여 있어 이 집계에서 모두 보수적으로 제외했다.
- 이 문서를 추가한 커밋과 이후 커밋은 위 숫자에 포함하지 않았다. 최종 main에는 위 구간 전체가 포함되어야 한다.
- 빈 커밋, 봇 빌드 산출물 커밋, 자체 변경 없는 병합 커밋은 이 구간에 없다.
- 설정·콘텐츠·템플릿·스타일·동작·출처 문서·오류 수정·검증 증빙을 실제 수정한 이력이다. AI 보조를 활용했으며 자동 채점 승인으로 간주하지 않는다.
- 전체 목록과 수정 파일은 [commit-audit.json](commit-audit.json)에 기록했다.
- 이력: https://github.com/JiseongParkk/jswebsite/commits/261a571b2a185538bbbbb3630702f94a8a718c0a/

## 재집계

저장소 루트에서 `python scripts/audit-commits.py --base a8b1a30 --head 최종SHA`를 실행한다. 후보 목록의 diff를 확인해 제외 항목을 차감한다. 최종 보고서에는 마지막 main SHA와 같은 Actions URL을 사용한다.

## 작업별 커밋

- [9dee9ad](https://github.com/JiseongParkk/jswebsite/commit/9dee9ad79c77122ed98381cfa282a5d91ce25572) · Pin the known working Hugo Extended, Node and Go versions
- [f714414](https://github.com/JiseongParkk/jswebsite/commit/f7144148cf03234eeecf16e71f4a883f4d063f51) · Exclude local credentials, Python caches and generated reports
- [170d565](https://github.com/JiseongParkk/jswebsite/commit/170d565cf04061e71347507a067049d8a9277597) · Configure the portfolio for Korean and the public project URL
- [e49d2d9](https://github.com/JiseongParkk/jswebsite/commit/e49d2d914328a973eb301dbc4a7f0924439ca16c) · Remove published demo posts and notes from both content mounts
- [9008ca0](https://github.com/JiseongParkk/jswebsite/commit/9008ca03e45d82904cfa150006828b75be4c2ca6) · Replace John and fictional credentials with Jiseong Park identity
- [843cdd6](https://github.com/JiseongParkk/jswebsite/commit/843cdd60f8cfff3aad5ce945519ebad675731dc3) · Add Korean labels for navigation and accessible controls
- [a4a3339](https://github.com/JiseongParkk/jswebsite/commit/a4a33399413393aee8cb650ecd11741f52ae2cb3) · Create an original signal-and-scan identity mark and favicon
- [df16ec1](https://github.com/JiseongParkk/jswebsite/commit/df16ec10e297e69d886acdc799576cfdac55e10a) · Define a concise Korean portfolio navigation structure
- [a903704](https://github.com/JiseongParkk/jswebsite/commit/a90370451422f6266ae305d2559a0cbc3a3eb4f6) · Establish readable typography and medical imaging design tokens
- [0d3f351](https://github.com/JiseongParkk/jswebsite/commit/0d3f351d393000ca2c6d3879ec88eafc3983a20a) · Build a configurable site-level homepage while retaining the Toha fallback
- [c1ce68c](https://github.com/JiseongParkk/jswebsite/commit/c1ce68ce84c223a6998302d60f7adb06587b0a83) · Add a personal brand header and semantic section navigation
- [1a642c4](https://github.com/JiseongParkk/jswebsite/commit/1a642c414099798fd043903b16c42394c2e54e15) · Support a keyboard-accessible mobile menu and width changes
- [56e017c](https://github.com/JiseongParkk/jswebsite/commit/56e017cbdc9f5cb6ef9d1f9ce026e737d7159b11) · Write a biomedical engineering introduction and imaging career focus
- [fe2cbc2](https://github.com/JiseongParkk/jswebsite/commit/fe2cbc2a7780fcd982dcfe366f9b548931c2ce4a) · Create an MRI-led hero with original copy and image attribution
- [e533f19](https://github.com/JiseongParkk/jswebsite/commit/e533f19f48a92913f229448ee637c2a7039019d5) · Describe the major, career direction and personal learning approach
- [3ff7cae](https://github.com/JiseongParkk/jswebsite/commit/3ff7caef92d122b7c6336181b355562d0d2cbf78) · Add an accessible personal profile section without fictional credentials
- [8bbba11](https://github.com/JiseongParkk/jswebsite/commit/8bbba11c60d3bafadf80ced7104b30515e7fcf66) · Explain three medical imaging interests with concrete reasons and next steps
- [4050d84](https://github.com/JiseongParkk/jswebsite/commit/4050d84c9a149fb0dcf0c67e471761c8b1946126) · Present acquisition, reconstruction and validation as distinct interests
- [2f112ce](https://github.com/JiseongParkk/jswebsite/commit/2f112ce068ea828b2b9850dfe615ed7df844159e) · Connect current tool experience to actual portfolio work
- [d9efe46](https://github.com/JiseongParkk/jswebsite/commit/d9efe4654e494b27753f7f8ac05a109120e8d4f2) · Display skill usage examples without unsupported proficiency scores
- [a4f1854](https://github.com/JiseongParkk/jswebsite/commit/a4f1854958cec25dc16ba00fbe40f4c71ed3d870) · Add an attributed CC BY-SA sagittal MRI educational image
- [e66b3b3](https://github.com/JiseongParkk/jswebsite/commit/e66b3b389fffe638a3adb274d39a3559b8953b87) · Add a CC0 axial CT image and preserve the original attribution
- [002ac0a](https://github.com/JiseongParkk/jswebsite/commit/002ac0aa53a1c946a358961975fd51f0aa4e55b3) · Write MRI and CT educational captions and distinguish external examples
- [d71ee83](https://github.com/JiseongParkk/jswebsite/commit/d71ee83b61fb427f532a718bcea45578afe18925) · Add proportionate MRI and CT image galleries with alternative descriptions
- [3e5e3b3](https://github.com/JiseongParkk/jswebsite/commit/3e5e3b31eb4eb3961f28c36ff49ffd5299424ade) · Implement keyboard-operable CT display brightness and reset controls
- [28d6bc5](https://github.com/JiseongParkk/jswebsite/commit/28d6bc589ef7076a79daf70085e5fc2754ac2b5c) · Explain the scope and limits of an original CT acquisition animation
- [6f53458](https://github.com/JiseongParkk/jswebsite/commit/6f534589d27dd06be50a96ee1425d2b261f03258) · Draw a semantic CT acquisition schematic as an optional site feature
- [efd9c2f](https://github.com/JiseongParkk/jswebsite/commit/efd9c2fdfcfd92792546936eb2151e206a6d641e) · Style the CT concept animation with clear labels and playback controls
- [fa6bd49](https://github.com/JiseongParkk/jswebsite/commit/fa6bd49f09d065b2036c5fc86abbbd6118f71603) · Animate the CT source and detector with play, pause and reset
- [7e202e3](https://github.com/JiseongParkk/jswebsite/commit/7e202e3b0bb1f76d5e725c467cdd7c66f2d56df4) · Record the real portfolio-building activity with role, process and limitations
- [3474239](https://github.com/JiseongParkk/jswebsite/commit/3474239ce84d1a66ec4363eb6683cc7794108e33) · Publish an evidence-linked activity record ready for future project additions
- [d252a5e](https://github.com/JiseongParkk/jswebsite/commit/d252a5e6f706286b1b9345ae2ad65231a6ba1929) · Define actionable medical imaging learning goals and expected outputs
- [590fb0d](https://github.com/JiseongParkk/jswebsite/commit/590fb0dbc0824d8ede5439a98025f513fea234d6) · Present learning plans as future actions rather than completed projects
- [f1dcf7d](https://github.com/JiseongParkk/jswebsite/commit/f1dcf7d29ed4b98c52d33a894ba121223704cdc5) · Record theme, image licenses and primary medical imaging references
- [8b1bf82](https://github.com/JiseongParkk/jswebsite/commit/8b1bf824945b86483e67b6d85f290c5bc84f0bf6) · Expose source attribution and license links on the public page
- [9f273d9](https://github.com/JiseongParkk/jswebsite/commit/9f273d9c04f33579bab07ab469e66d35d59a49fb) · Add personal footer navigation and retain the Toha MIT credit
- [368c9cc](https://github.com/JiseongParkk/jswebsite/commit/368c9ccad0fb92660ac81af83a64a55b67cb661f) · Adapt all portfolio sections for mobile, tablet and desktop widths
- [8166831](https://github.com/JiseongParkk/jswebsite/commit/81668319a74b614190b344353d75b3b08c2c2565) · Add a skip link, visible keyboard focus and anchor clearance
- [2a6760f](https://github.com/JiseongParkk/jswebsite/commit/2a6760f1b7dfcf9968d1a0eacb2f1a1aaa8efc65) · Respect reduced motion and keep the CT animation opt-in
- [802f583](https://github.com/JiseongParkk/jswebsite/commit/802f5831e89b5795a87a2bd71079d7a6c7fc5f6a) · Provide a Korean not-found page with a project-path-safe home link
- [b55f05e](https://github.com/JiseongParkk/jswebsite/commit/b55f05ea4a459cee68e3785899bc16b2164158b1) · Set personal Korean search and sharing metadata
- [577068d](https://github.com/JiseongParkk/jswebsite/commit/577068d7be376e861a9c4cf0daf400c7f40d9ad2) · Make portfolio content readable when printed or saved as PDF
- [8a49b1f](https://github.com/JiseongParkk/jswebsite/commit/8a49b1ff573608e3ac473e2b5137155095f705ec) · Indicate the visible section in the navigation without rewriting history
- [59f9f4b](https://github.com/JiseongParkk/jswebsite/commit/59f9f4b7d0eb543188972c727547dec6cbc9bc0b) · Attach the built commit and Actions URL to every Pages artifact
- [bfd9e58](https://github.com/JiseongParkk/jswebsite/commit/bfd9e5806384ae319020c95d5db96d75068dc315) · Link the public footer to the version actually deployed
- [2ae5d8b](https://github.com/JiseongParkk/jswebsite/commit/2ae5d8bcd7b243ad9f3a23a7c67f3a7afc4f352b) · Document image reuse conditions and the scope of AI-assisted site work
- [47a9708](https://github.com/JiseongParkk/jswebsite/commit/47a970820e17a27d9947f01b3a570a56cc66d862) · Replace the demo README with reproducible portfolio editing and deployment instructions
- [b7be9c0](https://github.com/JiseongParkk/jswebsite/commit/b7be9c0f76db2774a2fc2012cbf4bc397b27a344) · Record actual AI requests, adopted changes and deferred project scope
- [5318f0d](https://github.com/JiseongParkk/jswebsite/commit/5318f0d0de7d84b26fb9bcddb7e60a8ed740617f) · Map the implemented site to coursework evidence and remaining submission steps
- [52b866b](https://github.com/JiseongParkk/jswebsite/commit/52b866be363e3e9d4ca083aa164efb6a867a8497) · Add a reproducible commit-range audit with exact SHAs and changed paths
- [c249f18](https://github.com/JiseongParkk/jswebsite/commit/c249f18355eb1923057e235e403ef2c8cd5d7bda) · Fix the Hugo about-title parse error with explicit title lines
- [d82e50b](https://github.com/JiseongParkk/jswebsite/commit/d82e50b161bc0b664a020ad830bca7a8df04ddda) · Fix newline serialization in the deployment version recorder
- [b8a256e](https://github.com/JiseongParkk/jswebsite/commit/b8a256e478ce5ac553da45d9c1d1abb8f5b8f033) · Use supported Hugo locale and language label configuration
- [b351cb5](https://github.com/JiseongParkk/jswebsite/commit/b351cb5e03e76c048a44195d474d17c36e6833d6) · Scope inherited theme release drafting to the upstream repository
- [cc23f8b](https://github.com/JiseongParkk/jswebsite/commit/cc23f8bbfc9b8dc98aeffb45e97761438ca41df4) · Avoid announcing the animation angle on every frame to screen readers
- [261a571](https://github.com/JiseongParkk/jswebsite/commit/261a571b2a185538bbbbb3630702f94a8a718c0a) · Save real deployment, responsive screenshots and interaction verification evidence
