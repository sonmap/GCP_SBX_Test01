#!/usr/bin/env python3
import json
import os
import sys

import google.auth
from google.auth import iam
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
]


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: group_upsert.py APPROVED_REQUEST_JSON")
    source = sys.argv[1]
    if source.startswith("gs://"):
        bucket, name = source[5:].split("/", 1)
        request = json.loads(storage.Client().bucket(bucket).blob(name).download_as_bytes())
    else:
        with open(source, encoding="utf-8") as stream:
            request = json.load(stream)

    # IAM signBlob performs Workspace DWD without a downloaded private key.
    adc, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    email = os.environ["WORKSPACE_DWD_SERVICE_ACCOUNT"]
    credentials = service_account.Credentials(
        signer=iam.Signer(Request(), adc, email),
        service_account_email=email,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
        subject=os.environ["GOOGLE_WORKSPACE_ADMIN_SUBJECT"],
    )
    directory = build("admin", "directory_v1", credentials=credentials, cache_discovery=False)
    group_email = request["identity"]["group_email"]
    approved_members = set(request["identity"]["members"])

    try:
        group = directory.groups().get(groupKey=group_email).execute()
    except HttpError as error:
        if error.resp.status != 404:
            raise
        group = directory.groups().insert(
            body={
                "email": group_email,
                "name": f"GCP DEV Sandbox {request['task']['name']}",
                "description": f"Managed sandbox group for {request['task']['display_name']}",
            }
        ).execute()

    existing = {}
    page_token = None
    while True:
        response = directory.members().list(groupKey=group["id"], pageToken=page_token).execute()
        for member in response.get("members", []):
            existing[member["email"].lower()] = member
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    for email in sorted(approved_members):
        if email.lower() not in existing:
            directory.members().insert(
                groupKey=group["id"], body={"email": email, "role": "MEMBER"}
            ).execute()

    for email, member in existing.items():
        if member.get("role") == "MEMBER" and email not in {value.lower() for value in approved_members}:
            directory.members().delete(groupKey=group["id"], memberKey=member["id"]).execute()

    print(json.dumps({"group_id": group["id"], "group_email": group_email, "members": sorted(approved_members)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
