# 실행 절차

## 준비

최신 gcloud와 Bash가 있는 관리 VM에서 저장소를 받습니다. 기존 프로젝트 결제·관리자 권한을 확인합니다.

```bash
git clone https://github.com/sonmap/GCP_SBX_Test01.git
cd GCP_SBX_Test01
gcloud auth list
gcloud config get-value project
```

[공통 변수](../gcloud/00-variables.md)의 export/프로젝트 번호 조회 블록을 같은 터미널에 복사합니다. config.json과 Python 통합 실행기는 사용하지 않습니다. 관리 계정·운영자·Folder·CIDR·인증서 이름을 확인합니다. 이 PoC의 프로젝트·네트워크·클러스터 값은 런타임 Schema와 YAML에도 있으므로 공통 변수만 단독 변경하지 않습니다.

## 1 관리자 권한

[01-admin.md](../gcloud/01-admin.md)의 API → 서비스 계정 → IAM 명령을 한 줄씩 실행합니다. 기존 sbx-manager/tf-manager는 describe 결과를 확인하고 create를 건너뜁니다. 여러 프로젝트와 Folder/Billing의 IAM을 변경할 수 있는 기존 관리자로 실행합니다.

## 2 공통 네트워크

[02-network.md](../gcloud/02-network.md)의 gcloud 명령을 개별 실행합니다. 명령마다 tf-manager impersonation을 명시합니다. VPC·서브넷·PSA·Shared VPC 연결을 조회하고 없는 것만 생성합니다. 기존 CIDR/Secondary Range/Host가 다르면 중단합니다. 403·연결 실패는 미존재로 취급하지 않습니다. Test GKE용 서브넷은 선택 항목입니다.

## 3 공통 기반

[03-foundation.md](../gcloud/03-foundation.md)의 Bucket·AR·Secret·Pool·GKE·Build·Run·Workflow·ALB 명령을 개별 실행합니다. YAML 입력 파일은 Git에 포함되어 있으며 Python으로 생성하지 않습니다. Workflow URL 치환만 문서의 sed 명령을 사용합니다.

기존 GKE는 Private/Autopilot/Subnet/Pod Range를 확인하고 생성 명령을 건너뜁니다. 기존 공통 ALB는 조회하여 재사용하고 URL Map 경로를 덮어쓰지 않습니다. 인증서가 없으면 HTTPS 명령 전에 별도 등록합니다. 이미지 Build와 Cloud Run/Workflow deploy는 실제 생성·갱신 작업입니다. 전체 실행 명령/--apply/미리보기 모드는 없습니다.

Private Pool → GKE Private IP의 VPN/BGP/방화벽/DNS 경로는 [별도 설계](cloudbuild-private-gke-vpn-design.md)를 따라 준비합니다. PSA만으로 Kubernetes API에 연결되지 않습니다. 기본은 internal endpoint입니다.

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

GitHub 자동 릴리스 Trigger는 [3단계의 선택 명령](../gcloud/03-foundation.md)으로 분리했습니다. Cloud Build GitHub App에 새 저장소 연결을 승인한 뒤 필요할 때만 해당 create 명령을 실행합니다.

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

## 검증

1~3단계 명령 문서의 Bash 구문, 변수 치환, Workflow 템플릿 치환을 gcloud 대역 프로그램으로 검사합니다. 실제 gcloud API는 호출하지 않습니다. 과제별 프로비저너는 기존 자동 테스트로 검사합니다.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

검증용 Python은 개발 검사에만 사용하며 1~3단계 실행에는 필요하지 않습니다. 실제 GCP 배포·이미지 Build·Workspace DWD·사설 경로는 검증하지 않았습니다. 이전 Terraform Provider 실행 검증도 환경 오류로 완료하지 못했으므로 Provider 스키마 기반 검증이 통과했다고 간주하지 않습니다. 실행 환경에서 Infrastructure Manager Plan과 실제 네트워크·권한을 확인해야 합니다.
