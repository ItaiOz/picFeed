# PicsFeed

A full-stack image voting application built with React, FastAPI, and PostgreSQL.

## Features

- Browse 100 images from Picsum Photos
- Vote (like/dislike) on images
- View live vote counts
- Export votes to CSV
- Dockerized development environment with hot-reload

## Tech Stack

**Frontend:**
- React 19 with TypeScript
- Material-UI (MUI)
- React Scripts

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL

**Infrastructure:**
- Docker & Docker Compose
- Uvicorn (ASGI server)

## Prerequisites

- Docker Desktop installed and running
- Git (for cloning the repository)

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ItaiOz/picsFeed.git
   cd picsFeed
   ```

2. **Start the application with Docker Compose:**
   
   **First run:**
   ```bash
   docker-compose up --build -d
   ```
   
   **Subsequent runs:**
   ```bash
   docker-compose up -d
   ```
   
   Note: Use `--build` flag only on first run or after dependency changes (package.json, requirements.txt) or Dockerfile modifications.

3. **Access the application:**
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)
   - **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Project Structure

```
picsFeed/
├── client/                      # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ImageCard.tsx
│   │   │   ├── ImageCard.test.tsx
│   │   │   ├── ImageCard.integration.test.tsx
│   │   │   └── Header.tsx
│   │   ├── hooks/              # Custom hooks (API requests)
│   │   │   └── useAppRequests.ts
│   │   ├── App.tsx             # Main app component
│   │   └── App.test.tsx
│   ├── Dockerfile
│   └── package.json
├── server/                      # FastAPI backend
│   ├── tests/                  # Server tests
│   │   ├── test_main.py        # Unit tests
│   │   └── test_integration.py # Integration tests
│   ├── main.py                 # API routes & startup logic
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # Database configuration
│   ├── Dockerfile
│   └── requirements.txt
├── e2e/                         # End-to-end tests
│   ├── tests/
│   │   └── picsfeed.spec.ts    # Playwright E2E tests
│   ├── playwright.config.ts
│   └── package.json
├── docker-compose.yml           # Development environment
└── docker-compose.test.yml      # Test database environment
```

## API Endpoints

- `GET /images` - Retrieve all images with vote counts
- `POST /vote` - Submit a vote (like/dislike)
- `GET /export-votes` - Download votes as CSV

## Development

The application is configured for hot-reload in Docker:

- **Frontend**: Changes to files in `client/src/` will automatically refresh the browser
- **Backend**: Changes to `.py` files will restart the server automatically

## Testing

PicsFeed includes comprehensive test coverage with unit, integration, and end-to-end tests.

### Client Tests (Unit + Integration)

```bash
cd client
npm test
```

Runs all Jest tests including:
- Unit tests (`.test.tsx`)
- Integration tests (`.integration.test.tsx`)

### Server Tests

**Unit Tests:**
```bash
cd server
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://picsfeed:picsfeed@localhost:5432/picsfeed"
pytest tests/test_main.py -v
```

**Integration Tests:**
```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
cd server
.\venv\Scripts\Activate.ps1
$env:TEST_DATABASE_URL="postgresql://picsfeed:picsfeed@localhost:5433/picsfeed_test"
pytest tests/test_integration.py -v

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

### End-to-End Tests (Playwright)

**First time setup:**
```bash
cd e2e
npm install
npx playwright install
```

**Run E2E tests:**
```bash
# Make sure app is running first
docker-compose up -d

# Run tests
cd e2e
npm test                # Headless mode
npm run test:headed     # Watch in browser
npm run test:ui         # Interactive UI mode
```

## Database Seeding

The application automatically seeds the database with 100 sample images from Picsum Photos on first startup.

## Environment Variables

The backend uses the following environment variable (configured in `docker-compose.yml`):
- `DATABASE_URL`: PostgreSQL connection string
- `WATCHPACK_POLLING`: Enables file watching on Windows for hot-reload

## License

MIT
