import os

# Import Configuration
class ImportConfig:
    # Debug mode - set to True to see detailed logs
    DEBUG_MODE = os.getenv('IMPORT_DEBUG', 'false').lower() == 'true'
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))  # seconds
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', '3'))
    
    # Threading Configuration
    MAX_WORKERS = int(os.getenv('IMPORT_MAX_WORKERS', '20'))
    
    # Batch Processing
    BATCH_SIZE = int(os.getenv('IMPORT_BATCH_SIZE', '1000'))
    
    # Connection Pool
    POOL_CONNECTIONS = int(os.getenv('POOL_CONNECTIONS', '20'))
    POOL_MAXSIZE = int(os.getenv('POOL_MAXSIZE', '100'))
    
    # Logging Configuration
    SHOW_SUCCESS_LOGS = os.getenv('SHOW_SUCCESS_LOGS', 'false').lower() == 'true'
    SHOW_404_ERRORS = os.getenv('SHOW_404_ERRORS', 'false').lower() == 'true'
    SHOW_API_ERRORS = os.getenv('SHOW_API_ERRORS', 'true').lower() == 'true'
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("=== Import Configuration ===")
        print(f"DEBUG_MODE: {cls.DEBUG_MODE}")
        print(f"API_TIMEOUT: {cls.API_TIMEOUT}s")
        print(f"API_MAX_RETRIES: {cls.API_MAX_RETRIES}")
        print(f"MAX_WORKERS: {cls.MAX_WORKERS}")
        print(f"BATCH_SIZE: {cls.BATCH_SIZE}")
        print(f"POOL_CONNECTIONS: {cls.POOL_CONNECTIONS}")
        print(f"POOL_MAXSIZE: {cls.POOL_MAXSIZE}")
        print(f"SHOW_SUCCESS_LOGS: {cls.SHOW_SUCCESS_LOGS}")
        print(f"SHOW_404_ERRORS: {cls.SHOW_404_ERRORS}")
        print(f"SHOW_API_ERRORS: {cls.SHOW_API_ERRORS}")
        print("===========================")

# Environment variables để cấu hình:
# 
# IMPORT_DEBUG=true              # Bật debug mode
# API_TIMEOUT=15                 # Timeout cho API calls (giây)
# API_MAX_RETRIES=5              # Số lần retry
# IMPORT_MAX_WORKERS=30          # Số worker threads
# IMPORT_BATCH_SIZE=100          # Kích thước batch
# POOL_CONNECTIONS=30            # Số connections trong pool
# POOL_MAXSIZE=150               # Max connections
# SHOW_SUCCESS_LOGS=true         # Hiển thị log thành công
# SHOW_404_ERRORS=true           # Hiển thị lỗi 404
# SHOW_API_ERRORS=false          # Ẩn lỗi API 