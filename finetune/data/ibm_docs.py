IBM_DOCS = [
    {
        "id": "ibm_001",
        "category": "compute",
        "text": "IBM Cloud Code Engine is a fully managed serverless platform that runs containerized workloads. It automatically scales from zero to thousands of instances based on demand. Pricing is per-second with no idle costs. Ideal for replacing on-premise application servers during migration."
    },
    {
        "id": "ibm_002", 
        "category": "database",
        "text": "IBM Db2 on Cloud is a fully managed SQL database service on IBM Cloud. It supports automatic backups, high availability with 99.99% SLA, and seamless migration from on-premise Db2, Oracle, and SQL Server databases. Encryption at rest and in transit included by default."
    },
    {
        "id": "ibm_003",
        "category": "storage",
        "text": "IBM Cloud Object Storage provides scalable, durable storage for unstructured data. It offers 99.999999999% durability, cross-region replication, and lifecycle policies. Cost is approximately $0.023 per GB per month for standard tier. Direct replacement for on-premise NAS and SAN storage."
    },
    {
        "id": "ibm_004",
        "category": "networking",
        "text": "IBM Cloud Virtual Private Cloud (VPC) provides isolated network environments with customizable subnets, security groups, and network ACLs. Supports site-to-site VPN for hybrid connectivity between on-premise data centers and IBM Cloud. Essential for lift-and-shift migrations."
    },
    {
        "id": "ibm_005",
        "category": "containers",
        "text": "IBM Cloud Kubernetes Service (IKS) is a managed Kubernetes platform with automatic updates, integrated monitoring, and multi-zone clusters for high availability. Supports existing Docker workloads with minimal changes. IBM handles control plane management."
    },
    {
        "id": "ibm_006",
        "category": "compliance",
        "text": "IBM Cloud meets GDPR requirements through data residency controls, data processing agreements, and built-in privacy by design. Clients can specify EU data centers to ensure personal data never leaves European jurisdiction. IBM Cloud compliance certifications include ISO 27001, SOC 2, and HIPAA."
    },
    {
        "id": "ibm_007",
        "category": "ai",
        "text": "IBM watsonx.ai is the enterprise AI studio on IBM Cloud. It provides access to foundation models including IBM Granite, supports fine-tuning, and includes prompt engineering tools. Integrated with IBM Cloud security and governance frameworks for enterprise deployment."
    },
    {
        "id": "ibm_008",
        "category": "migration",
        "text": "IBM Cloud Migration methodology follows four phases: Assess (1-2 weeks), Plan (2-3 weeks), Migrate (4-12 weeks), Optimize (ongoing). The Assess phase identifies all workloads, dependencies, and migration complexity. Cost savings typically range from 20-40% in year one after migration."
    },
    {
        "id": "ibm_009",
        "category": "security",
        "text": "IBM Cloud Security and Compliance Center provides continuous compliance monitoring, automated evidence collection, and remediation guidance. Supports frameworks including NIST 800-53, CIS Benchmarks, and PCI DSS. Essential for regulated industries migrating to cloud."
    },
    {
        "id": "ibm_010",
        "category": "cost",
        "text": "IBM Cloud cost estimation for a typical 20-server migration: compute savings 35-45% vs on-premise, storage savings 40-60%, networking costs reduce by 20-30%. Total 3-year TCO reduction averages $270,000 for a 20-server environment. IBM provides free migration cost assessment tools."
    }
]

DISTRACTOR_DOCS = [
    {
        "id": "aws_001",
        "text": "AWS EC2 provides resizable compute capacity. Instance types range from t3.micro to p4d.24xlarge. Auto Scaling groups manage capacity automatically."
    },
    {
        "id": "aws_002", 
        "text": "Amazon RDS supports MySQL, PostgreSQL, Oracle, and SQL Server. Multi-AZ deployments provide high availability with automatic failover."
    },
    {
        "id": "azure_001",
        "text": "Azure Virtual Machines support Windows and Linux workloads. Azure Migrate provides discovery and assessment tools for on-premise servers."
    },
    {
        "id": "azure_002",
        "text": "Azure Blob Storage offers hot, cool, and archive tiers. Lifecycle management policies automatically move data between tiers based on age."
    },
    {
        "id": "gcp_001",
        "text": "Google Cloud Compute Engine provides virtual machines with custom machine types. Sustained use discounts apply automatically for long-running workloads."
    }
]
