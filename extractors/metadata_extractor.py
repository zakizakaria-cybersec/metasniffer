import subprocess
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class MetadataExtractor:
    def extract_metadata(self, file_path: Path) -> dict:
        """
        Extract metadata from a file using exiftool.
        """
        try:
            result = subprocess.run(
                ['exiftool', '-json', str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)[0]
                return self._clean_metadata(metadata)
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            
        return {}
    
    def _clean_metadata(self, metadata: dict) -> dict:
        """
        Clean and standardize metadata fields.
        """
        clean_data = {}
        
        # Map of common author field names
        author_fields = [
            'Author', 'Creator', 'Artist', 'By-line',
            'Writer', 'Producer', 'Owner'
        ]
        
        for field in author_fields:
            if field in metadata and metadata[field]:
                clean_data['Author'] = metadata[field]
                break
                
        if 'CreateDate' in metadata:
            clean_data['Creation Date'] = metadata['CreateDate']
            
        return clean_data