# 파일별 설명

[폴더·파일과 실행 관계](file-relationships.md)에서 각 단계가 어떤 파일을 사용하는지 Mermaid로 확인할 수 있습니다. 이 표는 파일 경로와 역할을 찾는 데 사용합니다. 실제 명령은 [시작 안내](README.md)에서 [2단계 실행 절차](runbook-two-stage.md)로 이동해 확인하세요.

최초 공통 기반은 운영자가 개별 `gcloud` 명령으로 준비합니다. 과제 요청을 제출하면 Infrastructure Manager와 GKE 배포 도구가 순서대로 실행됩니다.

| 저장소 루트 기준 파일 경로 | 역할 |
|---|---|
| `.gitignore` | 로컬 설정·인증서·State·캐시 제외 |
| `01.docs/README.md` | 실제 수행 단계·실행 계정·완료 기준의 시작 안내 |
| `01.docs/admin-requests.md` | 관리자별 네트워크·데이터·인증 준비 요청 |
| `01.docs/architecture-and-operations.md` | 구조·권한 통합 영향·State 전환 |
| `01.docs/check-private-gke.yaml` | Private Pool에서 DNS 엔드포인트를 통해 Namespace 조회 |
| `01.docs/cloud-identity-group-terraform.md` | 그룹 관리자 역할·Customer ID·기존 그룹 import 안내 |
| `01.docs/cloudbuild-private-gke-vpn-design.md` | Private Pool의 GKE DNS 접속 점검과 사설 IP 점검 범위 |
| `01.docs/file-catalog.md` | 이 파일: 전체 파일 설명 |
| `01.docs/file-relationships.md` | 폴더와 파일별 Mermaid 실행·참조 관계 |
| `01.docs/git-sync-current-environment.md` | 코드 동기화와 기존 환경에서 재시험 |
| `01.docs/internal-alb-design.md` | Shared VPC 내부 ALB 구조와 리소스 |
| `01.docs/jupyterhub-internal-alb-oauth-runbook.md` | ALB·OAuth 접속 설명 |
| `01.docs/minimal-ip-design.md` | 공통 기반과 과제 네트워크의 IP 최소화 설계 |
| `01.docs/network-resource-design.md` | 프로젝트·서브넷·Pool·자원 매핑 |
| `01.docs/operator-command-guide.md` | 운영자 계정과 실제 개별 명령 |
| `01.docs/runbook-two-stage.md` | 실행 순서 |
| `01.docs/sbx03-google-oauth-runbook.md` | Google OAuth 클라이언트·콜백 등록 및 로그인 점검 |
| `01.docs/sbx03-https-certificate-runbook.md` | 내부 HTTPS ALB, 인증서, Windows 접속 확인 |
| `01.docs/sbx03-new-project-runbook.md` | 신규 과제 생성과 GKE 복구 후 재시험 |
| `01.docs/tf-manager-project.md` | 플랫폼 프로젝트와 배포 서비스 계정의 범위 |
| `01.docs/work-order.md` | 운영 단계와 관련 명령 문서 연결 |
| `02.sandbox_setup_01_gcloud/00-variables.md` | 공통 변수·프로젝트 번호 조회 |
| `02.sandbox_setup_01_gcloud/01-admin.md` | 1단계 API·두 계정·IAM의 개별 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/02-network.md` | 2단계 네트워크의 조회/생성 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/02-subnet-iam.md` | Subnet별 계정 사용 권한, VPC Admin 수행 |
| `02.sandbox_setup_01_gcloud/03-foundation.md` | 3단계 공통 기반의 개별 gcloud 명령 |
| `02.sandbox_setup_01_gcloud/04-manual-gcloud.md` | OAuth Secret 등록과 릴리스·미러링·Notebook 이미지 빌드 명령 |
| `02.sandbox_setup_01_gcloud/05-deploy.md` | 승인 객체 버전·해시 확인, Workflow 제출과 결과 확인 |
| `02.sandbox_setup_01_gcloud/06-iam-migration.md` | 기존 Host 광역 바인딩의 검토·정리 명령, 신규 설치 필수 아님 |
| `02.sandbox_setup_01_gcloud/configs/bootstrap-build.yaml` | 초기 두 실행 이미지 Build 입력 |
| `02.sandbox_setup_01_gcloud/configs/provisioner-env.yaml` | Cloud Run 환경변수 입력 |
| `02.sandbox_setup_01_gcloud/configs/workflow.template.yaml` | Workflows OIDC 호출 템플릿, URL만 치환 |
| `02.sandbox_setup_01_gcloud/mirror-jupyter.sh` | Chart·기본 이미지를 내부 AR로 복사하는 Build 제출 |
| `02.sandbox_setup_01_gcloud/release.sh` | 현재 Git 커밋 기준 플랫폼 릴리스 Build 제출 |
| `03.cloudbuild/mirror-jupyterhub-chart.yaml` | JupyterHub Chart 내부 미러링 |
| `03.cloudbuild/mirror-jupyterhub-images.yaml` | JupyterHub 이미지 내부 미러링 |
| `03.cloudbuild/platform-release.yaml` | Runner/Provisioner 빌드·소스 ZIP 게시·Cloud Run 갱신 |
| `04.Jupiter-setup-image/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `04.Jupiter-setup-image/README.md` | 해당 기능 설명서 |
| `04.Jupiter-setup-image/build-gcloud.sh` | tf-manager로 Notebook 이미지 Build 제출 |
| `04.Jupiter-setup-image/cloudbuild.yaml` | Notebook 표준 이미지 빌드 |
| `04.Jupiter-setup-image/start-sandbox-notebook.sh` | 사용자별 마운트 경로를 HOME으로 설정하고 Notebook 서버 시작 |
| `05.sandbox_json/sbx01-approved-request.json` | 과제 요청 예시, 새 릴리스 값으로 교체 필요 |
| `05.sandbox_json/sbx03-request.template.json` | 신규 프로젝트 요청 초안. 실제 승인 및 릴리스 값 입력 필요 |
| `06.sandbox_json_rules/README.md` | JSON 입력 규칙과 런타임 규격 사본의 관계 |
| `06.sandbox_json_rules/sandbox-request.schema.json` | 런타임과 동기화한 참고 요청 규격 |
| `07.sandbox_request_api/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `07.sandbox_request_api/README.md` | 신청 접수 API 역할 설명 |
| `07.sandbox_request_api/main.py` | 승인 JSON 검증·배포 ZIP 생성·동적 Build 생성 |
| `07.sandbox_request_api/requirements.txt` | Python 라이브러리 의존성 |
| `07.sandbox_request_api/sandbox-request.schema.json` | 실제 런타임 요청 규격 |
| `08.sandbox_setup_02_terraform/README.md` | 과제별 독립 IM State 안내 |
| `08.sandbox_setup_02_terraform/deployments/05-group/main.tf` | 과제 Google Group과 구성원 관리 |
| `08.sandbox_setup_02_terraform/deployments/05-group/variables.tf` | 그룹·구성원 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/05-group/versions.tf` | 그룹 단계의 Terraform·Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/10-project/main.tf` | 프로젝트·API·자동화 IAM |
| `08.sandbox_setup_02_terraform/deployments/10-project/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/10-project/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/20-network/main.tf` | 선택적 과제 네트워크 |
| `08.sandbox_setup_02_terraform/deployments/20-network/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/20-network/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/main.tf` | 과제 Group IAM |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/30-project-iam/versions.tf` | Terraform/Provider 버전 |
| `08.sandbox_setup_02_terraform/deployments/40-data/main.tf` | Dataset·Bucket·Notebook GSA·Workload Identity·승인 데이터레이크 권한 |
| `08.sandbox_setup_02_terraform/deployments/40-data/variables.tf` | 입력 변수 |
| `08.sandbox_setup_02_terraform/deployments/40-data/versions.tf` | Terraform/Provider 버전 |
| `09.sandbox_gke_deployer/Dockerfile` | 해당 프로그램 실행 이미지 정의 |
| `09.sandbox_gke_deployer/README.md` | GKE·Jupyter 배포 도구 역할 설명 |
| `09.sandbox_gke_deployer/apply_gke_workload.py` | Namespace·KSA·RBAC·Quota·JupyterHub·NEG |
| `09.sandbox_gke_deployer/reconcile_postdeploy.py` | WI 확인·Backend·Health Check·공통 ALB 경로 연결 |
| `09.sandbox_gke_deployer/requirements.txt` | Python 라이브러리 의존성 |
| `10.sandbox_deploy_tools/README.md` | 배포 보조 도구와 scripts 용어 설명 |
| `10.sandbox_deploy_tools/preflight-instance-son.sh` | gcloud·계정 사전 확인 |
| `10.sandbox_deploy_tools/publish-sandbox-source.sh` | 과제별 Terraform 소스 ZIP 게시 |
| `10.sandbox_deploy_tools/run-approved-workflow.sh` | 승인 요청 업로드·Generation/해시·Workflow 실행 |
| `10.sandbox_deploy_tools/set-jupyter-oauth-secrets.sh` | OAuth 비밀값을 Secret Manager 버전에 등록 |
| `10.sandbox_deploy_tools/set-request-release.py` | 새 release.json 값으로 요청 source 갱신 |
| `11.tests/test_build_paths.py` | 빌드 Context·Docker COPY 경로·삭제 컴포넌트 참조 검사 |
| `11.tests/test_commandbooks.py` | 명령 Bash 구문·변수 치환·Workflow 치환의 오프라인 검증 |
| `11.tests/test_internal_alb.py` | Workload Identity 연결과 내부 ALB 백엔드·호스트 경로 검증 |
| `11.tests/test_provisioning.py` | 실제 생성 ZIP·Build 계정·그룹 순서·선택 네트워크 검증 |
| `11.tests/test_release_bootstrap.py` | 릴리스 설정 검증과 소스 게시 빌드 구성 검사 |
| `README.md` | 시작 문서 |
| `requirements-dev.txt` | 로컬 검증 의존성 |
