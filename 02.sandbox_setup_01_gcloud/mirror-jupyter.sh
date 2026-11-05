#!/usr/bin/env bash
# Fully-managed Cloud Build intentionally downloads public upstream images/chart.
set -euo pipefail
SBX_GKE_PROJECT="${SBX_GKE_PROJECT:-pjt-d-host01}"
cd "$(dirname "$0")/.."
l2comn_PROJECT=prj-b-cicd-local-236d
REGION=asia-northeast3
SA="tf-manager@${SBX_GKE_PROJECT}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${l2comn_PROJECT}/ar-sbxtest01-platform/sbxtest01-automation-runner:bootstrap"
for name in chart images; do
  CMD=(gcloud builds submit --no-source --project="$l2comn_PROJECT" --region="$REGION"
    --impersonate-service-account="$SA"
    --service-account="projects/${SBX_GKE_PROJECT}/serviceAccounts/${SA}"
    --config="03.cloudbuild/mirror-jupyterhub-${name}.yaml"
    --substitutions="_AUTOMATION_IMAGE=${IMAGE}")
  if [[ "${1:-}" == '--apply' ]]; then
    "${CMD[@]}"
  else
    printf '%q ' "${CMD[@]}"
    printf '\n'
  fi
done
