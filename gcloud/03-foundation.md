# 3. 공통 기반 — 개별 gcloud 명령

2단계 완료 후 tf-manager로 실행합니다. Bucket → AR → Secret → Pool → GKE → 이미지 → Cloud Run → Workflow → ALB 순서입니다.

먼저 [공통 변수](00-variables.md)를 같은 터미널에 설정합니다. 각 코드 블록을 **한 개씩** 실행하고 결과를 확인합니다. 전체 실행 스크립트나 Python 호출은 없습니다.

**조회와 생성은 별도입니다.** 조회 성공 시 기대값을 확인하고 바로 다음 생성 명령은 건너뜁니다. 명시적 Not Found일 때만 생성합니다. 403·인증·연결 오류는 미존재가 아니므로 중단합니다. 명령은 실제 작업이며 `--apply`/미리보기 모드가 없습니다.

기존 GKE는 Autopilot, Private Nodes/Endpoint, 서브넷과 Pod Range를 확인하고 create-auto를 건너뜁니다. 이미지 Build와 Cloud Run/Workflow deploy는 실행할 때마다 갱신 작업을 수행합니다. Private Pool → GKE 사설 경로는 별도로 준비합니다.

## 1. storage buckets create gs://prj-b-cicd-local-236d-sbxtest01-requests

조회:

```bash
gcloud storage buckets describe "gs://${CICD_PROJECT}-sbxtest01-requests" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud storage buckets create "gs://${CICD_PROJECT}-sbxtest01-requests" "--project=${CICD_PROJECT}" "--location=${REGION}" --uniform-bucket-level-access --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 2. storage buckets update gs://prj-b-cicd-local-236d-sbxtest01-requests

실행:

```bash
gcloud storage buckets update "gs://${CICD_PROJECT}-sbxtest01-requests" --versioning --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 3. storage buckets create gs://prj-b-cicd-local-236d-sbxtest01-bundles

조회:

```bash
gcloud storage buckets describe "gs://${CICD_PROJECT}-sbxtest01-bundles" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud storage buckets create "gs://${CICD_PROJECT}-sbxtest01-bundles" "--project=${CICD_PROJECT}" "--location=${REGION}" --uniform-bucket-level-access --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 4. storage buckets update gs://prj-b-cicd-local-236d-sbxtest01-bundles

실행:

```bash
gcloud storage buckets update "gs://${CICD_PROJECT}-sbxtest01-bundles" --versioning --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 5. storage buckets create gs://prj-b-cicd-local-236d-sbxtest01-build-source

조회:

```bash
gcloud storage buckets describe "gs://${CICD_PROJECT}-sbxtest01-build-source" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud storage buckets create "gs://${CICD_PROJECT}-sbxtest01-build-source" "--project=${CICD_PROJECT}" "--location=${REGION}" --uniform-bucket-level-access --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 6. storage buckets update gs://prj-b-cicd-local-236d-sbxtest01-build-source

실행:

```bash
gcloud storage buckets update "gs://${CICD_PROJECT}-sbxtest01-build-source" --versioning --public-access-prevention "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 7. storage buckets add-iam-policy-binding gs://prj-b-cicd-local-236d-sbxtest01-requests · roles/storage.objectAdmin

실행:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CICD_PROJECT}-sbxtest01-requests" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/storage.objectAdmin "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 8. storage buckets add-iam-policy-binding gs://prj-b-cicd-local-236d-sbxtest01-bundles · roles/storage.objectAdmin

실행:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CICD_PROJECT}-sbxtest01-bundles" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/storage.objectAdmin "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 9. storage buckets add-iam-policy-binding gs://prj-b-cicd-local-236d-sbxtest01-bundles · roles/storage.objectViewer

실행:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CICD_PROJECT}-sbxtest01-bundles" "--member=serviceAccount:service-${CICD_PROJECT_NUMBER}@gcp-sa-config.iam.gserviceaccount.com" --role=roles/storage.objectViewer "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 10. artifacts repositories create ar-sbxtest01-platform

조회:

```bash
gcloud artifacts repositories describe ar-sbxtest01-platform "--project=${CICD_PROJECT}" "--location=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud artifacts repositories create ar-sbxtest01-platform "--project=${CICD_PROJECT}" "--location=${REGION}" --repository-format=docker "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 11. artifacts repositories add-iam-policy-binding ar-sbxtest01-platform · roles/artifactregistry.reader

실행:

```bash
gcloud artifacts repositories add-iam-policy-binding ar-sbxtest01-platform "--project=${CICD_PROJECT}" "--location=${REGION}" "--member=serviceAccount:${GKE_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role=roles/artifactregistry.reader "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 12. artifacts repositories add-iam-policy-binding ar-sbxtest01-platform · roles/artifactregistry.reader

실행:

```bash
gcloud artifacts repositories add-iam-policy-binding ar-sbxtest01-platform "--project=${CICD_PROJECT}" "--location=${REGION}" "--member=serviceAccount:${CICD_PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --role=roles/artifactregistry.reader "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 13. secrets create jupyter-oauth-client-id

조회:

```bash
gcloud secrets describe jupyter-oauth-client-id "--project=${CICD_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud secrets create jupyter-oauth-client-id "--project=${CICD_PROJECT}" --replication-policy=user-managed "--locations=${REGION}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 14. secrets add-iam-policy-binding jupyter-oauth-client-id · roles/secretmanager.secretAccessor

실행:

```bash
gcloud secrets add-iam-policy-binding jupyter-oauth-client-id "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/secretmanager.secretAccessor "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 15. secrets create jupyter-oauth-client-secret

조회:

```bash
gcloud secrets describe jupyter-oauth-client-secret "--project=${CICD_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud secrets create jupyter-oauth-client-secret "--project=${CICD_PROJECT}" --replication-policy=user-managed "--locations=${REGION}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 16. secrets add-iam-policy-binding jupyter-oauth-client-secret · roles/secretmanager.secretAccessor

실행:

```bash
gcloud secrets add-iam-policy-binding jupyter-oauth-client-secret "--project=${CICD_PROJECT}" "--member=serviceAccount:${TF_MANAGER}" --role=roles/secretmanager.secretAccessor "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 17. builds worker-pools create pool-sbxtest01

조회:

```bash
gcloud builds worker-pools describe pool-sbxtest01 "--project=${CICD_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud builds worker-pools create pool-sbxtest01 "--project=${CICD_PROJECT}" "--region=${REGION}" --worker-machine-type=e2-standard-4 --worker-disk-size=100 --no-public-egress "--peered-network=projects/${HOST_PROJECT}/global/networks/${NETWORK}" "--peered-network-ip-range=${PSA_CIDR}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 18. container clusters create-auto gke-sbx-main-an3

조회:

```bash
gcloud container clusters describe "${MAIN_CLUSTER}" "--project=${GKE_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"autopilot.enabled": true, "privateClusterConfig.enablePrivateNodes": true, "privateClusterConfig.enablePrivateEndpoint": true, "ipAllocationPolicy.clusterSecondaryRangeName": "pods-dev-sbx-gke-01-an3-main"}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud container clusters create-auto "${MAIN_CLUSTER}" "--project=${GKE_PROJECT}" "--region=${REGION}" "--network=projects/${HOST_PROJECT}/global/networks/${NETWORK}" "--subnetwork=projects/${HOST_PROJECT}/regions/${REGION}/subnetworks/${MAIN_SUBNET}" "--cluster-secondary-range-name=${MAIN_POD_RANGE}" --enable-private-nodes --enable-private-endpoint "--master-ipv4-cidr=${MAIN_CP_CIDR}" --enable-master-authorized-networks "--master-authorized-networks=${ADMIN_CIDR},${PSA_CIDR}" --enable-master-global-access --release-channel=regular "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 19. 선택 · container clusters create-auto gke-dev-cicd-01-an3

조회:

```bash
gcloud container clusters describe "${TEST_CLUSTER}" "--project=${CICD_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"autopilot.enabled": true, "privateClusterConfig.enablePrivateNodes": true, "privateClusterConfig.enablePrivateEndpoint": true, "ipAllocationPolicy.clusterSecondaryRangeName": "pods-dev-cicd-gke-01-an3-test"}`. 값이 다르면 중단합니다.

테스트 클러스터를 추가하는 경우에만 실행합니다. 기본 과제용 Main GKE만 사용하면 이 항목을 생략합니다.

없는 경우에만 생성:

```bash
gcloud container clusters create-auto "${TEST_CLUSTER}" "--project=${CICD_PROJECT}" "--region=${REGION}" "--network=projects/${HOST_PROJECT}/global/networks/${NETWORK}" "--subnetwork=projects/${HOST_PROJECT}/regions/${REGION}/subnetworks/${TEST_SUBNET}" "--cluster-secondary-range-name=${TEST_POD_RANGE}" --enable-private-nodes --enable-private-endpoint "--master-ipv4-cidr=${TEST_CP_CIDR}" --enable-master-authorized-networks "--master-authorized-networks=${ADMIN_CIDR},${PSA_CIDR}" --enable-master-global-access --release-channel=regular "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

Cloud Build의 선언형 입력 파일은 [`configs/bootstrap-build.yaml`](configs/bootstrap-build.yaml)입니다. Runner와 Provisioner 이미지 두 개를 빌드합니다. Python으로 생성하지 않습니다.

## 20. builds submit .

실행:

```bash
gcloud builds submit . "--project=${CICD_PROJECT}" "--region=${REGION}" "--service-account=projects/${CICD_PROJECT}/serviceAccounts/${TF_MANAGER}" "--gcs-source-staging-dir=gs://${CICD_PROJECT}-sbxtest01-build-source/source" --config=gcloud/configs/bootstrap-build.yaml "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

Cloud Run 환경변수는 [`configs/provisioner-env.yaml`](configs/provisioner-env.yaml)입니다. 비밀값은 포함하지 않습니다. 이 파일의 프로젝트·리전 값도 공통 변수와 일치해야 합니다.

## 21. run deploy run-sbxtest01-provisioner

실행:

```bash
gcloud run deploy run-sbxtest01-provisioner "--project=${CICD_PROJECT}" "--region=${REGION}" "--image=${REGION}-docker.pkg.dev/${CICD_PROJECT}/ar-sbxtest01-platform/run-sbxtest01-provisioner:bootstrap" "--service-account=${SBX_MANAGER}" --no-allow-unauthenticated --ingress=all --timeout=300 --max-instances=2 --env-vars-file=gcloud/configs/provisioner-env.yaml "--network=projects/${HOST_PROJECT}/global/networks/${NETWORK}" "--subnet=projects/${HOST_PROJECT}/regions/${REGION}/subnetworks/${RUN_SUBNET}" --vpc-egress=private-ranges-only "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 22. run services add-iam-policy-binding run-sbxtest01-provisioner · roles/run.invoker

실행:

```bash
gcloud run services add-iam-policy-binding run-sbxtest01-provisioner "--project=${CICD_PROJECT}" "--region=${REGION}" "--member=serviceAccount:${SBX_MANAGER}" --role=roles/run.invoker "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 23. run services describe run-sbxtest01-provisioner

실행:

```bash
gcloud run services describe run-sbxtest01-provisioner "--project=${CICD_PROJECT}" "--region=${REGION}" '--format=value(status.url)' "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## Workflow 입력 파일 준비

앞의 Cloud Run describe가 성공했고 URL이 비어 있지 않은지 확인한 뒤 URL 자리만 바꿉니다. 아래는 조회·파일 치환 명령이며 배포 실행기가 아닙니다. `${args}` 등 Workflows 표현식은 그대로 유지합니다.

```bash
export PROVISIONER_URL="$(gcloud run services describe run-sbxtest01-provisioner --project="${CICD_PROJECT}" --region="${REGION}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}" --format='value(status.url)')"
mkdir -p .local
sed "s|__PROVISIONER_URL__|${PROVISIONER_URL}|g" gcloud/configs/workflow.template.yaml > .local/workflow.yaml
```

## 24. workflows deploy workflow-sbxtest01-provision

실행:

```bash
gcloud workflows deploy workflow-sbxtest01-provision "--project=${CICD_PROJECT}" "--location=${REGION}" "--service-account=${SBX_MANAGER}" --source=.local/workflow.yaml "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 25. projects add-iam-policy-binding prj-b-cicd-local-236d · roles/workflows.invoker

실행:

```bash
gcloud projects add-iam-policy-binding "${CICD_PROJECT}" "--member=${OPERATOR_MEMBER}" --role=roles/workflows.invoker --condition=None "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 26. storage buckets add-iam-policy-binding gs://prj-b-cicd-local-236d-sbxtest01-requests · roles/storage.objectAdmin

실행:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CICD_PROJECT}-sbxtest01-requests" "--member=${OPERATOR_MEMBER}" --role=roles/storage.objectAdmin "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 27. storage buckets add-iam-policy-binding gs://prj-b-cicd-local-236d-sbxtest01-bundles · roles/storage.objectViewer

실행:

```bash
gcloud storage buckets add-iam-policy-binding "gs://${CICD_PROJECT}-sbxtest01-bundles" "--member=${OPERATOR_MEMBER}" --role=roles/storage.objectViewer "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 28. compute addresses create ip-alb-sbxtest01-shared

조회:

```bash
gcloud compute addresses describe ip-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute addresses create ip-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --global --ip-version=IPV4 "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 29. compute backend-services create bes-alb-sbxtest01-shared-default

조회:

```bash
gcloud compute backend-services describe bes-alb-sbxtest01-shared-default "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute backend-services create bes-alb-sbxtest01-shared-default "--project=${GKE_PROJECT}" --global --protocol=HTTP --load-balancing-scheme=EXTERNAL "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 30. compute url-maps create urlmap-alb-sbxtest01-shared

조회:

```bash
gcloud compute url-maps describe urlmap-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute url-maps create urlmap-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --global --default-service=bes-alb-sbxtest01-shared-default "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 31. compute target-http-proxies create http-proxy-alb-sbxtest01-shared

조회:

```bash
gcloud compute target-http-proxies describe http-proxy-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute target-http-proxies create http-proxy-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --url-map=urlmap-alb-sbxtest01-shared "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 32. compute forwarding-rules create fr-alb-sbxtest01-shared-http

조회:

```bash
gcloud compute forwarding-rules describe fr-alb-sbxtest01-shared-http "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute forwarding-rules create fr-alb-sbxtest01-shared-http "--project=${GKE_PROJECT}" --global --load-balancing-scheme=EXTERNAL --address=ip-alb-sbxtest01-shared --target-http-proxy=http-proxy-alb-sbxtest01-shared --ports=80 "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 33. compute ssl-certificates describe cert-jupyter-sbx01-self

확인:

```bash
gcloud compute ssl-certificates describe "${SSL_CERTIFICATE}" "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 34. compute target-https-proxies create https-proxy-alb-sbxtest01-shared

조회:

```bash
gcloud compute target-https-proxies describe https-proxy-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute target-https-proxies create https-proxy-alb-sbxtest01-shared "--project=${GKE_PROJECT}" --url-map=urlmap-alb-sbxtest01-shared "--ssl-certificates=${SSL_CERTIFICATE}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 35. compute forwarding-rules create fr-alb-sbxtest01-shared-https

조회:

```bash
gcloud compute forwarding-rules describe fr-alb-sbxtest01-shared-https "--project=${GKE_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud compute forwarding-rules create fr-alb-sbxtest01-shared-https "--project=${GKE_PROJECT}" --global --load-balancing-scheme=EXTERNAL --address=ip-alb-sbxtest01-shared --target-https-proxy=https-proxy-alb-sbxtest01-shared --ports=443 "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 36. 선택 · builds triggers create github

Cloud Build GitHub App에 새 저장소 연결을 승인했고 자동 릴리스가 필요한 경우에만 실행합니다. 필요 없으면 이 항목 전체를 생략합니다.

조회:

```bash
gcloud builds triggers describe trigger-sbxtest01-platform-release "--project=${CICD_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

없는 경우에만 생성:

```bash
gcloud builds triggers create github --name=trigger-sbxtest01-platform-release "--project=${CICD_PROJECT}" "--region=${REGION}" --repo-owner=sonmap --repo-name=GCP_SBX_Test01 "--branch-pattern=^main$" --build-config=cloudbuild/platform-release.yaml "--service-account=projects/${CICD_PROJECT}/serviceAccounts/${TF_MANAGER}" '--substitutions=_RELEASE_ID=git-$SHORT_SHA,_COMMIT_SHA=$COMMIT_SHA' "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 다음 작업

OAuth Secret 값 등록 → Workspace DWD 승인 확인 → 플랫폼 릴리스 → Chart/이미지 미러링 → Notebook 표준 이미지 빌드 → 승인 요청 실행은 [실행 절차](../docs/runbook-two-stage.md)를 따릅니다. HTTPS 인증서는 기존 SSL 리소스를 참조하며 PEM/키는 Git에 넣지 않습니다. 인증서 조회가 Not Found이면 HTTPS Proxy/443 Forwarding Rule 명령을 실행하지 말고 인증서부터 별도 등록합니다.
