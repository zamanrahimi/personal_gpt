provider "aws" {
  region = "us-east-1"
}

# Data source: Get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Security Group to allow HTTP access
resource "aws_security_group" "web_sg" {
  name        = "web_sg"
  description = "Allow HTTP traffic"
  ingress {
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
    cidr_blocks = ["0.0.0.0/0"]  # 
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "hello_world" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  key_name      = "rtp-03"  # Replace with your existing key pair name

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              set -ex

              # Update packages and install Docker
              yum update -y
              amazon-linux-extras install docker -y
              service docker start
              usermod -a -G docker ec2-user
              systemctl enable docker

              # Create a FastAPI app directory
              mkdir /home/ec2-user/fastapi-app
              cd /home/ec2-user/fastapi-app

              # Write FastAPI app code
              cat > main.py <<APP
              from fastapi import FastAPI

              app = FastAPI()

              @app.get("/")
              def read_root():
                  return {"message": "Hello from FastAPI in Docker on EC2!"}
              APP

              # Write Dockerfile
              cat > Dockerfile <<DOCKER
              FROM python:3.12-slim

              WORKDIR /app
              COPY main.py /app/

              RUN pip install --no-cache-dir fastapi uvicorn

              CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
              DOCKER

              # Build Docker image and run it
              docker build -t fastapi-app .
              docker run -d -p 80:80 --name fastapi-container fastapi-app
            EOF





  tags = {
    Name = "HelloWorldInstance"
  }
}
