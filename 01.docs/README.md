# 여기서 시작하세요 — 실제 수행 순서

> **현재 작업 기준:** 공통 인프라는 작업자가 개별 gcloud 명령으로 구축합니다. 과제는 포털이 GCS에 저장한 승인 JSON을 대상으로 작업자가 [Deploy 명령](../02.sandbox_setup_01_gcloud/05-deploy.md)을 실행합니다. GCS 이벤트 자동 시작·포털 결과 자동 전달은 추후 적용하며 현재 필수 구축 단계가 아닙니다. 기존 Deploy 내부의 API·Build·Terraform·GKE 처리 코드는 사용합니다.

**[작업 순서 Mermaid + 실행 문서·폴더 링크](work-order.md)**를 먼저 여세요. 번호별 링크로 해당 명령과 소스를 확인할 수 있습니다. 명령은 관리 VM의 저장소 루트에서 실행합니다.

**실행할 문서는 [실제 수행 절차](runbook-two-stage.md)입니다.** 저장소 루트에서 시작하고, 각 단계의 성공 기준을 확인한 뒤 다음 단계로 진행합니다.

| 실제 순서 | 수행 작업 | 수행자·실행 계정 | 완료 기준 |
|---|---|---|---|
| 0 | 소스 받기·변수·도구 확인 | 운영자 | 계정/프로젝트 조회 성공 |
| 1 | API·두 SA·IAM 준비 | 기존 권한 관리자 | 두 SA 조회·tf-manager 위임 성공 |
| 2 | Shared VPC·Subnet·PSA·방화벽 | tf-manager | CIDR/연결/방화벽 확인 |
| 3 | Bucket·AR·Private Pool·GKE·Run·Workflow·ALB | tf-manager | 각 서비스 조회·Run healthz 성공 |
| 4 | Jupyter OAuth·Workspace DWD 승인 | GCP 운영자·Workspace 관리자 | Secret ENABLED·위임 승인 |
| 5 | Private Pool → GKE API 접속 점검 | tf-manager Build | 접속 점검 Build SUCCESS |
| 6 | 플랫폼 릴리스 게시 | tf-manager Build | 이미지·소스 ZIP·release.json 생성 |
| 7 | Jupyter Chart/기본 이미지 미러링 | tf-manager Build | Chart/이미지 게시 성공 |
| 8 | 사용자 Notebook 표준 이미지 빌드 | tf-manager Build | 표준 이미지 조회 성공 |
| 9 | 수동 시험: 실제 과제값과 릴리스를 신청 JSON에 반영 | 시험 운영자 | request/source/data 설정 확인 |
| 10 | 수동 시험: 승인 요청 업로드·Workflow 호출 | 시험 운영자 | ACCEPTED·Build 시작 |
| 11 | Build·IM·GKE·ALB·로그인·BQ 점검 | 운영자·승인 사용자 | Build SUCCESS·Notebook/BQ 테스트 성공 |

폴더 번호는 자료를 찾기 위한 흐름 표기입니다. 실제 최초 구축에서는 Cloud Run API와 GKE 배포 도구의 이미지가 3단계에서 함께 빌드됩니다. 07/08/09 폴더는 요청 후 자동 호출되는 코드이며, 폴더 안에서 프로그램을 차례로 수동 실행하지 않습니다.

## 필요한 문서만 여세요

| 문서 | 언제 보는가 |
|---|---|
| [runbook-two-stage.md](runbook-two-stage.md) | 처음부터 끝까지 실제 실행 |
| [cloudbuild-private-gke-vpn-design.md](cloudbuild-private-gke-vpn-design.md) | 5단계 Private GKE 접속 점검이 실패할 때 |
| [jupyterhub-external-alb-oauth-runbook.md](jupyterhub-external-alb-oauth-runbook.md) | 4단계 OAuth 준비·11단계 접속 확인 |
| [architecture-and-operations.md](architecture-and-operations.md) | 실행 계정·자동화 경계·현재 코드 제한 확인 |
| [file-relationships.md](file-relationships.md) | 사람이 실행하는 작업과 자동 호출 관계 확인 |
| [file-catalog.md](file-catalog.md) | 특정 파일의 역할 조회 |

기존 별도 BQ 프로젝트의 조회 권한은 해당 관리자가 부여합니다. 별도 데이터레이크 권한 자동화 서비스는 제거되어 있습니다. 현재 과제별 40-data의 Dataset/GCS 구성은 유지되어 있으므로, 기존 BQ만 사용하는 설계와 구분해서 신청값을 확인합니다.

관리자 준비 작업은 [개별 gcloud 실행 문서](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md)를 사용합니다. shell 실행 없이 OAuth 등록·릴리스·미러링·Notebook 빌드를 수행합니다. 과제 요청은 포털→GCS가 운영 기준이며, 수동 요청 제출은 연동 시험용입니다. GCS 이벤트 시작과 배포 결과의 포털 전달은 추가 구현 대상입니다.
