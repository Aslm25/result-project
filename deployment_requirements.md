# Deployment Requirements

## Python Version
- **Required**: Python 3.11 or higher
- **Recommended**: Python 3.11.x

## Core Dependencies

### Web Framework
```
Flask>=3.1.1
Werkzeug>=3.1.3
Gunicorn>=23.0.0
```

### Data Processing & Excel Handling
```
pandas>=2.3.1
openpyxl>=3.1.5
xlrd>=2.0.2
```

### Database Support (Optional for advanced features)
```
Flask-SQLAlchemy>=3.1.1
psycopg2-binary>=2.9.10
```

### Validation
```
email-validator>=2.2.0
```

## Installation Commands

### For pip installation:
```bash
pip install Flask>=3.1.1
pip install Werkzeug>=3.1.3
pip install Gunicorn>=23.0.0
pip install pandas>=2.3.1
pip install openpyxl>=3.1.5
pip install xlrd>=2.0.2
pip install Flask-SQLAlchemy>=3.1.1
pip install psycopg2-binary>=2.9.10
pip install email-validator>=2.2.0
```

### For conda installation:
```bash
conda install python=3.11
conda install flask pandas openpyxl xlrd gunicorn
pip install Flask-SQLAlchemy psycopg2-binary email-validator
```

## InfinityFree Hosting Compatibility

### Required for InfinityFree:
- All dependencies are compatible with standard shared hosting
- No special server configuration needed
- Uses standard HTTP/HTTPS protocols
- File-based session storage (no database required)

### Deployment files needed:
- All Python files (.py)
- templates/ folder with HTML files
- static/ folder with CSS/JS files
- data/ folder for Excel files
- Gunicorn configuration (gunicorn_config.py)

### Memory requirements:
- Minimum: 128MB RAM
- Recommended: 512MB RAM for large Excel files
- Disk space: ~50MB for application + your data files

## Environment Variables (Optional)
```
SESSION_SECRET=your_secret_key_here
```

## Startup Command
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

Or with configuration file:
```bash
gunicorn -c gunicorn_config.py main:app
```