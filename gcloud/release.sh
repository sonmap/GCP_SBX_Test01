#!/usr/bin/env bash
# Run after bootstrap. No GCP calls occur unless --apply is supplied.
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT=prj-b-cicd-local-236d
REGION=asia-northeast3
BUILD_SA="projects/${PROJECT}/serviceAccounts/tf-manager@${PROJECT}.iam.gserviceaccount.com"
COMMIT="$(git rev-parse HEAD)"
RELEASE_ID="git-${COMMIT:0:12}"
if [[ -n "$(git status --porcelain)" ]]; then
  echo 'Commit local changes before publishing an immutable release.' >&2
  exit 2
fi
CMD=(gcloud builds submit . --project="$PROJECT" --region="$REGION"
  --impersonate-service-account="tf-manager@${PROJECT}.iam.gserviceaccount.com"
  --service-account="$BUILD_SA"
  --gcs-source-staging-dir="gs://${PROJECT}-sbxtest01-build-source/source"
  --config=cloudbuild/platform-release.yaml
  --substitutions="_RELEASE_ID=${RELEASE_ID},_COMMIT_SHA=${COMMIT}")
if [[ "${1:-}" == '--apply' ]]; then
  "${CMD[@]}"
  echo "gs://${PROJECT}-sbxtest01-bundles/platform-releases/${RELEASE_ID}/release.json"
else
  printf '%q ' "${CMD[@]}"
  printf '\nAdd --apply to execute.\n'
fi
