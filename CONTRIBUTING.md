# Contributing to QR Code Reader Premium

Thank you for your interest in contributing to QR Code Reader Premium! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)
- Redis (optional, for caching)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/qrRobust-scanner.git
   cd qrRobust-scanner
   ```

2. **Set up the backend**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the development servers**
   ```bash
   # Terminal 1: Backend
   python -m uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend
   npm start
   ```

## Contributing Guidelines

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **JavaScript/React**: Use ESLint and Prettier
- **Commit messages**: Use conventional commits format

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Update documentation if needed
   - Ensure all tests pass

3. **Commit your changes**
   ```bash
   git commit -m "feat: add new QR code generation feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear description
   - Link any related issues
   - Request review from maintainers

### Testing

- **Backend**: Run `pytest` in the root directory
- **Frontend**: Run `npm test` in the frontend directory
- **Integration**: Ensure both services work together

### Documentation

- Update README.md for new features
- Add docstrings to Python functions
- Include JSDoc comments for JavaScript functions
- Update API documentation

## Issue Guidelines

### Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)
- Screenshots if applicable

### Feature Requests

For feature requests, please include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Any design mockups or examples

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or reach out to the maintainers if you have any questions!