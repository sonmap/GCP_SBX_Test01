#!/usr/bin/env bash
set -euo pipefail
command -v python3
command -v gcloud
gcloud auth list
gcloud config get-value project
echo 'Review python3 gcloud/bootstrap.py admin/network/foundation before --apply.'
