// Main JavaScript for Arabic Excel Search Application
document.addEventListener('DOMContentLoaded', function() {
    
    // File upload handling
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const file = fileInput.files[0];
            
            if (file) {
                // Validate file size
                const maxSize = 50 * 1024 * 1024; // 50MB
                if (file.size > maxSize) {
                    e.preventDefault();
                    alert('حجم الملف كبير جداً. الحد الأقصى 50 ميجابايت');
                    return;
                }
                
                // Validate file type
                const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                                    'application/vnd.ms-excel'];
                const fileName = file.name.toLowerCase();
                
                if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
                    e.preventDefault();
                    alert('نوع الملف غير مدعوم. يرجى رفع ملف Excel (.xlsx أو .xls)');
                    return;
                }
                
                // Show progress
                showUploadProgress();
            }
        });
    }
    
    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                updateFileInfo(file);
            }
        });
    }
    
    // Search form handling
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = document.getElementById('query').value.trim();
            
            if (!query) {
                e.preventDefault();
                alert('يرجى إدخال نص البحث');
                return;
            }
            
            // Show loading state
            showSearchLoading();
        });
        
        // Auto-focus on query input
        const queryInput = document.getElementById('query');
        if (queryInput) {
            queryInput.focus();
        }
    }
    
    // Search type change handler
    const searchTypeRadios = document.querySelectorAll('input[name="search_type"]');
    searchTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateSearchPlaceholder();
            updateSearchHelp();
        });
    });
    
    // Initialize tooltips
    initializeTooltips();
    
    // Auto-hide alerts after 5 seconds
    autoHideAlerts();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
});

function showUploadProgress() {
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    
    if (uploadBtn && uploadProgress) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>جاري الرفع...';
        uploadProgress.style.display = 'block';
    }
}

function updateFileInfo(file) {
    const fileSize = formatFileSize(file.size);
    const fileName = file.name;
    
    // Create or update file info display
    let fileInfo = document.getElementById('fileInfo');
    if (!fileInfo) {
        fileInfo = document.createElement('div');
        fileInfo.id = 'fileInfo';
        fileInfo.className = 'mt-2 small text-muted';
        document.getElementById('file').parentNode.appendChild(fileInfo);
    }
    
    fileInfo.innerHTML = `
        <i class="fas fa-file-excel me-1"></i>
        ${fileName} (${fileSize})
    `;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showSearchLoading() {
    const searchBtn = document.querySelector('#searchForm button[type="submit"]');
    if (searchBtn) {
        searchBtn.disabled = true;
        const originalText = searchBtn.innerHTML;
        searchBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>جاري البحث...';
        
        // Re-enable after a delay (fallback)
        setTimeout(() => {
            searchBtn.disabled = false;
            searchBtn.innerHTML = originalText;
        }, 10000);
    }
}

function updateSearchPlaceholder() {
    const queryInput = document.getElementById('query');
    const selectedType = document.querySelector('input[name="search_type"]:checked');
    
    if (queryInput && selectedType) {
        if (selectedType.value === 'name') {
            queryInput.placeholder = 'أدخل جزء من الاسم...';
        } else {
            queryInput.placeholder = 'أدخل رقم الجلوس...';
        }
    }
}

function updateSearchHelp() {
    const searchHelpText = document.getElementById('searchHelpText');
    const selectedType = document.querySelector('input[name="search_type"]:checked');
    
    if (searchHelpText && selectedType) {
        if (selectedType.value === 'name') {
            searchHelpText.textContent = 'البحث الذكي يجد النتائج المشابهة حتى مع الاختلافات البسيطة';
        } else {
            searchHelpText.textContent = 'البحث برقم الجلوس يجد المطابقة الدقيقة أو الجزئية';
        }
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+F or Cmd+F to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            const queryInput = document.getElementById('query');
            if (queryInput) {
                e.preventDefault();
                queryInput.focus();
                queryInput.select();
            }
        }
        
        // Escape to clear search or go back
        if (e.key === 'Escape') {
            const queryInput = document.getElementById('query');
            if (queryInput && queryInput.value) {
                queryInput.value = '';
                queryInput.focus();
            } else {
                // Go back to main page if on results page
                if (window.location.pathname.includes('search')) {
                    window.location.href = '/';
                }
            }
        }
        
        // Enter to submit search form
        if (e.key === 'Enter' && document.activeElement && document.activeElement.id === 'query') {
            const searchForm = document.getElementById('searchForm');
            if (searchForm) {
                searchForm.submit();
            }
        }
    });
}

// Utility functions
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function formatNumber(num) {
    return num.toLocaleString('ar-SA');
}

// Export functions for potential external use
window.ArabicExcelSearch = {
    showUploadProgress,
    showSearchLoading,
    updateSearchPlaceholder,
    updateSearchHelp,
    formatFileSize,
    formatNumber,
    debounce
};

// Service Worker registration for offline capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
