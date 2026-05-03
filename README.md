## botCommander

**botCommander** is a lightweight, **Flask-based** management panel designed for streamlined administration of Telegram bot fleets. The project automates the bot lifecycle by leveraging the **Docker API** for process isolation and management.

Instead of manually managing containers via the terminal, botCommander provides a centralized interface to deploy, monitor, and stop your bots with ease.

---

### 🚀 Key Features

*   **Docker API Integration:** Start, stop, and restart bots as individual Docker containers.
*   **Flask Web Interface:** An intuitive dashboard to control all active processes.
*   **Dynamic Configuration:** Inject environment variables (such as `API_TOKEN`) directly into containers upon launch.
*   **Status Monitoring:** Real-time tracking of container states (running/stopped/exited).
*   **Full Isolation:** Each bot operates in its own environment, eliminating dependency conflicts.

---

### 🛠 Tech Stack

*   **Python 3.12+**
*   **Flask** (Backend & Web UI)
*   **Docker SDK for Python** (Interaction with Docker Engine)
*   **uvicorn** (Recommended for production deployment)

---

### 📋 Prerequisites

The host system must have Docker installed and the current user must have access permissions to the Docker socket (`/var/run/docker.sock`).

```bash
# Verify Docker is running
docker --version
```

---

### 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DollaR84/botCommander.git
   cd botCommander
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r src/requirements.txt
   ```
   
   3. **pre-init:**
   ```bash
   chmod +x init.sh
   ./init.sh
   ```

### 🐳 Running with Docker

You can also run **botCommander** itself inside a container. To do this, ensure you mount the Docker socket:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

### 🤝 Contributing

Pull requests and bug reports are welcome! If you have ideas for improving functionality or security, feel free to open a new Issue.

---
