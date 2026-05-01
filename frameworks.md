# Framework Reference

## CIS Benchmarks

The [Center for Internet Security (CIS) Benchmarks](https://www.cisecurity.org/cis-benchmarks) are consensus-based configuration guidelines developed by security experts. Each benchmark applies to a specific technology and is versioned.

### Levels

| Level | Description |
|-------|-------------|
| Level 1 | Essential, lower-impact recommendations suitable for all environments. Minimal performance impact. |
| Level 2 | Stricter, defense-in-depth settings for environments where security is the top priority. May impact usability. |

### Relevant benchmarks this agent covers

- CIS Amazon Web Services Foundations Benchmark
- CIS Microsoft Azure Foundations Benchmark
- CIS Google Cloud Platform Foundation Benchmark
- CIS Distribution-Independent Linux Benchmark
- CIS Microsoft Windows Server 2022 Benchmark
- CIS Kubernetes Benchmark

---

## NIST SP 800-53 Rev 5

[NIST Special Publication 800-53](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) provides a catalog of security and privacy controls for federal information systems, widely adopted in private sector as a compliance framework.

### Control families covered

| Family | ID | Description |
|--------|----|-------------|
| Access Control | AC | Policies and procedures for system access |
| Audit and Accountability | AU | Event logging, audit record review |
| Configuration Management | CM | Baseline configs, change control |
| Identification and Authentication | IA | MFA, password management |
| Incident Response | IR | Incident handling procedures |
| Risk Assessment | RA | Vulnerability scanning, risk analysis |
| System and Communications Protection | SC | Boundary protection, encryption in transit |
| System and Information Integrity | SI | Malware protection, flaw remediation |

### Control baselines

Controls are organized into three impact baselines:

- **Low** — appropriate for systems where loss of confidentiality, integrity, or availability has limited adverse effect
- **Moderate** — appropriate for most federal systems
- **High** — appropriate for systems where loss would have severe or catastrophic effect

---

## SOC 2 Type II

SOC 2 is an auditing standard developed by the AICPA. Type II reports cover the design and operating effectiveness of controls over a period of time (typically 6–12 months).

### Trust Services Criteria

| Category | ID | Focus |
|----------|----|-------|
| Security | CC1–CC9 | Common criteria — controls environment, risk assessment, monitoring |
| Availability | A1 | System availability as committed or agreed |
| Confidentiality | C1 | Information designated as confidential is protected |
| Processing Integrity | PI1 | System processing is complete, accurate, timely |
| Privacy | P1–P8 | Personal information collected, used, retained, disclosed appropriately |

---

## Mapping between frameworks

Many controls are related across frameworks. For example:

| Requirement | CIS | NIST | SOC 2 |
|-------------|-----|------|-------|
| Multi-factor authentication | CIS 1.5 (AWS) | IA-2(1) | CC6.1 |
| Audit logging | CIS 2.2.1 (AWS) | AU-2, AU-9 | CC7.2 |
| Encryption at rest | CIS 2.4.x | SC-28 | CC6.7 |
| Network segmentation | CIS 4.x | SC-7 | CC6.6 |
| Vulnerability management | CIS 7.x | SI-2, RA-5 | CC7.1 |
