# tf-manager 소속 — pjt-d-host01

| 구분 | 프로젝트 / 계정 |
|---|---|
| tf-manager 소속 | SBX_GKE_PROJECT = pjt-d-host01 |
| Terraform·부모/자식 Build 실행 계정 | tf-manager@pjt-d-host01.iam.gserviceaccount.com |
| 계정 리소스 경로 | projects/pjt-d-host01/serviceAccounts/tf-manager@pjt-d-host01.iam.gserviceaccount.com |
| Build·IM·Run·Workflow·AR·GCS 실행 자원 | l2comn_PROJECT = prj-b-cicd-local-236d |
| sbx-manager 소속 | prj-b-cicd-local-236d — 이번 변경 대상 아님 |

## 관리자가 수행할 순서

[01-admin.md](../02.sandbox_setup_01_gcloud/01-admin.md)의 개별 명령을 기준으로 다음 작업을 수행합니다.

1. pjt-d-host01에서 IAM·IAM Credentials 등 필요한 API를 활성화합니다.
2. 조직 정책 관리자는 pjt-d-host01의 iam.disableCrossProjectServiceAccountUsage 유효 정책을 확인하고, 프로젝트 간 사용을 허용합니다. 403은 미설정으로 처리하지 않습니다.
3. pjt-d-host01에 tf-manager를 생성하거나 기존 계정을 확인합니다.
4. 새 계정에 자동화 실행 프로젝트·VPC Host·GKE·과제 프로젝트·Folder/Billing 범위의 기존 배포 권한을 부여합니다.
5. 운영자와 기존 sbx-manager에는 새 tf-manager의 사용 권한을, 자동화 프로젝트의 Infrastructure Manager 서비스 에이전트에는 새 계정의 Service Account User를 부여합니다. Cloud Build 서비스 에이전트에는 새 계정의 Token Creator를 부여합니다. 해당 명령은 계정 리소스 범위로 작성했습니다.
6. Cloud Identity 그룹 관리자 역할도 새 tf-manager의 **Unique ID**를 대상으로 확인·부여합니다. Customer ID와 Jupyter OAuth는 별개 설정입니다.
7. 변경된 provisioner-env.yaml로 플랫폼 릴리스를 게시합니다. GCS·이미지·Private Pool 위치를 이동하지 않습니다. 새 요청은 새 release.json을 사용합니다.
8. Private Pool 접속 점검과 과제 Deploy를 수행하고 Build·IM·GKE 결과를 확인합니다.

서비스 계정은 소속 프로젝트를 직접 이동할 수 없으므로 pjt-d-host01의 계정을 생성·사용하도록 소스를 변경한 것입니다. 기존 계정의 IAM/Workspace 권한은 새 계정으로 자동 이전되지 않습니다. 저장소 수정 과정에서 실제 계정을 생성하거나 기존 계정을 삭제하지 않았습니다. 기존 배포가 사용하는 이전 계정은 의존성을 확인하기 전에 삭제하지 않습니다.

## 직접 확인

```bash
export ADMIN_ACCOUNT="admin@sonmap.net"
export SBX_GKE_PROJECT="pjt-d-host01"
export l2comn_PROJECT="prj-b-cicd-local-236d"
export TF_MANAGER="tf-manager@${SBX_GKE_PROJECT}.iam.gserviceaccount.com"
export TF_MANAGER_RESOURCE="projects/${SBX_GKE_PROJECT}/serviceAccounts/${TF_MANAGER}"

gcloud iam service-accounts describe "${TF_MANAGER}" --project="${SBX_GKE_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='table(email,uniqueId,disabled)'
gcloud iam service-accounts get-iam-policy "${TF_MANAGER}" --project="${SBX_GKE_PROJECT}" --account="${ADMIN_ACCOUNT}"
gcloud resource-manager org-policies describe iam.disableCrossProjectServiceAccountUsage --effective --project="${SBX_GKE_PROJECT}" --account="${ADMIN_ACCOUNT}"
```

## 공식 참고

- [Cloud Build 프로젝트 간 서비스 계정 사용](https://docs.cloud.google.com/build/docs/securing-builds/configure-user-specified-service-accounts#cross-project_setup)
- [Infrastructure Manager 프로젝트 간 권한](https://docs.cloud.google.com/infrastructure-manager/docs/configure-service-account#grant_access_across_multiple_projects)
