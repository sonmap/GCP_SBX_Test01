# GKE Sandbox 실행 안내

관리 VM `infra-son01`에서 **처음에는 1차**, 공통 기반이 이미 있으면 **2차**부터 진행합니다.

| 할 일 | 이 문서부터 열기 |
|---|---|
| **1차 · 공통 인프라 구축** | [1차 인프라 구축](01-infra-setup.md) — 계정·네트워크·GKE·Private Pool·배포 서비스와 HTTPS 준비 |
| **2차 · sbx03 Sandbox 배포** | [2차 Sandbox 배포](02-sandbox-deploy.md) — 승인 요청 확인, Workflow 제출, 빌드·Notebook 확인 |
| **GKE 삭제 후 다시 시험** | [sbx03 재시험 절차](sbx03-new-project-runbook.md#6-실제-작업-기록과-다음-테스트-순서) — 백업·클러스터 복구·동일 과제 재배포 |

<details>
<summary>상세 절차와 참고 문서</summary>

- [전체 실행 절차](runbook-two-stage.md) · [실환경 개별 명령](operator-command-guide.md) · [작업 순서](work-order.md)
- [폴더·파일 Mermaid 구성도](file-relationships.md) · [파일별 역할](file-catalog.md)
- [Private Pool GKE 접속 점검](cloudbuild-private-gke-vpn-design.md) · [Workspace 그룹 관리자 승인](cloud-identity-group-terraform.md)
- [HTTPS·인증서](sbx03-https-certificate-runbook.md) · [Google OAuth](sbx03-google-oauth-runbook.md)

</details>
