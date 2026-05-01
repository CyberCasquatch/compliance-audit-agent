"""
frameworks.py — Reference control definitions for CIS Benchmarks and NIST SP 800-53.

These are used for UI display, documentation, and prompt enrichment.
The agent uses Claude to interpret controls dynamically, but this module
provides a structured reference for filtering and labelling.
"""

from dataclasses import dataclass
from typing import Literal


SeverityLevel = Literal["critical", "high", "medium", "low", "info"]
ControlStatus = Literal["pass", "fail", "warn"]


@dataclass
class ControlRef:
    id: str
    title: str
    framework: Literal["CIS", "NIST", "SOC2"]
    category: str
    severity: SeverityLevel
    description: str


# ─────────────────────────────────────────────────────────── CIS AWS Benchmark

CIS_AWS_CONTROLS = [
    ControlRef("CIS-1.1", "Avoid the use of the root account", "CIS", "IAM", "critical", "The root account has unrestricted access to all AWS resources."),
    ControlRef("CIS-1.4", "Ensure IAM root account access key does not exist", "CIS", "IAM", "critical", "Root account should not have programmatic access keys."),
    ControlRef("CIS-1.5", "Ensure MFA is enabled for the root account", "CIS", "IAM", "critical", "Root account must require MFA for all sign-ins."),
    ControlRef("CIS-1.10", "Ensure MFA is enabled for all IAM users", "CIS", "IAM", "high", "All IAM users with a console password should have MFA enabled."),
    ControlRef("CIS-1.14", "Ensure access keys are rotated every 90 days", "CIS", "IAM", "high", "Access keys older than 90 days increase the risk of compromise."),
    ControlRef("CIS-2.1.1", "Ensure S3 buckets deny public access", "CIS", "Storage", "high", "S3 buckets should not allow public read or write access."),
    ControlRef("CIS-2.1.2", "Ensure S3 bucket versioning is enabled", "CIS", "Storage", "medium", "Versioning protects against accidental deletion and overwrites."),
    ControlRef("CIS-2.2.1", "Ensure CloudTrail is enabled in all regions", "CIS", "Logging", "high", "CloudTrail should capture API activity across all AWS regions."),
    ControlRef("CIS-2.3.1", "Ensure GuardDuty is enabled", "CIS", "Config", "high", "GuardDuty provides intelligent threat detection."),
    ControlRef("CIS-3.1", "Ensure VPC flow logging is enabled", "CIS", "Network", "medium", "Flow logs capture network traffic metadata for analysis."),
    ControlRef("CIS-4.1", "Ensure no security groups allow 0.0.0.0/0 to SSH", "CIS", "Network", "critical", "Open SSH access exposes instances to brute-force attacks."),
    ControlRef("CIS-4.2", "Ensure no security groups allow 0.0.0.0/0 to RDP", "CIS", "Network", "critical", "Open RDP access exposes instances to exploitation."),
]

# ─────────────────────────────────────────────────────── NIST SP 800-53 Rev 5

NIST_CONTROLS = [
    ControlRef("NIST-AC-2", "Account Management", "NIST", "IAM", "high", "Manage information system accounts, including establishing, activating, modifying, reviewing, disabling, and removing accounts."),
    ControlRef("NIST-AC-3", "Access Enforcement", "NIST", "IAM", "high", "Enforce approved authorizations for logical access to information."),
    ControlRef("NIST-AC-17", "Remote Access", "NIST", "Network", "high", "Establish and document usage restrictions and implementation guidance for remote access."),
    ControlRef("NIST-AU-2", "Event Logging", "NIST", "Logging", "medium", "Identify the types of events that the system is capable of logging."),
    ControlRef("NIST-AU-9", "Protection of Audit Information", "NIST", "Logging", "high", "Protect audit information and audit tools from unauthorized access, modification, and deletion."),
    ControlRef("NIST-CM-2", "Baseline Configuration", "NIST", "Config", "medium", "Develop, document, and maintain a current baseline configuration of the information system."),
    ControlRef("NIST-CM-6", "Configuration Settings", "NIST", "Config", "medium", "Establish and document configuration settings for IT products employed within the information system."),
    ControlRef("NIST-IA-2", "Identification and Authentication", "NIST", "IAM", "critical", "Uniquely identify and authenticate organizational users."),
    ControlRef("NIST-IA-5", "Authenticator Management", "NIST", "IAM", "high", "Manage information system authenticators by verifying identity before issuing authenticators."),
    ControlRef("NIST-SC-7", "Boundary Protection", "NIST", "Network", "high", "Monitor and control communications at the external boundary and key internal boundaries."),
    ControlRef("NIST-SC-28", "Protection of Information at Rest", "NIST", "Encryption", "high", "Protect the confidentiality and integrity of information at rest."),
    ControlRef("NIST-SI-2", "Flaw Remediation", "NIST", "Config", "high", "Identify, report, and correct information system flaws."),
    ControlRef("NIST-SI-3", "Malicious Code Protection", "NIST", "Config", "high", "Employ malicious code protection mechanisms at information system entry and exit points."),
]

ALL_CONTROLS = CIS_AWS_CONTROLS + NIST_CONTROLS


def get_controls_for_framework(framework: str) -> list[ControlRef]:
    """Return controls relevant to the requested framework."""
    if framework == "cis":
        return CIS_AWS_CONTROLS
    if framework == "nist":
        return NIST_CONTROLS
    if framework == "both":
        return ALL_CONTROLS
    return ALL_CONTROLS


def get_control_by_id(control_id: str) -> ControlRef | None:
    """Look up a control by its ID string."""
    for c in ALL_CONTROLS:
        if c.id.lower() == control_id.lower():
            return c
    return None
