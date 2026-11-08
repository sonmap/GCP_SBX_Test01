**[Git 최신 설정 동기화·현재 단계 재개](git-sync-current-environment.md)** — 로컬 Customer ID를 보존하고, 프로젝트 치환 없이 Private Pool 점검을 실행합니다.

> 신규 프로젝트·과제 전용 GSA 생성은 [sbx03 신규 과제 절차](sbx03-new-project-runbook.md)를 우선 적용합니다. 기존 프로젝트 재사용 절차와 구분하세요.

# 현재 실환경 실행 가이드

**[개별 명령으로 따라 하는 실제 작업 가이드](operator-command-guide.md)** — `gcp-sbx-edp-gke01` / `gcp-prod-edp-hub-vpchost`, `son@sonmap.net` / `admin@sonmap.net` 계정 구분, 실제 대역·오류 해결·현재 진행 상태를 반영했습니다. 현재 환경의 명령 실행은 이 링크에서 시작하세요. 관련 기본값도 현재 환경으로 동기화했습니다.

---

# 여기서 시작하세요 — 실제 수행 순서

> **[서브넷별 IAM](../02.sandbox_setup_01_gcloud/02-subnet-iam.md)**: VPC Admin이 네트워크를 준비한 뒤 GKE·ALB VIP 서브넷에 필요한 계정만 사용 권한을 부여합니다. 이후 tf-manager로 내부 ALB를 구성합니다.

> **[내부 사설 ALB 설계](internal-alb-design.md)**: ALB·VIP는 gcp-sbx-edp-gke01, /27 VIP Subnet과 최소 /26 프록시 Subnet은 Shared VPC Host에 둡니다. 후보 CIDR은 VPC Admin 승인 후 적용합니다.

> **[IP 최소화 구성](minimal-ip-design.md)**: Cloud Run·과제별 서브넷은 기본 생성하지 않고, 기존 GKE·Private Pool PSA를 유지·재사용합니다.

**[프로젝트·서브넷·Private Pool·GCP 자원 설계표](network-resource-design.md)** — 기존 과제 SBX 프로젝트 재사용 기준입니다.

> **프로젝트 통합:** GKE·Build·Workflows·AR·GCS·Run·IM과 두 서비스 계정을 모두 **gcp-sbx-edp-gke01**에 구성합니다. [통합 자원·실행 순서·기존 배포 확인](tf-manager-project.md)

## tf-manager 소속 프로젝트

Terraform·Build 실행 계정은 **tf-manager@gcp-sbx-edp-gke01.iam.gserviceaccount.com**입니다. 두 서비스 계정과 Build·Infrastructure Manager·AR·GCS·Run·Workflow·GKE는 모두 SBX_GKE_PROJECT 하나에 구성합니다. [통합 프로젝트 구성과 사전 준비](tf-manager-project.md)을 확인하세요.

> **담당 구분:** Private Pool → GKE 사설 경로와 기존 BigQuery 데이터 조회 권한은 **VPC Admin 요청사항**입니다. 인증서·DNS는 **별도 진행**합니다. tf-manager의 그룹 관리자 역할은 과제 Google Group 관리용, Jupyter OAuth는 사용자 로그인용입니다. [담당자 요청서·인증 설명](admin-requests.md)을 확인하세요.

> **현재 작업 기준:** 공통 인프라는 작업자가 개별 gcloud 명령으로 구축합니다. 과제는 포털이 GCS에 저장한 승인 JSON을 대상으로 작업자가 [Deploy 명령](../02.sandbox_setup_01_gcloud/05-deploy.md)을 실행합니다. GCS 이벤트 자동 시작·포털 결과 자동 전달은 추후 적용하며 현재 필수 구축 단계가 아닙니다. 기존 Deploy 내부의 API·Build·Terraform·GKE 처리 코드는 사용합니다.

**[작업 순서 Mermaid + 실행 문서·폴더 링크](work-order.md)**를 먼저 여세요. 번호별 링크로 해당 명령과 소스를 확인할 수 있습니다. 명령은 관리 VM의 저장소 루트에서 실행합니다.

**실행할 문서는 [실제 수행 절차](runbook-two-stage.md)입니다.** 저장소 루트에서 시작하고, 각 단계의 성공 기준을 확인한 뒤 다음 단계로 진행합니다.

| 실제 순서 | 수행 작업 | 수행자·실행 계정 | 완료 기준 |
|---|---|---|---|
| 0 | 소스 받기·변수·도구 확인 | 운영자 | 계정/프로젝트 조회 성공 |
| 1 | API·두 SA·IAM 준비 | 기존 권한 관리자 | 두 SA 조회·tf-manager 위임 성공 |
| 2 | Shared VPC·Subnet·PSA·방화벽 | VPC Admin | CIDR/연결/방화벽 확인 |
| 2-1 | GKE·ALB VIP Subnet별 IAM | VPC Admin | 필요한 네 개 Network User 바인딩 확인 |
| 3 | Bucket·AR·Private Pool·GKE·Run·Workflow·ALB | tf-manager | 각 서비스 조회·Run healthz 성공 |
| 4 | Jupyter OAuth·tf-manager 그룹 관리자 역할 | GCP 운영자·Workspace 관리자 | Secret ENABLED·그룹 관리자 역할·Customer ID 준비 |
| 5 | Private Pool → GKE API 접속 점검 | tf-manager Build | 접속 점검 Build SUCCESS |
| 6 | 플랫폼 릴리스 게시 | tf-manager Build | 이미지·소스 ZIP·release.json 생성 |
| 7 | Jupyter Chart/기본 이미지 미러링 | tf-manager Build | Chart/이미지 게시 성공 |
| 8 | 사용자 Notebook 표준 이미지 빌드 | tf-manager Build | 표준 이미지 조회 성공 |
| 9 | 수동 시험: 실제 과제값과 릴리스를 신청 JSON에 반영 | 시험 운영자 | request/source/data 설정 확인 |
| 10 | 수동 시험: 승인 요청 업로드·Workflow 호출 | 시험 운영자 | ACCEPTED·Build 시작 |
| 11 | Build·IM·GKE·ALB·로그인·BQ 점검 | 운영자·승인 사용자 | Build SUCCESS·Notebook/BQ 테스트 성공 |

폴더 번호는 자료를 찾기 위한 흐름 표기입니다. 실제 최초 구축에서는 Cloud Run API와 GKE 배포 도구의 이미지가 3단계에서 함께 빌드됩니다. 07/08/09 폴더는 요청 후 자동 호출되는 코드이며, 폴더 안에서 프로그램을 차례로 수동 실행하지 않습니다.

## sbx03 사용자 접속 설정

| 구분 | 실행 문서 | 확인 기준 |
|---|---|---|
| 내부 HTTPS ALB·인증서 | [TLS 인증서와 Windows 신뢰 설정](sbx03-https-certificate-runbook.md) | 내부 VIP 443, 이름 해석, HTTPS 로그인 화면 |
| Google OAuth | [웹 클라이언트와 콜백 주소 등록](sbx03-google-oauth-runbook.md) | Google 로그인 후 JupyterHub로 복귀 |
| 사용자 Notebook 홈 | [Notebook 이미지 빌드 및 적용](../04.Jupiter-setup-image/README.md) | `user01`의 홈 `/home/user01` |

## 필요한 문서만 여세요

| 문서 | 언제 보는가 |
|---|---|
| [runbook-two-stage.md](runbook-two-stage.md) | 처음부터 끝까지 실제 실행 |
| [cloudbuild-private-gke-vpn-design.md](cloudbuild-private-gke-vpn-design.md) | 5단계 Private Pool → GKE DNS 접속 점검 YAML 설명·실행·오류 확인 |
| [jupyterhub-internal-alb-oauth-runbook.md](jupyterhub-internal-alb-oauth-runbook.md) | 4단계 OAuth 준비·11단계 접속 확인 |
| [architecture-and-operations.md](architecture-and-operations.md) | 실행 계정·자동화 경계·현재 코드 제한 확인 |
| [file-relationships.md](file-relationships.md) | 사람이 실행하는 작업과 자동 호출 관계 확인 |
| [file-catalog.md](file-catalog.md) | 특정 파일의 역할 조회 |

기존 별도 BQ 프로젝트의 조회 권한은 해당 관리자가 부여합니다. 별도 데이터레이크 권한 자동화 서비스는 제거되어 있습니다. 현재 과제별 40-data의 Dataset/GCS 구성은 유지되어 있으므로, 기존 BQ만 사용하는 설계와 구분해서 신청값을 확인합니다.

관리자 준비 작업은 [개별 gcloud 실행 문서](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md)를 사용합니다. shell 실행 없이 OAuth 등록·릴리스·미러링·Notebook 빌드를 수행합니다. 과제 요청은 포털→GCS가 운영 기준이며, 수동 요청 제출은 연동 시험용입니다. GCS 이벤트 시작과 배포 결과의 포털 전달은 추가 구현 대상입니다.

## sbx03 시험 기록과 재실행

[지금까지의 작업과 GKE 삭제 후 재시험 순서](sbx03-new-project-runbook.md#6-실제-작업-기록과-다음-테스트-순서)를 따라 진행합니다. 백업, GKE·Private Pool 확인, 승인 요청 재제출, Windows·HTTPS·OAuth, Notebook 검증 순서로 실행 명령과 Mermaid 흐름도를 정리했습니다.
