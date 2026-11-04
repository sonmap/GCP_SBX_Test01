import contextlib
import copy
import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bootstrap',ROOT/'gcloud/bootstrap.py')
bootstrap=importlib.util.module_from_spec(spec); spec.loader.exec_module(bootstrap)
CONFIG=json.loads((ROOT/'gcloud/config.example.json').read_text())


class BootstrapTests(unittest.TestCase):
    def test_preview_never_contacts_cloud_or_writes_generated_files(self):
        for phase in ['admin','network','foundation']:
            b=bootstrap.Bootstrap(copy.deepcopy(CONFIG),False,phase)
            with mock.patch('subprocess.run') as run, mock.patch.object(Path,'write_text') as write, contextlib.redirect_stdout(io.StringIO()):
                getattr(b,phase)()
            run.assert_not_called(); write.assert_not_called()

    def test_permission_denied_is_not_resource_absence(self):
        b=bootstrap.Bootstrap(CONFIG,True)
        with mock.patch('subprocess.run',return_value=subprocess.CompletedProcess([],1,'','PERMISSION_DENIED: get denied')):
            with self.assertRaisesRegex(RuntimeError,'PERMISSION_DENIED'): b.read('compute','networks','describe','example')

    def test_not_found_is_only_create_case(self):
        b=bootstrap.Bootstrap(CONFIG,True)
        with mock.patch('subprocess.run',return_value=subprocess.CompletedProcess([],1,'','NOT_FOUND: no such network')):
            self.assertIsNone(b.read('compute','networks','describe','example'))

    def test_existing_cidr_drift_stops_without_mutation(self):
        b=bootstrap.Bootstrap(CONFIG,True,'network')
        with mock.patch.object(b,'read',return_value={'ipCidrRange':'10.99.0.0/24'}),mock.patch.object(b,'run') as run:
            with self.assertRaisesRegex(ValueError,'no automatic replacement'):
                b.ensure(['describe'],['create'],{'ipCidrRange':'10.252.0.0/24'})
            run.assert_not_called()

    def test_only_two_custom_sa_creates_and_no_keys(self):
        b=bootstrap.Bootstrap(CONFIG)
        with contextlib.redirect_stdout(io.StringIO()) as stream: b.admin()
        text=stream.getvalue()
        commands=[line for line in text.splitlines() if line.startswith('gcloud iam service-accounts create ')]
        self.assertEqual(len(commands),2)
        self.assertTrue(any('create sbx-manager ' in c for c in commands))
        self.assertTrue(any('create tf-manager ' in c for c in commands))
        self.assertNotIn(' keys create ',text)
        self.assertNotIn('roles/owner',text)
        self.assertNotIn('roles/editor',text)

    def test_cidr_overlap_rejected_before_gcloud(self):
        c=copy.deepcopy(CONFIG);c['run_cidr']=c['main_node_cidr']
        with self.assertRaisesRegex(ValueError,'overlaps'): bootstrap.validate_config(c)

    def test_schema_target_changes_are_not_silent(self):
        c=copy.deepcopy(CONFIG);c['gke_project']='other-project'
        with self.assertRaisesRegex(ValueError,'pins project'): bootstrap.validate_config(c)

    def test_private_endpoint_default_and_build_identity(self):
        b=bootstrap.Bootstrap(CONFIG,phase='foundation')
        with contextlib.redirect_stdout(io.StringIO()) as stream: b.foundation()
        text=stream.getvalue()
        self.assertIn('--enable-private-endpoint',text)
        self.assertIn('--no-public-egress',text)
        self.assertIn('--service-account=projects/prj-b-cicd-local-236d/serviceAccounts/tf-manager@',text)
        self.assertNotIn('--allow-unauthenticated ',text)


if __name__=='__main__': unittest.main()
