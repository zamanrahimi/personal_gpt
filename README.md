# Deployment

✅ Step-by-Step: Deploy via GitHub Actions
🔹 1. Ensure EC2 is Ready
Port 22 (SSH) and 80 (HTTP) open in EC2 security group.

Docker is installed and running.

Your EC2 public IP is available.

```bash
ssh-keygen -t rsa -b 4096 -f deploy_key

Add deploy_key.pub to ~/.ssh/authorized_keys on your EC2 instance:

# in EC2
mkdir -p ~/.ssh
echo "<contents-of-deploy_key.pub>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
