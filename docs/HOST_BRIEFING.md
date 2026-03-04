# Host Briefing: Meraki Wireless Ansible Episode

**Episode**: Unplugged Connectivity - Network Automation with Ansible and Meraki  
**Host**: Dan Klamert  
**Format**: Tutorial/Hands-on walkthrough  
**Target Audience**: Network engineers and DevOps professionals (beginner to intermediate)

---

## Episode Overview

This episode demonstrates how to automate Cisco Meraki wireless network management using Ansible. Viewers will learn to set up the project, configure API access, and run playbooks for SSID management, bulk AP deployment, and compliance checking.

**Key Learning Outcomes:**
- Setting up Ansible for network automation
- Using the Meraki API with Ansible
- Creating and running playbooks
- Understanding Ansible roles and inventory
- Troubleshooting common issues

---

## Episode Structure & Suggested Questions

### Segment 1: Introduction (0:00 - 5:00)

**Opening Hook Questions:**
- "How many of you spend hours manually configuring wireless networks?"
- "What if you could automate SSID management across hundreds of access points?"
- "Today we're going to automate Meraki wireless networks with Ansible - let's see how it works."

**Transition Cue:**
> "Before we dive in, let's talk about what we're building and why it matters."

**Key Points to Cover:**
- What is network automation and why it matters
- Ansible vs other automation tools (why Ansible for networks)
- Meraki API capabilities
- What viewers will build today

**Suggested Questions:**
- "For those new to Ansible, can you explain what makes it different from other automation tools?"
- "Why did you choose Ansible specifically for network automation?"
- "What are the main pain points this solves for network engineers?"

---

### Segment 2: Prerequisites & Meraki API Setup (5:00 - 15:00)

**Transition Cue:**
> "Before we start coding, let's make sure everyone has what they need. You'll need access to a Meraki organization - even a small test network works."

**Key Points:**
- Prerequisites (Python, Git, Make)
- Setting up Meraki API access in Dashboard
- How to generate an API key
- Using a test org/network for safe learning

**Suggested Questions:**
- "What kind of Meraki setup do viewers need to follow along?"
- "Walk us through enabling API access and getting an API key"
- "Should viewers use a test network or is it safe on production?"
- "For someone who's never used the Meraki API before, what should they know?"

**"Intentional Skeptic" Moments:**
- "Is it safe to run this against a production network?"
- "What if someone doesn't have Python 3.12 - can they still follow along?"
- "What happens if I make a mistake with the API - can I undo it?"

**Transition Cue:**
> "Now that we have our API access set up, let's get the project on our machines."

---

### Segment 3: Forking & Cloning (15:00 - 20:00)

**Transition Cue:**
> "The code is already written - we just need to get it on our machines. Let's fork and clone the repository."

**Key Points:**
- Why fork instead of clone directly
- How to fork on GitHub
- Cloning your fork
- Understanding the repository structure

**Suggested Questions:**
- "Why should viewers fork instead of just cloning?"
- "What's the difference between forking and cloning?"
- "Can you give us a quick tour of the repository structure?"

**"Intentional Skeptic" Moments:**
- "Do viewers need to know Git to follow along?"
- "What if someone just wants to download the code without Git?"

**Transition Cue:**
> "Great! Now we have the code. Let's set up our environment and get everything installed."

---

### Segment 4: Environment Setup (20:00 - 30:00)

**Transition Cue:**
> "Setting up Python projects can be intimidating, but we've made it easy with a single command."

**Key Points:**
- Virtual environments - why they matter
- Running `make setup` (one command setup)
- Activating virtual environment
- Installing dependencies and collections
- Verifying installation

**Suggested Questions:**
- "Why use a virtual environment instead of installing globally?"
- "What exactly does `make setup` do behind the scenes?"
- "How do viewers know if everything installed correctly?"
- "What if someone doesn't have Make installed?"

**"Intentional Skeptic" Moments:**
- "Virtual environments always confuse me - can you explain why we need this?"
- "What if the setup fails? How do viewers troubleshoot?"
- "Is there a way to set this up without Make?"

**Transition Cue:**
> "Perfect! Now for the important part - configuring our API credentials securely."

---

### Segment 5: API Key Configuration (30:00 - 35:00)

**Transition Cue:**
> "We need to connect to Meraki, but we need to do it securely. Let's configure our API key."

**Key Points:**
- Copying `.env.example` to `.env`
- Adding API key and organization ID
- Why `.env` is gitignored
- Alternative: Ansible Vault for production
- Testing the connection

**Suggested Questions:**
- "Why use a `.env` file instead of hardcoding the API key?"
- "Is it safe to commit the `.env` file to Git?"
- "When should someone use Ansible Vault instead of `.env`?"
- "How do we verify the API key works?"

**"Intentional Skeptic" Moments:**
- "Wait, isn't storing API keys in a file a security risk?"
- "What if someone accidentally commits their `.env` file?"
- "How is Ansible Vault different from just using `.env`?"

**Transition Cue:**
> "Everything's configured - let's run our first playbook and see it in action!"

---

### Segment 6: Running First Playbook (35:00 - 45:00)

**Transition Cue:**
> "This is the moment of truth - let's execute our first Ansible playbook and automate some Meraki configuration."

**Key Points:**
- Syntax check first (`--syntax-check`)
- Understanding playbook output
- What "ok" vs "changed" means
- Verbose mode for debugging (`-vvv`)
- Interpreting results

**Suggested Questions:**
- "What does `--syntax-check` do and why run it first?"
- "Can you explain what we're seeing in this output?"
- "What's the difference between 'ok' and 'changed' in Ansible?"
- "What if the playbook fails - how do we debug it?"

**"Intentional Skeptic" Moments:**
- "This looks like it's just reading data - where's the actual automation?"
- "What if I run this playbook twice - will it break anything?"
- "How do I know this actually worked if I can't see the Meraki dashboard?"

**Transition Cue:**
> "That was cool, but we can do more. Let's look at how to detect configuration drift and maintain a source of truth."

---

### Segment 6.5: Configuration Drift Detection (45:00 - 50:00)

**Transition Cue:**
> "Now that we've run our first playbook, let's talk about one of the most powerful features - configuration drift detection."

**Key Points:**
- What is configuration drift and why it matters
- Establishing a "golden network" baseline
- Group policy drift detection
- Check mode vs auto-remediation
- Generating drift reports

**Demo Flow:**
1. Show the source of truth in `group_vars/all.yml` (group policies)
2. Run drift detection in check mode: `ansible-playbook playbooks/group_policy_drift.yml --check`
3. Manually change a group policy in Meraki Dashboard (bandwidth limit)
4. Run drift detection again to show the drift
5. Run in remediation mode to auto-correct the drift
6. Show the generated markdown report

**Suggested Questions:**
- "What is configuration drift and why should I care about it?"
- "How does this help with security and compliance?"
- "Can you show us an example of drift detection in action?"
- "What happens when drift is detected - does it automatically fix it?"
- "How often should someone run these drift checks?"

**"Intentional Skeptic" Moments:**
- "Why not just make changes directly in the Dashboard when needed?"
- "What if someone intentionally changed a configuration - won't this break it?"
- "This seems like it could be dangerous - what if it reverts an emergency fix?"
- "How do I know which changes were intentional vs drift?"

**Transition Cue:**
> "Understanding how this all works will help you customize it for your needs. Let's look under the hood."

---

### Segment 7: Architecture Deep Dive (50:00 - 55:00)

**Transition Cue:**
> "Understanding how Ansible connects everything together will help you customize this for your own needs."

**Key Points:**
- Inventory files (where playbooks run)
- Group variables (configuration)
- Playbooks (what to do)
- Roles (how to do it)
- Data flow: inventory → playbooks → roles → Meraki API

**Suggested Questions:**
- "Can you walk us through how Ansible knows where to run this playbook?"
- "What's the difference between a playbook and a role?"
- "How do variables flow from inventory to roles?"
- "If I want to add my own network, what do I need to change?"

**"Intentional Skeptic" Moments:**
- "This seems like a lot of moving parts - is it really simpler than just using the Meraki dashboard?"
- "Why separate playbooks and roles? Couldn't you just put everything in one file?"
- "What if I want to run this against multiple organizations?"

**Transition Cue:**
> "Things don't always go smoothly. Let's talk about common issues and how to fix them."

---

### Segment 8: Troubleshooting (55:00 - 60:00)

**Transition Cue:**
> "You're going to run into issues - everyone does. Let's cover the most common problems and how to solve them."

**Key Points:**
- Rate limiting (429 errors)
- Authentication failures (401 errors)
- Sandbox limitations
- Python/Ansible version issues
- Debugging with `-vvv`

**Suggested Questions:**
- "What's the most common error viewers will hit?"
- "How do you debug when a playbook fails?"
- "What should someone do if they get rate limited?"
- "What if the API key stops working?"

**"Intentional Skeptic" Moments:**
- "What if none of these solutions work?"
- "How do I know if it's my code or a Meraki API issue?"
- "Is there a way to test without hitting the API?"

**Transition Cue:**
> "We've covered a lot. Let's wrap up with next steps and answer your questions."

---

### Segment 9: Q&A & Next Steps (60:00+)

**Suggested Questions to Address:**
- "What are the next playbooks viewers should try?"
- "How do you use the group policy drift detection in production?"
- "How do you customize this for production use?"
- "Can this work with other network vendors?"
- "What other Meraki operations can be automated?"
- "How do you contribute improvements back to the project?"
- "What about firewall rule drift or SSID policy drift?"

**Closing Points:**
- Link to repository
- Documentation links
- How to contribute
- What to learn next

---

## Ansible Glossary for Host

**Quick reference for explaining Ansible terms naturally:**

### Core Concepts

- **Playbook**: A YAML file that defines what to automate (the "recipe")
- **Role**: Reusable collection of tasks, variables, and templates (the "ingredients")
- **Inventory**: List of hosts/systems to manage (the "where")
- **Task**: A single action to perform (e.g., "create SSID")
- **Module**: The tool that performs the action (e.g., `cisco.meraki.networks_ssids`)
- **Handler**: A task that runs only when notified (like a callback)
- **Variable**: A value that can change (like `meraki_api_key`)

### Execution Terms

- **Idempotent**: Running multiple times produces the same result (safe to rerun)
- **Check Mode**: Dry run - shows what would change without making changes
- **Gather Facts**: Collect information about target systems (we disable this for API)
- **Become**: Escalate privileges (like sudo - we don't need this for API)

### Output Terms

- **ok**: Task completed, no changes needed (desired state already met)
- **changed**: Task made changes (something was modified)
- **failed**: Task encountered an error
- **skipped**: Task was skipped (condition not met)

### File Types

- **YAML**: Human-readable data format (`.yml` files)
- **Jinja2**: Template engine for dynamic content (`.j2` files)
- **Vault**: Encrypted file for secrets (`ansible-vault`)

---

## "Intentional Skeptic" Moments

**These are moments where Dan should play devil's advocate or ask "dumb" questions that viewers are thinking:**

### Setup Phase
- "Why is this so complicated? Can't we just install Ansible and go?"
- "Do I really need all these dependencies?"
- "What if I'm on Windows - will this work?"

### Configuration Phase
- "Why not just hardcode the API key in the playbook?"
- "Is a small test network enough to learn on?"
- "What if I lose my API key?"

### Execution Phase
- "How do I know this actually worked?"
- "What if I run this twice - will it break something?"
- "Can I undo changes if something goes wrong?"

### Architecture Phase
- "Why so many files? Couldn't this be simpler?"
- "What's the benefit over just using the Meraki dashboard?"
- "Is this really faster than doing it manually?"

### Troubleshooting Phase
- "What if nothing in the troubleshooting guide helps?"
- "How do I know if it's my fault or Meraki's fault?"
- "Is there a way to test without using real API calls?"

**How to Use These:**
- Don't script these - let them come naturally
- Use them to address common viewer concerns
- They make the content more relatable
- They help viewers feel their questions are valid

---

## Transition Phrases

**Use these to smoothly move between segments:**

- "Now that we have X, let's Y..."
- "Before we move on, let's make sure..."
- "This is cool, but here's what's really interesting..."
- "You might be wondering..."
- "Let's pause here and talk about..."
- "Here's where it gets interesting..."
- "Before we dive deeper..."
- "Let's take a step back and understand..."

---

## Visual Cues for Host

### When to Show Terminal
- During setup commands
- When running playbooks
- When showing error messages
- When demonstrating troubleshooting

### When to Show Code/Config Files
- Explaining inventory structure
- Showing variable definitions
- Demonstrating playbook structure
- Explaining role organization

### When to Show Meraki Dashboard
- Verifying API key works
- Showing where to find organization ID
- Demonstrating what was changed
- Comparing manual vs automated approach

### When to Use Diagrams
- Explaining data flow (inventory → playbook → role → API)
- Showing project structure
- Explaining variable precedence
- Demonstrating execution flow

---

## Common Viewer Questions (Be Ready)

### Beginner Questions
- "Do I need to know Python?"
- "Can I use this on Windows?"
- "What if I don't have Meraki hardware?"
- "Is Ansible free?"
- "How is this different from Terraform?"

### Intermediate Questions
- "How do I add my own networks?"
- "Can I customize the playbooks?"
- "How do I handle multiple environments?"
- "What about error handling?"
- "How do I test playbooks safely?"

### Advanced Questions
- "How do I extend this for other vendors?"
- "Can I integrate this with CI/CD?"
- "What about state management?"
- "How do I handle secrets in production?"
- "What's the performance impact?"

---

## Key Talking Points (Don't Forget)

1. **Security**: Always emphasize not committing secrets, using vaults, etc.
2. **Idempotency**: Explain why it's safe to run playbooks multiple times
3. **Sandbox vs Production**: Clear distinction and when to use each
4. **Beginner-Friendly**: Reassure viewers this is approachable
5. **Real-World**: Connect to actual network engineering scenarios
6. **Community**: Mention how to contribute and get help

---

## Post-Episode Checklist

After recording, ensure:
- [ ] Repository link is in description
- [ ] All documentation links work
- [ ] Meraki Developer Hub link is current
- [ ] Timestamps are accurate
- [ ] Code examples match what's shown
- [ ] No API keys visible in video
- [ ] All commands shown are correct

---

## Notes for Host

- **Pace**: Don't rush - viewers need time to follow along
- **Errors**: If something breaks, that's great content! Show troubleshooting
- **Pauses**: Give viewers time to type commands
- **Encouragement**: Remind viewers it's okay to pause and catch up
- **Real Talk**: Acknowledge when something is tricky or confusing
- **Next Steps**: Always end with clear next steps

---

**Remember**: Viewers are learning. Go slow, explain why, and make it relatable. Good luck! 🎥
