#!/usr/bin/env python3
"""Three gcloud bootstrap phases. Default: print commands, never contact GCP.

No Terraform, REST writes or SDK resource creation is used in phases 1-3.
Config/generated files contain no secret values. Existing infrastructure is
validated and reused; IAM bindings are additive. Resource drift stops execution.
"""
import argparse
import ipaddress
import json
import re
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Bootstrap:
    def __init__(self, config, apply=False, phase="admin"):
        self.c = config
        self.apply = apply
        self.phase = phase
        self.project = config["cicd_project"]
        self.region = config["region"]
        self.sbx = f"sbx-manager@{self.project}.iam.gserviceaccount.com"
        self.tf = f"tf-manager@{self.project}.iam.gserviceaccount.com"
        self.tf_resource = f"projects/{self.project}/serviceAccounts/{self.tf}"
        self.requests = f"{self.project}-sbxtest01-requests"
        self.bundles = f"{self.project}-sbxtest01-bundles"
        self.staging = f"{self.project}-sbxtest01-build-source"
        self.pool = f"projects/{self.project}/locations/{self.region}/workerPools/pool-sbxtest01"
        self.registry = f"{self.region}-docker.pkg.dev/{self.project}/ar-sbxtest01-platform"
        self.local = ROOT / ".local"

    def command(self, args):
        auth = [f"--account={self.c['admin_account']}"]
        if self.phase != "admin":
            auth.append(f"--impersonate-service-account={self.tf}")
        return ["gcloud", *map(str, args), *auth, "--quiet"]

    def run(self, *args, capture=False):
        cmd = self.command(args)
        print(shlex.join(cmd), flush=True)
        if not self.apply:
            return ""
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture, check=True)
        return result.stdout.strip() if capture else ""

    def read(self, *args):
        if not self.apply:
            print("# CHECK " + shlex.join(self.command([*args, "--format=json"])))
            return None
        result = subprocess.run(self.command([*args, "--format=json"]), cwd=ROOT,
                                text=True, capture_output=True, check=False)
        if result.returncode == 0:
            return json.loads(result.stdout or "{}")
        # A permission, connectivity or authentication error must never mean absent.
        error = result.stderr
        if re.search(r"\bNOT_FOUND\b|\bwas not found\b|\bdoes not exist\b|\bcould not be found\b", error, re.I):
            return None
        raise RuntimeError(error.strip())

    def ensure(self, describe, create, expected=None):
        current = self.read(*describe)
        if current is None:
            if not self.apply:
                print("# CREATE ONLY IF ABSENT")
            self.run(*create)
        else:
            for key, value in (expected or {}).items():
                actual = current
                for part in key.split("."):
                    actual = actual.get(part) if isinstance(actual, dict) else None
                if actual != value:
                    raise ValueError(f"existing {describe}: {key}={actual!r}, expected {value!r}; no automatic replacement")
            print(f"# REUSE {describe}")
        return current

    def generated(self, name, value):
        path = self.local / name
        if self.apply:
            self.local.mkdir(exist_ok=True)
            path.write_text(json.dumps(value, indent=2) if not isinstance(value, str) else value)
        else:
            print(f"# GENERATED {path.relative_to(ROOT)}: {json.dumps(value, ensure_ascii=False)}")
        return str(path)

    def project_role(self, project, member, *roles):
        for role in roles:
            self.run("projects", "add-iam-policy-binding", project,
                     f"--member={member}", f"--role={role}", "--condition=None")

    def sa_role(self, email, member, role):
        self.run("iam", "service-accounts", "add-iam-policy-binding", email,
                 f"--project={self.project}", f"--member={member}", f"--role={role}", "--condition=None")

    def number(self, project):
        if not self.apply:
            return {self.project: "CICD_PROJECT_NUMBER", self.c['gke_project']: "GKE_PROJECT_NUMBER",
                    self.c['host_project']: "HOST_PROJECT_NUMBER"}.get(project, "PROJECT_NUMBER")
        return self.run("projects", "describe", project, "--format=value(projectNumber)", capture=True)

    def enable(self, project, services):
        self.run("services", "enable", *[f"{service}.googleapis.com" for service in services], f"--project={project}")

    def admin(self):
        c = self.c
        self.enable(self.project, ["serviceusage", "iam", "iamcredentials", "compute", "container",
                    "cloudbuild", "config", "run", "workflows", "artifactregistry", "secretmanager",
                    "storage", "logging", "cloudresourcemanager", "cloudbilling", "admin", "cloudscheduler"])
        self.enable(c["host_project"], ["compute", "container", "servicenetworking"])
        self.enable(c["gke_project"], ["container", "compute"])
        for service in ["cloudbuild", "config", "run", "workflows", "cloudscheduler", "container"]:
            self.run("beta", "services", "identity", "create", f"--service={service}.googleapis.com", f"--project={self.project}")
        self.run("beta", "services", "identity", "create", "--service=container.googleapis.com", f"--project={c['gke_project']}")
        self.run("beta", "services", "identity", "create", "--service=container.googleapis.com", f"--project={c['host_project']}")
        for account, display in [("sbx-manager", "sbx_manager"), ("tf-manager", "tf_manager")]:
            self.ensure(["iam", "service-accounts", "describe", f"{account}@{self.project}.iam.gserviceaccount.com", f"--project={self.project}"],
                        ["iam", "service-accounts", "create", account, f"--project={self.project}", f"--display-name={display}"])
        tf = f"serviceAccount:{self.tf}"
        sbx = f"serviceAccount:{self.sbx}"
        self.project_role(self.project, tf, "roles/serviceusage.serviceUsageAdmin", "roles/iam.serviceAccountAdmin",
                          "roles/resourcemanager.projectIamAdmin", "roles/storage.admin", "roles/secretmanager.admin",
                          "roles/artifactregistry.admin", "roles/cloudbuild.builds.editor", "roles/cloudbuild.workerPoolOwner",
                          "roles/cloudbuild.workerPoolUser", "roles/config.admin", "roles/config.agent",
                          "roles/run.admin", "roles/workflows.admin", "roles/container.admin", "roles/compute.viewer",
                          "roles/logging.logWriter", "roles/serviceusage.serviceUsageConsumer")
        self.project_role(self.project, sbx, "roles/cloudbuild.builds.editor", "roles/cloudbuild.workerPoolUser",
                          "roles/workflows.invoker", "roles/logging.logWriter", "roles/serviceusage.serviceUsageConsumer")
        self.project_role(c["host_project"], tf, "roles/compute.networkAdmin", "roles/compute.securityAdmin", "roles/compute.networkUser", "roles/servicenetworking.networksAdmin", "roles/serviceusage.serviceUsageConsumer")
        self.project_role(c["gke_project"], tf, "roles/container.admin", "roles/compute.loadBalancerAdmin", "roles/compute.viewer", "roles/serviceusage.serviceUsageConsumer")
        self.sa_role(self.tf, c["operator_member"], "roles/iam.serviceAccountTokenCreator")
        self.sa_role(self.sbx, c["operator_member"], "roles/iam.serviceAccountTokenCreator")
        self.sa_role(self.tf, c["operator_member"], "roles/iam.serviceAccountUser")
        self.sa_role(self.sbx, tf, "roles/iam.serviceAccountUser")
        self.sa_role(self.sbx, tf, "roles/iam.serviceAccountTokenCreator")
        self.sa_role(self.tf, sbx, "roles/iam.serviceAccountUser")
        self.sa_role(self.tf, tf, "roles/iam.serviceAccountUser")
        # gcloud impersonation for network/foundation and custom build authentication.
        self.sa_role(self.tf, tf, "roles/iam.serviceAccountTokenCreator")
        number = self.number(self.project)
        self.sa_role(self.tf, f"serviceAccount:service-{number}@gcp-sa-config.iam.gserviceaccount.com", "roles/iam.serviceAccountUser")
        self.sa_role(self.tf, f"serviceAccount:service-{number}@gcp-sa-cloudbuild.iam.gserviceaccount.com", "roles/iam.serviceAccountTokenCreator")
        # Existing-project PoC and future folder-created tasks use the same executor.
        self.project_role(c["existing_task_project"], tf, "roles/browser", "roles/resourcemanager.projectIamAdmin",
                          "roles/serviceusage.serviceUsageAdmin", "roles/bigquery.admin", "roles/storage.admin")
        if c["folder_id"]:
            for role in ["roles/resourcemanager.projectCreator", "roles/resourcemanager.projectIamAdmin", "roles/compute.xpnAdmin"]:
                self.run("resource-manager", "folders", "add-iam-policy-binding", c["folder_id"],
                         f"--member={tf}", f"--role={role}", "--condition=None")
        if c["billing_account"]:
            self.run("billing", "accounts", "add-iam-policy-binding", c["billing_account"], f"--member={tf}", "--role=roles/billing.user")
        # Google-managed agents/default node SAs are not extra custom automation SAs.
        for project in dict.fromkeys([self.project, c["gke_project"]]):
            n = self.number(project)
            self.project_role(c["host_project"], f"serviceAccount:service-{n}@container-engine-robot.iam.gserviceaccount.com",
                              "roles/container.hostServiceAgentUser", "roles/compute.networkUser")
            self.project_role(c["host_project"], f"serviceAccount:{n}@cloudservices.gserviceaccount.com", "roles/compute.networkUser")
        self.project_role(c["host_project"], f"serviceAccount:service-{number}@serverless-robot-prod.iam.gserviceaccount.com", "roles/compute.networkUser")
        for project in dict.fromkeys([self.project, c["gke_project"]]):
            n = self.number(project)
            self.project_role(project, f"serviceAccount:{n}-compute@developer.gserviceaccount.com", "roles/container.defaultNodeServiceAccount")
            self.run("iam", "service-accounts", "add-iam-policy-binding", f"{n}-compute@developer.gserviceaccount.com",
                     f"--project={project}", f"--member={tf}", "--role=roles/iam.serviceAccountUser", "--condition=None")
        print("# Workspace administrator must authorize the sbx-manager OAuth client ID for the two Directory group scopes.")

    def subnet(self, name, cidr, secondary=None):
        c = self.c
        base = [f"--project={c['host_project']}", f"--region={self.region}"]
        create = ["compute", "networks", "subnets", "create", name, *base, f"--network={c['network']}",
                  f"--range={cidr}", "--enable-private-ip-google-access"]
        if secondary:
            create.append(f"--secondary-range={secondary[0]}={secondary[1]}")
        current = self.ensure(["compute", "networks", "subnets", "describe", name, *base], create,
                              {"ipCidrRange": cidr, "network": f"https://www.googleapis.com/compute/v1/projects/{c['host_project']}/global/networks/{c['network']}"})
        if current and secondary:
            ranges = {r['rangeName']: r['ipCidrRange'] for r in current.get('secondaryIpRanges', [])}
            if ranges.get(secondary[0]) != secondary[1]:
                raise ValueError(f"{name}: existing Pod range differs; no automatic overwrite")
        self.run("compute", "networks", "subnets", "update", name, *base, "--enable-private-ip-google-access")

    def network(self):
        c = self.c; host = c["host_project"]
        self.ensure(["compute", "networks", "describe", c['network'], f"--project={host}"],
                    ["compute", "networks", "create", c['network'], f"--project={host}", "--subnet-mode=custom"],
                    {"autoCreateSubnetworks": False})
        # Shared VPC host/association changes require folder XPN bootstrap permission.
        host_info = self.read("compute", "shared-vpc", "get-host-project", host)
        if not host_info:
            self.run("compute", "shared-vpc", "enable", host)
        for project in dict.fromkeys([c['gke_project'], self.project]):
            current = self.read("compute", "shared-vpc", "get-host-project", project)
            if not current:
                self.run("compute", "shared-vpc", "associated-projects", "add", project, f"--host-project={host}")
            elif current.get('name') != host:
                raise ValueError(f"{project}: already associated to a different Shared VPC host")
        self.subnet(c['main_subnet'], c['main_node_cidr'], (c['main_pod_range'], c['main_pod_cidr']))
        if c['create_test_cluster']:
            self.subnet(c['test_subnet'], c['test_node_cidr'], (c['test_pod_range'], c['test_pod_cidr']))
        self.subnet(c['run_subnet'], c['run_cidr'])
        self.subnet(c['task_subnet'], c['task_cidr'])
        address, prefix = c['psa_cidr'].split('/')
        net = f"projects/{host}/global/networks/{c['network']}"
        self.ensure(["compute", "addresses", "describe", c['psa_name'], f"--project={host}", "--global"],
                    ["compute", "addresses", "create", c['psa_name'], f"--project={host}", "--global", "--purpose=VPC_PEERING",
                     "--addresses="+address, "--prefix-length="+prefix, "--network="+net],
                    {"address": address, "prefixLength": int(prefix), "purpose": "VPC_PEERING"})
        peering = self.read("services", "vpc-peerings", "list", f"--project={host}", f"--network={c['network']}", "--service=servicenetworking.googleapis.com")
        if not peering:
            self.run("services", "vpc-peerings", "connect", f"--project={host}", f"--network={c['network']}",
                     "--service=servicenetworking.googleapis.com", f"--ranges={c['psa_name']}")
        elif not any(c['psa_name'] in p.get('reservedPeeringRanges', []) for p in peering):
            raise ValueError("Existing PSA connection uses other ranges; explicitly merge approved ranges before proceeding")
        self.ensure(["compute", "firewall-rules", "describe", "fw-sbxtest01-alb-hc", f"--project={host}"],
                    ["compute", "firewall-rules", "create", "fw-sbxtest01-alb-hc", f"--project={host}",
                     f"--network={c['network']}", "--direction=INGRESS", "--allow=tcp:8000",
                     "--source-ranges=35.191.0.0/16,130.211.0.0/22", f"--destination-ranges={c['main_pod_cidr']}"],
                    {"sourceRanges": ["35.191.0.0/16", "130.211.0.0/22"], "destinationRanges": [c['main_pod_cidr']]})
        print("# Before workload deployment: complete private-pool to private-GKE VPN/BGP routing; VPC peering is not transitive.")

    def bucket(self, name):
        self.ensure(["storage", "buckets", "describe", f"gs://{name}"],
                    ["storage", "buckets", "create", f"gs://{name}", f"--project={self.project}", f"--location={self.region}",
                     "--uniform-bucket-level-access", "--public-access-prevention"])
        self.run("storage", "buckets", "update", f"gs://{name}", "--versioning", "--public-access-prevention")

    def bucket_role(self, name, member, role):
        self.run("storage", "buckets", "add-iam-policy-binding", f"gs://{name}", f"--member={member}", f"--role={role}")

    def cluster(self, test=False):
        c=self.c; kind="test" if test else "main"
        project=self.project if test else c['gke_project']; name=c[f'{kind}_cluster']
        args=["container", "clusters", "create-auto", name, f"--project={project}", f"--region={self.region}",
              f"--network=projects/{c['host_project']}/global/networks/{c['network']}",
              f"--subnetwork=projects/{c['host_project']}/regions/{self.region}/subnetworks/{c[kind+'_subnet']}",
              f"--cluster-secondary-range-name={c[kind+'_pod_range']}", "--enable-private-nodes", "--enable-private-endpoint",
              f"--master-ipv4-cidr={c[kind+'_control_plane_cidr']}", "--enable-master-authorized-networks",
              f"--master-authorized-networks={c['admin_cidr']},{c['psa_cidr']}", "--enable-master-global-access", "--release-channel=regular"]
        if c['gke_endpoint_mode']=="dns":
            args += ["--enable-dns-access", "--enable-k8s-tokens-via-dns"]
        current = self.ensure(["container", "clusters", "describe", name, f"--project={project}", f"--region={self.region}"], args,
                    {"autopilot.enabled": True, "privateClusterConfig.enablePrivateNodes": True,
                     "privateClusterConfig.enablePrivateEndpoint": True,
                     "ipAllocationPolicy.clusterSecondaryRangeName": c[kind+'_pod_range']})
        if current:
            subnet = current.get('subnetwork', '')
            if not subnet.endswith('/'+c[kind+'_subnet']):
                raise ValueError(f"existing cluster subnet differs: {subnet}")
            if c['gke_endpoint_mode']=='dns' and not current.get('controlPlaneEndpointsConfig',{}).get('dnsEndpointConfig',{}).get('allowExternalTraffic'):
                raise ValueError("DNS endpoint not enabled on existing cluster; explicitly update it or use private endpoint mode")

    def shared_alb(self):
        c=self.c; project=c['gke_project']; base=[f"--project={project}", "--global"]
        alb='alb-sbxtest01-shared'
        self.ensure(["compute", "addresses", "describe", "ip-"+alb, *base],
                    ["compute", "addresses", "create", "ip-"+alb, *base, "--ip-version=IPV4"])
        self.ensure(["compute", "backend-services", "describe", f"bes-{alb}-default", *base],
                    ["compute", "backend-services", "create", f"bes-{alb}-default", *base, "--protocol=HTTP", "--load-balancing-scheme=EXTERNAL"])
        self.ensure(["compute", "url-maps", "describe", "urlmap-"+alb, *base],
                    ["compute", "url-maps", "create", "urlmap-"+alb, *base, f"--default-service=bes-{alb}-default"])
        for proto, port in [('http',80),('https',443)]:
            extra=[]
            if proto=='https':
                certificate=self.read("compute", "ssl-certificates", "describe", c['ssl_certificate_name'], *base)
                if self.apply and certificate is None:
                    raise ValueError("Create the SSL certificate outside Git first; no certificate/private key is generated or uploaded by bootstrap")
                extra=["--ssl-certificates="+c['ssl_certificate_name']]
            self.ensure(["compute", f"target-{proto}-proxies", "describe", f"{proto}-proxy-{alb}", f"--project={project}"],
                        ["compute", f"target-{proto}-proxies", "create", f"{proto}-proxy-{alb}", f"--project={project}", "--url-map=urlmap-"+alb, *extra])
            self.ensure(["compute", "forwarding-rules", "describe", f"fr-{alb}-{proto}", *base],
                        ["compute", "forwarding-rules", "create", f"fr-{alb}-{proto}", *base, "--load-balancing-scheme=EXTERNAL",
                         "--address=ip-"+alb, f"--target-{proto}-proxy={proto}-proxy-{alb}", f"--ports={port}"])

    def foundation(self):
        c=self.c; tf=f"serviceAccount:{self.tf}"; sbx=f"serviceAccount:{self.sbx}"
        for bucket in [self.requests,self.bundles,self.staging]: self.bucket(bucket)
        self.bucket_role(self.requests,sbx,"roles/storage.objectAdmin")
        self.bucket_role(self.bundles,sbx,"roles/storage.objectAdmin")
        number=self.number(self.project)
        self.bucket_role(self.bundles,f"serviceAccount:service-{number}@gcp-sa-config.iam.gserviceaccount.com","roles/storage.objectViewer")
        self.ensure(["artifacts", "repositories", "describe", "ar-sbxtest01-platform", f"--project={self.project}", f"--location={self.region}"],
                    ["artifacts", "repositories", "create", "ar-sbxtest01-platform", f"--project={self.project}", f"--location={self.region}", "--repository-format=docker"])
        for project in dict.fromkeys([c['gke_project'],self.project]):
            n=self.number(project)
            self.run("artifacts", "repositories", "add-iam-policy-binding", "ar-sbxtest01-platform", f"--project={self.project}",
                     f"--location={self.region}", f"--member=serviceAccount:{n}-compute@developer.gserviceaccount.com", "--role=roles/artifactregistry.reader")
        for name in ['jupyter-oauth-client-id','jupyter-oauth-client-secret']:
            self.ensure(["secrets", "describe", name, f"--project={self.project}"],
                        ["secrets", "create", name, f"--project={self.project}", "--replication-policy=user-managed", f"--locations={self.region}"])
            self.run("secrets", "add-iam-policy-binding", name, f"--project={self.project}", f"--member={tf}", "--role=roles/secretmanager.secretAccessor")
        self.ensure(["builds", "worker-pools", "describe", "pool-sbxtest01", f"--project={self.project}", f"--region={self.region}"],
                    ["builds", "worker-pools", "create", "pool-sbxtest01", f"--project={self.project}", f"--region={self.region}",
                     "--worker-machine-type=e2-standard-4", "--worker-disk-size=100", "--no-public-egress",
                     f"--peered-network=projects/{c['host_project']}/global/networks/{c['network']}", f"--peered-network-ip-range={c['psa_cidr']}"])
        self.cluster()
        if c['create_test_cluster']: self.cluster(test=True)
        build = {'steps':[
            {'name':'gcr.io/cloud-builders/docker','args':['build','-t',f'{self.registry}/sbxtest01-automation-runner:bootstrap','automation-runner']},
            {'name':'gcr.io/cloud-builders/docker','args':['build','-t',f'{self.registry}/run-sbxtest01-provisioner:bootstrap','cloudrun-provisioner']}],
            'images':[f'{self.registry}/sbxtest01-automation-runner:bootstrap', f'{self.registry}/run-sbxtest01-provisioner:bootstrap'],
            'options':{'logging':'CLOUD_LOGGING_ONLY'}}
        path=self.generated('bootstrap-build.json',build)
        self.run("builds", "submit", ".", f"--project={self.project}", f"--region={self.region}",
                 f"--service-account={self.tf_resource}", f"--gcs-source-staging-dir=gs://{self.staging}/source", f"--config={path}")
        env={"GCP_PROJECT":self.project,"GCP_REGION":self.region,"REQUEST_BUCKET":self.requests,"BUNDLE_BUCKET":self.bundles,
             "GITHUB_REPOSITORY":"sonmap/GCP_SBX_Test01","WORKER_POOL":self.pool,"WORKSPACE_ADMIN_SUBJECT":c['workspace_admin_subject'],
             "JUPYTER_CHART_URI":f"oci://{self.registry}/jupyterhub","JUPYTER_CHART_VERSION":"4.2.0", "GKE_ENDPOINT_MODE":c['gke_endpoint_mode']}
        env_path=self.generated('run-env.json',env)
        self.run("run", "deploy", "run-sbxtest01-provisioner", f"--project={self.project}", f"--region={self.region}",
                 f"--image={self.registry}/run-sbxtest01-provisioner:bootstrap", f"--service-account={self.sbx}",
                 "--no-allow-unauthenticated", "--ingress=all", "--timeout=300", "--max-instances=2", f"--env-vars-file={env_path}",
                 f"--network=projects/{c['host_project']}/global/networks/{c['network']}",
                 f"--subnet=projects/{c['host_project']}/regions/{self.region}/subnetworks/{c['run_subnet']}", "--vpc-egress=private-ranges-only")
        self.run("run", "services", "add-iam-policy-binding", "run-sbxtest01-provisioner", f"--project={self.project}",
                 f"--region={self.region}", f"--member={sbx}", "--role=roles/run.invoker")
        url=self.run("run", "services", "describe", "run-sbxtest01-provisioner", f"--project={self.project}", f"--region={self.region}", "--format=value(status.url)", capture=True) or "https://PROVISIONER_URL"
        # JSON is valid YAML, but Workflows source is supplied as ordinary YAML.
        workflow='''main:
  params: [args]
  steps:
    - invoke:
        call: http.post
        args:
          url: "URL/provision"
          auth:
            type: OIDC
            audience: "URL"
          body: ${args}
        result: response
    - done:
        return: ${response.body}
'''.replace('URL',url)
        workflow_path=self.generated('workflow.yaml',workflow)
        self.run("workflows", "deploy", "workflow-sbxtest01-provision", f"--project={self.project}", f"--location={self.region}",
                 f"--service-account={self.sbx}", f"--source={workflow_path}")
        self.project_role(self.project,c['operator_member'],"roles/workflows.invoker")
        # Operator uploads approved requests; access is bucket scoped.
        self.bucket_role(self.requests,c['operator_member'],"roles/storage.objectAdmin")
        self.bucket_role(self.bundles,c['operator_member'],"roles/storage.objectViewer")
        if c['create_shared_alb']: self.shared_alb()
        if c['create_github_trigger']:
            self.ensure(["builds", "triggers", "describe", "trigger-sbxtest01-platform-release", f"--project={self.project}", f"--region={self.region}"],
                        ["builds", "triggers", "create", "github", "--name=trigger-sbxtest01-platform-release", f"--project={self.project}", f"--region={self.region}",
                         "--repo-owner=sonmap", "--repo-name=GCP_SBX_Test01", "--branch-pattern=^main$", "--build-config=cloudbuild/platform-release.yaml",
                         f"--service-account={self.tf_resource}",
                         f"--substitutions=_RELEASE_ID=git-$SHORT_SHA,_COMMIT_SHA=$COMMIT_SHA"])
        print("# Next: register OAuth secrets + Workspace DWD; publish a versioned release; mirror chart/images; build Notebook image; update request source.")


def validate_config(c):
    for field in ['cicd_project','host_project','gke_project','existing_task_project']:
        if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]',c[field]): raise ValueError(f'invalid {field}')
    # Runtime request schema uses these fixed PoC targets. Fail instead of silently splitting targets.
    if (c['cicd_project'],c['host_project'],c['gke_project'],c['region'],c['network'],c['main_cluster']) != (
        'prj-b-cicd-local-236d','pjt-d-shared-base','pjt-d-host01','asia-northeast3','vpc-d-shared-base','gke-sbx-main-an3'):
        raise ValueError('This PoC release pins project/network/cluster targets; update runtime schema and helpers together before changing them')
    if c['gke_endpoint_mode'] not in ('internal','dns'): raise ValueError('gke_endpoint_mode must be internal or dns')
    networks=[]
    fields=['main_node_cidr','main_pod_cidr','main_control_plane_cidr','run_cidr','task_cidr','psa_cidr']
    if c['create_test_cluster']: fields += ['test_node_cidr','test_pod_cidr','test_control_plane_cidr']
    for field in fields:
        net=ipaddress.ip_network(c[field],strict=True)
        if net.version!=4: raise ValueError(f'{field} must be IPv4')
        for previous,other in networks:
            if net.overlaps(other): raise ValueError(f'{field} overlaps {previous}')
        networks.append((field,net))
    if ipaddress.ip_network(c['task_cidr']).prefixlen != 24: raise ValueError('task_cidr must be /24')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['admin','network','foundation'])
    parser.add_argument('--config',default=str(ROOT/'gcloud/config.json'))
    parser.add_argument('--apply',action='store_true',help='Execute gcloud commands; default prints commands without accessing GCP')
    args=parser.parse_args()
    config=json.loads(Path(args.config).read_text())
    validate_config(config)
    bootstrap=Bootstrap(config,args.apply,args.phase)
    getattr(bootstrap,args.phase)()


if __name__=='__main__':
    main()
