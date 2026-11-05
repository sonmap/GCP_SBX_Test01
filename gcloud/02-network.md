# 2. 공통 네트워크 — 주석으로 통합한 gcloud 명령

필요한 변수 선언을 아래 코드 블록 맨 앞에 포함했습니다. 별도 문서에서 변수를 설정할 필요 없이, 이 문서의 선언부터 같은 터미널에서 실행합니다. `# 주석`을 보며 순서대로 실행하고, **기존 자원이 있으면 해당 생성 명령을 건너뜁니다.** 403·인증·연결 오류면 중단합니다. 선택 작업은 주석을 해제한 경우에만 실행합니다.

```bash
# ── 이 문서에서 사용하는 변수 선언 ──
# 아래 값을 확인하고 이 블록부터 같은 터미널에서 실행합니다.
unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT
export ADMIN_ACCOUNT=admin@sonmap.net
export CICD_PROJECT=prj-b-cicd-local-236d
export HOST_PROJECT=pjt-d-shared-base
export GKE_PROJECT=pjt-d-host01
export REGION=asia-northeast3
export NETWORK=vpc-d-shared-base
export MAIN_SUBNET=subnet-dev-sbx-gke-01-an3-main
export MAIN_NODE_CIDR=10.252.0.0/24
export MAIN_POD_RANGE=pods-dev-sbx-gke-01-an3-main
export MAIN_POD_CIDR=10.240.0.0/20
export TEST_SUBNET=subnet-dev-cicd-gke-01-an3-test
export TEST_NODE_CIDR=10.252.1.0/26
export TEST_POD_RANGE=pods-dev-cicd-gke-01-an3-test
export TEST_POD_CIDR=10.240.32.0/22
export RUN_SUBNET=subnet-dev-cicd-run-01-an3-egress
export RUN_CIDR=10.251.0.0/26
export TASK_SUBNET=subnet-sbx01-an3
export TASK_CIDR=172.31.110.0/24
export PSA_NAME=prip-dev-cicd-cbp-01-an3-psa
export TF_MANAGER="tf-manager@${CICD_PROJECT}.iam.gserviceaccount.com"
export PSA_ADDRESS="10.250.0.0"
export PSA_PREFIX_LENGTH="24"
# 이 값들은 1·2·3단계에서 동일하게 사용합니다.

# 먼저 기존 Primary/Secondary 대역을 확인합니다.
# Node · Pod · Control Plane · PSA 대역이 겹치거나 기존 설정과 다르면 중단합니다.

# ── 기존 대역 먼저 확인 ──
gcloud compute networks subnets list --project="${HOST_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 1. compute networks create vpc-d-shared-base ──
# 기존 자원 확인
gcloud compute networks describe "${NETWORK}" --project="${HOST_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"autoCreateSubnetworks": false} — 다르면 중단합니다.
gcloud compute networks create "${NETWORK}" --project="${HOST_PROJECT}" --subnet-mode=custom --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 2. compute shared-vpc get-host-project pjt-d-shared-base ──
# 기존 자원 확인
gcloud compute shared-vpc get-host-project "${HOST_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 3. compute shared-vpc enable pjt-d-shared-base ──
# 앞의 조회에서 이미 같은 Host에 연결되어 있으면 아래 명령은 건너뜁니다. 다른 Host면 중단합니다.
gcloud compute shared-vpc enable "${HOST_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 4. compute shared-vpc get-host-project pjt-d-host01 ──
# 기존 자원 확인
gcloud compute shared-vpc get-host-project "${GKE_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 5. compute shared-vpc associated-projects add pjt-d-host01 ──
# 앞의 조회에서 이미 같은 Host에 연결되어 있으면 아래 명령은 건너뜁니다. 다른 Host면 중단합니다.
gcloud compute shared-vpc associated-projects add "${GKE_PROJECT}" --host-project="${HOST_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 6. compute shared-vpc get-host-project prj-b-cicd-local-236d ──
# 기존 자원 확인
gcloud compute shared-vpc get-host-project "${CICD_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 7. compute shared-vpc associated-projects add prj-b-cicd-local-236d ──
# 앞의 조회에서 이미 같은 Host에 연결되어 있으면 아래 명령은 건너뜁니다. 다른 Host면 중단합니다.
gcloud compute shared-vpc associated-projects add "${CICD_PROJECT}" --host-project="${HOST_PROJECT}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 8. compute networks subnets create subnet-dev-sbx-gke-01-an3-main ──
# 기존 자원 확인
gcloud compute networks subnets describe "${MAIN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"ipCidrRange": "10.252.0.0/24", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"} — 다르면 중단합니다.
gcloud compute networks subnets create "${MAIN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --network="${NETWORK}" --range="${MAIN_NODE_CIDR}" --enable-private-ip-google-access --secondary-range="${MAIN_POD_RANGE}=${MAIN_POD_CIDR}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 9. compute networks subnets update subnet-dev-sbx-gke-01-an3-main ──
gcloud compute networks subnets update "${MAIN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 10. 선택 · compute networks subnets create subnet-dev-cicd-gke-01-an3-test ──
# 선택 작업: 필요한 경우에만 아래 명령의 주석을 해제합니다.
# 기존 자원 확인
# gcloud compute networks subnets describe "${TEST_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"ipCidrRange": "10.252.1.0/26", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"} — 다르면 중단합니다.
# gcloud compute networks subnets create "${TEST_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --network="${NETWORK}" --range="${TEST_NODE_CIDR}" --enable-private-ip-google-access --secondary-range="${TEST_POD_RANGE}=${TEST_POD_CIDR}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 11. 선택 · compute networks subnets update subnet-dev-cicd-gke-01-an3-test ──
# 선택 작업: 필요한 경우에만 아래 명령의 주석을 해제합니다.
# gcloud compute networks subnets update "${TEST_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 12. compute networks subnets create subnet-dev-cicd-run-01-an3-egress ──
# 기존 자원 확인
gcloud compute networks subnets describe "${RUN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"ipCidrRange": "10.251.0.0/26", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"} — 다르면 중단합니다.
gcloud compute networks subnets create "${RUN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --network="${NETWORK}" --range="${RUN_CIDR}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 13. compute networks subnets update subnet-dev-cicd-run-01-an3-egress ──
gcloud compute networks subnets update "${RUN_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 14. compute networks subnets create subnet-sbx01-an3 ──
# 기존 자원 확인
gcloud compute networks subnets describe "${TASK_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"ipCidrRange": "172.31.110.0/24", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"} — 다르면 중단합니다.
gcloud compute networks subnets create "${TASK_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --network="${NETWORK}" --range="${TASK_CIDR}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 15. compute networks subnets update subnet-sbx01-an3 ──
gcloud compute networks subnets update "${TASK_SUBNET}" --project="${HOST_PROJECT}" --region="${REGION}" --enable-private-ip-google-access --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 16. compute addresses create prip-dev-cicd-cbp-01-an3-psa ──
# 기존 자원 확인
gcloud compute addresses describe "${PSA_NAME}" --project="${HOST_PROJECT}" --global --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"address": "10.250.0.0", "prefixLength": 24, "purpose": "VPC_PEERING"} — 다르면 중단합니다.
gcloud compute addresses create "${PSA_NAME}" --project="${HOST_PROJECT}" --global --purpose=VPC_PEERING --addresses="${PSA_ADDRESS}" --prefix-length="${PSA_PREFIX_LENGTH}" --network="projects/${HOST_PROJECT}/global/networks/${NETWORK}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 17. services vpc-peerings list ──
# 기존 자원 확인
gcloud services vpc-peerings list --project="${HOST_PROJECT}" --network="${NETWORK}" --service=servicenetworking.googleapis.com --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 18. services vpc-peerings connect ──
# 앞의 조회에 PSA Range 연결이 이미 있으면 건너뜁니다. 기존 Range를 덮어쓰지 않습니다.
gcloud services vpc-peerings connect --project="${HOST_PROJECT}" --network="${NETWORK}" --service=servicenetworking.googleapis.com --ranges="${PSA_NAME}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"

# ── 19. compute firewall-rules create fw-sbxtest01-alb-hc ──
# 기존 자원 확인
gcloud compute firewall-rules describe fw-sbxtest01-alb-hc --project="${HOST_PROJECT}" --format=json --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
# 조회 결과가 명시적 Not Found일 때만 아래 생성 명령을 실행합니다.
# 기존 자원 확인값: {"sourceRanges": ["35.191.0.0/16", "130.211.0.0/22"], "destinationRanges": ["10.240.0.0/20"]} — 다르면 중단합니다.
gcloud compute firewall-rules create fw-sbxtest01-alb-hc --project="${HOST_PROJECT}" --network="${NETWORK}" --direction=INGRESS --allow=tcp:8000 --source-ranges=35.191.0.0/16,130.211.0.0/22 --destination-ranges="${MAIN_POD_CIDR}" --account="${ADMIN_ACCOUNT}" --impersonate-service-account="${TF_MANAGER}"
```
