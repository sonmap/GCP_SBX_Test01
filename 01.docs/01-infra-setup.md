# 1차 공통 인프라 구축

관리 VM `infra-son01`의 저장소 루트에서 진행합니다. 공통 기반을 처음 만들 때 한 번 실행하며, 기존 자원은 조회해서 재사용합니다. 표의 **명령 문서**에는 해당 단계에서 입력할 개별 `gcloud` 명령이 있습니다.

```bash
cd ~/GCP_SBX_Test01
git status --short
git pull --ff-only
```

## 1. 표를 위에서 아래로 실행

| 순서 | 실행할 명령 문서 | 다음 단계로 넘어가는 기준 |
|---|---|---|
| 1 | [공통 변수](../02.sandbox_setup_01_gcloud/00-variables.md) → [API·서비스 계정·IAM](../02.sandbox_setup_01_gcloud/01-admin.md) | 플랫폼 `gcp-sbx-edp-gke01`에서 `tf-manager`와 `sbx-manager`가 조회됨 |
| 2 | [Shared VPC·서브넷·PSA·방화벽](../02.sandbox_setup_01_gcloud/02-network.md) → [서브넷 사용 권한](../02.sandbox_setup_01_gcloud/02-subnet-iam.md) | VPC 관리자 `admin@sonmap.net`이 호스트 프로젝트에서 서브넷과 권한 확인 |
| 3 | [공통 기반 생성](../02.sandbox_setup_01_gcloud/03-foundation.md) | GCS·Artifact Registry·Private Pool·GKE·초기 이미지·Cloud Run·Workflow·공통 ALB 리소스 조회 성공 |
| 4 | [Workspace 그룹 관리 역할 승인](cloud-identity-group-terraform.md) → [OAuth Secret 등록](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md#4-oauth-값-등록) | Workspace 최고 관리자가 `tf-manager`에 역할 부여. 실제 Customer ID와 OAuth Secret 준비 |
| 5 | 아래 **GKE 접속 점검** 실행 | 관리 VM과 Private Pool 양쪽에서 Namespace 조회 성공 |
| 6 | [플랫폼 릴리스 게시](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md#5-플랫폼-릴리스-게시) → [Chart·이미지 미러링](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md#6-chart와-기본-이미지-미러링) → [Notebook 이미지 빌드](../02.sandbox_setup_01_gcloud/04-manual-gcloud.md#7-notebook-표준-이미지-빌드) | `release.json`, 내부 Chart, Notebook 이미지 확인 |
| 7 | [내부 HTTPS ALB·인증서](sbx03-https-certificate-runbook.md) → [Google 로그인 콜백](sbx03-google-oauth-runbook.md) | 내부 VIP TCP 443 연결과 대상 도메인의 DNS·인증서·콜백 등록 확인 |

플랫폼 작업의 제출 계정은 `son@sonmap.net`입니다. Cloud Build와 Infrastructure Manager는 `tf-manager`, Cloud Run과 Workflow는 `sbx-manager`로 실행합니다. Workspace 역할 승인과 JupyterHub OAuth 등록은 서로 다른 작업입니다.

현재 시험 환경의 Private Pool은 **`e2-standard-2`**입니다. 기반 문서의 초기 `e2-standard-4` 예시를 적용하기 전에 [sbx03 시험 기록의 Pool 설정](sbx03-new-project-runbook.md#62-gke-복구와-private-pool-점검)을 확인하세요. 상위 빌드와 하위 빌드가 동시에 워커를 사용합니다.

## 2. GKE 접속 점검 · 복사해서 실행

GKE와 초기 Runner 이미지가 준비된 뒤 실행합니다. 클러스터를 새로 만들었으면 DNS 엔드포인트를 활성화하고 kubeconfig를 갱신합니다.

```bash
gcloud container clusters update gke-sbx-main-an3 --project=gcp-sbx-edp-gke01 --region=asia-northeast3 --enable-dns-access --account=son@sonmap.net

KUBECONFIG="$HOME/.kube/config-sbx-dns" gcloud container clusters get-credentials gke-sbx-main-an3 --project=gcp-sbx-edp-gke01 --region=asia-northeast3 --dns-endpoint --account=son@sonmap.net

CLOUDSDK_CORE_ACCOUNT=son@sonmap.net kubectl --kubeconfig="$HOME/.kube/config-sbx-dns" get namespaces

gcloud builds submit --no-source --config=01.docs/check-private-gke.yaml \
  --project=gcp-sbx-edp-gke01 --region=asia-northeast3 --account=son@sonmap.net \
  --service-account=projects/gcp-sbx-edp-gke01/serviceAccounts/tf-manager@gcp-sbx-edp-gke01.iam.gserviceaccount.com
```

빌드가 `SUCCESS`이고 로그에 Namespace 목록이 표시되면 통과입니다. 실패 시 [점검 YAML 사용법](cloudbuild-private-gke-vpn-design.md)에서 오류가 난 단계만 확인합니다.

GKE만 삭제했다가 재시험하는 경우에는 [GKE 복구 절차](sbx03-new-project-runbook.md#6-실제-작업-기록과-다음-테스트-순서)에서 시작하세요. 공통 기반 준비가 끝나면 [2차 Sandbox 배포](02-sandbox-deploy.md)로 이동합니다.
