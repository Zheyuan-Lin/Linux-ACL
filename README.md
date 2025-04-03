# Linux ACL Manager Web Application

A web-based graphical interface for managing Linux ACLs on research storage systems.

## Project Overview

The Linux ACL Manager provides an intuitive web interface to manage Access Control Lists (ACLs) on Linux file systems. While traditional POSIX permissions are sufficient for simple scenarios, research environments often require more fine-grained access control that Linux ACLs can provide. This application simplifies the management of these advanced permissions through a user-friendly interface.

### Key Features

- **Web-Based File Browser**: Navigate through your storage system with an intuitive file explorer
- **ACL Visualization**: See permissions at a glance with color-coded indicators
- **Interactive ACL Management**: Add, modify, or remove ACL entries with a simple interface
- **LDAP Authentication**: Integrate with your existing directory service
- **Secure Deployment Options**: Run as a limited service account with proper permissions

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for frontend development)
- Linux system with ACL support (getfacl/setfacl commands)
- LDAP server for authentication (optional, local auth available for development)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linux-acl-manager.git
   cd linux-acl-manager
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application at `http://localhost:8080`

### Manual Installation

#### Backend

1. Set up a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .# Linux-ACL
