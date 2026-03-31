# Meraki Wireless Compliance Report

**Generated:** 2026-03-31T00:36:26Z  
**Mode:** LIVE MODE  
**Report ID:** 1774917386

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Networks Checked** | 1 |
| **Networks Compliant** | 0 ✅ |
| **Networks Non-Compliant** | 1 ⚠️ |
| **Total SSIDs Checked** | 15 |
| **SSIDs Compliant** | 15 ✅ |
| **SSIDs Non-Compliant** | 1 ⚠️ |
| **Group Policies Checked** | 1 |
| **Group Policies Non-Compliant** | 0 ⚠️ |

**Overall Compliance Status:** ⚠️ **FAIL**
---

## Network Details

### LAB-Site1

**Network ID:** `L_3664241246819323813`  
**Dashboard (Wireless SSIDs):** [Open](https://n509.dashboard.meraki.com/LAB-Site1-applia/n/Reucybfwb/manage/clients)  
**Compliance Status:** ⚠️ **NON-COMPLIANT**  
**Drift Detected:** ✅ **NO**
#### SSID Compliance Matrix

| SSID Name | Number | Status | Enabled | Auth Mode | Encryption | WPA Encryption Mode | Visible | Broadcast | Min Bitrate | Band Selection |
|-----------|--------|--------|---------|-----------|------------|---------------------|---------|-----------|-------------|----------------|
| **Corp-Secure** | 0 | ✅ PASS | ✅ True | ✅ psk | ✅ wpa | ✅ WPA2 only | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Corp-Guest** | 1 | ✅ PASS | ✅ True | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **test** | 2 | ✅ PASS | ✅ True | ✅ psk | ✅ wpa | ✅ WPA3 Transition Mode | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 4** | 3 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 5** | 4 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 6** | 5 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 7** | 6 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 8** | 7 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 9** | 8 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 10** | 9 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 11** | 10 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 12** | 11 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 13** | 12 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 14** | 13 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |
| **Unconfigured SSID 15** | 14 | ✅ PASS | ✅ False | ✅ open | ✅ unknown | ✅  | ✅ True | ✅ False | ✅ 11 | ✅ Dual band operation |


#### Group Policy ACL Audit

| Group Policy | ID | Firewall Settings | L3 Rules | L7 Rules | Status |
|--------------|----|-------------------|----------|----------|--------|
| **Lab-Site1 Restricted Policy** | 100 | custom | 3 | 0 | ✅ PASS |


✅ **All SSIDs in this network are compliant with desired state.**


---


## Compliance Check Details

### Checked Fields

The following SSID configuration fields were checked for compliance:

- `enabled` - SSID enabled/disabled status
- `authMode` - Authentication mode (open, psk, 8021x, etc.)
- `encryptionMode` - Transport mode (`open` for open auth, otherwise `wpa`)
- `wpaEncryptionMode` - Allowed WPA profile (`WPA2 only` or `WPA3 Transition Mode`)
- `visible` - SSID visibility in broadcast
- `broadcast` - SSID broadcast status
- `minBitrate` - Minimum bitrate (Mbps)
- `bandSelection` - Band selection mode
- Group policy ACL posture:
  - Seeded group policies must match the desired baseline in `group_vars/meraki_group_policies.yml` (rule-level, case-insensitive)
  - L3 ACL rule action (allow/deny) drift is detected per rule by matching on destCidr + protocol + destPort
  - Missing desired L3 rules and firewall settings changes are flagged as critical
  - Custom group policies should contain at least one L3 or L7 ACL rule
  - L3 ACLs must not contain `allow any/any` rules

### Legend

- ✅ **PASS** - Configuration matches desired state
- ⚠️ **FAIL** - Configuration differs from desired state (drift detected)
- → Indicates drift: Current → Desired value

---

## Recommendations

1. **Review Non-Compliant Networks**: 1 network require attention
2. **Investigate Drift**: Check Meraki Dashboard for manual changes that caused configuration drift
3. **Review Group Policy ACLs**: Validate custom group policies are restrictive and contain explicit ACLs
4. **Restore Compliance**: Use Ansible playbooks to restore desired configuration state
5. **Prevent Future Drift**: Consider implementing:
   - Dashboard access controls
   - Change approval workflows
   - Regular automated compliance checks (schedule with cron)

---

## Next Steps

1. **Review this report** for any non-compliant configurations
2. **Investigate root cause** of any detected drift
3. **Remediate** using Ansible playbooks if needed
4. **Schedule regular checks** to prevent future drift

---

*Report generated by Ansible Meraki Compliance Role*  
*For questions or issues, refer to the project documentation*
