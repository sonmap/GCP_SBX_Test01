# 사용자 Notebook 표준 이미지

`Dockerfile`은 내부 sample Notebook 이미지에 gcloud/git/jq와 pandas/pyarrow/BigQuery/GCS 라이브러리를 추가합니다. `cloudbuild.yaml`로 빌드하고 `build-gcloud.sh`로 제출합니다. 모든 Build는 tf-manager를 명시적으로 사용합니다.

미러링 후 다음 명령으로 빌드합니다.

```bash
CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT=tf-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com bash 04.Jupiter-setup-image/build-gcloud.sh
```

이미지: `asia-northeast3-docker.pkg.dev/prj-b-cicd-local-236d/ar-sbxtest01-platform/jupyterhub-k8s-singleuser-standard:4.2.0-r1-test`.

이 이미지는 apply_gke_workload.py가 새 사용자 Pod에 지정합니다. 이미 실행 중인 Pod는 자동 교체되지 않습니다. 이미지 적용 테스트에서 사용자 PVC를 삭제하지 않습니다. `/home/jovyan`의 PVC 데이터와 컨테이너의 설치 프로그램은 별도입니다. Notebook KSA는 중앙 sbx-manager를 사용하므로 이 버전은 과제별 IAM 격리가 없는 PoC용입니다.
