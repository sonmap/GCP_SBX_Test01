# 1. 관리자 권한 — 개별 gcloud 명령

기존 권한 관리자로 실행합니다. API → 두 계정 → IAM 순서입니다.

먼저 [공통 변수](00-variables.md)를 같은 터미널에 설정합니다. 각 코드 블록을 **한 개씩** 실행하고 결과를 확인합니다. 전체 실행 스크립트나 Python 호출은 없습니다.

**조회와 생성은 별도입니다.** 조회 성공 시 기대값을 확인하고 바로 다음 생성 명령은 건너뜁니다. 명시적 Not Found일 때만 생성합니다. 403·인증·연결 오류는 미존재가 아니므로 중단합니다. 명령은 실제 작업이며 `--apply`/미리보기 모드가 없습니다.

## 1. services enable serviceusage.googleapis.com iam.googleapis.com iamcredentials.googleapis.com

실행:

```bash
gcloud services enable serviceusage.googleapis.com iam.googleapis.com iamcredentials.googleapis.com compute.googleapis.com container.googleapis.com cloudbuild.googleapis.com config.googleapis.com run.googleapis.com workflows.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com storage.googleapis.com logging.googleapis.com cloudresourcemanager.googleapis.com cloudbilling.googleapis.com admin.googleapis.com cloudscheduler.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 2. services enable compute.googleapis.com container.googleapis.com servicenetworking.googleapis.com

실행:

```bash
gcloud services enable compute.googleapis.com container.googleapis.com servicenetworking.googleapis.com "--project=${HOST_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 3. services enable container.googleapis.com compute.googleapis.com

실행:

```bash
gcloud services enable container.googleapis.com compute.googleapis.com "--project=${GKE_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 4. beta services identity create

실행:

```bash
gcloud beta services identity create --service=cloudbuild.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 5. beta services identity create

실행:

```bash
gcloud beta services identity create --service=config.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 6. beta services identity create

실행:

```bash
gcloud beta services identity create --service=run.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 7. beta services identity create

실행:

```bash
gcloud beta services identity create --service=workflows.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 8. beta services identity create

실행:

```bash
gcloud beta services identity create --service=cloudscheduler.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 9. beta services identity create

실행:

```bash
gcloud beta services identity create --service=container.googleapis.com "--project=${CICD_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 10. beta services identity create

실행:

```bash
gcloud beta services identity create --service=container.googleapis.com "--project=${GKE_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 11. beta services identity create

실행:

```bash
gcloud beta services identity create --service=container.googleapis.com "--project=${HOST_PROJECT}" "--account=${ADMIN_ACCOUNT}"
```

## 12. iam service-accounts create sbx-manager

조회:

```bash
gcloud iam service-accounts describe "${SBX_MANAGER}" "--project=${CICD_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}"
```

없는 경우에만 생성:

```bash
gcloud iam service-accounts create sbx-manager "--project=${CICD_PROJECT}" --display-name=sbx_manager "--account=${ADMIN_ACCOUNT}"
```

## 13. iam service-accounts create tf-manager

조회:

```bash
gcloud iam service-accounts describe "${TF_MANAGER}" "--project=${CICD_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}"
```

없는 경우에만 생성:

```bash
gcloud iam service-accounts create tf-manager "--project=${CICD_PROJECT}" --display-name=tf_manager "--account=${ADMIN_ACCOUNT}"
```

## 14. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/serviceusage.serviceUsageAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/serviceusage.serviceUsageAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 15. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/iam.serviceAccountAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 16. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/resourcemanager.projectIamAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/resourcemanager.projectIamAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 17. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/storage.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/storage.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 18. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/secretmanager.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/secretmanager.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 19. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/artifactregistry.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/artifactregistry.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 20. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/cloudbuild.builds.editor

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/cloudbuild.builds.editor --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 21. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/cloudbuild.workerPoolOwner

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/cloudbuild.workerPoolOwner --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 22. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/cloudbuild.workerPoolUser

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/cloudbuild.workerPoolUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 23. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/config.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/config.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 24. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/config.agent

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/config.agent --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 25. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/run.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/run.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 26. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/workflows.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/workflows.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 27. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/container.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/container.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 28. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/compute.viewer

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.viewer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 29. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/logging.logWriter

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/logging.logWriter --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 30. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/serviceusage.serviceUsageConsumer

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/serviceusage.serviceUsageConsumer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 31. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/cloudbuild.builds.editor

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/cloudbuild.builds.editor --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 32. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/cloudbuild.workerPoolUser

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/cloudbuild.workerPoolUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 33. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/workflows.invoker

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/workflows.invoker --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 34. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/logging.logWriter

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/logging.logWriter --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 35. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/serviceusage.serviceUsageConsumer

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/serviceusage.serviceUsageConsumer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 36. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.networkAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 37. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.securityAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.securityAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 38. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 39. projects add-iam-policy-binding pjt-d-shared-base · roles/servicenetworking.networksAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/servicenetworking.networksAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 40. projects add-iam-policy-binding pjt-d-shared-base · roles/serviceusage.serviceUsageConsumer

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/serviceusage.serviceUsageConsumer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 41. projects add-iam-policy-binding pjt-d-host01 · roles/container.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${GKE_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/container.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 42. projects add-iam-policy-binding pjt-d-host01 · roles/compute.loadBalancerAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${GKE_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.loadBalancerAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 43. projects add-iam-policy-binding pjt-d-host01 · roles/compute.viewer

실행:

```bash
gcloud projects add-iam-policy-binding "${GKE_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.viewer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 44. projects add-iam-policy-binding pjt-d-host01 · roles/serviceusage.serviceUsageConsumer

실행:

```bash
gcloud projects add-iam-policy-binding "${GKE_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/serviceusage.serviceUsageConsumer --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 45. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountTokenCreator

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=${OPERATOR_MEMBER}" --role=roles/iam.serviceAccountTokenCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 46. iam service-accounts add-iam-policy-binding sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountTokenCreator

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${SBX_MANAGER}" "--project=${CICD_PROJECT}" "--member=${OPERATOR_MEMBER}" --role=roles/iam.serviceAccountTokenCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 47. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=${OPERATOR_MEMBER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 48. iam service-accounts add-iam-policy-binding sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${SBX_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 49. iam service-accounts add-iam-policy-binding sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountTokenCreator

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${SBX_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountTokenCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 50. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 51. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 52. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountTokenCreator

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountTokenCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 53. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@gcp-sa-config.iam.gserviceaccount.com" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 54. iam service-accounts add-iam-policy-binding tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com · roles/iam.serviceAccountTokenCreator

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${TF_MANAGER}" "--project=${CICD_PROJECT}" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@gcp-sa-cloudbuild.iam.gserviceaccount.com" --role=roles/iam.serviceAccountTokenCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 55. projects add-iam-policy-binding pjt-net-hub-base · roles/browser

실행:

```bash
gcloud projects add-iam-policy-binding "${TASK_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/browser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 56. projects add-iam-policy-binding pjt-net-hub-base · roles/resourcemanager.projectIamAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${TASK_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/resourcemanager.projectIamAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 57. projects add-iam-policy-binding pjt-net-hub-base · roles/serviceusage.serviceUsageAdmin

실행:

```bash
gcloud projects add-iam-policy-binding "${TASK_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/serviceusage.serviceUsageAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 58. projects add-iam-policy-binding pjt-net-hub-base · roles/bigquery.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${TASK_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/bigquery.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 59. projects add-iam-policy-binding pjt-net-hub-base · roles/storage.admin

실행:

```bash
gcloud projects add-iam-policy-binding "${TASK_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/storage.admin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 60. resource-manager folders add-iam-policy-binding 154455658682 · roles/resourcemanager.projectCreator

실행:

```bash
gcloud resource-manager folders add-iam-policy-binding "${FOLDER_ID}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/resourcemanager.projectCreator --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 61. resource-manager folders add-iam-policy-binding 154455658682 · roles/resourcemanager.projectIamAdmin

실행:

```bash
gcloud resource-manager folders add-iam-policy-binding "${FOLDER_ID}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/resourcemanager.projectIamAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 62. resource-manager folders add-iam-policy-binding 154455658682 · roles/compute.xpnAdmin

실행:

```bash
gcloud resource-manager folders add-iam-policy-binding "${FOLDER_ID}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/compute.xpnAdmin --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 63. projects add-iam-policy-binding pjt-d-shared-base · roles/container.hostServiceAgentUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@container-engine-robot.iam.gserviceaccount.com" --role=roles/container.hostServiceAgentUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 64. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@container-engine-robot.iam.gserviceaccount.com" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 65. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${CICD_PROJECT_NUMBER}@cloudservices.gserviceaccount.com" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 66. projects add-iam-policy-binding pjt-d-shared-base · roles/container.hostServiceAgentUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:service-${GKE_PROJECT_NUMBER}@container-engine-robot.iam.gserviceaccount.com" --role=roles/container.hostServiceAgentUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 67. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:service-${GKE_PROJECT_NUMBER}@container-engine-robot.iam.gserviceaccount.com" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 68. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:${GKE_PROJECT_NUMBER}@cloudservices.gserviceaccount.com" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 69. projects add-iam-policy-binding pjt-d-shared-base · roles/compute.networkUser

실행:

```bash
gcloud projects add-iam-policy-binding "${HOST_PROJECT}" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com" --role=roles/compute.networkUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 70. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/container.defaultNodeServiceAccount

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=serviceAccount:${CICD_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role=roles/container.defaultNodeServiceAccount --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 71. iam service-accounts add-iam-policy-binding CICD_PROJECT_NUMBER-compute@developer.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${CICD_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 72. projects add-iam-policy-binding pjt-d-host01 · roles/container.defaultNodeServiceAccount

실행:

```bash
gcloud projects add-iam-policy-binding "${GKE_PROJECT}" "--member=serviceAccount:${GKE_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role=roles/container.defaultNodeServiceAccount --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 73. iam service-accounts add-iam-policy-binding GKE_PROJECT_NUMBER-compute@developer.gserviceaccount.com · roles/iam.serviceAccountUser

실행:

```bash
gcloud iam service-accounts add-iam-policy-binding "${GKE_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" "--project=${GKE_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/iam.serviceAccountUser --condition=None "--account=${ADMIN_ACCOUNT}"
```

## 선택: 신규 과제 프로젝트의 Billing 연결 권한

공통 변수의 BILLING_ACCOUNT에 실제 Billing ID를 입력한 경우에만 실행합니다. 기존 프로젝트만 사용하면 생략합니다.

```bash
gcloud billing accounts add-iam-policy-binding "${BILLING_ACCOUNT}" --member="serviceAccount:${TF_MANAGER}" --role=roles/billing.user --account="${ADMIN_ACCOUNT}"
```

Workspace DWD 승인은 별도 관리 콘솔 작업입니다. sbx-manager의 OAuth Client ID를 다음 조회로 확인하고 두 Directory Group scope를 승인합니다.

```bash
gcloud iam service-accounts describe "${SBX_MANAGER}" --project="${CICD_PROJECT}" --account="${ADMIN_ACCOUNT}" --format='value(oauth2ClientId)'
```
