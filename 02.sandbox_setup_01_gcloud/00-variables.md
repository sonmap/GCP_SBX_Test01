# 공통 변수 — 같은 터미널에서 설정

## 프로젝트 기준과 변수명

이 작업의 주 대상은 **SBX_GKE_PROJECT=pjt-d-host01**입니다. 공통 GKE와 Sandbox의 JupyterHub·Notebook Pod가 이 프로젝트에서 실행됩니다. 자동화 실행·이미지 보관은 SBX_GKE_PROJECT, Shared VPC는 VPC_HOST_PROJECT, 과제의 데이터·Query Job 자원은 SBX_PROJECT에 둡니다.

```bash
export SBX_GKE_PROJECT="pjt-d-host01"          # 주 대상: Sandbox GKE
export SBX_NAME="sbx01"                      # 과제·Namespace 이름
export VPC_HOST_PROJECT="pjt-d-shared-base"   # Shared VPC
export SBX_PROJECT="pjt-net-hub-base"         # 과제 자원·Query Job
```

변수명은 대소문자를 구분합니다. SBX_GKE_PROJECT를 모든 자동화·GKE 자원의 공통 프로젝트 변수로 사용합니다. Cloud Run API와 Build 배포 코드 사이의 실행 환경변수도 SBX_GKE_PROJECT로 통일했습니다. Cloud Build 사용자 치환 변수는 형식 제약에 맞춰 _SBX_GKE_PROJECT를 사용합니다. Cloud Run 설정과 API·배포 도구 이미지는 함께 갱신해야 합니다. JSON의 project.project_id·gke.project_id와 Terraform 입력 필드명은 포털 요청 규격이므로 유지합니다.

저장소 루트에서 아래 값을 확인한 뒤 블록을 복사합니다. 변수 지정과 프로젝트 번호 조회만 수행하며 자원은 생성하지 않습니다. 새로운 터미널에서는 다시 설정합니다. 이 값은 기존 PoC 기준이며 프로젝트·GKE 변경은 런타임 Schema와 YAML 입력 파일도 함께 맞춰야 합니다.

```bash
unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT
export ADMIN_ACCOUNT=admin@sonmap.net
export OPERATOR_MEMBER=user:admin@sonmap.net
export SBX_GKE_PROJECT="pjt-d-host01"
export VPC_HOST_PROJECT="pjt-d-shared-base"
export SBX_PROJECT="pjt-net-hub-base"
export FOLDER_ID=154455658682
export REGION=asia-northeast3
export NETWORK=vpc-d-shared-base
export MAIN_CLUSTER=gke-sbx-main-an3
export TEST_CLUSTER=gke-dev-cicd-01-an3
export MAIN_SUBNET=subnet-dev-sbx-gke-01-an3-main
export MAIN_NODE_CIDR=10.252.0.0/24
export MAIN_POD_RANGE=pods-dev-sbx-gke-01-an3-main
export MAIN_POD_CIDR=10.240.0.0/20
export MAIN_CP_CIDR=10.253.0.0/28
export TEST_SUBNET=subnet-dev-cicd-gke-01-an3-test
export TEST_NODE_CIDR=10.252.1.0/26
export TEST_POD_RANGE=pods-dev-cicd-gke-01-an3-test
export TEST_POD_CIDR=10.240.32.0/22
export TEST_CP_CIDR=10.253.0.16/28
export RUN_SUBNET=subnet-dev-cicd-run-01-an3-egress
export RUN_CIDR=10.251.0.0/26
export TASK_SUBNET=subnet-sbx01-an3
export TASK_CIDR=172.31.110.0/24
export PSA_NAME=prip-dev-cicd-cbp-01-an3-psa
export PSA_CIDR=10.250.0.0/24
export ADMIN_CIDR=172.31.10.0/24
export SSL_CERTIFICATE=cert-jupyter-sbx01-self
export BILLING_ACCOUNT=""
export TF_MANAGER="tf-manager@${SBX_GKE_PROJECT}.iam.gserviceaccount.com"
export SBX_MANAGER="sbx-manager@${SBX_GKE_PROJECT}.iam.gserviceaccount.com"
export PSA_ADDRESS="10.250.0.0"
export PSA_PREFIX_LENGTH="24"
export SBX_GKE_PROJECT_NUMBER="$(gcloud projects describe "${SBX_GKE_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='value(projectNumber)')"
```

## 조회 결과 확인

```bash
export SBX_GKE_PROJECT="pjt-d-host01"
gcloud auth list
gcloud projects describe "${SBX_GKE_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(projectId,projectNumber)'
```

프로젝트 번호가 숫자가 아니거나 조회가 실패하면 1단계로 진행하지 않습니다. 서비스 계정 표시 이름은 sbx_manager/tf_manager, 실제 ID는 sbx-manager/tf-manager입니다. 관리자는 여러 프로젝트와 Folder/Billing 범위에 필요한 기존 권한을 보유해야 합니다. Google 서비스 에이전트·노드 기본 SA와 Kubernetes KSA는 두 사용자 관리 계정과 별개입니다.

실행 순서: [1 관리자](01-admin.md) → [2 네트워크](02-network.md) → [3 공통 기반](03-foundation.md).
