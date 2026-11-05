# 파일별 설명

최초 기반은 gcloud, 과제별 자원은 Infrastructure Manager입니다.

| 파일 | 역할 |
|---|---|
| `.gitignore` | 로컬 설정·인증서·State·캐시 제외 |
| `README.md` | 시작 문서 |
| `09.sandbox_gke_deployer/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `09.sandbox_gke_deployer/apply_gke_workload.py` | Namespace·KSA·RBAC·Quota·JupyterHub·NEG |
| `09.sandbox_gke_deployer/group_upsert.py` | Workspace Group 동기화, sandbox_deploy_tools 원본의 배포 실행용 사본 |
| `09.sandbox_gke_deployer/reconcile_postdeploy.py` | WI 확인·Backend·Health Check·공통 ALB 경로 연결 |
| `09.sandbox_gke_deployer/requirements.txt` | Python 라이브러리 의존성 |
| `03.cloudbuild/mirror-jupyterhub-chart.yaml` | JupyterHub Chart 내부 미러링 |
| `03.cloudbuild/mirror-jupyterhub-images.yaml` | JupyterHub 이미지 내부 미러링 |
| `03.cloudbuild/platform-release.yaml` | Runner/Provisioner 빌드·소스 ZIP 게시·Cloud Run 갱신 |
| `07.sandbox_request_api/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `07.sandbox_request_api/main.py` | 승인 JSON 검증·배포 ZIP 생성·동적 Build 생성 |
| `07.sandbox_request_api/requirements.txt` | Python 라이브러리 의존성 |
| `07.sandbox_request_api/sandbox-request.schema.json` | 실제 런타임 요청 규격 |
| `01.docs/architecture-and-operations.md` | 구조·권한 통합 영향·State 전환 |
| `01.docs/cloudbuild-private-gke-vpn-design.md` | Private Pool 사설 IP 경로 전제와 DNS 대안 |
| `01.docs/file-catalog.md` | 이 파일: 전체 파일 설명 |
| `01.docs/file-relationships.md` | 전체 파일 관계 Mermaid |
| `01.docs/jupyterhub-external-alb-oauth-runbook.md` | ALB·OAuth 접속 설명 |
| `01.docs/runbook-two-stage.md` | 실행 순서 |
| `05.sandbox_json/sbx01-approved-request.json` | 과제 요청 예시, 새 릴리스 값으로 교체 필요 |
| `02.sandbox_setup_01_gcloud/mirror-jupyter.sh` | Chart·기본 이미지를 내부 AR로 복사하는 Build 제출 |
| `02.sandbox_setup_01_gcloud/release.sh` | 현재 Git 커밋 기준 플랫폼 릴리스 Build 제출 |
| `04.Jupiter-setup-image/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `04.Jupiter-setup-image/README.md` | 해당 기능 설명서 |
| `04.Jupiter-setup-image/build-gcloud.sh` | tf-manager로 Notebook 이미지 Build 제출 |
| `04.Jupiter-setup-image/cloudbuild.yaml` | Notebook 표준 이미지 빌드 |
| `requirements-dev.txt` | 로컬 검증 의존성 |
| `06.sandbox_json_rules/sandbox-request.schema.json` | 런타임과 동기화한 참고 요청 규격 |
| `10.sandbox_deploy_tools/group_upsert.py` | 키 없는 IAM 서명으로 Workspace Group/구성원 동기화 |
| `10.sandbox_deploy_tools/preflight-instance-son.sh` | gcloud·계정 사전 확인 |
| `10.sandbox_deploy_tools/publish-sandbox-source.sh` | 과제별 Terraform 소스 ZIP 게시 |
| `10.sandbox_deploy_tools/run-approved-workflow.sh` | 승인 요청 업로드·Generation/해시·Workflow 실행 |
| `10.sandbox_deploy_tools/set-jupyter-oauth-secrets.sh` | OAuth 비밀값을 Secret Manager 버전에 등록 |
| `10.sandbox_deploy_tools/set-request-release.py` | 새 release.json 값으로 요청 source 갱신 |
| `08.sandbox_setup_02_terraform/README.md` | 과제별 독립 IM State 안내 |
| `08.sandbox_setup_02_terraform/deployments/10-project/main.tf` | 프로젝트·API·자동화 IAM |
| `08.sandbox_setup_02_terraform/deployments/10-project/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/10-project/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/20-network/main.tf` | 선택적 과제 네트워크 |
| `08.sandbox_setup_02_terraform/deployments/20-network/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/20-network/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/main.tf` | 과제 Group IAM |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/40-data/main.tf` | Dataset·Bucket·공통 GSA·WI |
| `08.sandbox_setup_02_terraform/deployments/40-data/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/40-data/versions.tf` | Terraform/Provider 버전 |
| `11.tests/test_provisioning.py` | 실제 생성 ZIP·Build 계정·그룹 순서·선택 네트워크 검증 |
| `02.sandbox_setup_01_gcloud/00-variables.md` | 공통 변수·프로젝트 번호 조회 |
| `02.sandbox_setup_01_gcloud/01-admin.md` | 1단계 API·두 계정·IAM의 개별 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/02-network.md` | 2단계 네트워크의 조회/생성 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/03-foundation.md` | 3단계 공통 기반의 개별 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/configs/bootstrap-build.yaml` | 초기 두 실행 이미지 Build 입력 |
| `02.sandbox_setup_01_gcloud/configs/provisioner-env.yaml` | Cloud Run 환경변수 입력 |
| `02.sandbox_setup_01_gcloud/configs/workflow.template.yaml` | Workflows OIDC 호출 템플릿, URL만 치환 |
| `11.tests/test_commandbooks.py` | 명령 Bash 구문·변수 치환·Workflow 치환의 오프라인 검증 |
| `09.sandbox_gke_deployer/README.md` | GKE·Jupyter 배포 도구 역할 설명 |
| `07.sandbox_request_api/README.md` | 신청 접수 API 역할 설명 |
| `06.sandbox_json_rules/README.md` | JSON 입력 규칙과 런타임 규격 사본의 관계 |
| `10.sandbox_deploy_tools/README.md` | 배포 보조 도구와 scripts 용어 설명 |
| `11.tests/test_build_paths.py` | 빌드 Context·Docker COPY 경로·삭제 컴포넌트 참조 검사 |
