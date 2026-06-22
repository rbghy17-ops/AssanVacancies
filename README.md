name: Backend Tests

on:
  push:
    branches: ["main", "dev"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:6.0
        ports:
          - 27017:27017

    env:
      MONGO_URI: mongodb://localhost:27017/assam_vacancies_test
      JWT_SECRET: ci-test-secret-not-for-production
      JWT_ALGORITHM: HS256
      JWT_EXPIRY_MINUTES: 60
      ENVIRONMENT: test
      DEBUG: false

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install backend dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short# Here are your Instructions
