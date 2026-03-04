# Fix All Linting Errors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix every linting error reported by yamllint and ansible-lint so that `make lint` passes clean.

**Architecture:** Three layers of fixes: (1) fix the linting *config* files so they are valid and match our desired rules, (2) fix *formatting* errors (trailing spaces, line length) across all YAML files, (3) fix *semantic* errors (wrong variable names, wrong module usage, missing strategy declaration). Also fix `requirements.txt` so the tooling installs cleanly.

**Tech Stack:** ansible-lint (>=25.x, compatible with ansible-core 2.20.2), yamllint, pre-commit

---

## Error Inventory

| Category | Count | Fix Strategy |
|---|---|---|
| Missing `.yamllint` config | 1 file | Create file |
| Invalid `.ansible-lint` config | 2 bad keys | Remove `cache` and `parseable`; add skips |
| `requirements.txt` dependency conflict | 1 conflict | Bump jinja2 to 3.1.6 |
| `.pre-commit-config.yaml` outdated versions | 2 refs | Bump ansible-lint rev, pin yamllint path |
| Trailing spaces | ~50 instances / 10 files | Strip trailing whitespace |
| Line length >160 chars (ansible-lint) | 14 lines | Wrap long Jinja expressions |
| `var-naming[pattern]` (camelCase vars) | 8 instances / 1 file | Rename to snake_case |
| `var-naming[no-role-prefix]` | 54 instances | Skip in config (intentionally shared vars) |
| `name[casing]` | 1 instance | Capitalize handler name |
| `args[module]` wrong module | 1 instance | Replace `community.general.github_issue` with `ansible.builtin.uri` |
| `run-once[task]` | 7 instances | Set `strategy: linear` on play |

---

### Task 1: Create `.yamllint` config

The `.pre-commit-config.yaml` references `-c=.yamllint` but the file doesn't exist. Without it yamllint uses defaults (80 char line limit), producing 100+ false-positive line-length errors.

**Files:**
- Create: `.yamllint`

**Step 1: Create the `.yamllint` file**

```yaml
---
extends: default

rules:
  line-length:
    max: 160
    level: warning
  truthy:
    allowed-values: ['true', 'false', 'yes', 'no', 'on', 'off']
    check-keys: false
  comments:
    require-starting-space: true
    ignore-shebangs: true
    min-spaces-from-content: 1
  comments-indentation: disable
  document-start: disable
  trailing-spaces: {}

ignore: |
  .github/
  .devcontainer/
  vault/
  .ansible/
  venv/
  .git/
  node_modules/
```

**Step 2: Verify yamllint loads the config**

Run: `. venv/bin/activate && yamllint -c .yamllint group_vars/all.yml`
Expected: Only trailing-spaces errors, no line-length errors (lines are <160).

**Step 3: Commit**

```bash
git add .yamllint
git commit -m "chore: add .yamllint config with 160 char line limit"
```

---

### Task 2: Fix `.ansible-lint` config

The current config has two keys (`cache` and `parseable`) that are invalid in ansible-lint >=25.x, plus a broken nested `rules:` structure. Also need to skip `var-naming[no-role-prefix]` and `run-once[task]` since these are intentional patterns.

**Files:**
- Modify: `.ansible-lint`

**Step 1: Replace the entire `.ansible-lint` file**

```yaml
---
# Ansible Lint Configuration
# See: https://ansible-lint.readthedocs.io/configuring/

skip_list:
  - yaml[line-length]
  - name[casing]
  - name[role-name]
  - command-instead-of-module
  - no-log-password
  - var-naming[no-role-prefix]
  - run-once[task]

enable_list:
  - yaml
  - name
  - syntax-check
  - risky-shell-pipe
  - risky-file-permissions

exclude_paths:
  - .github/
  - .devcontainer/
  - vault/
  - .ansible/
  - venv/
  - .git/
  - __pycache__/
  - "*.pyc"
  - .env

use_default_rules: true
```

Key changes from old file:
- Removed `cache: true` (not a valid key in ansible-lint >=25.x)
- Removed `parseable: false` (not a valid key)
- Removed `verbosity: 1` (use CLI flag instead)
- Removed broken nested `rules:` block
- Added `var-naming[no-role-prefix]` to skip_list (54 violations are intentionally shared vars like `meraki_api_key`)
- Added `run-once[task]` to skip_list (7 violations are intentional reporting tasks with linear strategy)

**Step 2: Verify ansible-lint loads the config**

Run: `. venv/bin/activate && ansible-lint playbooks/ roles/ 2>&1 | head -5`
Expected: No "Invalid configuration file" error.

**Step 3: Commit**

```bash
git add .ansible-lint
git commit -m "fix: update .ansible-lint config for ansible-lint 25.x compatibility"
```

---

### Task 3: Fix `requirements.txt` dependency conflict

`jinja2==3.1.4` conflicts with `meraki==2.0.3` which requires `jinja2==3.1.6`. Also `ansible-lint==6.22.2` is incompatible with `ansible-core==2.20.2`.

**Files:**
- Modify: `requirements.txt`

**Step 1: Update pinned versions**

Change line 15 from:
```
ansible-lint==6.22.2
```
to:
```
ansible-lint>=25.0.0
```

Change line 31 from:
```
jinja2==3.1.4
```
to:
```
jinja2==3.1.6
```

**Step 2: Verify clean install**

Run:
```bash
rm -rf venv && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
```
Expected: No `ResolutionImpossible` error.

**Step 3: Also update `.pre-commit-config.yaml` ansible-lint rev**

Change line 52 from:
```yaml
    rev: v6.22.2  # Latest version as of February 2026
```
to:
```yaml
    rev: v25.0.0
```

**Step 4: Commit**

```bash
git add requirements.txt .pre-commit-config.yaml
git commit -m "fix: resolve dependency conflicts in requirements.txt and pre-commit config"
```

---

### Task 4: Strip trailing whitespace from all YAML files

~50 trailing-space errors across 10+ project files. This is the single biggest category of errors.

**Files:**
- Modify: `.pre-commit-config.yaml`
- Modify: `playbooks/compliance_check.yml`
- Modify: `roles/meraki_compliance/tasks/main.yml`
- Modify: `group_vars/meraki_orgs.yml`
- Modify: `group_vars/all.yml`
- Modify: `inventory/sandbox.yml`
- Modify: `.github/workflows/validate.yml`

**Step 1: Run a sed command to strip trailing whitespace from all project YAML files (excluding venv/)**

```bash
find . -name '*.yml' -o -name '*.yaml' | grep -v venv/ | grep -v .git/ | xargs sed -i '' 's/[[:space:]]*$//'
```

**Step 2: Verify no trailing spaces remain**

Run: `. venv/bin/activate && yamllint -c .yamllint -d '{extends: default, rules: {line-length: disable, truthy: disable, document-start: disable, comments-indentation: disable}}' playbooks/ roles/ group_vars/ inventory/ .pre-commit-config.yaml .github/ 2>&1 | grep trailing`
Expected: No output (no trailing-spaces errors).

**Step 3: Commit**

```bash
git add -A
git commit -m "fix: strip trailing whitespace from all YAML files"
```

---

### Task 5: Wrap long Jinja lines in `roles/meraki_compliance/tasks/main.yml`

14 lines exceed 160 chars. These are long Jinja2 comparison expressions on lines 41, 78-84, 131-132, 150, and in `security_baseline.yml` lines 65 and 140.

**Files:**
- Modify: `roles/meraki_compliance/tasks/main.yml:41` (188 chars)
- Modify: `roles/meraki_compliance/tasks/main.yml:78-84` (284-349 chars each)
- Modify: `roles/meraki_compliance/tasks/main.yml:131-132` (197, 175 chars)
- Modify: `roles/meraki_compliance/tasks/main.yml:150` (161 chars)
- Modify: `roles/meraki_compliance/tasks/security_baseline.yml:65` (169 chars)
- Modify: `roles/meraki_compliance/tasks/security_baseline.yml:140` (183 chars)
- Modify: `playbooks/compliance_check.yml:190` (211 chars)

**Step 1: Fix line 41 — wrap the `selectattr` chain**

Replace the single-line `desired_config` set_fact with a YAML folded block scalar:

```yaml
- name: Find desired SSID configuration for this network
  ansible.builtin.set_fact:
    desired_config: >-
      {{ meraki_desired_ssids
         | selectattr('network_name', 'equalto', inventory_hostname)
         | selectattr('network_id', 'equalto', current_network_id)
         | first
         | default({}) }}
  when:
    - meraki_desired_ssids is defined
    - meraki_desired_ssids | length > 0
```

**Step 2: Fix lines 78-84 — extract diff variables into a separate vars block**

Each `*_diff` variable is a massive one-liner. Wrap each onto multiple lines using YAML folded block scalars. For example, the `enabled_diff` variable on line 78:

```yaml
    enabled_diff: >-
      {{ {'current': current_ssid.enabled | default(false),
          'desired': desired_ssid.enabled | default(current_ssid.enabled | default(false))}
         if (desired_ssid.enabled | default(current_ssid.enabled | default(false)))
            != (current_ssid.enabled | default(false))
         else {} }}
```

Apply the same pattern to `authMode_diff`, `encryptionMode_diff`, `visible_diff`, `broadcast_diff`, `minBitrate_diff`, and `bandSelection_diff` (lines 79-84).

**Step 3: Fix lines 131-132 — wrap `compliant`/`drift_detected` expressions**

```yaml
    network_compliance: >-
      {{
        network_compliance | combine({
          'compliant': (network_compliance.ssids
            | selectattr('compliant', 'equalto', true)
            | list | length == network_compliance.ssids | length)
            if network_compliance.ssids | length > 0 else true,
          'drift_detected': (network_compliance.ssids
            | selectattr('drift_detected', 'equalto', true)
            | list | length > 0)
            if network_compliance.ssids | length > 0 else false,
          'drift_count': network_compliance.ssids
            | selectattr('drift_detected', 'equalto', true)
            | list | length
        })
      }}
```

**Step 4: Fix line 150 — wrap `ssids_non_compliant` expression**

```yaml
          'ssids_non_compliant': compliance_results.ssids_non_compliant
            + (network_compliance.ssids
               | selectattr('compliant', 'equalto', false)
               | list | length),
```

**Step 5: Fix security_baseline.yml lines 65 and 140**

Wrap the long message strings and set_fact expressions using `>-` folded block scalars.

**Step 6: Fix compliance_check.yml line 190**

Wrap the long `msg:` template line using YAML block scalar.

**Step 7: Verify no lines exceed 160 chars**

Run: `. venv/bin/activate && ansible-lint playbooks/ roles/ 2>&1 | grep 'line-length'`
Expected: No output.

**Step 8: Commit**

```bash
git add roles/meraki_compliance/tasks/main.yml roles/meraki_compliance/tasks/security_baseline.yml playbooks/compliance_check.yml
git commit -m "fix: wrap long Jinja2 expressions to stay under 160 char line limit"
```

---

### Task 6: Rename camelCase variables to snake_case

8 instances of `var-naming[pattern]` in `roles/meraki_compliance/tasks/main.yml`. The Meraki API returns camelCase field names, but Ansible vars should be snake_case.

**Files:**
- Modify: `roles/meraki_compliance/tasks/main.yml`

**Step 1: Rename the diff variables (lines 79-84, 91-96)**

| Old Name | New Name |
|---|---|
| `authMode_diff` | `auth_mode_diff` |
| `encryptionMode_diff` | `encryption_mode_diff` |
| `minBitrate_diff` | `min_bitrate_diff` |
| `bandSelection_diff` | `band_selection_diff` |

These appear in two places each: the `vars:` declaration (lines 79-84) and the `ssid_differences` dict assembly (lines 91-96).

Do a find-and-replace within the file:
- `authMode_diff` -> `auth_mode_diff` (lines 79, 91)
- `encryptionMode_diff` -> `encryption_mode_diff` (lines 80, 92)
- `minBitrate_diff` -> `min_bitrate_diff` (lines 83, 95)
- `bandSelection_diff` -> `band_selection_diff` (lines 84, 96)

Important: The dict *keys* in `ssid_differences` (like `'authMode'`, `'encryptionMode'`) and the `ssid_check_result.current` keys should stay camelCase because they mirror the Meraki API response fields. Only the *variable names* change.

**Step 2: Verify no var-naming[pattern] errors**

Run: `. venv/bin/activate && ansible-lint playbooks/ roles/ 2>&1 | grep 'var-naming\[pattern\]'`
Expected: No output.

**Step 3: Commit**

```bash
git add roles/meraki_compliance/tasks/main.yml
git commit -m "fix: rename camelCase diff variables to snake_case for ansible-lint"
```

---

### Task 7: Fix handler name casing

1 instance of `name[casing]` in `roles/meraki_ssid/handlers/main.yml:2`.

**Files:**
- Modify: `roles/meraki_ssid/handlers/main.yml`

**Step 1: Capitalize the handler name**

Change line 2 from:
```yaml
- name: log ssid changes
```
to:
```yaml
- name: Log SSID changes
```

**Step 2: Update any `notify:` references to this handler**

Search for `notify:` references in `roles/meraki_ssid/tasks/main.yml` and update to match.

Run: `grep -rn 'log ssid changes' roles/meraki_ssid/`

Change any matches from `log ssid changes` to `Log SSID changes`.

**Step 3: Verify no name[casing] errors**

Run: `. venv/bin/activate && ansible-lint playbooks/ roles/ 2>&1 | grep 'name\[casing\]'`
Expected: No output.

**Step 4: Commit**

```bash
git add roles/meraki_ssid/
git commit -m "fix: capitalize handler name for ansible-lint name[casing] rule"
```

---

### Task 8: Fix `community.general.github_issue` usage

The task "Create GitHub Issue for compliance violation" uses `community.general.github_issue` to *create* an issue, but this module is read-only — it only supports `action: get_status`. It requires `issue` (number) and `organization` params which are not provided. Replace with `ansible.builtin.uri` to call the GitHub API directly.

**Files:**
- Modify: `playbooks/compliance_check.yml:108-165`

**Step 1: Replace the `community.general.github_issue` task**

Replace the task at line 108 with:

```yaml
    - name: Create GitHub Issue for compliance violation
      ansible.builtin.uri:
        url: "https://api.github.com/repos/{{ compliance_github_repo }}/issues"
        method: POST
        headers:
          Authorization: "Bearer {{ compliance_github_token }}"
          Accept: "application/vnd.github+json"
        body_format: json
        body:
          title: >-
            Wireless Compliance Violation - {{ ansible_date_time.date }}
          body: "{{ lookup('template', 'compliance_issue.md.j2') }}"
          labels:
            - compliance
            - automated
        status_code: [201]
      when:
        - compliance_results is defined
        - compliance_failed | default(false) | bool
        - compliance_alerting_enabled | default(false) | bool
        - compliance_github_alert_enabled | default(false) | bool
      run_once: true
      delegate_to: localhost
      no_log: true
      tags: always
```

Note: The body template should be extracted to `roles/meraki_compliance/templates/compliance_issue.md.j2` to keep it maintainable. For now, you can use an inline body similar to the existing one but under 160 chars per line.

Alternatively, if you want to keep it simpler without a template file, construct the body inline:

```yaml
    - name: Create GitHub Issue for compliance violation
      ansible.builtin.uri:
        url: >-
          https://api.github.com/repos/{{ compliance_github_repo }}/issues
        method: POST
        headers:
          Authorization: "Bearer {{ compliance_github_token }}"
          Accept: "application/vnd.github+json"
        body_format: json
        body:
          title: >-
            Wireless Compliance Violation -
            {{ ansible_date_time.date }}
          body: >-
            ## Wireless Compliance Violation Detected

            **Date:** {{ ansible_date_time.iso8601 }}

            Networks Non-Compliant:
            {{ compliance_results.networks_non_compliant }}

            SSIDs Non-Compliant:
            {{ compliance_results.ssids_non_compliant }}
          labels:
            - compliance
            - automated
        status_code: [201]
      when:
        - compliance_results is defined
        - compliance_failed | default(false) | bool
        - compliance_alerting_enabled | default(false) | bool
        - compliance_github_alert_enabled | default(false) | bool
      run_once: true
      delegate_to: localhost
      no_log: true
      tags: always
```

**Step 2: Verify no args[module] error**

Run: `. venv/bin/activate && ansible-lint playbooks/ roles/ 2>&1 | grep 'args\[module\]'`
Expected: No output.

**Step 3: Commit**

```bash
git add playbooks/compliance_check.yml
git commit -m "fix: replace community.general.github_issue with ansible.builtin.uri for issue creation"
```

---

### Task 9: Set `strategy: linear` on compliance_check play

7 `run-once[task]` warnings because ansible-lint warns that `run_once` may behave differently with `strategy: free`. Setting `strategy: linear` explicitly silences this. (Already skipped in config from Task 2, but this is the proper fix if you want to un-skip later.)

> Note: This is already handled by the skip_list in Task 2. This task is OPTIONAL — only do it if you want to remove `run-once[task]` from the skip_list later.

**Files:**
- Modify: `playbooks/compliance_check.yml`

**Step 1: Add `strategy: linear` to the alerting play**

Find the play block that contains the `run_once` tasks (the alerting section, around line 30) and add `strategy: linear`:

```yaml
- name: Compliance alerting and reporting
  hosts: meraki_networks
  strategy: linear
  gather_facts: true
```

**Step 2: Commit (if applied)**

```bash
git add playbooks/compliance_check.yml
git commit -m "fix: set strategy linear on compliance play to satisfy run-once rule"
```

---

### Task 10: Final verification — full lint pass

**Step 1: Run full ansible-lint**

```bash
. venv/bin/activate && ansible-lint playbooks/ roles/
```

Expected: `Passed: 0 failure(s), 0 warning(s)` (or only the warnings you've chosen to keep).

**Step 2: Run yamllint**

```bash
. venv/bin/activate && yamllint -c .yamllint playbooks/ roles/ group_vars/ inventory/ .pre-commit-config.yaml
```

Expected: No errors. Warnings for line-length (>160) only if any remain.

**Step 3: Run syntax checks**

```bash
. venv/bin/activate && ansible-playbook --syntax-check playbooks/ssid_management.yml && \
ansible-playbook --syntax-check playbooks/compliance_check.yml && \
ansible-playbook --syntax-check playbooks/config_snapshot.yml
```

Expected: All pass.

**Step 4: Commit final state if any stragglers**

```bash
git add -A
git commit -m "chore: fix remaining lint issues"
```

---

## Execution Order

Tasks 1-3 must go first (config fixes). Tasks 4-8 can be parallelized. Task 9 is optional. Task 10 is the final gate.

```
Task 1 (create .yamllint) ──┐
Task 2 (fix .ansible-lint) ──┼── Task 4 (trailing spaces) ──┐
Task 3 (fix requirements) ──┘   Task 5 (line length) ───────┤
                                Task 6 (camelCase vars) ─────┼── Task 10 (verify)
                                Task 7 (handler name) ───────┤
                                Task 8 (github_issue) ───────┤
                                Task 9 (strategy) ───────────┘
```
