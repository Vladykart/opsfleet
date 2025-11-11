# Contributing to LangGraph Data Analysis Agent

Thank you for your interest in contributing!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/opsfleet.git
   cd opsfleet
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

4. Format code:
   ```bash
   black src/
   ```

5. Lint code:
   ```bash
   flake8 src/
   ```

6. Commit your changes:
   ```bash
   git commit -m "Add your meaningful commit message"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a Pull Request

## Code Style

- Follow PEP 8
- Use Black for formatting
- Maximum line length: 127 characters
- Use type hints where possible
- Add docstrings to all functions and classes

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure CI passes
- Request review from maintainers

## Questions?

Open an issue for any questions or concerns.
