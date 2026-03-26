# Software Development with Claude Code

A course repository featuring accompanying code for the course exercises.

## 📚 Course Overview

This repository contains multiple mini-projects and exercises that teach software development practices using Claude Code. All projects work with the **Chinook sample database**, a realistic music store dataset, allowing you to focus on development patterns rather than data setup.

## 🗂️ Project Structure

### Main Projects

Each project directory contains a `CLAUDE.md` file with specific instructions and context for that exercise.

**Music Analytics API** - Build REST APIs for querying music data


**Music Analytics Reporter** - CLI tool for generating music database reports

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (or pip)
- Claude Code CLI installed

## 📦 Dependencies

Key packages included:
- **Flask/FastAPI** - Web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **pytest** - Testing framework
- **requests/httpx** - HTTP clients

See `pyproject.toml` for the complete list.

## 💾 Database

All projects share the `chinook.db` SQLite database containing:
- Artists, Albums, Tracks
- Genres, Playlists
- Customers, Invoices
- Sales data

Use any SQLite client or the MCP database tools to explore the schema.

## 📋 Learning Path

1. Start with the **API projects** to learn REST API patterns
2. Progress to the **Reporter projects** to practice planning and implementation
3. Use Archive projects to see alternative approaches

Each project builds on patterns from previous exercises.

## 🔗 Resources

- [Claude Code Documentation](https://claude.com/claude-code)
- [Claude API Documentation](https://anthropic.com/docs)
- [Chinook Database Schema](https://www.sqlalchemy-utils.org/)

