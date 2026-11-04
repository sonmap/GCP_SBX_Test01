import copy
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('provisioner',ROOT/'cloudrun-provisioner/main.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
ENV={'GCP_PROJECT':'prj-b-cicd-local-236d','GCP_REGION':'asia-northeast3',
     'BUNDLE_BUCKET':'prj-b-cicd-local-236d-sbxtest01-bundles',
     'REQUEST_BUCKET':'prj-b-cicd-local-236d-sbxtest01-requests',
     'WORKER_POOL':'projects/prj-b-cicd-local-236d/locations/asia-northeast3/workerPools/pool-sbxtest01',
     'WORKSPACE_ADMIN_SUBJECT':'admin@sonmap.net',
     'JUPYTER_CHART_URI':'oci://example/jupyterhub','JUPYTER_CHART_VERSION':'4.2.0'}


def payload():
    data=json.loads((ROOT/'examples/sbx01-approved-request.json').read_text())
    data['source']['sha256']='a'*64
    data['source']['release_id']='git-test123'
    return data


class ProvisioningTests(unittest.TestCase):
    @mock.patch.dict(os.environ,ENV)
    def test_bundles_use_shared_gsa_and_import_only_dataset_bucket(self):
        written={}
        bucket=mock.Mock();bucket.name=ENV['BUNDLE_BUCKET'];bucket.blob.side_effect=lambda name:name
        def download(source,destination):
            shutil.copytree(ROOT/'terraform',destination/'terraform')
            return destination
        with mock.patch.object(p.storage,'Client') as client, mock.patch.object(p,'download_source_archive',side_effect=download),mock.patch.object(p,'upload_immutable',side_effect=lambda name,data,ctype:written.setdefault(name,data)):
            client.return_value.bucket.return_value=bucket
            prefix,manifest=p.assemble_bundles(payload(),b'{}')
        self.assertEqual(set(manifest['bundles']),{'10-project','20-network','30-project-iam','40-data'})
        data_zip=next(v for k,v in written.items() if k.endswith('/data.zip'))
        with zipfile.ZipFile(io.BytesIO(data_zip)) as archive:
            variables=json.loads(archive.read('terraform.auto.tfvars.json'))
            self.assertEqual(variables['jupyter_gsa_email'],'sbx-manager@prj-b-cicd-local-236d.iam.gserviceaccount.com')
            imports=archive.read('imports.tf').decode()
            self.assertIn('google_bigquery_dataset.sandbox',imports)
            self.assertIn('google_storage_bucket.sandbox',imports)
            self.assertNotIn('google_service_account',imports)
            self.assertNotIn('resource "google_service_account"',archive.read('main.tf').decode())

    @mock.patch.dict(os.environ,ENV)
    def test_build_execution_identities_and_group_order(self):
        with mock.patch.object(p.cloudbuild_v1,'CloudBuildClient') as client:
            p.start_build(payload(),'gs://example/request.json','gs://example/bundle')
            self.assertEqual(client.return_value.create_build.call_args.kwargs['parent'], 'projects/prj-b-cicd-local-236d/locations/asia-northeast3')
            build=client.return_value.create_build.call_args.kwargs['build']
        spec=json.loads(p.cloudbuild_v1.Build.to_json(build))
        self.assertEqual(spec['serviceAccount'],f"projects/{ENV['GCP_PROJECT']}/serviceAccounts/tf-manager@{ENV['GCP_PROJECT']}.iam.gserviceaccount.com")
        self.assertIn('group_upsert.py',spec['steps'][0]['args'][0])
        commands=spec['steps'][2]['args'][1]
        self.assertIn('deployments/sbxtest01-',commands)
        self.assertNotIn('sa-im-',commands)
        self.assertEqual(commands.count('tf-manager@'),4)
        self.assertIn('pool-sbxtest01',spec['options']['pool']['name'])

    @mock.patch.dict(os.environ,ENV)
    def test_optional_network_is_not_applied(self):
        data=payload();data['network']['required']=False;data['network']['shared_vpc_join']=False
        with mock.patch.object(p.cloudbuild_v1,'CloudBuildClient') as client:
            p.start_build(data,'gs://example/request.json','gs://example/bundle')
        build=client.return_value.create_build.call_args.kwargs['build']
        text=build.steps[2].args[1]
        self.assertNotIn('/network.zip',text)
        self.assertIn('/data.zip',text)

    def test_placeholder_release_rejected(self):
        data=payload();data['source']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'publish a new'): p.validate_semantics(data)

    def test_schema_reference_matches_runtime(self):
        self.assertEqual(json.loads((ROOT/'schemas/sandbox-request.schema.json').read_text()),p.SCHEMA)
        p.VALIDATOR.validate(payload())

    def test_runner_group_sync_matches_source(self):
        self.assertEqual((ROOT/'scripts/group_upsert.py').read_bytes(),(ROOT/'automation-runner/group_upsert.py').read_bytes())


if __name__=='__main__': unittest.main()
