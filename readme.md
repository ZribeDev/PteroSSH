# PteroSSH Guide

This guide walks you through the steps to configure your Pterodactyl panel and connect to your server's websocket.

## Prerequisites

Before starting, ensure you have:

- SSH access to the server where Pterodactyl is hosted.
- The `connect.py` Python script available on the server.
- Permissions to edit the Pterodactyl configuration file (if necessary).

## Steps

### 1. SSH Connection

First, connect to your server using SSH. Replace `your_username` and `your_server_ip` with your actual SSH username and server IP address.

```bash
ssh your_username@your_server_ip
```

### 2. Modify Pterodactyl Configuration

Run the following commands as root user:

```bash
sed -i '/allowed_origins: \[\]/c\allowed_origins:\n- '\''*'\''' /etc/pterodactyl/config.yml
systemctl restart wings
```

- After running these commands you can exit SSH!

### 3. Execute the Connect Script

```bash
python connect.py <server_id>
```

- The `<server_id>` can be found by looking at the URL when viewing your server on the Pterodactyl panel.

### 4. Obtain API Key and Panel URL

To complete the connection, you need your API key and the URL of the Pterodactyl panel.

- Go to your profile on the Pterodactyl panel to find or generate your API key.
- The panel URL is the base URL you use to access the Pterodactyl website.

### 5. Input API Key and Panel URL

When prompted by the `connect.py` script, input the API key and the URL of the Pterodactyl panel to finally connect.
