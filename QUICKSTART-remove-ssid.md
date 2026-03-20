# Quick Start: Remove an SSID

## The Easiest Way (Recommended)

```bash
make remove-ssid-menu
```

That's it! The interactive menu will:
1. Show you all your networks
2. Show you all SSIDs (from Meraki and config files)
3. Let you select with numbers (no typing!)
4. Clean up everything automatically

## What You'll See

```
═══════════════════════════════════════════════════════════
  SSID Removal Tool - Interactive Menu
═══════════════════════════════════════════════════════════

  Fetching networks...

═══════════════════════════════════════════════════════════
  Available Networks
═══════════════════════════════════════════════════════════

  [ 1] LAB-Site1
  [ 2] LAB-Site2
  [ 3] Home
  [ 0] All networks

═══════════════════════════════════════════════════════════

Select network number (0 for all): 1

  Fetching SSIDs from LAB-Site1...

═══════════════════════════════════════════════════════════
  Available SSIDs
═══════════════════════════════════════════════════════════

  From Selected Network:
  [ 1] Corp-Secure                      (✓ enabled)
  [ 2] Corp-Guest                       (✓ enabled)
  [ 3] test                             (✓ enabled)

  From Config Files Only:
  [ 4] Corp-Secur                       (config only)

  [ 0] Enter SSID name manually

═══════════════════════════════════════════════════════════

Select SSID number (0 for manual entry): 4

═══════════════════════════════════════════════════════════
  Selection Complete
═══════════════════════════════════════════════════════════
  SSID: Corp-Secur
  Network: LAB-Site1
═══════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════
  Execution Plan
═══════════════════════════════════════════════════════════
  SSID to remove : Corp-Secur
  Target network : LAB-Site1
  Actions        : Remove from Meraki (if exists) + Cleanup config files
═══════════════════════════════════════════════════════════

NOTE: Config files will be cleaned up even if SSID is not found in Meraki.

Proceed with removal? [y/N]: y

Removing SSID 'Corp-Secur' from network: LAB-Site1
[Ansible playbook runs...]
```

## What Gets Cleaned Up

✅ **Meraki Network** - SSID removed (if it exists)  
✅ **group_vars/meraki_orgs.yml** - Removed from deployment config  
✅ **group_vars/meraki_networks.yml** - Removed from compliance state  
✅ **baselines/*/ssids.yml** - Removed from snapshots  

## Special Cases Handled

### Config-Only SSIDs (Typos)

If you see `(config only)` next to an SSID, it means:
- It exists in your config files
- But not in Meraki (maybe a typo or already removed)
- **The menu will clean it up for you!**

### SSID Not Found

If the SSID isn't in Meraki:
```
SSID "Corp-Secur" not found in network LAB-Site1.
Will still clean up configuration files.

✅ Cleaned from group_vars/meraki_orgs.yml
✅ Cleaned from group_vars/meraki_networks.yml
✅ Cleaned from baselines/L_*/ssids.yml
```

**No problem!** Config files are cleaned anyway.

## Other Options

### Preview First (Dry Run)
```bash
make remove-ssid-check
# Shows what would happen without making changes
```

### Manual Input (Without Menu)
```bash
make remove-ssid
# Type SSID name and network manually
```

## Troubleshooting

### "Run 'make setup' first"
```bash
make setup
```

### "ModuleNotFoundError: No module named 'requests'"
```bash
make setup
# or
pip install requests pyyaml
```

### "ERROR: MERAKI_DASHBOARD_API_KEY not found"
Check your `.env` file:
```bash
cat .env | grep MERAKI_DASHBOARD_API_KEY
```

## Summary

**Just remember:**
```bash
make remove-ssid-menu
```

The menu handles everything else! 🎉

## Documentation

- **Full Guide**: `docs/interactive-ssid-removal.md`
- **Make Targets**: `docs/make-remove-ssid.md`
- **Quick Reference**: `docs/QUICKREF-remove-ssid.md`
- **All Fixes**: `docs/CHANGELOG-ssid-cleanup.md`
