# Replit.md - Arabic Excel Search Application

## Overview

This is a Flask-based web application that allows users to upload Excel files and search through Arabic text content. The application provides fuzzy search capabilities for Arabic names and student ID numbers, with proper Arabic text normalization and RTL (Right-to-Left) language support.

## User Preferences

Preferred communication style: Simple, everyday language.
File handling: User prefers to upload files directly to data folder via file manager rather than using web upload interface.

## System Architecture

### Frontend Architecture
- **Framework**: HTML templates with Bootstrap 5 RTL support
- **Styling**: Custom CSS with Arabic font (Noto Sans Arabic) and dark theme
- **JavaScript**: Vanilla JS for file upload validation and progress indication
- **Language Support**: Full Arabic RTL layout with proper text alignment
- **Responsive Design**: Bootstrap-based responsive components

### Backend Architecture
- **Framework**: Flask web framework
- **File Processing**: pandas for Excel file manipulation
- **Search Engine**: Custom Arabic search implementation with fuzzy matching
- **Session Management**: Flask sessions for temporary data storage
- **File Handling**: Werkzeug utilities for secure file uploads

### Key Components

1. **Flask Application (`app.py`)**
   - Main web server handling routes and requests
   - File upload management with size and type validation
   - Session-based data persistence
   - Integration with Excel processor and search engine

2. **Excel Processor (`excel_processor.py`)**
   - Handles Excel file reading and processing
   - Arabic text normalization (removes diacritics, normalizes characters)
   - Automatic column detection for names and IDs
   - Data cleaning and preparation

3. **Arabic Search Engine (`arabic_search.py`)**
   - Fuzzy search implementation for Arabic text
   - Column identification for names and student IDs
   - Search indexing for performance optimization
   - Similarity matching using SequenceMatcher

4. **Templates**
   - `base.html`: Base template with RTL layout and dark theme
   - `index.html`: Main page with file upload and search interface
   - `search_results.html`: Results display with pagination

## Data Flow

1. **File Upload**: User uploads Excel file through web interface
2. **Processing**: ExcelProcessor normalizes Arabic text and identifies columns
3. **Indexing**: ArabicSearchEngine creates search indices from processed data
4. **Storage**: Data stored in Flask session for persistence
5. **Search**: User queries processed through fuzzy matching algorithm
6. **Results**: Matching records displayed with pagination support

## External Dependencies

### Python Packages
- **Flask**: Web framework for application server
- **pandas**: Data manipulation and Excel file processing
- **Werkzeug**: WSGI utilities and secure filename handling
- **difflib**: String similarity matching for fuzzy search

### Frontend Libraries
- **Bootstrap 5**: UI framework with RTL support
- **Font Awesome**: Icons for user interface
- **Google Fonts**: Noto Sans Arabic font for proper Arabic rendering

### File Storage
- **Local Storage**: Uploaded files stored in `uploads/` directory
- **Session Storage**: Processed data temporarily stored in Flask sessions
- **Memory**: Search indices maintained in application memory

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` runs the Flask development server
- **Configuration**: Environment variables for session secrets
- **Debug Mode**: Enabled for development with detailed logging

### Production Considerations
- **WSGI**: ProxyFix middleware configured for reverse proxy deployment
- **File Limits**: 50MB maximum file size limit
- **Security**: Secure filename handling and file type validation
- **Logging**: Configurable logging levels for monitoring

### Architecture Decisions

1. **File Management**: Dual approach for file handling
   - **Web Upload**: Traditional upload interface for general users
   - **Data Folder**: Direct file placement via file manager (user preference)
   - **Benefit**: Flexibility for different user workflows

2. **Large File Optimization**: Enhanced for 200,000+ record datasets
   - **Problem**: Worker timeouts with large Excel files
   - **Solution**: Optimized pandas reading, chunked processing, progress logging
   - **Timeout**: Extended to 300 seconds for large file processing

3. **Session-based Storage**: Chosen for simplicity over database persistence
   - **Pros**: Quick development, no database setup required
   - **Cons**: Data lost on session expiry, limited scalability

4. **In-memory Search Indexing**: Selected for performance over database queries
   - **Pros**: Fast search responses, no database overhead
   - **Cons**: Memory usage scales with data size

5. **Fuzzy Matching**: Implemented for Arabic text variations
   - **Problem**: Arabic names have multiple valid spellings
   - **Solution**: Custom normalization + SequenceMatcher similarity
   - **Benefit**: More user-friendly search experience

6. **RTL Layout**: Full Arabic language support implemented
   - **Requirement**: Proper Arabic text display and navigation
   - **Solution**: Bootstrap RTL + custom CSS + Arabic fonts
   - **Result**: Native Arabic user experience

The application is designed for educational institutions to search student records in Arabic Excel files, with emphasis on user-friendly interface and accurate search results despite spelling variations common in Arabic text.