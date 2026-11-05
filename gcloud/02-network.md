# 2. 공통 네트워크 — 개별 gcloud 명령

1단계 완료 후 tf-manager를 impersonation합니다. 기존 자원을 조회하고 없는 항목만 생성합니다.

먼저 [공통 변수](00-variables.md)를 같은 터미널에 설정합니다. 각 코드 블록을 **한 개씩** 실행하고 결과를 확인합니다. 전체 실행 스크립트나 Python 호출은 없습니다.

**조회와 생성은 별도입니다.** 조회 성공 시 기대값을 확인하고 바로 다음 생성 명령은 건너뜁니다. 명시적 Not Found일 때만 생성합니다. 403·인증·연결 오류는 미존재가 아니므로 중단합니다. 명령은 실제 작업이며 `--apply`/미리보기 모드가 없습니다.

## 기존 대역 먼저 확인

서브넷 Primary/Secondary 대역과 Control Plane·PSA 대역이 겹치지 않는지 비교합니다. 기존 설정이 다르면 생성/갱신 명령을 실행하지 말고 중단합니다. Main/Test Subnet은 secondaryIpRanges의 rangeName과 ipCidrRange도 공통 변수의 Pod Range/CIDR와 일치해야 합니다.

```bash
gcloud compute networks subnets list "--project=${HOST_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

Shared VPC `get-host-project`가 현재 Host를 반환하면 연결 명령은 건너뜁니다. 다른 Host면 중단합니다. PSA는 기존 연결에 설정된 예약 Range를 확인하고, 이미 연결되어 있으면 connect를 건너뜁니다.

## 1. compute networks create vpc-d-shared-base

조회:

```bash
gcloud compute networks describe "${NETWORK}" "--project=${HOST_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"autoCreateSubnetworks": false}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute networks create "${NETWORK}" "--project=${HOST_PROJECT}" --subnet-mode=custom "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 2. compute shared-vpc get-host-project pjt-d-shared-base

확인:

```bash
gcloud compute shared-vpc get-host-project "${HOST_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 3. compute shared-vpc enable pjt-d-shared-base

실행:

```bash
gcloud compute shared-vpc enable "${HOST_PROJECT}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 4. compute shared-vpc get-host-project pjt-d-host01

확인:

```bash
gcloud compute shared-vpc get-host-project "${GKE_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 5. compute shared-vpc associated-projects add pjt-d-host01

실행:

```bash
gcloud compute shared-vpc associated-projects add "${GKE_PROJECT}" "--host-project=${HOST_PROJECT}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 6. compute shared-vpc get-host-project prj-b-cicd-local-236d

확인:

```bash
gcloud compute shared-vpc get-host-project "${CICD_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 7. compute shared-vpc associated-projects add prj-b-cicd-local-236d

실행:

```bash
gcloud compute shared-vpc associated-projects add "${CICD_PROJECT}" "--host-project=${HOST_PROJECT}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 8. compute networks subnets create subnet-dev-sbx-gke-01-an3-main

조회:

```bash
gcloud compute networks subnets describe "${MAIN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"ipCidrRange": "10.252.0.0/24", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute networks subnets create "${MAIN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" "--network=${NETWORK}" "--range=${MAIN_NODE_CIDR}" --enable-private-ip-google-access "--secondary-range=${MAIN_POD_RANGE}=${MAIN_POD_CIDR}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 9. compute networks subnets update subnet-dev-sbx-gke-01-an3-main

실행:

```bash
gcloud compute networks subnets update "${MAIN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 10. 선택 · compute networks subnets create subnet-dev-cicd-gke-01-an3-test

조회:

```bash
gcloud compute networks subnets describe "${TEST_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"ipCidrRange": "10.252.1.0/26", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"}`. 값이 다르면 중단합니다.

테스트 클러스터를 추가하는 경우에만 실행합니다. 기본 과제용 Main GKE만 사용하면 이 항목을 생략합니다.

없는 경우에만 생성:

```bash
gcloud compute networks subnets create "${TEST_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" "--network=${NETWORK}" "--range=${TEST_NODE_CIDR}" --enable-private-ip-google-access "--secondary-range=${TEST_POD_RANGE}=${TEST_POD_CIDR}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 11. 선택 · compute networks subnets update subnet-dev-cicd-gke-01-an3-test

테스트 클러스터용 서브넷을 사용하는 경우에만 실행합니다.

실행:

```bash
gcloud compute networks subnets update "${TEST_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 12. compute networks subnets create subnet-dev-cicd-run-01-an3-egress

조회:

```bash
gcloud compute networks subnets describe "${RUN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"ipCidrRange": "10.251.0.0/26", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute networks subnets create "${RUN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" "--network=${NETWORK}" "--range=${RUN_CIDR}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 13. compute networks subnets update subnet-dev-cicd-run-01-an3-egress

실행:

```bash
gcloud compute networks subnets update "${RUN_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 14. compute networks subnets create subnet-sbx01-an3

조회:

```bash
gcloud compute networks subnets describe "${TASK_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"ipCidrRange": "172.31.110.0/24", "network": "https://www.googleapis.com/compute/v1/projects/pjt-d-shared-base/global/networks/vpc-d-shared-base"}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute networks subnets create "${TASK_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" "--network=${NETWORK}" "--range=${TASK_CIDR}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 15. compute networks subnets update subnet-sbx01-an3

실행:

```bash
gcloud compute networks subnets update "${TASK_SUBNET}" "--project=${HOST_PROJECT}" "--region=${REGION}" --enable-private-ip-google-access "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 16. compute addresses create prip-dev-cicd-cbp-01-an3-psa

조회:

```bash
gcloud compute addresses describe "${PSA_NAME}" "--project=${HOST_PROJECT}" --global --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"address": "10.250.0.0", "prefixLength": 24, "purpose": "VPC_PEERING"}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute addresses create "${PSA_NAME}" "--project=${HOST_PROJECT}" --global --purpose=VPC_PEERING "--addresses=${PSA_ADDRESS}" --prefix-length="${PSA_PREFIX_LENGTH}" "--network=projects/${HOST_PROJECT}/global/networks/${NETWORK}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 17. services vpc-peerings list

확인:

```bash
gcloud services vpc-peerings list "--project=${HOST_PROJECT}" "--network=${NETWORK}" --service=servicenetworking.googleapis.com --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 18. services vpc-peerings connect

실행:

```bash
gcloud services vpc-peerings connect "--project=${HOST_PROJECT}" "--network=${NETWORK}" --service=servicenetworking.googleapis.com "--ranges=${PSA_NAME}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

## 19. compute firewall-rules create fw-sbxtest01-alb-hc

조회:

```bash
gcloud compute firewall-rules describe fw-sbxtest01-alb-hc "--project=${HOST_PROJECT}" --format=json "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```

기존 자원 확인값: `{"sourceRanges": ["35.191.0.0/16", "130.211.0.0/22"], "destinationRanges": ["10.240.0.0/20"]}`. 값이 다르면 중단합니다.

없는 경우에만 생성:

```bash
gcloud compute firewall-rules create fw-sbxtest01-alb-hc "--project=${HOST_PROJECT}" "--network=${NETWORK}" --direction=INGRESS --allow=tcp:8000 --source-ranges=35.191.0.0/16,130.211.0.0/22 "--destination-ranges=${MAIN_POD_CIDR}" "--account=${ADMIN_ACCOUNT}" "--impersonate-service-account=${TF_MANAGER}"
```
