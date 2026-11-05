# 실행 절차

## 준비

Python 3.10 이상과 최신 gcloud가 있는 관리 VM에서 실행합니다. 기존 프로젝트의 결제와 관리자 권한을 먼저 확인합니다. 로컬 PC에 Terraform을 설치할 필요는 없습니다.

```bash
git clone https://github.com/sonmap/GCP_SBX_Test01.git
cd GCP_SBX_Test01
cp gcloud/config.example.json gcloud/config.json
gcloud auth list
gcloud config get-value project
```

`gcloud/config.json`의 관리자/운영자, Folder, CIDR, 기존 프로젝트, 인증서 이름을 확인합니다. 새 프로젝트 생성을 사용할 때만 billing_account를 채웁니다. 예제 프로젝트/네트워크/리전은 런타임 Schema와 함께 고정되어 있어 단독 변경하면 검증이 거부합니다. create_test_cluster는 기본 false입니다. 원본의 Internal ALB 잔여 서브넷/예약 IP는 현행 External ALB에 필요 없어 새로 생성하지 않습니다.

## 1 관리자 권한

관리자로 로그인한 뒤 명령 출력부터 확인합니다. --apply는 계정/API/IAM을 실제 변경합니다.

```bash
python3 gcloud/bootstrap.py admin
python3 gcloud/bootstrap.py admin --apply
```

sbx-manager와 tf-manager 두 계정만 생성합니다. 기존 관리자에게 여러 프로젝트의 IAM 변경 권한과 Folder/Billing 범위 권한이 필요합니다. GCP 서비스 에이전트는 API 활성화에 따라 별도 생성됩니다.

## 2 공통 네트워크

```bash
python3 gcloud/bootstrap.py network
python3 gcloud/bootstrap.py network --apply
```

tf-manager를 impersonation하여 실행합니다. 기존 VPC/서브넷/PSA가 있으면 재사용합니다. 기존 CIDR 또는 PSA Range가 다르면 자동 덮어쓰지 않고 중단합니다. 기존 서비스 프로젝트가 다른 Host에 연결되어 있어도 중단합니다.

## 3 공통 기반

공통 HTTPS ALB를 활성화하려면 설정의 SSL 인증서 리소스가 GKE 프로젝트에 미리 있어야 합니다. 인증서 PEM/개인키는 Git에 넣지 않습니다. 기존 인증서를 재사용하거나 별도 절차로 등록합니다.

```bash
python3 gcloud/bootstrap.py foundation
python3 gcloud/bootstrap.py foundation --apply
```

첫 Build는 bootstrap 태그로 Runner/Provisioner 이미지를 만듭니다. 다음 릴리스 과정이 승인 요청에 사용할 고정 버전을 만듭니다. Bootstrap 재실행은 Cloud Run을 bootstrap 이미지로 갱신하므로 운영 릴리스를 유지하려면 재실행 뒤 release.sh를 다시 실행합니다.

GKE는 기존 private 클러스터를 재사용합니다. Private Pool → GKE Private IP의 VPN/BGP/방화벽/DNS 경로는 [별도 설계](cloudbuild-private-gke-vpn-design.md)를 따라 준비합니다. PSA만으로 Kubernetes API에 연결되지 않습니다. `gke_endpoint_mode=dns`는 명시적 선택 사항입니다.

## 사용자 이미지와 플랫폼 릴리스

1. Workspace 관리자 콘솔에서 sbx-manager의 oauth2ClientId로 DWD를 승인합니다. 필요한 scope는 `https://www.googleapis.com/auth/admin.directory.group` 및 `https://www.googleapis.com/auth/admin.directory.group.member`입니다. SA 키 파일은 만들지 않습니다.
2. Jupyter OAuth Secret 값을 등록합니다. 이 명령은 tf-manager 권한으로 실행합니다.

```bash
CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT=tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com bash scripts/set-jupyter-oauth-secrets.sh
```

3. 소스 커밋을 기준으로 새 릴리스를 게시합니다. 로컬 수정이 있으면 중단합니다.

```bash
bash gcloud/release.sh
bash gcloud/release.sh --apply
```

4. Chart/기본 이미지 미러링 후 사용자 이미지를 만듭니다. 미러링 Build는 인터넷에서 다운로드하므로 완전관리형 Cloud Build를 사용합니다.

```bash
bash gcloud/mirror-jupyter.sh
bash gcloud/mirror-jupyter.sh --apply
CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT=tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com bash jupyter-singleuser-standard/build-gcloud.sh
```

GitHub 자동 릴리스 Trigger는 기본 false입니다. 먼저 Cloud Build GitHub App에 **새 저장소** 연결을 승인한 뒤 create_github_trigger=true로 바꾸고 foundation을 실행합니다. Trigger가 원본 저장소를 가리키지 않도록 확인합니다.

## 과제 요청

release.sh가 출력한 release.json URI를 사용합니다. 아래 RELEASE_ID는 출력된 실제 값으로 바꿉니다.

```bash
mkdir -p .local
gcloud storage cp gs://prj-b-cicd-local-236d-sbxtest01-bundles/platform-releases/RELEASE_ID/release.json .local/release.json
python3 scripts/set-request-release.py examples/sbx01-approved-request.json .local/release.json .local/request.json
```

`.local/request.json`을 검토하고 다시 승인합니다. 예제는 기존 프로젝트/Dataset/Bucket 채택을 요청하므로 실제 자원 존재와 이전 State 관리 중지 여부를 확인합니다. 신규 데이터 자원이면 adopt_existing_resources=false로 변경합니다. 새 과제명/구성원/도메인/Request ID도 함께 맞춥니다.

```bash
bash scripts/run-approved-workflow.sh REQ-20261105-001 .local/request.json
```

Workflow 성공은 요청 접수 성공이며 최종 자원 배포 성공을 뜻하지 않습니다.

```bash
gcloud builds list --project=prj-b-cicd-local-236d --region=asia-northeast3 --limit=5
gcloud infra-manager deployments list --project=prj-b-cicd-local-236d --location=asia-northeast3 --filter='name:sbxtest01-'
```

ALB의 IP에 DNS 또는 PoC hosts 파일을 연결하고 등록된 인증서/도메인과 일치하는지 확인합니다. KSA annotation은 sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com이어야 합니다. OAuth Callback URL은 `https://<과제 도메인>/hub/oauth_callback`입니다.

데이터레이크 권한 처리는 별도 datalake-access-provisioner를 배포하고 요청 JSON을 업로드합니다. 이 컴포넌트도 동일한 두 계정만 사용합니다.

## 검증 기록

저장소 반영 시 Python 자동 테스트 14개, Python/Shell 구문 검사, Terraform HCL·JSON·YAML 파싱 검사를 통과했습니다. 명령 출력 모드는 GCP에 접속하거나 자원을 변경하지 않는 것을 테스트했습니다.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

실제 GCP 배포·이미지 Build·Workspace DWD·사설 경로는 검증하지 않았습니다. 추가 Terraform 1.5.7 validate 시도는 로컬 Google Provider 캐시 체크섬 불일치 및 plugin 실행 오류로 완료하지 못했습니다. 따라서 Provider 스키마 기반 검증이 통과했다고 간주하지 않습니다. 실행 VM/Infrastructure Manager 환경에서 해당 검증과 신규 자원 Plan을 확인한 후 배포합니다. 최초 1~3단계는 Terraform Provider와 무관한 gcloud 경로입니다.
