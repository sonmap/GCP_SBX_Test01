# Sandbox 배포 보조 도구

기존 `scripts`는 **반복 작업을 돕는 짧은 프로그램 모음**이라는 뜻입니다. 이 폴더는 그중 Sandbox 배포에 필요한 보조 도구를 모았습니다.

| 파일 | 하는 일 |
|---|---|
| preflight-instance-son.sh | gcloud와 실행 계정 확인 |
| publish-sandbox-source.sh | 과제별 Terraform 소스를 ZIP으로 묶어 GCS 게시 |
| run-approved-workflow.sh | 승인 JSON 업로드 후 Workflow 실행 |
| set-jupyter-oauth-secrets.sh | Jupyter OAuth 값을 Secret Manager에 등록 |
| set-request-release.py | 신청 JSON에 새 릴리스 소스 정보 반영 |
| group_upsert.py | Google Group과 구성원 동기화 |

일반 실행 순서는 `docs/runbook-two-stage.md`를 따릅니다. `group_upsert.py`는 `sandbox_gke_deployer/`의 동일 파일과 함께 유지하며 Cloud Build 안에서 사용합니다. 최초 인프라 1~3단계 명령은 이 폴더가 아니라 `infra_setup_gcloud/`에 있습니다.
