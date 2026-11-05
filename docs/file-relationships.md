# 폴더와 파일 관계

실선은 실행/호출, 점선은 설정/소스 참조입니다. 1~3단계는 모두 gcloud입니다.

```mermaid
flowchart TD
  CFG["sandbox_setup_01_gcloud/00-variables.md"] -.-> A["sandbox_setup_01_gcloud/01-admin.md: 개별 gcloud"]
  CFG -.-> N["sandbox_setup_01_gcloud/02-network.md: 개별 gcloud"]
  CFG -.-> F["sandbox_setup_01_gcloud/03-foundation.md: 개별 gcloud"]
  Y["sandbox_setup_01_gcloud/configs/: YAML 입력 파일"] -.-> F
  A --> N
  N --> F
  F --> REL["sandbox_setup_01_gcloud/release.sh"]
  REL --> YAML["cloudbuild/platform-release.yaml"]
  YAML --> RD["sandbox_gke_deployer/Dockerfile"]
  YAML --> PD["sandbox_request_api/Dockerfile"]
  YAML --> ZIP["sandbox_deploy_tools/publish-sandbox-source.sh"]
  ZIP --> SRC["GCS 플랫폼 소스 ZIP·release.json"]
  RD --> AR["Artifact Registry"]
  PD --> AR
  SRC --> SET["sandbox_deploy_tools/set-request-release.py"]
  EX["sandbox_json/sbx01-approved-request.json"] --> SET
  SET --> APPROVED["검토·승인된 요청 JSON"]
```

```mermaid
flowchart TD
  REQ["승인 JSON"] --> SEND["sandbox_deploy_tools/run-approved-workflow.sh"]
  SEND --> STORE["GCS 승인 요청"]
  SEND --> WF["Workflows: sbx-manager"]
  WF --> API["sandbox_request_api/main.py: sbx-manager"]
  STORE --> API
  SCHEMA["sandbox_request_api/sandbox-request.schema.json"] -.-> API
  REF["sandbox_json_rules/sandbox-request.schema.json: 참고 사본"] -.-> SCHEMA
  SOURCE["GCS 플랫폼 소스 ZIP"] -.-> API
  API --> BUNDLE["과제별 배포 ZIP"]
  BUNDLE --> BUILD["동적 Cloud Build: tf-manager"]
  BUILD --> GRP["sandbox_gke_deployer/group_upsert.py"]
  GRP --> IM["Infrastructure Manager: tf-manager"]
  IM --> T1["sandbox_setup_02_terraform/deployments/10-project/"]
  T1 --> T2["20-network/: 선택적"]
  T2 --> T3["30-project-iam/"]
  T3 --> T4["40-data/"]
  T4 --> RUN["자식 Cloud Build Private Pool: tf-manager"]
  RUN --> K8S["sandbox_gke_deployer/apply_gke_workload.py"]
  K8S --> LB["sandbox_gke_deployer/reconcile_postdeploy.py"]
  LB --> USER["Jupyter Notebook·공통 ALB 경로"]
  USER -.-> GSA["KSA → sbx-manager"]
```

```mermaid
flowchart TD
  M["sandbox_setup_01_gcloud/mirror-jupyter.sh"] --> MC["cloudbuild/mirror-jupyterhub-chart.yaml"]
  M --> MI["cloudbuild/mirror-jupyterhub-images.yaml"]
  MC --> AR["Artifact Registry: Chart·기본 이미지"]
  MI --> AR
  AR -.-> JD["Jupiter-setup-image/Dockerfile"]
  JB["Jupiter-setup-image/build-gcloud.sh"] --> JY["Jupiter-setup-image/cloudbuild.yaml"]
  JY --> JD
  JD --> IMG["표준 사용자 Notebook 이미지"]
  IMG --> POD["Notebook Pod"]
  SEC["sandbox_deploy_tools/set-jupyter-oauth-secrets.sh"] --> SM["Secret Manager"]
  SM -.-> K["apply_gke_workload.py"]
  IMG -.-> K
```


각 Terraform 폴더의 main.tf/variables.tf/versions.tf는 함께 읽습니다. 최초 기반용 Terraform 00-admin/00-network-host/01-foundation과 중복 배포 경로는 제거했습니다. sandbox_deploy_tools/group_upsert.py는 Runner 안의 동일 파일과 동기화해 유지합니다.
