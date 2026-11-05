# 구조와 실행 계정

기존 `sonmap/Gcp_Managed_GKE_GIT_ETC_09`의 커밋 `4f0cae91c6483380b4e2fb2b705a63129db395eb`를 기준으로 새 저장소를 구성했습니다. 원본 저장소와 GCP 자원은 이 코드 변경으로 수정되지 않습니다.

## 1~3단계: 개별 gcloud 명령

| 단계 | 문서 | 실행 주체 |
|---|---|---|
| 공통 변수 | sandbox_setup_01_gcloud/00-variables.md | 기존 관리자 |
| 1 관리자 권한 | sandbox_setup_01_gcloud/01-admin.md | 기존 권한 관리자 |
| 2 공통 네트워크 | sandbox_setup_01_gcloud/02-network.md | tf-manager impersonation |
| 3 공통 기반 | sandbox_setup_01_gcloud/03-foundation.md | tf-manager impersonation |

문서의 각 gcloud 명령을 복사하여 개별 실행합니다. Python 통합 실행기와 config.json은 제거했습니다. 자동 미리보기/--apply 모드는 없으며 조회와 생성 명령을 명확히 분리했습니다. 조회 성공 시 CIDR/Private/Pod Range 등 값을 확인하고 create를 건너뜁니다. 명시적 Not Found일 때만 생성하며 403·인증·연결 오류면 중단합니다. 기존 State/URL Map 경로는 자동 삭제하지 않습니다.

Cloud Build, Cloud Run 환경변수, Workflows의 선언형 입력 파일은 sandbox_setup_01_gcloud/configs/에 있습니다. Workflow URL 자리만 sed로 바꿉니다. 1~3단계 실행에 Python/Terraform 설치는 필요하지 않습니다. 과제별 배포의 기존 Python/Infrastructure Manager는 유지합니다.

## 두 사용자 관리 서비스 계정

| 표시 이름 | 실제 ID | 용도 |
|---|---|---|
| sbx_manager | sbx-manager | Cloud Run, Workflow, Workspace DWD 서명 대상, Notebook GSA |
| tf_manager | tf-manager | gcloud 초기 구축, 모든 Cloud Build, Infrastructure Manager, Kubernetes/Helm, ALB |

서비스 계정 ID에는 밑줄이 허용되지 않아 실제 ID는 하이픈을 사용합니다. Kubernetes KSA는 GCP IAM 서비스 계정이 아니므로 과제별 `ksa-jupyter-<task>`를 유지합니다. Google 서비스 에이전트와 GKE 노드의 자동 생성 Compute 기본 SA도 서비스 동작에 필요하며 위 두 사용자 관리 계정 수에 포함하지 않습니다.

정확히 두 계정으로 통합했으므로 Notebook과 제어 서비스가 sbx-manager를 공유합니다. Notebook은 sbx-manager가 보유한 데이터 권한뿐 아니라 Cloud Build 제출 권한 및 tf-manager actAs 권한도 얻습니다. 여러 과제의 데이터 권한도 이 계정에 합쳐집니다. 따라서 이 버전은 신뢰된 사용자만 사용하는 PoC용이며, Namespace 분리만으로 과제별 GCP 권한을 격리하지 못합니다. 운영 전환 시 Notebook GSA를 분리해야 합니다.

관리자 단계는 Owner/Editor를 새로 부여하지 않습니다. 기능별 사전 정의 역할을 더하는 방식이며, tf-manager에 통합된 권한 범위는 원본의 여러 실행 계정을 합친 범위입니다. 프로젝트 생성 Folder와 Billing 권한은 공통 변수에 지정된 범위에만 추가합니다. `OPERATOR_MEMBER`의 실제 계정을 `ADMIN_ACCOUNT`와 맞춥니다.

## 과제별 배포는 Infrastructure Manager 유지

Cloud Run은 승인 JSON의 GCS Generation/SHA256과 런타임 Schema를 검사합니다. 승인된 릴리스의 소스 ZIP을 읽어 프로젝트/네트워크/IAM/데이터 배포 ZIP을 생성합니다.

Cloud Run이 생성하는 Build가 실제 실행 경로입니다. Cloud Build YAML 기반의 이전 대체 orchestrator와 중복 Kubernetes Terraform Root는 제거했습니다.

1. Cloud Build가 Workspace Group/구성원을 동기화합니다. IAM signBlob으로 sbx-manager의 DWD 자격을 사용하므로 JSON 키를 다운로드하지 않습니다.
2. 그룹 전파 대기 후 tf-manager로 Infrastructure Manager의 네 단계를 순차 실행합니다. network.required=false면 네트워크 단계를 생략합니다.
3. 같은 tf-manager로 Private Pool의 자식 Build에서 `apply_gke_workload.py`를 실행합니다. Namespace/KSA/RBAC/Quota와 JupyterHub를 설치합니다.
4. `reconcile_postdeploy.py`가 Workload Identity를 확인하고 NEG/Backend/Health Check/공통 ALB 경로를 연결합니다.

State는 Infrastructure Manager Deployment별로 관리합니다. 새 Deployment 이름은 `sbxtest01-<task>-<project-hash>-<stage>`이며 기존 `im-*` State를 변경하지 않습니다. 중앙 sbx-manager는 data source로 조회하므로 새 GSA를 생성하거나 import하지 않습니다. `adopt_existing_resources=true`는 Dataset/Bucket 두 개만 편입합니다.

## 네트워크와 외부 연결 경계

GKE는 Private Node/Private IP Endpoint를 사용합니다. 기본 `GKE_ENDPOINT_MODE=internal`이며 API 연결은 `--internal-ip`입니다. Private Pool에서 Private GKE까지의 VPN/BGP 경로는 별도 준비해야 합니다. PSA/VPC peering만으로는 전이 라우팅이 되지 않습니다. 같은 리전/다른 리전 라우팅과 방화벽 및 DNS는 실제 환경에서 점검합니다.

`provisioner-env.yaml`의 GKE_ENDPOINT_MODE를 dns로 바꾼 경우에만 IAM 인증 DNS endpoint를 사용합니다. Cloud Run은 Workflows의 OIDC 호출을 받기 위해 ingress=all이지만 익명 호출을 허용하지 않습니다. 이는 네트워크 수준 private ingress와 다릅니다. 사용자 Jupyter 접속은 원본의 Classic External ALB 구조를 유지합니다. 완전 사설 사용자 접속이 필요하면 별도의 Internal ALB 설계로 변경해야 합니다.

부트스트랩 이미지 빌드와 미러링은 외부 패키지를 받는 완전관리형 Cloud Build에서 수행합니다. 과제 배포 Private Pool에는 외부 IP가 없습니다. Google API/DNS 및 Artifact Registry에 도달하는 경로는 필요합니다.

## 기존 환경과의 전환

기존 Terraform State는 자동 변경/삭제하지 않습니다. 기존 SA도 자동 삭제하거나 IAM을 회수하지 않습니다. 원본 Terraform과 새 gcloud가 같은 자원을 동시에 관리하면 드리프트가 발생할 수 있습니다.

- 원본 배포 Trigger/Workflow를 중지하고 State를 백업한 뒤 전환합니다.
- 새 `sbxtest01` 버킷/이미지/Cloud Run/Workflow/Pool/ALB 이름으로 실행 경로를 분리했습니다. GKE/Shared VPC/기존 Dataset/Bucket은 재사용할 수 있습니다.
- Dataset/Bucket을 새 Infrastructure Manager State에 편입하려면 이전 관리 경로를 먼저 중지하고 소유권을 정리합니다. 기존 State에서 제거할 때 실제 자원을 삭제하지 않도록 합니다.
- Workspace 관리자는 sbx-manager의 OAuth client ID로 두 Directory Group scope의 Domain-wide Delegation을 별도 승인해야 합니다. OAuth Client ID/Secret 값도 Secret Manager에 별도 등록합니다.
- 새 플랫폼 릴리스가 만들어지기 전에는 예제 JSON의 placeholder source로 배포할 수 없습니다. 이전 릴리스 ZIP을 재사용하지 않습니다.
- 비용중지 Terraform 프로필은 새 저장소에서 제거했습니다. 공통 GKE를 삭제하면 기존 과제도 영향을 받으므로 자동 삭제 스크립트는 제공하지 않습니다.

## 소스 폴더명 변경 후 릴리스

소스 폴더명을 변경했으므로 새 플랫폼 릴리스에서 이미지와 소스 ZIP을 함께 생성해야 합니다. ZIP 내부 Root는 `sandbox_setup_02_terraform/deployments/`이며 sandbox_request_api도 같은 경로를 읽습니다. 이전 릴리스 ZIP을 새 API 이미지와 섞지 않습니다. Cloud Run/Workflow/Artifact Registry 이미지 이름은 이번 소스 경로 정리로 변경하지 않습니다.

별도 데이터레이크 조회 권한 자동화 코드는 제거했습니다. 기존 BQ 프로젝트의 데이터 접근 권한은 해당 프로젝트 관리자가 관리합니다. 과제별 40-data의 Dataset/GCS 및 Workload Identity 구성은 그대로 유지합니다. 이번 변경은 저장소 소스만 정리하며 이미 배포된 GCP 서비스나 기존 BQ 자원을 삭제하지 않습니다.
