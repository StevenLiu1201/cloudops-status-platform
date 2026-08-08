# CloudOps Status Platform

CloudOps Status Platform is a deliberately small FastAPI service built as a hands-on Cloud and DevOps portfolio project. The application stays simple so the repository can focus on containerization, automated testing, infrastructure, deployment, networking, security, and observability.

The current implementation runs FastAPI and PostgreSQL as health-checked Docker containers. CI/CD, AWS, CloudWatch, and Terraform are planned but are not implemented yet.

## Current architecture

```mermaid
flowchart LR
    User["User / API client"] -->|"HTTP :8000"| API["FastAPI container"]
    API -->|"PostgreSQL :5432<br/>internal Docker network"| DB["PostgreSQL container"]
    DB --> Volume[("postgres_data volume")]
    Compose["Docker Compose"] -.->|"builds and manages"| API
    Compose -.->|"creates and manages"| DB
```

Only the API port is published to the host. PostgreSQL is reachable from the API through the private Compose network and is not published on a host port.

## Implemented technologies

| Technology | Current use |
| --- | --- |
| Python 3.12 | Application runtime |
| FastAPI | REST API and interactive OpenAPI documentation |
| Uvicorn | ASGI development and container server |
| PostgreSQL 18 | Persistent application database |
| SQLAlchemy | Database engine, sessions, and model mapping |
| Psycopg | PostgreSQL driver |
| pytest | Automated endpoint tests |
| Docker | Reproducible application image |
| Docker Compose | API and database orchestration |

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Confirms that the API process is responding |
| `GET` | `/api/status` | Returns the service name, environment, and status |
| `GET` | `/api/version` | Returns the configured application version |
| `GET` | `/api/database-status` | Runs a query to verify PostgreSQL connectivity |
| `GET` | `/docs` | Opens the interactive OpenAPI documentation |

## Quick start with Docker

### Prerequisites

- Docker Desktop with Docker Compose
- PowerShell for the commands shown below

Clone the repository, move into its root directory, and create a local configuration file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholder Docker database password:

```text
POSTGRES_DB=cloudops_status
POSTGRES_USER=cloudops_app
POSTGRES_PASSWORD=choose_a_local_docker_password
```

Build and start the environment:

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8000/docs> or test the health endpoints listed above.

Compose waits for PostgreSQL to become healthy before starting FastAPI. The API entrypoint initializes the schema and then starts Uvicorn.

Stop the environment while retaining its database volume:

```powershell
docker compose down
```

## Verification and troubleshooting

Show container health and published ports:

```powershell
docker compose ps
```

Follow API or database logs:

```powershell
docker compose logs -f api
docker compose logs -f db
```

Call every API endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod http://127.0.0.1:8000/api/version
Invoke-RestMethod http://127.0.0.1:8000/api/database-status
```

Run the automated tests inside the API container:

```powershell
docker compose exec api python -m pytest backend/tests -v
```

Confirm that the database table exists:

```powershell
docker compose exec db psql -U cloudops_app -d cloudops_status -c "\dt"
```

The named `postgres_data` volume persists database files when containers are replaced. `docker compose down --volumes` permanently removes that local containerized data and should only be used when a clean database is intentional.

## Native Python and PostgreSQL setup

Docker is the recommended path, but the API can also use PostgreSQL installed directly on the host.

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env` to the application user's local PostgreSQL connection URL:

```text
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/DATABASE
```

Initialize the schema and start the API:

```powershell
python -m backend.app.init_db
python -m uvicorn backend.app.main:app --reload
```

Run the local test suite:

```powershell
python -m pytest backend\tests -v
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `APP_NAME` | `cloudops-api` | Service name returned by `/api/status` |
| `APP_VERSION` | `1.0.0` | Version returned by `/api/version` |
| `APP_ENVIRONMENT` | `development` | Runtime environment returned by `/api/status` |
| `DATABASE_URL` | None | SQLAlchemy connection URL used outside Compose |
| `POSTGRES_DB` | `cloudops_status` | Database initialized by the PostgreSQL container |
| `POSTGRES_USER` | `cloudops_app` | Application database user initialized by the container |
| `POSTGRES_PASSWORD` | Required | Local container database password |

The real `.env` file is excluded from Git and the Docker build context. Only `.env.example`, containing placeholders, belongs in source control. Database passwords, AWS credentials, API keys, and tokens must never be committed.

## Project structure

```text
.
|-- backend/
|   |-- app/                 # FastAPI, configuration, database, and model code
|   |-- tests/               # Automated API tests
|   |-- Dockerfile           # API image definition
|   |-- entrypoint.sh        # Schema initialization and Uvicorn startup
|   `-- requirements.txt     # Python dependencies
|-- compose.yaml             # API, PostgreSQL, network, health checks, and volume
|-- .dockerignore            # Files excluded from Docker build context
|-- .env.example             # Safe configuration template
|-- .gitignore               # Local files excluded from Git
`-- README.md
```

## Security choices

- The application uses a dedicated PostgreSQL user instead of the `postgres` administrator.
- Database credentials come from runtime environment variables and are not copied into the image.
- The real `.env` file is excluded from both Git and Docker builds.
- PostgreSQL has no published host port in the Compose environment.
- The API container runs as a non-root Linux user.
- API and database services use health checks.

The Compose environment is intended for local development. Production deployment will require managed secrets, restricted cloud networking, HTTPS, least-privilege IAM, image scanning, and monitored infrastructure.

## Planned cloud architecture

The next major implementation stages will add CI and an initial AWS deployment before introducing Kubernetes.

```mermaid
flowchart LR
    Developer["Developer"] --> GitHub["GitHub repository"]
    GitHub --> Actions["GitHub Actions<br/>planned"]
    Actions --> EC2["Amazon EC2<br/>planned"]
    EC2 --> RDS["Amazon RDS PostgreSQL<br/>planned private database"]
    EC2 --> CloudWatch["Amazon CloudWatch<br/>planned logs and metrics"]
    Terraform["Terraform<br/>planned after manual AWS deployment"] -.-> EC2
    Terraform -.-> RDS
```

Planned stages include:

1. GitHub Actions continuous integration
2. Manual AWS deployment using VPC networking, EC2, RDS, IAM, and security groups
3. CloudWatch logs, metrics, and alarms
4. GitHub Actions continuous delivery using AWS OpenID Connect
5. Reproducible infrastructure with Terraform

Kubernetes, EKS, Prometheus, Grafana, feature flags, and additional security scanning are later improvements, not current capabilities.
