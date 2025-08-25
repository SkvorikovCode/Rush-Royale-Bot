import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from .config import get_settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with appropriate handlers."""
    settings = get_settings()
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if settings.debug:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if settings.log_file or settings.logs_dir:
        log_file = settings.log_file or str(Path(settings.logs_dir) / "api.log")
        
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        
        if settings.debug:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger."""
    return setup_logger(name)

class LogCapture:
    """Capture logs for monitoring and WebSocket broadcasting."""
    
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.entries: list = []
        self.handler = LogCaptureHandler(self)
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)
    
    def add_entry(self, record: logging.LogRecord):
        """Add a log entry."""
        entry = {
            "id": f"{record.created}_{record.thread}",
            "timestamp": datetime.fromtimestamp(record.created),
            "level": record.levelname.lower(),
            "source": record.name,
            "message": record.getMessage(),
            "details": {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
        }
        
        # Add exception info if present
        if record.exc_info:
            entry["details"]["exception"] = logging.Formatter().formatException(record.exc_info)
        
        self.entries.append(entry)
        
        # Keep only the most recent entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_recent_entries(self, limit: int = 100, level: Optional[str] = None) -> list:
        """Get recent log entries."""
        entries = self.entries
        
        if level:
            entries = [e for e in entries if e["level"] == level.lower()]
        
        return entries[-limit:]
    
    def clear(self):
        """Clear all captured entries."""
        self.entries.clear()

class LogCaptureHandler(logging.Handler):
    """Handler that captures logs for the LogCapture system."""
    
    def __init__(self, capture: LogCapture):
        super().__init__()
        self.capture = capture
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to the capture system."""
        try:
            self.capture.add_entry(record)
        except Exception:
            # Avoid infinite recursion if logging fails
            pass

# Global log capture instance
_log_capture: Optional[LogCapture] = None

def get_log_capture() -> LogCapture:
    """Get the global log capture instance."""
    global _log_capture
    if _log_capture is None:
        _log_capture = LogCapture()
    return _log_capture

def log_performance(func):
    """Decorator to log function performance."""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(
                f"Function {func.__name__} executed successfully",
                extra={"execution_time": execution_time}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed: {str(e)}",
                extra={"execution_time": execution_time, "error": str(e)}
            )
            raise
    
    return wrapper

def log_api_request(func):
    """Decorator to log API requests."""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger("api")
        
        # Extract request info if available
        request_info = {}
        for arg in args:
            if hasattr(arg, 'method') and hasattr(arg, 'url'):
                request_info = {
                    "method": arg.method,
                    "url": str(arg.url),
                    "client": str(getattr(arg, 'client', 'unknown'))
                }
                break
        
        logger.info(
            f"API request: {func.__name__}",
            extra=request_info
        )
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"API request {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(
                f"API request {func.__name__} failed: {str(e)}",
                extra={"error": str(e)}
            )
            raise
    
    return wrapper