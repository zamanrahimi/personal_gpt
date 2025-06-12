provider "aws" {
  region = "us-east-1"
}

# ✅ Latest Ubuntu 22.04 AMI from Canonical
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ✅ Security Group to allow HTTP and SSH
resource "aws_security_group" "web_sg" {
  name        = "web_sg"
  description = "Allow HTTP and SSH traffic"
  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ✅ EC2 Instance with Docker, Git, and Ollama setup
resource "aws_instance" "personal_gpt" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.large" # ⛔ t2.micro may not be enough to run Ollama; use t2.medium or larger
  key_name      = "rtp-03"    # 🔁 Replace with your key name

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # ⬇️ Increase root volume size
  root_block_device {
    volume_size = 30  # Minimum 30 GB
    volume_type = "gp2"
  }

  user_data = <<-EOF
              #!/bin/bash
              set -ex

              # Update and install Docker
              apt update -y
              apt install -y docker.io git curl

              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu

              # Install Ollama
              curl -fsSL https://ollama.com/install.sh | sh

              # Create systemd service for Ollama
              cat <<EOT | sudo tee /etc/systemd/system/ollama.service
              [Unit]
              Description=Ollama Service
              After=network.target docker.service
              Requires=docker.service

              [Service]
              ExecStart=/usr/local/bin/ollama serve
              Restart=always
              User=ubuntu
              WorkingDirectory=/home/ubuntu
              Environment=OLLAMA_MODELS=/home/ubuntu/.ollama/models

              [Install]
              WantedBy=multi-user.target
              EOT

              # Enable and start the Ollama service
              systemctl daemon-reexec
              systemctl daemon-reload
              systemctl enable ollama
              systemctl start ollama

              # Wait a bit and pull model
              sleep 10
              sudo -u ubuntu /usr/local/bin/ollama run llama3 --model-only
 
  
              EOF

  tags = {
    Name = "personal_gpt"
  }
}

# ✅ Elastic IP association (replace allocation_id with yours)
resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.personal_gpt.id
  allocation_id = "eipalloc-0e9890f51b3d2da8b"
}
