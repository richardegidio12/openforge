# MCP: Cloud Infrastructure

## Kubernetes (EKS / AKS / GKE)

**Package:** `mcp-server-kubernetes` (community)

Works with any Kubernetes cluster — AWS EKS, Azure AKS, Google GKE. The MCP reads your `~/.kube/config` and operates against the active context.

**What the Agent can do:**
- Check pod status and logs (Spark executors, Flink TaskManagers, Airflow workers)
- Inspect resource usage (CPU/memory) for data workloads
- Debug CrashLoopBackOff and OOMKilled containers
- Scale deployments and StatefulSets
- Apply Kubernetes manifests (SparkApplication, FlinkDeployment, etc.)
- Check PersistentVolumeClaims for storage issues

**Usage in OpenForge sessions:**

```
# Check Spark job status on EKS
User: "is the Spark backfill job running?"

Agent:
→ kubectl get sparkapplication -n data-platform
→ kubectl describe sparkapplication silver-orders-backfill

"SparkApplication silver-orders-backfill:
State: RUNNING
Driver: Running (1 pod)
Executors: 6/8 running (2 pending — waiting for node)
Started: 09:23
Duration: 18 min
Progress: ~65% (estimated by records/s)"

# Debug OOMKilled Flink job
User: "Flink is crashing with OOMKilled"

Agent:
→ kubectl get pods -n streaming -l app=flink-orders-processor
→ kubectl describe pod flink-orders-processor-taskmanager-0

"TaskManager pod OOMKilled. Memory limit: 4Gi, actual usage: 4.1Gi.
Last event: 'OOMKilled' at 09:31.

Cause: RocksDB state growing beyond heap. Options:
1. Increase memory limit to 6Gi (update FlinkDeployment)
2. Add state.backend.rocksdb.memory.managed=true
3. Reduce session.timeout.ms to clear state earlier

Should I apply option 2 (least disruptive)?"

User: "yes"
Agent:
→ Edits FlinkDeployment YAML
→ kubectl apply -f flink-orders-processor.yaml
"Configuration applied. TaskManagers restarting. Monitoring..."

# Check Airflow worker logs on GKE
Agent:
→ kubectl logs -n airflow airflow-worker-abc123 --tail=100
"Worker log: Task extract_erp_orders failed with
OperationalError: connection to server at 'erp-host' (10.0.1.5)
failed: SSL SYSCALL error: EOF detected
Consistent with yesterday's error at 02:17."

# Resource pressure analysis
User: "is the cluster having resource issues?"

Agent:
→ kubectl top nodes
→ kubectl top pods -n data-platform --sort-by=memory

"Top memory consumers:
1. spark-backfill-executor-3: 7.2Gi / 8Gi (90%) ⚠️
2. flink-taskmanager-0: 4.1Gi / 4Gi (103%) 🔴 OOM risk
3. airflow-scheduler: 1.2Gi / 2Gi (60%) ✅

Node data-node-3: CPU 78%, Memory 91% — near the limit.
Recommend scaling the node group or reducing Spark backfill parallelism."
```

**Switching between clusters (EKS/AKS/GKE):**
```bash
# List available contexts
kubectl config get-contexts

# Switch to EKS
kubectl config use-context arn:aws:eks:us-east-1:123456:cluster/data-platform

# Switch to GKE
kubectl config use-context gke_my-project_us-central1_data-cluster

# The MCP uses the active context automatically
```

**Setup:**
```json
"kubernetes": {
  "command": "npx",
  "args": ["-y", "mcp-server-kubernetes"],
  "env": {
    "KUBECONFIG": "$HOME/.kube/config"
  }
}
```

**Useful namespaces to be aware of:**
```
data-platform    ← Dagster, Airflow, general data workloads
spark-jobs       ← Spark Operator and submitted SparkApplications
streaming        ← Flink Operator and FlinkDeployments
monitoring       ← Prometheus, Grafana, Thanos
```

---

## Apache Ranger

**Package:** `mcp-server-apache-ranger` (community)

**What the Agent can do:**
- Check access policies for specific users/groups on tables or columns
- Create and update access policies
- Review audit logs for data access events
- Check data masking policies (PII column masking)
- Validate that a user cannot access restricted data

**Usage in OpenForge sessions:**

```
# Security Consultant: validate Bronze is restricted
User: "confirming analysts cannot access Bronze"

Agent:
→ GET /service/public/v2/api/policy?serviceName=hive&resource=bronze.*
→ GET /service/public/v2/api/policy?serviceName=hdfs&resource=/data/bronze/*

"Bronze policies:
HDFS /data/bronze/*:
  Allow: ingestion-sa (READ, WRITE), transformation-sa (READ)
  Deny all others: ✅

Hive bronze.*:
  Allow: transformation-sa (SELECT)
  Deny: analyst_group ✅

Bronze is correctly restricted. Analyst access denial confirmed."

# Check PII masking policy
User: "is the email masking policy active for analysts?"

Agent:
→ GET /service/public/v2/api/policy?policyType=MASKING&resource=silver.orders.customer_email

"Masking policy on silver.orders.customer_email:
  Group: analyst_group → MASK_HASH (SHA-256) ✅
  Group: data_engineers → NONE (access to real hash) ✅
  SA ingestion-sa: NONE (access to original email in Bronze only) ✅

Policy active and correct."

# Create new access policy (for the consultancy example)
User: "create a temporary access policy for consultancy XYZ"

Agent:
→ POST /service/public/v2/api/policy
{
  "name": "consultancy-xyz-temp-2024-05",
  "service": "bigquery",
  "resources": {"table": {"values": ["gold.fct_orders"]}},
  "policyItems": [{
    "users": ["consultancy-xyz@external.com"],
    "accesses": [{"type": "select", "isAllowed": true}]
  }],
  "validitySchedules": [{"endTime": "2024-05-15 23:59:59"}]
}
"Policy created. consultancy-xyz@external.com has READ access
to gold.fct_orders until 2024-05-15. Access expires automatically."
```

**Setup:**
```json
"apache-ranger": {
  "command": "npx",
  "args": ["-y", "mcp-server-apache-ranger"],
  "env": {
    "RANGER_HOST": "http://YOUR_RANGER_HOST:6080",
    "RANGER_USERNAME": "openforge_agent",
    "RANGER_PASSWORD": "$RANGER_PASSWORD"
  }
}
```
