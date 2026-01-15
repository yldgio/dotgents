# Installation

Agent Scaffold is a Python package distributed via PyPI. We recommend using `uv` for installation and management, but it works with standard `pip` as well.

## Prerequisites

- **Python**: Version 3.10 or higher.
- **Package Manager**: `uv` (recommended) or `pip`.

## Installation Methods

### Option 1: Using `uvx` (Recommended)

If you have `uv` installed, you can run Agent Scaffold directly without a permanent installation. This ensures you are always using the latest version (unless pinned) and keeps your global environment clean.

```bash
uvx agent-scaffold <command>
```

For example:
```bash
uvx agent-scaffold --version
```

### Option 2: Installing with `uv`

To install it into a virtual environment:

```bash
uv pip install agent-scaffold
```

### Option 3: Installing with `pip`

```bash
pip install agent-scaffold
```

## Verifying Installation

After installation, verify that the CLI is available:

```bash
agent-scaffold --version
```

You should see output similar to:
```
agent-scaffold, version 0.1.0
```
