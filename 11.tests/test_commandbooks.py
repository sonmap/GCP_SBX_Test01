import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ['00-variables.md', '01-admin.md', '02-network.md', '03-foundation.md']


def blocks(name):
    return re.findall(r'```bash\n(.*?)\n```', (ROOT / '02.sandbox_setup_01_gcloud' / name).read_text(), re.S)


class CommandbookTests(unittest.TestCase):
    def test_all_blocks_are_valid_bash_and_no_python_executor(self):
        self.assertFalse((ROOT / '02.sandbox_setup_01_gcloud/bootstrap.py').exists())
        self.assertFalse((ROOT / '02.sandbox_setup_01_gcloud/config.example.json').exists())
        for name in BOOKS:
            for block in blocks(name):
                self.assertNotRegex(block, r'\bpython[0-9.]*\b|\bterraform\b|\bfor\b|\bwhile\b|\bfunction\b')
                result = subprocess.run(['bash', '-n'], input=block, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, (name, result.stderr))
        # Each actual gcloud operation is individually copyable on one line.
        for name in BOOKS[1:]:
            for block in blocks(name):
                if block.startswith('gcloud '):
                    self.assertEqual(len(block.splitlines()), 1)

    def test_expansion_and_workflow_rendering_without_cloud_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / 'bin').mkdir()
            shutil.copytree(ROOT / '02.sandbox_setup_01_gcloud/configs', work / '02.sandbox_setup_01_gcloud/configs')
            stub = work / 'bin/gcloud'
            stub.write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$GCLOUD_TEST_LOG"
case "$*" in
  *'value(projectNumber)'*) printf '123456789012\\n' ;;
  *'value(status.url)'*) printf 'https://provisioner.example.run.app\\n' ;;
  *) printf '{}\\n' ;;
esac
''')
            stub.chmod(0o755)
            script = 'set -eu\n' + '\n'.join(block for name in BOOKS for block in blocks(name))
            env = dict(os.environ, PATH=str(work / 'bin') + os.pathsep + os.environ['PATH'], GCLOUD_TEST_LOG=str(work / 'calls.log'))
            env.pop('SHORT_SHA', None)
            env.pop('COMMIT_SHA', None)
            result = subprocess.run(['bash'], input=script, cwd=work, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = (work / '.local/workflow.yaml').read_text()
            self.assertNotIn('__PROVISIONER_URL__', rendered)
            self.assertIn('https://provisioner.example.run.app/provision', rendered)
            self.assertIn('${args}', rendered)
            self.assertIn('${response.body}', rendered)
            workflow = yaml.safe_load(rendered)
            auth = workflow['main']['steps'][0]['invoke']['args']['auth']
            self.assertEqual(auth['audience'], 'https://provisioner.example.run.app')
            calls = (work / 'calls.log').read_text().splitlines()
            creates = [c for c in calls if c.startswith('iam service-accounts create ')]
            self.assertEqual(len(creates), 2)
            self.assertTrue(any('create sbx-manager ' in c for c in creates))
            self.assertTrue(any('create tf-manager ' in c and '--project=pjt-d-host01' in c for c in creates))
            self.assertTrue(any('create sbx-manager ' in c and '--project=pjt-d-host01' in c for c in creates))
            account_calls=[c for c in calls if c.startswith('iam service-accounts ') and ' tf-manager@' in c]
            self.assertTrue(account_calls)
            self.assertTrue(all('--project=pjt-d-host01' in c for c in account_calls))
            self.assertFalse(any('iam.disableCrossProjectServiceAccountUsage' in c for c in calls))
            self.assertIn('_RELEASE_ID=git-$SHORT_SHA,_COMMIT_SHA=$COMMIT_SHA', (ROOT / '02.sandbox_setup_01_gcloud/03-foundation.md').read_text())
            self.assertFalse(any('${' in c for c in calls))
            for call in calls:
                if call.startswith(('compute ', 'storage ', 'builds ', 'run ', 'workflows ')):
                    self.assertIn('--impersonate-service-account=tf-manager@', call)

    def test_static_configs_match_runtime_targets_and_reference_files_exist(self):
        configs = ROOT / '02.sandbox_setup_01_gcloud/configs'
        env = yaml.safe_load((configs / 'provisioner-env.yaml').read_text())
        self.assertEqual(env['SBX_GKE_PROJECT'], 'pjt-d-host01')
        self.assertEqual(env['GKE_ENDPOINT_MODE'], 'internal')
        self.assertEqual(env['SBX_GKE_PROJECT'], 'pjt-d-host01')
        build = yaml.safe_load((configs / 'bootstrap-build.yaml').read_text())
        self.assertEqual(build['options']['logging'], 'CLOUD_LOGGING_ONLY')
        self.assertEqual(len(build['images']), 2)
        for name in BOOKS:
            for target in re.findall(r'--(?:config|env-vars-file)=([^\s"\']+)', '\n'.join(blocks(name))):
                self.assertTrue((ROOT / target).is_file(), target)

    def test_unified_platform_endpoints(self):
        configs = ROOT / '02.sandbox_setup_01_gcloud/configs'
        env = yaml.safe_load((configs / 'provisioner-env.yaml').read_text())
        project = env['SBX_GKE_PROJECT']
        self.assertEqual(project, 'pjt-d-host01')
        self.assertEqual(env['REQUEST_BUCKET'], project + '-sbxtest01-requests')
        self.assertEqual(env['BUNDLE_BUCKET'], project + '-sbxtest01-bundles')
        self.assertEqual(env['WORKER_POOL'], f'projects/{project}/locations/asia-northeast3/workerPools/pool-sbxtest01')
        self.assertTrue(env['JUPYTER_CHART_URI'].startswith(f'oci://asia-northeast3-docker.pkg.dev/{project}/'))
        release = yaml.safe_load((ROOT / '03.cloudbuild/platform-release.yaml').read_text())
        self.assertEqual(release['substitutions']['_SBX_GKE_PROJECT'], project)
        self.assertEqual(release['substitutions']['_BUNDLE_BUCKET'], env['BUNDLE_BUCKET'])
        sample = json.loads((ROOT / '05.sandbox_json/sbx01-approved-request.json').read_text())
        self.assertEqual(sample['gke']['project_id'], project)
        self.assertTrue(sample['source']['archive_uri'].startswith('gs://' + env['BUNDLE_BUCKET'] + '/'))


if __name__ == '__main__':
    unittest.main()
