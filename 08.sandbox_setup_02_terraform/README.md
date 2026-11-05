# 과제별 Infrastructure Manager Terraform

최초 1~3단계는 `02.sandbox_setup_01_gcloud/01-admin.md`·`02-network.md`·`03-foundation.md`의 개별 명령으로 이전했습니다. 여기는 과제별 자원만 남깁니다.

| Root | 기능 | 실행 계정 |
|---|---|---|
| deployments/10-project | 신규/기존 프로젝트와 API·자동화 IAM | tf-manager |
| deployments/20-network | 선택적 과제 서브넷·Shared VPC 연결 | tf-manager |
| deployments/30-project-iam | 과제 Google Group 프로젝트 권한 | tf-manager |
| deployments/40-data | Dataset·Bucket·중앙 GSA 접근·Workload Identity | tf-manager |

중앙 `sbx-manager`는 data source로 조회합니다. 이 Terraform은 GSA를 생성하지 않습니다. 기존 자원 채택 옵션은 Dataset/Bucket만 import합니다.

각 Root는 `sbxtest01-<task>-<project-hash>-<stage>` Infrastructure Manager Deployment에서 독립 State로 관리합니다. VM에서 직접 terraform apply하지 않습니다. Kubernetes와 ALB 연결은 Cloud Build Runner가 처리합니다.
