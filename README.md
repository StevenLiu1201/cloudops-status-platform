# CloudOps Status Platform

[![CI Pipeline](https://github.com/StevenLiu1201/cloudops-status-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/StevenLiu1201/cloudops-status-platform/actions/workflows/ci.yml)

CloudOps Status Platform is a deliberately small FastAPI service built as a hands-on Cloud and DevOps portfolio project. The application stays simple so the repository can focus on containerization, automated testing, infrastructure, deployment, networking, security, and observability.

The application is deployed manually to AWS: a Dockerized FastAPI service runs on Amazon EC2 and connects to Amazon RDS for PostgreSQL in private subnets. CloudWatch centralizes application logs and monitors EC2 CPU with an SNS-integrated alarm. GitHub Actions automatically tests the API and builds its Docker image on pushes and pull requests to `main`. Deployment automation and Terraform are planned but are not implemented yet.

## Current architecture

```mermaid
flowchart LR
    User["Authorized API client"] -->|"HTTP :8000<br/>source IP restricted"| EC2SG["EC2 security group"]
    EC2SG --> EC2["Amazon EC2<br/>Amazon Linux 2023"]
    EC2 --> API["Dockerized FastAPI"]
    API -->|"PostgreSQL :5432"| RDSSG["RDS security group"]
    RDSSG --> RDS[("Amazon RDS PostgreSQL<br/>private subnets")]
    SSM["AWS Systems Manager"] -->|"IAM-authenticated session<br/>no inbound SSH"| EC2
    API -->|"awslogs driver"| Logs["CloudWatch Logs<br/>7-day retention"]
    EC2 --> Metrics["CloudWatch CPU metric"]
    Metrics --> Alarm["High CPU alarm"]
    Alarm --> SNS["Amazon SNS email notification"]
```

The EC2 instance is in a public subnet and is managed through AWS Systems Manager without an inbound SSH rule or key pair. RDS is not publicly accessible and accepts PostgreSQL traffic only from the EC2 security group. The local Docker Compose environment remains available for development.

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
| GitHub Actions | Automated tests and Docker image builds |
| Amazon EC2 | Hosts the Dockerized API on Amazon Linux 2023 |
| Amazon RDS | Managed PostgreSQL database in private subnets |
| Amazon VPC | Custom public/private subnet and routing design |
| AWS IAM | Administrator group and EC2 Systems Manager role |
| AWS Systems Manager | Keyless instance administration without inbound SSH |
| Amazon CloudWatch | Centralized API logs, EC2 CPU metrics, and alarm state tracking |
| Amazon SNS | Email notification for the high-CPU alarm |

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
- The AWS database is deployed without public access across two private subnets.
- The RDS security group accepts PostgreSQL only from the EC2 security group.
- EC2 administration uses an IAM role and Systems Manager instead of SSH keys.
- EC2 requires IMDSv2 and does not expose port 22.
- The deployed application uses a non-administrative PostgreSQL role.
- The EC2 role can write only to the `/cloudops/api` CloudWatch log group.
- Application logs expire after seven days to limit storage cost.

The current cloud deployment is a learning environment rather than a production system. It uses source-IP-restricted HTTP on port 8000 and a root-readable EC2 environment file. Production deployment will require HTTPS, managed secrets, a stable ingress layer, image scanning, and more complete application-level metrics.

## Monitoring validation

- Docker's `awslogs` driver sends FastAPI and Uvicorn output to `/cloudops/api`.
- The log group uses a seven-day retention policy.
- An EC2 `CPUUtilization` alarm evaluates two consecutive five-minute datapoints against a 70% threshold.
- Amazon SNS sends email when the alarm enters `ALARM`.
- A controlled CPU load test validated the complete `OK → ALARM → OK` lifecycle while the API and RDS connection remained healthy.
- The first load test reached only approximately 50% CPU and did not trigger the alarm. Increasing the controlled workload and allowing two complete metric periods produced the expected alarm transition, demonstrating the effect of metric aggregation and evaluation periods.

## AWS deployment

The manual AWS implementation and its verification steps are documented in [docs/aws-manual-deployment.md](docs/aws-manual-deployment.md).

## Delivery roadmap

```mermaid
flowchart LR
    Developer["Developer"] --> GitHub["GitHub repository"]
    GitHub --> Actions["GitHub Actions<br/>CI implemented; CD planned"]
    Actions -.->|"manual deployment today"| EC2["Amazon EC2<br/>implemented"]
    EC2 --> RDS["Amazon RDS PostgreSQL<br/>implemented private database"]
    EC2 --> CloudWatch["Amazon CloudWatch<br/>implemented logs and alarms"]
    Terraform["Terraform<br/>planned after manual AWS deployment"] -.-> EC2
    Terraform -.-> RDS
```

Planned stages include:

1. GitHub Actions continuous delivery using AWS OpenID Connect
2. Reproducible infrastructure with Terraform

Kubernetes, EKS, Prometheus, Grafana, feature flags, and additional security scanning are later improvements, not current capabilities.
