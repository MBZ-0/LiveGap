# CI/CD Setup Documentation

## Overview

This project uses GitHub Actions for Continuous Integration (CI) to automatically run tests and generate coverage reports for both the backend (Python/FastAPI) and frontend (Next.js/React) components.

## Test Coverage Requirements

As per the course requirements, our application must achieve **at least 65% code coverage**.

### Coverage Thresholds
- 60-65%+ = 10pts
- 55-59.999% = 8pts
- 50-54.999% = 5pts
- < 50% = 0pts

## CI Workflow

The CI pipeline (`.github/workflows/ci.yml`) runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual trigger via GitHub Actions UI

### Jobs

1. **Backend Tests (Python)**
   - Runs pytest with coverage for Python/FastAPI backend
   - Generates coverage reports (HTML, XML, terminal)
   - Tests located in: `livegap-mini/backend/tests/`

2. **Frontend Tests (Next.js)**
   - Runs Jest with coverage for Next.js/React frontend
   - Generates coverage reports
   - Tests located in: `livegap-mini/frontend/{lib,app,components}/__tests__/`

3. **Combined Coverage Report**
   - Aggregates results from both backend and frontend
   - Provides downloadable artifacts

## Running Tests Locally

### Backend Tests

```bash
cd livegap-mini/backend

# Activate virtual environment (if using one)
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# or on Linux/Mac:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html -v

# View coverage report
# HTML report will be in htmlcov/index.html
```

### Frontend Tests

```bash
cd livegap-mini/frontend

# Install dependencies
npm install

# Run tests with coverage
npm run test:coverage

# View coverage report
# HTML report will be in coverage/lcov-report/index.html
```

## Viewing CI Results

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select the latest workflow run
4. View the summary for coverage reports
5. Download artifacts for detailed HTML coverage reports

### Example CI Run Link

After pushing your code, you can find the CI run at:
```
https://github.com/MBZ-0/LiveGap/actions
```

For your final submission, provide a link to a successful CI run that demonstrates your test coverage.

## Test Structure

### Backend Tests (`livegap-mini/backend/tests/`)
- `test_models.py` - Tests for Pydantic models
- `test_api.py` - Tests for FastAPI endpoints
- `test_url_matcher.py` - Tests for URL normalization utility
- `test_runner.py` - Tests for site loading and configuration

### Frontend Tests
- `lib/__tests__/utils.test.ts` - Tests for utility functions
- `app/about/__tests__/page.test.tsx` - Tests for About page
- `components/ui/__tests__/components.test.tsx` - Tests for UI components

## Adding New Tests

### Backend (Python)
1. Create test file in `livegap-mini/backend/tests/` with prefix `test_`
2. Write test functions with prefix `test_`
3. Use pytest fixtures and assertions
4. Run locally to verify

### Frontend (TypeScript/React)
1. Create `__tests__` directory next to the file you're testing
2. Create test file with `.test.ts` or `.test.tsx` extension
3. Use Jest and React Testing Library
4. Run locally to verify

## Coverage Configuration

### Backend (`pyproject.toml`)
- Source directory: `app/`
- Excludes: tests, pycache, venv
- Minimum coverage threshold can be adjusted in pytest config

### Frontend (`jest.config.js`)
- Covers: `app/`, `components/`, `lib/`
- Excludes: `.next/`, `node_modules/`, `.d.ts` files
- Minimum threshold: 50% (can be increased)

## Troubleshooting

### Backend tests failing?
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python version is 3.11+
- Verify that config files (sites.yaml) are present

### Frontend tests failing?
- Ensure dependencies are installed: `npm install`
- Check Node.js version is 20+
- Clear cache: `npm run test -- --clearCache`

## Next Steps

To improve coverage:
1. Add more unit tests for utility functions
2. Add integration tests for API endpoints
3. Add component tests for React components
4. Mock external dependencies (S3, OpenAI, etc.)
5. Test error handling paths

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Jest documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
