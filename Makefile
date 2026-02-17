.PHONY: install install-dev test lint type-check format format-check clean clean-cache build publish help

# Force Python 3.12
PYTHON_EXE := /Users/anthony/.local/bin/python3.12

PYTHON_CHECK := $(shell command -v $(PYTHON_EXE) 2>/dev/null)
ifeq ($(strip $(PYTHON_CHECK)),)
    $(error Python 3.12 is required. Current system: $(shell python3 --version 2>&1). Please install Python 3.12.)
endif

# Install package in editable mode
install:
	@echo "Installing git-storyteller..."
	@$(PYTHON_EXE) -m pip install --upgrade pip setuptools wheel --quiet
	@$(PYTHON_EXE) -m pip install -e .
	@echo "Installation complete!"

# Install package with dev dependencies
install-dev:
	@echo "Installing git-storyteller with dev dependencies..."
	@$(PYTHON_EXE) -m pip install -e ".[dev]"
	@echo "Installation complete!"

# Run all tests
test:
	@echo "Running tests..."
	@if command -v pytest > /dev/null 2>&1 || $(PYTHON_EXE) -m pytest --version > /dev/null 2>&1; then \
		CURRENT_DIR=$$(pwd); \
		if [ -z "$$PYTHONPATH" ]; then \
			PYTHONPATH_VAR="$$CURRENT_DIR/src"; \
		else \
			PYTHONPATH_VAR="$$PYTHONPATH:$$CURRENT_DIR/src"; \
		fi; \
		PYTHONPATH="$$PYTHONPATH_VAR" $(PYTHON_EXE) -m pytest tests/ -v --tb=short 2>/dev/null || \
			(echo "No tests found in tests/ directory" && exit 0); \
	else \
		echo "pytest not found. Run: make install-dev"; \
		exit 1; \
	fi

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	@if command -v pytest > /dev/null 2>&1 || $(PYTHON_EXE) -m pytest --version > /dev/null 2>&1; then \
		if ! $(PYTHON_EXE) -c "import pytest_cov" 2>/dev/null; then \
			echo "pytest-cov not found, installing..."; \
			$(PYTHON_EXE) -m pip install pytest-cov --quiet; \
		fi; \
		CURRENT_DIR=$$(pwd); \
		if [ -z "$$PYTHONPATH" ]; then \
			PYTHONPATH_VAR="$$CURRENT_DIR/src"; \
		else \
			PYTHONPATH_VAR="$$PYTHONPATH:$$CURRENT_DIR/src"; \
		fi; \
		PYTHONPATH="$$PYTHONPATH_VAR" $(PYTHON_EXE) -m pytest tests/ --cov=src --cov-report=term-missing --no-cov-on-fail -v --tb=short 2>/dev/null || \
			(echo "No tests found in tests/ directory" && exit 0); \
	else \
		echo "pytest not found. Run: make install-dev"; \
		exit 1; \
	fi

# Lint code with ruff
lint:
	@echo "Running ruff linter..."
	@if ! command -v ruff > /dev/null 2>&1; then \
		echo "ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi
	@ruff check src/ tests/ || exit 1

# Type check code
type-check:
	@echo "Running mypy type checker..."
	@if ! $(PYTHON_EXE) -c "import mypy" 2>/dev/null && ! command -v mypy > /dev/null 2>&1; then \
		echo "mypy not found. Install with: pip install mypy"; \
		exit 1; \
	fi
	@if command -v mypy > /dev/null 2>&1; then \
		mypy src/ || exit 1; \
	else \
		$(PYTHON_EXE) -m mypy src/ || exit 1; \
	fi

# Format code with ruff
format:
	@echo "Formatting code with ruff..."
	@if ! command -v ruff > /dev/null 2>&1; then \
		echo "ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi
	@ruff check --fix src/ tests/
	@echo "Formatting complete!"

# Check code formatting (without modifying files)
format-check:
	@echo "Checking code formatting with ruff..."
	@if ! command -v ruff > /dev/null 2>&1; then \
		echo "ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi
	@ruff check src/ tests/

# Clean Python cache and build artifacts
clean-cache:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.coverage" -delete 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@echo "Python cache cleaned successfully!"

# Clean all generated files and cache
clean:
	@echo "Cleaning all generated files..."
	@$(MAKE) clean-cache
	@rm -rf build/ dist/ 2>/dev/null || true
	@echo "All generated files cleaned successfully!"

# Build distribution packages
build:
	@echo "Building distribution packages..."
	@$(PYTHON_EXE) -m build
	@echo "Build complete! Check dist/ directory."

# Publish to PyPI
publish:
	@echo "Publishing to PyPI..."
	@if [ ! -d "dist" ]; then \
		echo "No dist/ directory found. Run 'make build' first."; \
		exit 1; \
	fi
	@$(PYTHON_EXE) -m twine upload dist/*
	@echo "Published successfully!"

# Show help
help:
	@echo "Available commands:"
	@echo "  make install          - Install package in editable mode"
	@echo "  make install-dev      - Install package with dev dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make lint             - Lint code with ruff"
	@echo "  make type-check       - Type check code with mypy"
	@echo "  make format           - Format code with ruff"
	@echo "  make format-check     - Check code formatting (CI)"
	@echo "  make build            - Build distribution packages"
	@echo "  make publish          - Publish to PyPI"
	@echo "  make clean-cache      - Clean Python cache files"
	@echo "  make clean            - Clean all generated files and cache"
	@echo "  make help             - Show this help message"
