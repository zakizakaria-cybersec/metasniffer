from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

def ensure_dir(directory: Path):
    """
    Ensure a directory exists, create if it doesn't.
    """
    directory.mkdir(parents=True, exist_ok=True)

def cleanup_files(directory: Path):
    """
    Remove all files in the specified directory.
    """
    try:
        shutil.rmtree(directory)
        directory.mkdir(exist_ok=True)
    except Exception as e:
        logger.error(f"Error cleaning up directory {directory}: {e}")