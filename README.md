# System Integration Project

This is a microservices-based system for processing and visualizing temperature data using various integration patterns.

## Architecture

The system consists of multiple services:

- **Frontend** - Next.js web application for data visualization and interaction
- **REST API Server** - REST API for handling HTTP requests
- **GraphQL Server** - GraphQL API for data queries
- **gRPC Server** - gRPC service for file processing
- **RabbitMQ Worker** - Worker service for processing CSV data

## Prerequisites

- Node.js 18+
- Python 3.8+
- Docker and Docker Compose
- RabbitMQ
- PostgreSQL

## Setup & Installation

1. Clone the repository:
```sh
git clone <repository-url>
```

2. Frontend setup:
```sh
cd frontend
npm install --force
```
Create `.env.development` and `.env.production` file based on [env.example](./frontend/env.example).

3. Build and run all services:
```sh
docker-compose up -d
```

## Usage

### Development
1. Start the frontend development server:
```sh
cd frontend
npm run dev
```
2. Access the application at `http://localhost:3000`

### Production

Build and start the frontend:
```sh
cd frontend
npm run build
npm start
```

## Features

- Interactive map visualization using Leaflet
- CSV file upload and processing
- XML data filtering and manipulation
- Real-time data updates
- Responsive material design UI

## Technology Stack
- **Frontend**
  - Next.js 15
  - Material UI
  - Leaflet
  - TailwindCSS
  - TypeScript
- **Backend**
  - Python
  - gRPC
  - GraphQL
  - RabbitMQ
  - PostgreSQL

## Documentation
- General:
  - [Presentation PDF](./IPVC-EI-TP_FINAL_EF-29950.pdf)

- Frontend modules:
  - [Tailwind CSS](https://tailwindcss.com/)
  - [Material UI](https://mui.com/)
  - [Leaflet](https://leafletjs.com/)
  - [React Leaflet](https://react-leaflet.js.org/)

## Project Structure
```
.
├── frontend/               # Next.js frontend application
├── graphql_server/        # GraphQL API server
├── grpc-server/           # gRPC service implementation
├── rest_api_server/       # REST API implementation
└── worker-rabbit-csv/     # RabbitMQ worker service
```

## Environment Variables

Frontend environment variables (`.env.development` / `.env.production`):
```sh
REST_API_BASE_URL=http://127.0.0.1:8000
GRAPHQL_API_BASE_URL=http://127.0.0.1:8001
NEXT_PUBLIC_URL=http://127.0.0.1:3001
```

## License
[LICENSE](LICENSE).
