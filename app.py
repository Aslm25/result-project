import os
import logging
import math
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import pandas as pd
from excel_processor import ExcelProcessor
from arabic_search import ArabicSearchEngine

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Global variables for data storage
excel_processor = None
search_engine = None

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_available_data_files():
    """Get list of Excel files from data directory"""
    data_files = []
    data_dir = app.config['DATA_FOLDER']
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if allowed_file(filename):
                filepath = os.path.join(data_dir, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    data_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_size,
                        'size_formatted': format_file_size(file_size)
                    })
    
    return sorted(data_files, key=lambda x: x['filename'])

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

@app.route('/')
def index():
    """Main page with file upload and search interface"""
    logging.info("Accessing main index page")
    has_data = 'excel_data' in session or session.get('has_data', False)
    columns = session.get('columns', [])
    data_files = get_available_data_files()
    
    # Log current session state for debugging
    logging.info(f"Session has_data: {has_data}, columns: {len(columns) if columns else 0}")
    
    return render_template('index.html', has_data=has_data, columns=columns, data_files=data_files)

@app.route('/home')
def home():
    """Alternative home route"""
    return redirect(url_for('index'))

@app.route('/load_data_file', methods=['POST'])
def load_data_file():
    """Load Excel file from data directory"""
    global excel_processor, search_engine
    
    filename = request.form.get('filename')
    if not filename:
        flash('لم يتم اختيار أي ملف', 'error')
        return redirect(url_for('index'))
    
    filepath = os.path.join(app.config['DATA_FOLDER'], filename)
    
    if not os.path.exists(filepath) or not allowed_file(filename):
        flash('الملف غير موجود أو نوعه غير مدعوم', 'error')
        return redirect(url_for('index'))
    
    # Check file size
    file_size = os.path.getsize(filepath)
    file_size_mb = file_size / (1024 * 1024)
    
    if file_size_mb > 30:  # Warn for files larger than 30MB
        flash(f'تحذير: حجم الملف كبير ({file_size_mb:.1f} ميجابايت). قد يستغرق التحميل عدة دقائق.', 'warning')
    
    try:
        logging.info(f"Starting to process file: {filename} ({file_size_mb:.1f}MB)")
        
        # Process Excel file
        excel_processor = ExcelProcessor()
        data, columns = excel_processor.load_excel(filepath)
        
        if data is None:
            flash('خطأ في معالجة ملف الإكسل', 'error')
            return redirect(url_for('index'))
        
        logging.info(f"Successfully loaded {len(data)} records with {len(columns)} columns")
        
        # Initialize search engine
        logging.info("Initializing search engine...")
        search_engine = ArabicSearchEngine(data, columns)
        logging.info("Search engine ready")
        
        # Store in session
        session['has_data'] = True
        session['columns'] = columns
        session['filename'] = filename
        session['total_records'] = len(data)
        
        flash(f'تم تحميل الملف بنجاح. عدد السجلات: {len(data):,}', 'success')
        
    except Exception as e:
        logging.error(f"Error processing file {filename}: {str(e)}")
        flash(f'خطأ في معالجة الملف: {str(e)}', 'error')
        # Clear any partial data
        excel_processor = None
        search_engine = None
        session.pop('has_data', None)
    
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle Excel file upload and processing"""
    global excel_processor, search_engine
    
    if 'file' not in request.files:
        flash('لم يتم اختيار أي ملف', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('لم يتم اختيار أي ملف', 'error')
        return redirect(request.url)
    
    if file and file.filename and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process Excel file
            excel_processor = ExcelProcessor()
            data, columns = excel_processor.load_excel(filepath)
            
            if data is None:
                flash('خطأ في معالجة ملف الإكسل', 'error')
                return redirect(url_for('index'))
            
            # Initialize search engine
            search_engine = ArabicSearchEngine(data, columns)
            
            # Store in session (for small datasets) or use file-based storage for large ones
            session['has_data'] = True
            session['columns'] = columns
            session['filename'] = filename
            session['total_records'] = len(data)
            
            flash(f'تم رفع الملف بنجاح. عدد السجلات: {len(data):,}', 'success')
            
            # Clean up uploaded file to save space
            os.remove(filepath)
            
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            flash(f'خطأ في معالجة الملف: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    flash('نوع الملف غير مدعوم. يرجى رفع ملف Excel (.xlsx أو .xls)', 'error')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    global search_engine
    
    if not search_engine:
        flash('يرجى رفع ملف Excel أولاً', 'error')
        return redirect(url_for('index'))
    
    search_type = request.form.get('search_type', 'name')
    query = request.form.get('query', '').strip()
    page = int(request.form.get('page', 1))
    per_page = 50  # Results per page
    
    if not query:
        flash('يرجى إدخال نص البحث', 'error')
        return redirect(url_for('index'))
    
    try:
        if search_type == 'id':
            # Search by رقم الجلوس (ID)
            results = search_engine.search_by_id(query)
        else:
            # Search by الاسم (name) with fuzzy matching
            results = search_engine.search_by_name(query)
        
        # Pagination
        total_results = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = results[start:end]
        
        # Calculate pagination info
        total_pages = (total_results + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('search_results.html',
                             results=paginated_results,
                             query=query,
                             search_type=search_type,
                             total_results=total_results,
                             page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             columns=session.get('columns', []))
    
    except Exception as e:
        logging.error(f"Error during search: {str(e)}")
        flash(f'خطأ في البحث: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/clear_data')
def clear_data():
    """Clear uploaded data and reset session"""
    global excel_processor, search_engine
    
    excel_processor = None
    search_engine = None
    
    # Clear session data
    keys_to_remove = ['has_data', 'columns', 'filename', 'total_records']
    for key in keys_to_remove:
        session.pop(key, None)
    
    flash('تم مسح البيانات بنجاح', 'success')
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('حجم الملف كبير جداً. الحد الأقصى 50 ميجابايت', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logging.error(f"Internal error: {str(e)}")
    flash('حدث خطأ داخلي في النظام', 'error')
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
