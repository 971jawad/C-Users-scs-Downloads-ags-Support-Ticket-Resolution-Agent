"""
Utility Functions for Support Agent

This module provides common utility functions used throughout the support
agent system, including logging setup, data formatting, file operations,
and monitoring helpers.
"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/agent.log",
    console_output: bool = True
) -> None:
    """
    Set up comprehensive logging for the support agent system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        console_output: Whether to also log to console
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Set up root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[]
    )
    
    # Add file handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logging.getLogger().addHandler(file_handler)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        logging.getLogger().addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("support_agent").setLevel(logging.INFO)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")

def log_escalation(escalation_data: Dict[str, Any], csv_file: str = "escalation_log.csv") -> bool:
    """
    Log escalated ticket data to CSV file for human review.
    
    This function maintains a comprehensive log of all escalated tickets
    with complete context for human agents to review and learn from.
    
    Args:
        escalation_data: Dictionary containing escalation information
        csv_file: Path to the escalation log CSV file
        
    Returns:
        True if logging was successful, False otherwise
    """
    try:
        logger = logging.getLogger(__name__)
        
        # Prepare CSV row data
        csv_row = {
            'timestamp': escalation_data.get('timestamp', datetime.now().isoformat()),
            'ticket_subject': escalation_data.get('ticket_subject', ''),
            'ticket_description': escalation_data.get('ticket_description', ''),
            'category': escalation_data.get('category', ''),
            'retry_attempts': escalation_data.get('retry_attempts', 0),
            'draft_count': len(escalation_data.get('drafts', [])),
            'feedback_count': len(escalation_data.get('review_feedback', [])),
            'context_documents': len(escalation_data.get('retrieved_context', [])),
            'final_drafts': json.dumps(escalation_data.get('drafts', [])),
            'review_feedback': json.dumps(escalation_data.get('review_feedback', [])),
            'context_summary': json.dumps([doc.get('source', 'unknown') for doc in escalation_data.get('retrieved_context', [])])
        }
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(csv_file)
        
        # Write to CSV
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = list(csv_row.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(csv_row)
        
        logger.info(f"Escalation logged to {csv_file}")
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error logging escalation: {str(e)}")
        return False

def save_escalation_log(escalation_data: Dict[str, Any], csv_file: str = "escalation_log.csv") -> bool:
    """
    Save escalation data to CSV log file.
    
    Args:
        escalation_data: Dictionary containing escalation details
        csv_file: Path to the CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Flatten complex data structures for CSV
        flattened_data = {
            'timestamp': escalation_data['timestamp'],
            'ticket_subject': escalation_data['ticket_subject'],
            'ticket_description': escalation_data['ticket_description'],
            'category': escalation_data['category'],
            'retries': escalation_data['retries'],
            'review_count': len(escalation_data.get('review_feedback', [])),
            'draft_count': len(escalation_data.get('final_drafts', []))
        }
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=flattened_data.keys())
            
            # Write header if this is a new file
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(flattened_data)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Escalation data saved to {csv_file}")
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving escalation log: {str(e)}")
        return False

def load_escalation_log(csv_file: str = "escalation_log.csv") -> pd.DataFrame:
    """
    Load the escalation log as a pandas DataFrame for analysis.
    
    Args:
        csv_file: Path to the escalation log CSV file
        
    Returns:
        DataFrame containing escalation data, empty if file doesn't exist
    """
    try:
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
        else:
            # Return empty DataFrame with expected columns
            columns = [
                'timestamp', 'ticket_subject', 'ticket_description', 'category',
                'retry_attempts', 'draft_count', 'feedback_count', 'context_documents',
                'final_drafts', 'review_feedback', 'context_summary'
            ]
            return pd.DataFrame(data=None, columns=columns)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading escalation log: {str(e)}")
        return pd.DataFrame()

def format_response(draft: str, category: str, ticket_subject: str) -> str:
    """
    Format a final response with professional styling and category-specific elements.
    
    Args:
        draft: The approved response draft
        category: Ticket category for custom formatting
        ticket_subject: Original ticket subject for reference
        
    Returns:
        Professionally formatted final response
    """
    try:
        # Category-specific closings
        category_closings = {
            'Billing': "If you have any additional billing questions, please don't hesitate to reach out.",
            'Technical': "If you continue to experience technical difficulties, please contact our technical support team.",
            'Security': "For any additional security concerns, please contact our security team immediately.",
            'General': "If you need any further assistance, please feel free to contact us."
        }
        
        # Format the response
        formatted_response = f"{draft.strip()}\n\n"
        
        # Add category-specific closing
        closing = category_closings.get(category, category_closings['General'])
        formatted_response += f"{closing}\n\n"
        
        # Add standard professional closing
        formatted_response += "Best regards,\nCustomer Support Team"
        
        return formatted_response
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error formatting response: {str(e)}")
        return draft  # Return original draft as fallback

def validate_ticket_input(ticket: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate support ticket input data.
    
    Args:
        ticket: Dictionary containing ticket data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required fields
        if not isinstance(ticket, dict):
            return False, "Ticket must be a dictionary"
        
        if 'subject' not in ticket:
            return False, "Ticket must have a 'subject' field"
        
        if 'description' not in ticket:
            return False, "Ticket must have a 'description' field"
        
        # Validate field types and content
        subject = ticket['subject']
        description = ticket['description']
        
        if not isinstance(subject, str) or not subject.strip():
            return False, "Subject must be a non-empty string"
        
        if not isinstance(description, str) or not description.strip():
            return False, "Description must be a non-empty string"
        
        # Check reasonable length limits
        if len(subject) > 200:
            return False, "Subject must be 200 characters or less"
        
        if len(description) > 5000:
            return False, "Description must be 5000 characters or less"
        
        return True, ""
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def create_system_status() -> Dict[str, Any]:
    """
    Create a system status report for monitoring and debugging.
    
    Returns:
        Dictionary containing system status information
    """
    try:
        # Check environment variables
        env_status = {
            'gemini_api_key_configured': bool(os.getenv('GEMINI_API_KEY')),
            'python_version': __import__('sys').version,
            'working_directory': os.getcwd()
        }
        
        # Check file system
        file_status = {
            'logs_directory_exists': os.path.exists('logs'),
            'data_directory_exists': os.path.exists('data'),
            'escalation_log_exists': os.path.exists('escalation_log.csv'),
            'knowledge_base_files': []
        }
        
        # Check for knowledge base files
        data_dir = 'data'
        if os.path.exists(data_dir):
            for category in ['billing', 'technical', 'security', 'general']:
                filename = f"{category}_docs.json"
                filepath = os.path.join(data_dir, filename)
                file_status['knowledge_base_files'].append({
                    'category': category,
                    'exists': os.path.exists(filepath),
                    'path': filepath
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'environment': env_status,
            'filesystem': file_status,
            'status': 'healthy'
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating system status: {str(e)}")
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

def ensure_directories():
    """
    Ensure all required directories exist for the support agent system.
    """
    directories = ['logs', 'data', 'indexes']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Ensured directories exist: {', '.join(directories)}")

def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned and normalized text
    """
    if not isinstance(text, str):
        return ""
    
    # Basic text cleaning
    cleaned = text.strip()
    
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Remove any control characters
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
    
    return cleaned

def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File size in MB, or 0 if file doesn't exist
    """
    try:
        if os.path.exists(filepath):
            size_bytes = os.path.getsize(filepath)
            return size_bytes / (1024 * 1024)
        return 0.0
    except Exception:
        return 0.0

def backup_escalation_log(csv_file: str = "escalation_log.csv") -> bool:
    """
    Create a backup of the escalation log file.
    
    Args:
        csv_file: Path to the escalation log file
        
    Returns:
        True if backup was successful, False otherwise
    """
    try:
        if not os.path.exists(csv_file):
            return True  # Nothing to backup
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"escalation_log_backup_{timestamp}.csv"
        
        # Copy the file
        import shutil
        shutil.copy2(csv_file, backup_file)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Escalation log backed up to {backup_file}")
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error backing up escalation log: {str(e)}")
        return False

# Performance monitoring utilities
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        else:
            duration = 0.0
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed {self.operation_name} after {duration:.3f}s: {exc_val}")
    
    @property
    def duration_seconds(self) -> float:
        """Get the operation duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

# Initialize required directories on module import
ensure_directories()
