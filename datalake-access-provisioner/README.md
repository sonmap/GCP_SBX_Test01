# 데이터레이크 조회 권한 자동화

pjt-c-admin의 BigQuery Dataset에 GSA/User/Group의 조회 권한을 부여/회수합니다. 기존 Dataset ACL을 유지하면서 요청 Principal만 변경합니다. Job 실행 권한은 별도로 관리합니다.

| 파일 | 역할 |
|---|---|
| main.py | GCS pending/ 요청 검증, GRANT/REVOKE, results/ 기록 |
| Dockerfile · requirements.txt | Cloud Run 실행 이미지·라이브러리 |
| cloudbuild.yaml | 이미지 빌드 |
| deploy-gcloud.sh | IAM·Cloud Run·5분 Scheduler 배포 |
| examples/request-sbx01.json | Dataset·Principal·조회 권한 요청 예시 |

Bootstrap의 두 SA가 먼저 존재해야 합니다. 이 스크립트는 새 SA를 생성하지 않습니다.

- Runtime와 Scheduler: sbx-manager
- Cloud Build: tf-manager (명시적 --service-account)
- Data Lake: sbx-manager에 Dataset get/update만 가진 custom role 추가
- 요청/결과 Bucket: sbx-manager objectViewer/objectCreator

```bash
bash datalake-access-provisioner/deploy-gcloud.sh
```

별도 배포는 서비스/Role/프로젝트 IAM 변경 권한이 있는 관리자로 실행합니다. Scheduler SA의 actAs 권한과 Cloud Run runtime SA actAs 권한이 필요합니다. Cloud Run은 익명 호출을 허용하지 않지만 ingress=all이므로 네트워크 수준 private ingress 서비스는 아닙니다. Scheduler는 OIDC로 인증합니다.

요청을 검토·승인한 뒤 업로드합니다.

```bash
gcloud storage cp datalake-access-provisioner/examples/request-sbx01.json gs://prj-b-cicd-local-236d-datalake-access-requests/pending/request-sbx01.json
gcloud scheduler jobs run datalake-access-provisioner-5m --project=prj-b-cicd-local-236d --location=asia-northeast3
gcloud storage ls gs://prj-b-cicd-local-236d-datalake-access-requests/results/
```

같은 Object Generation은 중복 처리하지 않습니다. 수정 재처리는 새 Generation으로 올립니다. 여러 Notebook이 같은 sbx-manager를 공유하므로 한 과제에 부여한 GSA 조회 권한을 다른 과제 Notebook도 사용할 수 있습니다.
