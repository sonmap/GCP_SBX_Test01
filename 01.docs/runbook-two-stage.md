# 실제 수행 절차 — 관리 VM에서 Notebook 접속까지

현재 저장소의 파일과 프로그램 동작을 기준으로 작성했습니다. 아래 명령은 **저장소 루트 `GCP_SBX_Test01`에서** 실행합니다. 각 코드 블록의 주석과 완료 기준을 확인하며 진행합니다. 문서의 명령은 작성·검사한 것이며 실제 GCP에 실행한 기록은 아닙니다.

## 0. 소스 받기·기본 변수 설정

수행자: 기존 관리 계정과 tf-manager 위임 권한을 사용할 운영자. 실행 환경은 Bash·최신 gcloud·git·jq·curl·Python 3.10 이상이 있는 관리 VM입니다. 1~3단계는 개별 gcloud 명령이며 Terraform/Python 통합 실행기가 없습니다. 이후 신청 JSON 보조 도구는 Python 표준 라이브러리를 사용합니다.

```bash
# 처음 한 번만 소스를 받습니다. 이미 받았다면 기존 폴더에서 git pull --ff-only 합니다.
git clone https://github.com/sonmap/GCP_SBX_Test01.git
cd GCP_SBX_Test01

# 아래 계정·프로젝트는 현재 PoC 코드의 실제 대상입니다.
export ADMIN_ACCOUNT="admin@sonmap.net"
export CICD_PROJECT="prj-b-cicd-local-236d"
export HOST_PROJECT="pjt-d-shared-base"
export GKE_PROJECT="pjt-d-host01"
export TASK_PROJECT="pjt-net-hub-base"
export REGION="asia-northeast3"
export MAIN_CLUSTER="gke-sbx-main-an3"
export TASK_NAME="sbx01"
export TF_MANAGER="tf-manager@${CICD_PROJECT}.iam.gserviceaccount.com"
export SBX_MANAGER="sbx-manager@${CICD_PROJECT}.iam.gserviceaccount.com"
export TF_MANAGER_RESOURCE="projects/${CICD_PROJECT}/serviceAccounts/${TF_MANAGER}"
export REQUEST_BUCKET="${CICD_PROJECT}-sbxtest01-requests"
export BUNDLE_BUCKET="${CICD_PROJECT}-sbxtest01-bundles"
export BUILD_STAGING_BUCKET="${CICD_PROJECT}-sbxtest01-build-source"
export RUN_SERVICE="run-sbxtest01-provisioner"
export WORKFLOW_NAME="workflow-sbxtest01-provision"
export JUPYTER_DOMAIN="jupyter-sbx01.sonmap.net"
export REQUEST_ID="REQ-20261105-001"

# 보조 스크립트의 gcloud도 같은 운영 계정으로 실행하도록 합니다.
export CLOUDSDK_CORE_ACCOUNT="${ADMIN_ACCOUNT}"
unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT

# 도구/계정과 대상 프로젝트를 확인합니다.
git --version
gcloud version
jq --version
curl --version
python3 --version
gcloud auth list
gcloud projects describe "${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(projectId,projectNumber)'
gcloud projects describe "${GKE_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(projectId,projectNumber)'
mkdir -p .local
```

완료 기준: 도구가 실행되고 관리자 계정이 인증되어 있으며 두 프로젝트가 조회됩니다. 새 터미널에서는 위 변수를 다시 설정합니다. 실제 계정·CIDR을 바꿀 경우 02 폴더의 각 변수 선언, YAML 및 JSON Schema에 고정된 대상도 함께 맞춰야 합니다.

## 1. 관리자 API·서비스 계정·IAM 준비

수행자: 대상 Project/Folder IAM과 필요한 Billing 범위를 관리할 수 있는 기존 관리자.

[01-admin.md](../02.sandbox_setup_01_gcloud/01-admin.md)의 **변수 선언부터** 실행합니다. API 활성화 → 서비스 에이전트 → sbx-manager/tf-manager → 각 프로젝트·Folder IAM 순서입니다. SA 조회가 성공하면 해당 create 명령은 건너뜁니다. Billing 권한은 새 프로젝트를 생성할 때만 선택합니다.

```bash
# 관리자 문서를 적용한 뒤 두 계정을 조회합니다.
gcloud iam service-accounts describe "${SBX_MANAGER}" --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(email,disabled)'
gcloud iam service-accounts describe "${TF_MANAGER}" --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(email,disabled)'

# 토큰을 출력하지 않고 tf-manager 위임으로 API 조회가 되는지 확인합니다.
gcloud services list --enabled --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --limit=3
```

완료 기준: 두 SA가 비활성 상태가 아니고 tf-manager를 사용한 조회가 성공합니다. 403·인증 실패를 미존재로 취급하지 않습니다.

## 2. Shared VPC·서브넷·PSA·방화벽 준비

실행 계정: tf-manager impersonation.

[02-network.md](../02.sandbox_setup_01_gcloud/02-network.md)의 변수를 확인한 뒤, 각 조회 결과를 보고 필요한 생성/갱신 명령만 실행합니다. Main GKE·Cloud Run·과제 서브넷이 기본 대상입니다. Test GKE용 서브넷은 선택 항목입니다.

```bash
# 생성 후 실제 연결과 대역을 조회합니다.
gcloud compute shared-vpc get-host-project "${GKE_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
gcloud compute shared-vpc get-host-project "${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
gcloud compute networks subnets list --project="${HOST_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format=json
gcloud services vpc-peerings list --project="${HOST_PROJECT}" --network=vpc-d-shared-base --service=servicenetworking.googleapis.com --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format=json
gcloud compute firewall-rules describe fw-sbxtest01-alb-hc --project="${HOST_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format=json
```

완료 기준: GKE/CI-CD 프로젝트의 Host가 pjt-d-shared-base이고, Primary·Secondary·Control Plane·PSA 대역에 중복이 없으며 설정한 Pod Range와 방화벽이 확인됩니다. **PSA 연결 성공만으로 Private Pool에서 GKE API 접속이 보장되지는 않습니다.**

## 3. 공통 실행 기반 구축

실행 계정: tf-manager. [03-foundation.md](../02.sandbox_setup_01_gcloud/03-foundation.md)를 열어 다음 순서로 명령을 실행합니다.

| 문서 안 순서 | 실제 작업 |
|---|---|
| 1~9 | 승인 요청·배포 ZIP·Build Source 버킷과 접근 권한 |
| 10~12 | 내부 Artifact Registry와 GKE 노드 읽기 권한 |
| 13~16 | Jupyter OAuth Secret 메타데이터와 읽기 권한 |
| 17~19 | Private Pool·Main GKE·선택적 Test GKE |
| 20 | bootstrap 이미지 두 개 빌드: 요청 API·GKE 배포 도구 |
| 21~27 | Cloud Run 배포·실제 URL 치환·Workflow 배포·호출 권한 |
| 28~35 | 공통 Classic External ALB와 기존 SSL 인증서 연결 |
| 36 | 선택: GitHub 자동 릴리스 Trigger |

기존 GKE/버킷/ALB 자원은 조회 결과를 비교하고 create를 건너뜁니다. Secret은 여기서 이름만 준비하고 실제 값은 4단계에서 등록합니다. SSL 인증서 `cert-jupyter-sbx01-self`가 없으면 HTTPS Proxy/443 명령 전에 인증서 담당자가 별도 등록해야 합니다. DNS/hosts 연결은 11단계에서 확인합니다.

```bash
# 공통 기반 적용 후 확인합니다.
gcloud builds worker-pools describe pool-sbxtest01 --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
gcloud container clusters describe "${MAIN_CLUSTER}" --project="${GKE_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='yaml(status,autopilot,network,subnetwork,privateClusterConfig,ipAllocationPolicy)'
gcloud workflows describe "${WORKFLOW_NAME}" --project="${CICD_PROJECT}" --location="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='yaml(state,serviceAccount,sourceContents)'
export RUN_URL="$(gcloud run services describe "${RUN_SERVICE}" --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='value(status.url)')"

# Run invoker인 sbx-manager로 인증합니다. 토큰을 파일에 저장하지 않습니다.
curl --fail --silent --show-error -H "Authorization: Bearer $(gcloud auth print-identity-token --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${SBX_MANAGER}" --audiences="${RUN_URL}")" "${RUN_URL}/healthz"
```

완료 기준: Main GKE RUNNING, Worker Pool 조회 성공, Workflow의 호출 URL이 실제 Run URL이며 healthz가 `{"status":"ok"}`를 반환합니다. 여기까지는 Jupyter 사용자 환경이 아직 설치되지 않았습니다. Foundation을 다시 수행하면 API 이미지가 bootstrap으로 갱신되므로 이후 6단계 릴리스를 다시 적용합니다.

## 4. Jupyter 로그인과 Workspace 위임 준비

### 4-1. Jupyter OAuth

OAuth 담당자가 웹 애플리케이션용 Client ID/Secret과 Callback URL `https://jupyter-sbx01.sonmap.net/hub/oauth_callback`을 준비합니다. 실행 계정 tf-manager로 다음 보조 명령을 실행하고 값을 입력합니다.

```bash
CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT="${TF_MANAGER}" bash 10.sandbox_deploy_tools/set-jupyter-oauth-secrets.sh

# 비밀값을 출력하지 않고 등록 상태만 확인합니다.
gcloud secrets versions describe latest --secret=jupyter-oauth-client-id --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='value(state)'
gcloud secrets versions describe latest --secret=jupyter-oauth-client-secret --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='value(state)'
```

완료 기준: 두 latest 버전이 ENABLED이고 OAuth Callback URL이 실제 접속 도메인과 일치합니다.

### 4-2. Workspace Domain-wide Delegation

```bash
# 이 값은 Workspace 관리자가 등록할 OAuth Client ID입니다. SA 이메일과 다릅니다.
gcloud iam service-accounts describe "${SBX_MANAGER}" --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='value(oauth2ClientId)'
```

Workspace 관리자가 위 Client ID를 Domain-wide Delegation에 승인하고 다음 두 Scope를 허용합니다.

- `https://www.googleapis.com/auth/admin.directory.group`
- `https://www.googleapis.com/auth/admin.directory.group.member`

위임 대상 관리자는 `02.sandbox_setup_01_gcloud/configs/provisioner-env.yaml`의 WORKSPACE_ADMIN_SUBJECT와 일치해야 합니다. 현재 값은 admin@sonmap.net입니다. Workspace 승인 작업은 GCP IAM 명령으로 대체되지 않습니다. SA JSON 키는 생성하지 않습니다.

완료 기준: Workspace 관리자가 해당 Client ID·두 Scope·위임 대상의 Group 관리 권한을 확인합니다. 실제 동기화는 요청 배포 Build 첫 단계에서 수행됩니다.

## 5. Private Pool에서 GKE 사설 API 연결 확인

실행 계정: tf-manager Build. 3단계가 만든 bootstrap 이미지를 사용해 Namespace 목록만 조회합니다. 아래 YAML은 GKE 자원을 생성하지 않습니다.

```bash
gcloud builds submit --no-source --config=01.docs/check-private-gke.yaml --project="${CICD_PROJECT}" --region="${REGION}" --service-account="${TF_MANAGER_RESOURCE}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
```

완료 기준: Build가 SUCCESS이고 로그에 Namespace 목록이 나옵니다. 실패하면 [사설 접속 점검 문서](cloudbuild-private-gke-vpn-design.md)에서 인증 실패와 라우팅 실패를 구분합니다. **이 확인이 통과하기 전에는 과제 신청을 제출하지 않습니다.** 현재 기본은 internal IP이며, 이 저장소는 HA VPN/BGP 경로를 자동 구축하지 않습니다.

## 6. 플랫폼의 고정 릴리스 게시

실행 계정: tf-manager Build. 저장소의 수정되지 않은 Git 커밋으로 API/배포 도구 이미지와 Terraform 소스 ZIP을 함께 게시합니다.

```bash
# 비어 있어야 합니다. 수정 파일이 있으면 commit 또는 별도 정리 후 진행합니다.
git status --porcelain
export RELEASE_ID="git-$(git rev-parse HEAD | cut -c1-12)"

# 첫 명령은 제출 명령 출력, 두 번째는 실제 Build 제출입니다.
bash 02.sandbox_setup_01_gcloud/release.sh
bash 02.sandbox_setup_01_gcloud/release.sh --apply

# Build 성공 후 생성된 release.json을 받아 봅니다.
gcloud storage cp "gs://${BUNDLE_BUCKET}/platform-releases/${RELEASE_ID}/release.json" .local/release.json --account="${ADMIN_ACCOUNT}"
jq '{release_id,git_commit,archive_uri,generation,sha256,runner_image,provisioner_image}' .local/release.json
```

완료 기준: 릴리스 Build SUCCESS, 두 이미지와 release.json/ZIP이 존재하고 release.json의 release_id가 위 RELEASE_ID와 일치합니다. ZIP 내부 Root는 `08.sandbox_setup_02_terraform/deployments/`입니다. 이전 폴더명의 ZIP을 새 API 이미지와 섞지 않습니다.

## 7. Chart와 기본 이미지 미러링

실행 계정: tf-manager Build. `mirror-jupyter.sh`는 기본 bootstrap Runner로 외부 Chart/이미지를 받아 내부 AR에 저장하는 두 Build를 제출합니다.

```bash
# 출력 확인 후 실제 미러링합니다.
bash 02.sandbox_setup_01_gcloud/mirror-jupyter.sh
bash 02.sandbox_setup_01_gcloud/mirror-jupyter.sh --apply

gcloud artifacts docker images list "${REGION}-docker.pkg.dev/${CICD_PROJECT}/ar-sbxtest01-platform" --include-tags --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
```

완료 기준: 두 Build SUCCESS. JupyterHub Chart 4.2.0, Hub 4.2.0, CHP 4.6.3, SingleUser sample 4.2.0이 내부 AR에 게시됩니다. 이 미러링은 외부 다운로드가 가능한 완전관리형 Build를 사용합니다. Private Pool에 외부 IP를 추가하는 작업이 아닙니다.

## 8. 사용자 Notebook 표준 이미지 빌드

```bash
CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT="${TF_MANAGER}" bash 04.Jupiter-setup-image/build-gcloud.sh

gcloud artifacts docker images describe "${REGION}-docker.pkg.dev/${CICD_PROJECT}/ar-sbxtest01-platform/jupyterhub-k8s-singleuser-standard:4.2.0-r1-test" --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
```

완료 기준: Build SUCCESS이고 이미지 describe가 성공합니다. 이 이미지는 이후 새 사용자 Notebook Pod에 설정됩니다. 기존 사용자 PVC는 삭제하지 않습니다.

## 9. 실제 과제 신청값과 릴리스 반영

수행자: 과제 승인 담당자·운영자. 먼저 현재 예제의 의미를 확인합니다.

| 예제 항목 | 현재 값·실제 의미 |
|---|---|
| project.create_project | false: 기존 pjt-net-hub-base 사용 |
| network.required/create_subnet | true/false: 기존 subnet-sbx01-an3 사용 |
| data.adopt_existing_resources | true: 기존 sbx01_main Dataset·과제 GCS Bucket 편입 |
| task/namespace | sbx01 |
| identity.members | 승인된 user01/user02 예시; 실제 계정으로 변경 |
| source | placeholder 상태이므로 이번 릴리스 값으로 반드시 교체 |

현재 40-data는 과제 Dataset/GCS/Workload Identity를 관리하는 필수 배포 단계입니다. 기존 별도 BQ 프로젝트만 조회하고 과제 Dataset/GCS를 구성하지 않는 모드는 아직 없습니다. 그런 설계가 목적이면 신청 전에 40-data 코드를 별도 변경해야 합니다.

```bash
# 이번 릴리스 정보를 반영한 작업용 신청서를 만듭니다.
python3 10.sandbox_deploy_tools/set-request-release.py 05.sandbox_json/sbx01-approved-request.json .local/release.json .local/request.json

# Request ID·사용자·기존 자원·source를 검토합니다.
jq '{request_id,approval,task,identity,project,network,data,gke,source}' .local/request.json
```

실제 계정·과제·Request ID·승인 내역을 작업용 JSON에 수정하고 최종 승인합니다. 신규 Dataset/Bucket이면 adopt_existing_resources=false, 기존 자원을 편입한다면 실제 존재와 이전 Terraform/IM 관리 중지·State 소유권 정리를 확인합니다. 같은 데이터를 두 State가 동시에 관리하지 않도록 합니다.

완료 기준: 최종 JSON이 실제 승인값이고 source가 이번 release.json과 일치합니다. Request ID는 실행할 때마다 새 값으로 관리합니다. 아래 단계는 해당 JSON의 Request ID를 직접 읽으므로 예제 ID를 명령에 고정하지 않습니다.

## 10. 승인 JSON 업로드·Workflow 실행

수행자: 3단계에서 requests Bucket 쓰기와 Workflow 호출 권한을 받은 운영자. 이 스크립트는 IAM 변경 권한이 큰 tf-manager 대신 현재 운영 계정으로 업로드·호출합니다.

```bash
unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT
export REQUEST_ID="$(jq -r '.request_id' .local/request.json)"
bash 10.sandbox_deploy_tools/run-approved-workflow.sh "${REQUEST_ID}" .local/request.json
```

완료 기준: Workflow 응답에 ACCEPTED와 operation/bundle_prefix가 표시됩니다. **이는 요청 접수 성공입니다. 최종 배포 결과는 다음 단계에서 확인합니다.**

이후 자동 호출 순서는 다음과 같습니다. 07/08/09 폴더에서 main.py나 terraform apply를 직접 실행할 필요가 없습니다.

1. Cloud Run: JSON·GCS Generation·SHA256 검증, 네 단계 ZIP 생성.
2. 부모 Cloud Build: Google Group 동기화 → 전파 대기 → Project → 선택적 Network → Project IAM → Data의 IM Deployment 적용.
3. 자식 Private Pool Build: Namespace/KSA/RBAC/Quota/JupyterHub 설치 → NEG 대기 → Backend/Health Check/공통 ALB 연결.

## 11. 최종 배포와 사용자 동작 확인

### 11-1. Workflow·Cloud Build·Infrastructure Manager

```bash
# 실행 시각과 Workflow 응답을 대조해 이번 요청의 실행을 찾습니다.
gcloud workflows executions list "${WORKFLOW_NAME}" --project="${CICD_PROJECT}" --location="${REGION}" --account="${ADMIN_ACCOUNT}" --limit=5

gcloud builds list --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --limit=10 --sort-by='~createTime' --format='table(id,status,createTime)'
gcloud infra-manager deployments list --project="${CICD_PROJECT}" --location="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --filter='name:sbxtest01-' --format='table(name,state,latestRevision)'

# 위 목록에서 확인한 실제 Build ID를 입력한 뒤 아래 두 줄을 실행합니다.
# export BUILD_ID="실제_BUILD_ID"
# gcloud builds describe "${BUILD_ID}" --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='yaml(id,status,steps)'
# gcloud builds log "${BUILD_ID}" --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
```

완료 기준: 이번 요청의 부모/자식 Build SUCCESS, 해당 과제 IM Deployment가 ACTIVE입니다. 최신 Revision은 APPLIED 상태를 확인합니다. 여러 과제의 Build가 섞여 있으면 생성 시각·로그의 request_id/배포 이름을 대조합니다. 예제는 Network를 포함한 네 Deployment이며 network.required=false면 세 Deployment입니다.

### 11-2. GKE와 ALB

관리 VM에서도 GKE Private IP에 도달할 수 있어야 합니다. 아래 환경변수는 이 터미널의 kubectl 인증에도 tf-manager를 사용하게 합니다.

```bash
export CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT="${TF_MANAGER}"
gcloud container clusters get-credentials "${MAIN_CLUSTER}" --project="${GKE_PROJECT}" --location="${REGION}" --internal-ip
kubectl -n "${TASK_NAME}" get pods,svc,pvc
kubectl -n "${TASK_NAME}" get serviceaccount "ksa-jupyter-${TASK_NAME}" -o yaml
kubectl -n "${TASK_NAME}" get service proxy-public -o yaml
gcloud compute backend-services get-health "bes-jupyter-${TASK_NAME}" --project="${GKE_PROJECT}" --global
gcloud compute addresses describe ip-alb-sbxtest01-shared --project="${GKE_PROJECT}" --global --format='value(address)'
unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT
```

완료 기준: Hub/Proxy 정상, KSA annotation이 sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com, Service NEG 정보 생성, Backend HEALTHY입니다. 사용자 Pod/PVC는 사용자가 로그인하여 서버를 시작한 뒤 생깁니다. 아직 로그인하지 않았다면 없는 것이 정상입니다.

### 11-3. 브라우저 로그인과 BQ

DNS 담당자가 Jupyter 도메인을 위 공통 ALB IP에 연결합니다. PoC에서 hosts 파일을 쓸 경우에도 실제 도메인과 인증서가 일치해야 합니다. 승인된 계정으로 `https://jupyter-sbx01.sonmap.net`에 접속하고 서버를 시작합니다. Notebook 셀에서 다음을 실행합니다.

```python
from google.cloud import bigquery

# Query Job 실행·인증부터 확인합니다. 외부 데이터 조회 권한 검사는 아닙니다.
client = bigquery.Client(project="pjt-net-hub-base")
print(list(client.query("SELECT 1 AS ok").result()))

# 기존 별도 BQ 프로젝트의 실제 Dataset/Table로 바꾼 뒤 실행합니다.
# print(list(client.query("SELECT * FROM `pjt-c-admin.DATASET.TABLE` LIMIT 1").result()))
```

완료 기준: 승인 사용자만 로그인하고 Notebook이 시작되며 SELECT 1이 성공합니다. 별도 pjt-c-admin 데이터 조회는 해당 관리자가 sbx-manager에 대상 Dataset 조회 권한을 부여한 뒤 검사합니다. 데이터 프로젝트의 조회 권한과 pjt-net-hub-base의 Query Job 권한은 별개입니다. 데이터레이크 권한 자동화 서비스는 이 저장소에서 제거되어 있습니다.

## 반복 실행·오류 시 기준

| 증상 | 확인할 단계·다음 작업 |
|---|---|
| SA/프로젝트 IAM 403 | 1단계의 실행 관리자와 대상 IAM 확인 |
| 기존 CIDR/서브넷/Host가 다름 | 2단계에서 중단하고 네트워크 설계 확인 |
| SSL 인증서 Not Found | 3단계 HTTPS Proxy/443 전에 인증서 별도 등록 |
| Group 동기화 invalid_grant/unauthorized_client | 4단계 DWD Client ID·Scope·위임 관리자 확인 |
| kubectl timeout | 5단계 Private Pool/관리 VM → GKE 경로 확인 |
| source ZIP/이미지 Not Found | 6단계 릴리스 ID·Generation·SHA256·이미지 태그 확인 |
| ImagePullBackOff | 7~8단계 내부 이미지 존재·노드 AR Reader 확인 |
| 기존 Dataset/Bucket 409 | 9단계 adopt_existing_resources와 실제 자원·State 확인 |
| Workflow SUCCEEDED인데 Notebook 없음 | 11단계의 부모/자식 Build 최종 결과 확인 |
| OAuth redirect 오류 | Callback URL·도메인·Secret 확인 |
| 별도 BQ 데이터 조회 403 | 데이터 프로젝트 Dataset 조회 권한과 Job 프로젝트 권한 확인 |

실패 후 무조건 같은 요청을 재전송하지 않습니다. API는 같은 request_id/release의 dispatch 기록을 재사용합니다. 해당 Build를 먼저 확인하고, 수정 후 새 최종 승인과 새 Request ID로 재실행합니다. 기존 Dataset/GCS/사용자 PVC를 오류 복구 목적으로 삭제하지 않습니다.

## 검증 범위와 참고 문서

```bash
# 개발 검사이며 GCP를 변경하지 않습니다.
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s 11.tests -v
```

문서/코드의 오프라인 검사와 실제 클라우드 배포 성공은 별개입니다. Cloud Build, DWD, 사설 경로, OAuth, 실제 BQ 조회는 위 완료 기준으로 실행 환경에서 확인해야 합니다. Terraform Provider 실행 검증도 이전 로컬 환경 오류로 완료되지 않았으며 여기서는 통과했다고 표시하지 않습니다.

공식 명령·상태 참고: [Build 제출](https://docs.cloud.google.com/sdk/gcloud/reference/builds/submit), [Workflow 실행 확인](https://docs.cloud.google.com/workflows/docs/executing-workflow), [IM Deployment 상태](https://docs.cloud.google.com/infrastructure-manager/docs/reference/rest/v1/projects.locations.deployments), [IM Revision 상태](https://docs.cloud.google.com/infrastructure-manager/docs/reference/rest/v1/projects.locations.deployments.revisions).
