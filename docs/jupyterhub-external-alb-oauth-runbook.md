# Jupyter 접속 경로와 OAuth

`sandbox_setup_01_gcloud/03-foundation.md`의 개별 명령이 공통 Classic External ALB `alb-sbxtest01-shared`를 생성합니다. 기존 SSL 인증서 리소스를 이름으로 참조하며 인증서/키를 Git에 저장하지 않습니다.

과제 배포의 `sandbox_gke_deployer/reconcile_postdeploy.py`가 과제별 Health Check/Backend를 만들고 NEG를 붙인 뒤 공통 URL Map `urlmap-alb-sbxtest01-shared`에 Host 경로를 추가합니다. GKE Service는 ClusterIP이며 GKE API는 private endpoint를 사용합니다. ALB 사용자 접속은 외부 경로입니다.

1. `sandbox_deploy_tools/set-jupyter-oauth-secrets.sh`로 OAuth Client ID/Secret을 Secret Manager에 등록합니다.
2. Google OAuth 설정에 `https://<도메인>/hub/oauth_callback`을 등록하고, 해당 도메인의 DNS/PoC hosts 파일을 공통 ALB IP로 연결합니다.

Backend HEALTHY, 인증서 도메인, OAuth 허용 사용자, KSA→sbx-manager 연결 순으로 확인합니다. 공유 계정에 따른 권한 범위는 architecture-and-operations.md를 참고합니다.
