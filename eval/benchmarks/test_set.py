"""
Test set for evaluating IBM Migration Advisor
---------------------------------------------
These 20 questions were NOT in the training data.
We use them to measure how much the model improved.
Senior engineers always evaluate on unseen data.
"""

TEST_QUESTIONS = [
    {
        "id": "test_001",
        "category": "compute",
        "question": "Our company runs 15 application servers on Windows Server 2019. What IBM Cloud service should we migrate to and what are the cost implications?",
        "reference_answer": "IBM Cloud Code Engine is the recommended service for migrating application servers. It is a fully managed serverless platform that eliminates idle server costs by scaling to zero when not in use. For 15 servers, expected compute savings are 35-45% compared to on-premise infrastructure. Pricing is per-second with no idle costs, making it significantly more cost-effective than maintaining physical Windows servers."
    },
    {
        "id": "test_002",
        "category": "database",
        "question": "We have an Oracle database with 2TB of data. How do we migrate it to IBM Cloud and what is the SLA?",
        "reference_answer": "IBM Db2 on Cloud supports seamless migration from Oracle databases. The service provides 99.99% SLA with automatic backups and high availability built in. Encryption at rest and in transit is included by default. For a 2TB Oracle migration, IBM provides migration tooling and the process typically falls within the Plan phase of the 4-phase IBM Cloud Migration methodology."
    },
    {
        "id": "test_003",
        "category": "compliance",
        "question": "We are a European company and must comply with GDPR. Can IBM Cloud guarantee our data stays in Europe?",
        "reference_answer": "IBM Cloud meets GDPR requirements through data residency controls that allow clients to specify EU data centers, ensuring personal data never leaves European jurisdiction. IBM provides data processing agreements and privacy by design. IBM Cloud compliance certifications include ISO 27001, SOC 2, and HIPAA, making it fully suitable for GDPR-compliant European operations."
    },
    {
        "id": "test_004",
        "category": "cost",
        "question": "What cost savings can we expect after migrating 20 servers to IBM Cloud over 3 years?",
        "reference_answer": "For a 20-server migration to IBM Cloud, expected savings are 35-45% on compute, 40-60% on storage, and 20-30% on networking costs. The total 3-year TCO reduction averages $270,000 for a 20-server environment. IBM provides free migration cost assessment tools to calculate exact savings based on your specific infrastructure configuration."
    },
    {
        "id": "test_005",
        "category": "migration",
        "question": "How long does a typical IBM Cloud migration take and what are the phases?",
        "reference_answer": "IBM Cloud Migration methodology follows four phases: Assess takes 1-2 weeks to identify all workloads and dependencies, Plan takes 2-3 weeks to design the target architecture, Migrate takes 4-12 weeks to execute the actual migration, and Optimize is ongoing after migration. Cost savings typically range from 20-40% in year one after migration completes."
    },
    {
        "id": "test_006",
        "category": "containers",
        "question": "We run Docker containers on premise. What is the best IBM Cloud service to host them?",
        "reference_answer": "IBM Cloud Kubernetes Service (IKS) is the recommended platform for Docker workloads. It is a managed Kubernetes platform that supports existing Docker workloads with minimal changes. IBM handles control plane management, provides automatic updates, integrated monitoring, and multi-zone clusters for high availability."
    },
    {
        "id": "test_007",
        "category": "storage",
        "question": "We have 50TB of unstructured data on NAS storage. What is the IBM Cloud equivalent and what does it cost?",
        "reference_answer": "IBM Cloud Object Storage is the direct replacement for on-premise NAS and SAN storage. It provides 99.999999999% durability with cross-region replication and lifecycle policies. Cost is approximately $0.023 per GB per month for standard tier, making 50TB approximately $1,150 per month — typically 40-60% less than on-premise NAS maintenance costs."
    },
    {
        "id": "test_008",
        "category": "networking",
        "question": "How do we maintain connectivity between our on-premise data center and IBM Cloud during migration?",
        "reference_answer": "IBM Cloud Virtual Private Cloud (VPC) provides hybrid connectivity through site-to-site VPN between on-premise data centers and IBM Cloud. VPC provides isolated network environments with customizable subnets, security groups, and network ACLs. This is essential for lift-and-shift migrations where some workloads remain on-premise during the transition period."
    },
    {
        "id": "test_009",
        "category": "security",
        "question": "How does IBM Cloud help us maintain compliance with NIST and PCI DSS after migration?",
        "reference_answer": "IBM Cloud Security and Compliance Center provides continuous compliance monitoring for NIST 800-53, CIS Benchmarks, and PCI DSS frameworks. It offers automated evidence collection and remediation guidance, making it essential for regulated industries. The service monitors your IBM Cloud environment continuously and alerts on any compliance drift."
    },
    {
        "id": "test_010",
        "category": "ai",
        "question": "We want to add AI capabilities to our applications after migrating to IBM Cloud. What platform should we use?",
        "reference_answer": "IBM watsonx.ai is the enterprise AI studio on IBM Cloud. It provides access to foundation models including IBM Granite, supports fine-tuning, and includes prompt engineering tools. It is integrated with IBM Cloud security and governance frameworks for enterprise deployment, making it the natural next step after completing cloud migration."
    },
    {
        "id": "test_011",
        "category": "compute",
        "question": "What happens to our application during peak traffic if we use IBM Cloud Code Engine?",
        "reference_answer": "IBM Cloud Code Engine automatically scales from zero to thousands of instances based on demand. During peak traffic, it scales up instantly to handle load, then scales back down when traffic decreases. This eliminates the need to provision for peak capacity on-premise, which is a major source of wasted infrastructure spend."
    },
    {
        "id": "test_012",
        "category": "database",
        "question": "What database migration tools does IBM provide for moving from SQL Server to IBM Cloud?",
        "reference_answer": "IBM Db2 on Cloud supports seamless migration from SQL Server databases with automatic backups and high availability. The service includes encryption at rest and in transit by default. IBM's migration methodology includes a dedicated Plan phase covering database migration design, and IBM provides tooling to assess SQL Server compatibility and automate the migration process."
    },
    {
        "id": "test_013",
        "category": "cost",
        "question": "How does IBM Cloud pricing compare to running 100 servers on-premise over 3 years?",
        "reference_answer": "For a 100-server migration, IBM Cloud TCO savings are approximately $1.3 million over 3 years. Compute savings run 35-45%, storage savings 40-60%, and networking 20-30%. IBM provides free migration cost assessment tools. The assessment phase itself, which costs approximately $32,000 manually, can be automated with IBM AI tools."
    },
    {
        "id": "test_014",
        "category": "migration",
        "question": "What does the Assess phase of IBM Cloud migration involve?",
        "reference_answer": "The Assess phase takes 1-2 weeks and identifies all workloads, server dependencies, application complexity, and migration readiness. It produces a complexity score and recommended migration pattern — rehost, replatform, or refactor. This phase is the foundation of the entire migration plan and determines the timeline, cost, and risk profile of the subsequent phases."
    },
    {
        "id": "test_015",
        "category": "compliance",
        "question": "We handle healthcare data. Is IBM Cloud HIPAA compliant?",
        "reference_answer": "IBM Cloud is HIPAA compliant. IBM Cloud compliance certifications include ISO 27001, SOC 2, and HIPAA, making it suitable for healthcare data workloads. IBM provides data processing agreements and privacy by design controls. The IBM Cloud Security and Compliance Center provides continuous monitoring to maintain HIPAA compliance after migration."
    },
    {
        "id": "test_016",
        "category": "containers",
        "question": "What level of Kubernetes management does IBM handle vs what we manage in IKS?",
        "reference_answer": "In IBM Cloud Kubernetes Service, IBM handles control plane management including master node operations, automatic updates, and infrastructure maintenance. The client manages worker nodes, application deployments, and workload configuration. IKS provides multi-zone clusters for high availability and integrated monitoring, significantly reducing operational overhead compared to self-managed Kubernetes."
    },
    {
        "id": "test_017",
        "category": "storage",
        "question": "How durable is IBM Cloud Object Storage compared to our on-premise storage?",
        "reference_answer": "IBM Cloud Object Storage provides 99.999999999% durability — eleven nines — with cross-region replication. This is significantly higher than typical on-premise NAS or SAN storage which usually achieves 99.9% to 99.99% durability. Lifecycle policies automatically manage data between tiers, and the cost is approximately $0.023 per GB per month for standard tier."
    },
    {
        "id": "test_018",
        "category": "networking",
        "question": "What security controls does IBM Cloud VPC provide for our network?",
        "reference_answer": "IBM Cloud VPC provides isolated network environments with customizable subnets, security groups, and network ACLs for fine-grained traffic control. It supports site-to-site VPN for hybrid connectivity. Security groups act as virtual firewalls at the instance level while network ACLs provide subnet-level controls, giving multiple layers of network security for migrated workloads."
    },
    {
        "id": "test_019",
        "category": "security",
        "question": "How does IBM Cloud Security and Compliance Center help after migration?",
        "reference_answer": "IBM Cloud Security and Compliance Center provides continuous compliance monitoring, automated evidence collection, and remediation guidance after migration. It supports NIST 800-53, CIS Benchmarks, and PCI DSS frameworks. The service continuously monitors your IBM Cloud environment and provides automated evidence for audits, significantly reducing the manual compliance overhead that exists with on-premise infrastructure."
    },
    {
        "id": "test_020",
        "category": "ai",
        "question": "Can IBM watsonx.ai be used with data that is already migrated to IBM Cloud?",
        "reference_answer": "IBM watsonx.ai is natively integrated with IBM Cloud, making it the natural AI layer for data already migrated to IBM Cloud. It provides access to IBM Granite foundation models, supports fine-tuning on your migrated data, and includes prompt engineering tools. The integration with IBM Cloud security and governance frameworks ensures enterprise data controls remain in place when adding AI capabilities."
    }
]
