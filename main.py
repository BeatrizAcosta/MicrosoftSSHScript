#SSHKey Windows Script for two accounts
import os
import subprocess
from pathlib import Path

#Settings
email_personal = "your_personal_email@example.com"   # Personal GitHub email
email_work = "your_work_email@example.com"           # Work GitHub email

repo_owner = "YourGitHubUsername"                   
repo_name = "YourRepositoryName"                  

#Paths
ssh_dir = Path.home() / ".ssh"
key_personal = ssh_dir / "id_ed25519_personal"
key_work = ssh_dir / "id_ed25519_work"
config_path = ssh_dir / "config"

#Ensure ~/.ssh exists
ssh_dir.mkdir(parents=True, exist_ok=True)

def ensure_keypair(private_key_path, email):
    """Generate an SSH key pair if missing, and ensure public key exists."""
    pub_key_path = private_key_path.with_suffix(".pub")
    
    if not private_key_path.exists():
        print(f"Generating key for {email} at {private_key_path} ...")
        subprocess.run([
            "ssh-keygen", "-t", "ed25519",
            "-C", email,
            "-f", str(private_key_path),
            "-N", ""  # No passphrase
        ], check=True)
    else:
        print(f"Private key exists: {private_key_path}")
    
    if not pub_key_path.exists():
        print(f"Public key missing; recreating {pub_key_path} from private key...")
        with open(pub_key_path, "w") as pub_file:
            subprocess.run(["ssh-keygen", "-y", "-f", str(private_key_path)], stdout=pub_file, check=True)

#Ensure keys & .pub files exist
ensure_keypair(key_personal, email_personal)
ensure_keypair(key_work, email_work)

#SSH config
id_personal = str(key_personal).replace("\\", "/")
id_work = str(key_work).replace("\\", "/")

config_content = f"""# Personal: applies to git@github.com:<owner>/<repo>.git
Host github.com
  HostName github.com
  User git
  IdentityFile {id_personal}
  IdentitiesOnly yes

# Optional Work alias (use if pushing to a work repo)
Host github-work
  HostName github.com
  User git
  IdentityFile {id_work}
  IdentitiesOnly yes
"""

with open(config_path, "w", encoding="ascii") as cfg:
    cfg.write(config_content)

#Public Keys 
print("\n== Public keys to add on GitHub ==")
print("\n--- Personal (.pub) ---")
print(key_personal.with_suffix(".pub").read_text())

print("\n--- Work (.pub) ---")
print(key_work.with_suffix(".pub").read_text())

input("\nAdd the personal key to your personal GitHub account, "
      "and the work key to your work GitHub account. Press Enter to test...")
print("\nTesting PERSONAL via github.com")
subprocess.run(["ssh", "-T", "-o", "IdentitiesOnly=yes", "-o", "StrictHostKeyChecking=accept-new", "git@github.com"])

print("\nTesting WORK via alias...")
subprocess.run(["ssh", "-T", "-o", "IdentitiesOnly=yes", "-o", "StrictHostKeyChecking=accept-new", "git@github-work"])

#Push 
print("\nTo link your repo and push with your personal key:")
print(f"  git remote set-url origin git@github.com:{repo_owner}/{repo_name}.git")
print("  git push -u origin main")
