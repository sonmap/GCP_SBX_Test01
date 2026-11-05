# 폴더와 파일 관계

실선은 실행/호출, 점선은 설정/소스 참조입니다. 1~3단계는 모두 gcloud입니다.

```mermaid
flowchart TD
  CFG["gcloud/00-variables.md"] -.-> A["gcloud/01-admin.md: 개별 gcloud"]
  CFG -.-> N["gcloud/02-network.md: 개별 gcloud"]
  CFG -.-> F["gcloud/03-foundation.md: 개별 gcloud"]
  Y["gcloud/configs/: YAML 입력 파일"] -.-> F
  A --> N
  N --> F
  F --> REL["gcloud/release.sh"]
  REL --> YAML["cloudbuild/platform-release.yaml"]
  YAML --> RD["automation-runner/Dockerfile"]
  YAML --> PD["cloudrun-provisioner/Dockerfile"]
  YAML --> ZIP["scripts/publish-sandbox-source.sh"]
  ZIP --> SRC["GCS 플랫폼 소스 ZIP·release.json"]
  RD --> AR["Artifact Registry"]
  PD --> AR
  SRC --> SET["scripts/set-request-release.py"]
  EX["examples/sbx01-approved-request.json"] --> SET
  SET --> APPROVED["검토·승인된 요청 JSON"]
```

```mermaid
flowchart TD
  REQ["승인 JSON"] --> SEND["scripts/run-approved-workflow.sh"]
  SEND --> STORE["GCS 승인 요청"]
  SEND --> WF["Workflows: sbx-manager"]
  WF --> API["cloudrun-provisioner/main.py: sbx-manager"]
  STORE --> API
  SCHEMA["cloudrun-provisioner/sandbox-request.schema.json"] -.-> API
  REF["schemas/sandbox-request.schema.json: 참고 사본"] -.-> SCHEMA
  SOURCE["GCS 플랫폼 소스 ZIP"] -.-> API
  API --> BUNDLE["과제별 배포 ZIP"]
  BUNDLE --> BUILD["동적 Cloud Build: tf-manager"]
  BUILD --> GRP["automation-runner/group_upsert.py"]
  GRP --> IM["Infrastructure Manager: tf-manager"]
  IM --> T1["terraform/02-sandbox/deployments/10-project/"]
  T1 --> T2["20-network/: 선택적"]
  T2 --> T3["30-project-iam/"]
  T3 --> T4["40-data/"]
  T4 --> RUN["자식 Cloud Build Private Pool: tf-manager"]
  RUN --> K8S["automation-runner/apply_gke_workload.py"]
  K8S --> LB["automation-runner/reconcile_postdeploy.py"]
  LB --> USER["Jupyter Notebook·공통 ALB 경로"]
  USER -.-> GSA["KSA → sbx-manager"]
```

```mermaid
flowchart TD
  M["gcloud/mirror-jupyter.sh"] --> MC["cloudbuild/mirror-jupyterhub-chart.yaml"]
  M --> MI["cloudbuild/mirror-jupyterhub-images.yaml"]
  MC --> AR["Artifact Registry: Chart·기본 이미지"]
  MI --> AR
  AR -.-> JD["jupyter-singleuser-standard/Dockerfile"]
  JB["jupyter-singleuser-standard/build-gcloud.sh"] --> JY["jupyter-singleuser-standard/cloudbuild.yaml"]
  JY --> JD
  JD --> IMG["표준 사용자 Notebook 이미지"]
  IMG --> POD["Notebook Pod"]
  SEC["scripts/set-jupyter-oauth-secrets.sh"] --> SM["Secret Manager"]
  SM -.-> K["apply_gke_workload.py"]
  IMG -.-> K
```

```mermaid
flowchart TD
  DEP["datalake-access-provisioner/deploy-gcloud.sh"] --> Y["cloudbuild.yaml: tf-manager"]
  Y --> D["Dockerfile·requirements.txt"]
  D --> R["Cloud Run main.py: sbx-manager"]
  DEP --> S["Scheduler: sbx-manager"]
  S -->|"5분"| R
  E["examples/request-sbx01.json"] --> P["GCS pending/"]
  P --> R
  R --> ACL["BigQuery Dataset ACL"]
  R --> RESULT["GCS results/"]
```

각 Terraform 폴더의 main.tf/variables.tf/versions.tf는 함께 읽습니다. 최초 기반용 Terraform 00-admin/00-network-host/01-foundation과 중복 배포 경로는 제거했습니다. scripts/group_upsert.py는 Runner 안의 동일 파일과 동기화해 유지합니다.
