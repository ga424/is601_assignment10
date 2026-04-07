# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

---

# ✅ 7. Running Tests Locally

This project includes both unit and integration tests.

## 1. Ensure PostgreSQL is available

If you use Docker Compose from this repo, PostgreSQL is exposed on host port `5433`.

## 2. Set the test database URL

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/fastapi_db"
```

## 3. Run unit + integration tests (excluding e2e)

```bash
pytest -v -m "not e2e"
```

## 4. Run all tests

```bash
pytest -v
```

---

# 🐳 8. Docker Hub Image

Update the repository name below with your Docker Hub username:

- Docker Hub repository: `https://hub.docker.com/r/ga424/is601-assignment10`
- Latest image tag: `ga424/is601-assignment10:latest`

---

# 🏗️ 9. Architecture and Key User Journeys

## Sequence Diagrams

### Calculator request flow

```mermaid
sequenceDiagram
   actor User
   participant Browser
   participant App as FastAPI App
   participant Ops as app.operations

   User->>Browser: Enter operands and choose an operation
   Browser->>App: POST /add, /subtract, /multiply, or /divide
   App->>App: Validate the request payload
   App->>Ops: Call the arithmetic helper
   alt Successful calculation
      Ops-->>App: Result value
      App-->>Browser: 200 JSON {result}
      Browser-->>User: Display the result
   else Divide by zero or invalid input
      Ops-->>App: Error / ValueError
      App-->>Browser: 400 JSON {error}
      Browser-->>User: Show an error message
   end
```

### User creation and lookup flow

```mermaid
sequenceDiagram
   actor User
   participant Browser
   participant App as FastAPI App
   participant DB as PostgreSQL

   User->>Browser: Submit the new user form
   Browser->>App: POST /users/
   App->>DB: Insert the user record
   DB-->>App: Persisted user row
   App-->>Browser: 200 JSON user record
   Browser-->>User: Confirm account creation

   User->>Browser: Open the user list view
   Browser->>App: GET /users/
   App->>DB: Query user records
   DB-->>App: User rows
   App-->>Browser: 200 JSON array
   Browser-->>User: Render the list of users
```

## C4 Documentation

### C4 Context

```mermaid
C4Context
   title FastAPI Calculator - System Context

   Person(user, "User", "Uses the browser UI or API client")
   System(system, "FastAPI Calculator", "Serves the calculator UI and user endpoints")
   SystemDb_Ext(database, "PostgreSQL", "Stores users and application data")

   Rel(user, system, "Uses", "HTTPS")
   Rel(system, database, "Reads from and writes to", "SQL")
```

### C4 Container

```mermaid
C4Container
   title FastAPI Calculator - Container Diagram

   Person(user, "User", "Uses the app in a browser")

   Container_Boundary(app, "FastAPI Calculator") {
      Container(web, "Web UI", "HTML/Jinja2", "Renders the landing page")
      Container(api, "FastAPI App", "Python / FastAPI", "Exposes calculator and user endpoints")
      Container(ops, "Operations Module", "Python", "Performs add, subtract, multiply, and divide")
      ContainerDb(db, "PostgreSQL", "PostgreSQL", "Stores users and application data")
   }

   Rel(user, web, "Loads", "HTTP")
   Rel(web, api, "Submits requests to", "JSON/HTTPS")
   Rel(api, ops, "Calls")
   Rel(api, db, "Reads from and writes to", "SQLAlchemy")
```

---

# 📝 10. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
