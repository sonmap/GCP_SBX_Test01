# 파일별 설명

최초 기반은 gcloud, 과제별 자원은 Infrastructure Manager입니다.

| 파일 | 역할 |
|---|---|
| `.gitignore` | 로컬 설정·인증서·State·캐시 제외 |
| `README.md` | 시작 문서 |
| `automation-runner/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `automation-runner/apply_gke_workload.py` | Namespace·KSA·RBAC·Quota·JupyterHub·NEG |
| `automation-runner/group_upsert.py` | Workspace Group 동기화, scripts 원본의 Runner 사본 |
| `automation-runner/reconcile_postdeploy.py` | WI 확인·Backend·Health Check·공통 ALB 경로 연결 |
| `automation-runner/requirements.txt` | Python 라이브러리 의존성 |
| `cloudbuild/mirror-jupyterhub-chart.yaml` | JupyterHub Chart 내부 미러링 |
| `cloudbuild/mirror-jupyterhub-images.yaml` | JupyterHub 이미지 내부 미러링 |
| `cloudbuild/platform-release.yaml` | Runner/Provisioner 빌드·소스 ZIP 게시·Cloud Run 갱신 |
| `cloudrun-provisioner/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `cloudrun-provisioner/main.py` | 승인 JSON 검증·배포 ZIP 생성·동적 Build 생성 |
| `cloudrun-provisioner/requirements.txt` | Python 라이브러리 의존성 |
| `cloudrun-provisioner/sandbox-request.schema.json` | 실제 런타임 요청 규격 |
| `datalake-access-provisioner/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `datalake-access-provisioner/README.md` | 해당 기능 설명서 |
| `datalake-access-provisioner/cloudbuild.yaml` | 데이터레이크 서비스 이미지 빌드 |
| `datalake-access-provisioner/deploy-gcloud.sh` | 동일한 두 계정으로 별도 권한 서비스 배포 |
| `datalake-access-provisioner/examples/request-sbx01.json` | Dataset 조회 권한 요청 예시 |
| `datalake-access-provisioner/main.py` | 데이터레이크 조회 권한 요청 처리 |
| `datalake-access-provisioner/requirements.txt` | Python 라이브러리 의존성 |
| `docs/architecture-and-operations.md` | 구조·권한 통합 영향·State 전환 |
| `docs/cloudbuild-private-gke-vpn-design.md` | Private Pool 사설 IP 경로 전제와 DNS 대안 |
| `docs/file-catalog.md` | 이 파일: 전체 파일 설명 |
| `docs/file-relationships.md` | 전체 파일 관계 Mermaid |
| `docs/jupyterhub-external-alb-oauth-runbook.md` | ALB·OAuth 접속 설명 |
| `docs/runbook-two-stage.md` | 실행 순서 |
| `examples/sbx01-approved-request.json` | 과제 요청 예시, 새 릴리스 값으로 교체 필요 |
| `gcloud/mirror-jupyter.sh` | Chart·기본 이미지를 내부 AR로 복사하는 Build 제출 |
| `gcloud/release.sh` | 현재 Git 커밋 기준 플랫폼 릴리스 Build 제출 |
| `jupyter-singleuser-standard/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `jupyter-singleuser-standard/README.md` | 해당 기능 설명서 |
| `jupyter-singleuser-standard/build-gcloud.sh` | tf-manager로 Notebook 이미지 Build 제출 |
| `jupyter-singleuser-standard/cloudbuild.yaml` | Notebook 표준 이미지 빌드 |
| `requirements-dev.txt` | 로컬 검증 의존성 |
| `schemas/sandbox-request.schema.json` | 런타임과 동기화한 참고 요청 규격 |
| `scripts/group_upsert.py` | 키 없는 IAM 서명으로 Workspace Group/구성원 동기화 |
| `scripts/preflight-instance-son.sh` | Python·gcloud·계정 사전 확인 |
| `scripts/publish-sandbox-source.sh` | 과제별 Terraform 소스 ZIP 게시 |
| `scripts/run-approved-workflow.sh` | 승인 요청 업로드·Generation/해시·Workflow 실행 |
| `scripts/set-jupyter-oauth-secrets.sh` | OAuth 비밀값을 Secret Manager 버전에 등록 |
| `scripts/set-request-release.py` | 새 release.json 값으로 요청 source 갱신 |
| `terraform/02-sandbox/README.md` | 과제별 독립 IM State 안내 |
| `terraform/02-sandbox/deployments/10-project/main.tf` | 프로젝트·API·자동화 IAM |
| `terraform/02-sandbox/deployments/10-project/variables.tf` | 입력 변수 |
| `terraform/02-sandbox/deployments/10-project/versions.tf` | Terraform/Provider 버전 |
| `terraform/02-sandbox/deployments/20-network/main.tf` | 선택적 과제 네트워크 |
| `terraform/02-sandbox/deployments/20-network/variables.tf` | 입력 변수 |
| `terraform/02-sandbox/deployments/20-network/versions.tf` | Terraform/Provider 버전 |
| `terraform/02-sandbox/deployments/30-project-iam/main.tf` | 과제 Group IAM |
| `terraform/02-sandbox/deployments/30-project-iam/variables.tf` | 입력 변수 |
| `terraform/02-sandbox/deployments/30-project-iam/versions.tf` | Terraform/Provider 버전 |
| `terraform/02-sandbox/deployments/40-data/main.tf` | Dataset·Bucket·공통 GSA·WI |
| `terraform/02-sandbox/deployments/40-data/variables.tf` | 입력 변수 |
| `terraform/02-sandbox/deployments/40-data/versions.tf` | Terraform/Provider 버전 |
| `tests/test_provisioning.py` | 실제 생성 ZIP·Build 계정·그룹 순서·선택 네트워크 검증 |
| `gcloud/00-variables.md` | 공통 변수·프로젝트 번호 조회 |
| `gcloud/01-admin.md` | 1단계 API·두 계정·IAM의 개별 gcloud 명령 |
| `gcloud/02-network.md` | 2단계 네트워크의 조회/생성 gcloud 명령 |
| `gcloud/03-foundation.md` | 3단계 공통 기반의 개별 gcloud 명령 |
| `gcloud/configs/bootstrap-build.yaml` | 초기 두 실행 이미지 Build 입력 |
| `gcloud/configs/provisioner-env.yaml` | Cloud Run 환경변수 입력 |
| `gcloud/configs/workflow.template.yaml` | Workflows OIDC 호출 템플릿, URL만 치환 |
| `tests/test_commandbooks.py` | 명령 Bash 구문·변수 치환·Workflow 치환의 오프라인 검증 |
