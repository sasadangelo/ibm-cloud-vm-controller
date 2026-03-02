# IBM Cloud VSI Controller — MCP Server

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://docs.astral.sh/uv/)

**IBM Cloud VM Controller** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes tools to manage **Virtual Server Instances (VSIs)** on IBM Cloud VPC.

It enables AI assistants (such as Claude, Cursor, or any MCP-compatible client) to autonomously **list**, **create**, **start**, **stop**, and **delete** IBM Cloud virtual machines through natural language — without writing a single line of code.

---

## 📋 Table of Contents

- [IBM Cloud VM Controller — MCP Server](#ibm-cloud-vm-controller--mcp-server)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🧱 Architecture](#-architecture)
  - [✅ Prerequisites](#-prerequisites)
  - [📦 Installation](#-installation)
    - [1. Clone the repository](#1-clone-the-repository)
    - [2. Install dependencies with `uv`](#2-install-dependencies-with-uv)
  - [⚙️ Configuration](#️-configuration)
    - [Environment variables (`.env`)](#environment-variables-env)
    - [Logging (`src/config.yaml`)](#logging-srcconfigyaml)
  - [🚀 Running the MCP Server](#-running-the-mcp-server)
    - [Development mode (with MCP Inspector)](#development-mode-with-mcp-inspector)
    - [Production mode](#production-mode)
  - [🛠️ MCP Tools Reference](#️-mcp-tools-reference)
    - [`list_vsi`](#list_vsi)
    - [`create_vsi`](#create_vsi)
    - [`start_vsi`](#start_vsi)
    - [`stop_vsi`](#stop_vsi)
    - [`delete_vsi`](#delete_vsi)
  - [🤖 Integrating with Claude Desktop](#-integrating-with-claude-desktop)
  - [🧪 Running Unit Tests](#-running-unit-tests)
  - [📁 Project Structure](#-project-structure)
  - [📄 License](#-license)

---

## ✨ Features

| Tool         | Description                                                          |
| ------------ | -------------------------------------------------------------------- |
| `list_vsi`   | List all VSIs in a given IBM Cloud region                            |
| `create_vsi` | Provision a new VSI with custom profile, image, and network settings |
| `start_vsi`  | Start a stopped VSI by ID                                            |
| `stop_vsi`   | Stop a running VSI by ID                                             |
| `delete_vsi` | Delete a stopped VSI by ID                                           |

---

## 🧱 Architecture

The server is built on top of [FastMCP](https://github.com/modelcontextprotocol/python-sdk) and follows a clean, layered architecture:

```
MCP Client (Claude, Cursor, …)
        │
        ▼
  MCP Server (FastMCP)          ← src/mcp_server.py
        │
        ▼
  VSIController (Service Layer) ← src/services/vsi_client.py
        │
        ▼
  Command Objects               ← src/services/commands/
  (list / create / start / stop / delete)
        │
        ▼
  IBM VPC Python SDK            ← ibm-vpc
```

Each operation is encapsulated in a dedicated **Command** class following the [Command Pattern](https://refactoring.guru/design-patterns/command). The IBM VPC client is managed as a **Singleton** per region.

See [docs/architecture.md](docs/architecture.md) for the full class diagram and design details.

---

## ✅ Prerequisites

| Tool                                        | Purpose                                 |
| ------------------------------------------- | --------------------------------------- |
| [Python ≥ 3.13](https://www.python.org/)    | Runtime                                 |
| [uv](https://docs.astral.sh/uv/)            | Fast Python package and project manager |
| [IBM Cloud account](https://cloud.ibm.com/) | Target cloud platform                   |
| IBM Cloud API Key                           | Authentication credential               |

> **Note:** `uv` replaces Poetry in this project. It handles virtual environments and dependency installation automatically.

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/sasadangelo/ibm-cloud-vm-controller.git
cd ibm-cloud-vm-controller
```

### 2. Install dependencies with `uv`

```bash
uv sync
```

This will create a virtual environment and install all required dependencies automatically.

---

## ⚙️ Configuration

### Environment variables (`.env`)

Copy the sample file and fill in your IBM Cloud credentials:

```bash
cp src/.env-sample src/.env
```

Edit `src/.env`:

```dotenv
# IBM Cloud API key — required for authentication
API_KEY=<your_ibm_cloud_api_key>

# Default region (used by main.py only; MCP tools accept region as a parameter)
IBM_REGION=us-east

# VPC and network settings (used by main.py and create_vsi tool)
VPC_ID=<your-vpc-id>
SUBNET_ID=<your-subnet-id>
IMAGE_ID=<your-image-id>
SSH_KEY_ID=<your-ssh-key-id>
VSI_PROFILE=bx2-2x8
```

> **Tip:** Retrieve your IBM Cloud resource IDs using the IBM Cloud CLI:
>
> ```bash
> ibmcloud is vpcs
> ibmcloud is subnets
> ibmcloud is images --visibility public | grep ubuntu
> ibmcloud is keys
> ```

### Logging (`src/config.yaml`)

Logging behaviour is controlled via `src/config.yaml`:

```yaml
log:
  level: INFO
  console: true
  file: null # Set a path (e.g. "logs/app.log") to enable file logging
  rotation: "10 MB"
  retention: "7 days"
  compression: "zip"
```

---

## 🚀 Running the MCP Server

### Development mode (with MCP Inspector)

```bash
uv run mcp dev src/mcp_server.py
```

This starts the server and opens the **MCP Inspector** in your browser, allowing you to interactively test all tools.

### Production mode

```bash
uv run python src/mcp_server.py
```

---

## 🛠️ MCP Tools Reference

All tools are exposed via the MCP protocol and can be invoked by any compatible AI client.

---

### `list_vsi`

List all Virtual Server Instances in a given IBM Cloud region.

**Parameters:**

| Name     | Type     | Required | Description                                            |
| -------- | -------- | -------- | ------------------------------------------------------ |
| `region` | `string` | ✅       | IBM Cloud region (e.g. `us-south`, `us-east`, `eu-de`) |

**Returns:** `list[dict]` — each item contains `id`, `name`, `status`, `zone`, `cpu`, `ram`.

**Example response:**

```json
[
  {
    "id": "0757-abc12345-...",
    "name": "my-web-server",
    "status": "running",
    "zone": "us-east-1",
    "cpu": 2,
    "ram": 8
  }
]
```

---

### `create_vsi`

Provision a new Virtual Server Instance.

**Parameters:**

| Name          | Type           | Required | Default   | Description                                   |
| ------------- | -------------- | -------- | --------- | --------------------------------------------- |
| `region`      | `string`       | ✅       | —         | IBM Cloud region                              |
| `name`        | `string`       | ✅       | —         | VSI name (lowercase alphanumeric and hyphens) |
| `zone`        | `string`       | ✅       | —         | Availability zone (e.g. `us-east-1`)          |
| `vpc_id`      | `string`       | ✅       | —         | VPC ID                                        |
| `subnet_id`   | `string`       | ✅       | —         | Subnet ID for the primary network interface   |
| `image_id`    | `string`       | ✅       | —         | OS image ID                                   |
| `profile`     | `string`       | ❌       | `bx2-2x8` | VSI profile (2 vCPU / 8 GB RAM)               |
| `ssh_key_ids` | `list[string]` | ❌       | `[]`      | SSH key IDs to inject                         |
| `user_data`   | `string`       | ❌       | `null`    | Cloud-init user data script                   |

**Returns:** `dict` — the created VSI with `id`, `name`, `status`, `zone`, `cpu`, `ram`.

---

### `start_vsi`

Start a stopped Virtual Server Instance.

**Parameters:**

| Name     | Type     | Required | Description                |
| -------- | -------- | -------- | -------------------------- |
| `region` | `string` | ✅       | IBM Cloud region           |
| `vsi_id` | `string` | ✅       | The ID of the VSI to start |

**Returns:** `string` — confirmation message.

---

### `stop_vsi`

Stop a running Virtual Server Instance.

**Parameters:**

| Name     | Type     | Required | Description               |
| -------- | -------- | -------- | ------------------------- |
| `region` | `string` | ✅       | IBM Cloud region          |
| `vsi_id` | `string` | ✅       | The ID of the VSI to stop |

**Returns:** `string` — confirmation message.

---

### `delete_vsi`

Delete a Virtual Server Instance. The VSI must be in `stopped` state before deletion.

**Parameters:**

| Name     | Type     | Required | Description                 |
| -------- | -------- | -------- | --------------------------- |
| `region` | `string` | ✅       | IBM Cloud region            |
| `vsi_id` | `string` | ✅       | The ID of the VSI to delete |

**Returns:** `string` — confirmation message.

---

## 🤖 Integrating with Claude Desktop

To use this MCP server with [Claude Desktop](https://claude.ai/download), add the following entry to your Claude Desktop configuration file.

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ibm-cloud-vm-controller": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/ibm-cloud-vm-controller",
        "python",
        "src/mcp_server.py"
      ],
      "env": {
        "API_KEY": "<your_ibm_cloud_api_key>"
      }
    }
  }
}
```

> Replace `/absolute/path/to/ibm-cloud-vm-controller` with the actual path on your machine.

After saving the file, restart Claude Desktop. You will see the IBM Cloud VM Controller tools available in the tool panel.

---

## 🧪 Running Unit Tests

```bash
uv run pytest -v tests/
```

Or with explicit `PYTHONPATH`:

```bash
PYTHONPATH=src uv run pytest -v tests/test_vsi_controller.py
```

> Make sure `src/.env` is properly configured with a valid IBM Cloud API key and that at least one VSI exists in your account for full integration test coverage.

---

## 📁 Project Structure

```
ibm-cloud-vm-controller/
├── src/
│   ├── mcp_server.py              # MCP server entry point (FastMCP tools)
│   ├── main.py                    # Standalone CLI entry point
│   ├── config.yaml                # Logging configuration
│   ├── .env-sample                # Environment variable template
│   │
│   ├── core/                      # Cross-cutting concerns
│   │   ├── config.py              # App settings (Pydantic + YAML)
│   │   └── log.py                 # Logging setup (Loguru)
│   │
│   ├── dtos/                      # Data Transfer Objects
│   │   ├── vsi.py                 # VSI model
│   │   └── vsi_template.py        # VSITemplate model (for creation)
│   │
│   └── services/                  # Business logic
│       ├── vsi_client.py          # VSIController — main service interface
│       └── commands/              # Command pattern implementations
│           ├── base.py            # BaseCommand + CommandResult
│           ├── ibm_vpc_client.py  # Singleton IBM VPC client factory
│           ├── list.py            # ListVSICommand
│           ├── create.py          # CreateVSICommand
│           ├── start.py           # StartVSICommand
│           ├── stop.py            # StopVSICommand
│           └── delete.py          # DeleteVSICommand
│
├── tests/
│   └── test_vsi_controller.py     # Unit tests
│
├── docs/
│   └── architecture.md            # Architecture overview and class diagram
│
├── pyproject.toml                 # Project metadata and dependencies
└── README.md
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

_Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk) · Powered by [IBM Cloud VPC API](https://cloud.ibm.com/apidocs/vpc)_
