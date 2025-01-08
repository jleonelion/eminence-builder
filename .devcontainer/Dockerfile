FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install libgtk for browsers
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libdrm2 \
    libgbm1 \
    libasound2 \
    libx11-xcb1

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
# Install python packages
RUN pip install playwright notebook poetry


# Install Terraform
RUN apt-get update && \
    apt-get install -y gnupg software-properties-common && \
    wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
