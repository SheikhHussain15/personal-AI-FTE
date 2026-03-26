"""
File System Watcher

Monitors the Inbox folder for new files and creates action files
in the Needs_Action folder for Claude Code to process.

This is the Bronze Tier watcher - simple, reliable, and doesn't require
external API credentials.
"""

import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped in the Inbox."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.name = filepath.name
        self.size = filepath.stat().st_size
        self.created = datetime.fromtimestamp(filepath.stat().st_ctime)
        self.modified = datetime.fromtimestamp(filepath.stat().st_mtime)
        self.content_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate MD5 hash of file content for deduplication."""
        hash_md5 = hashlib.md5()
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            'name': self.name,
            'size': self.size,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'hash': self.content_hash,
            'path': str(self.filepath)
        }


class FilesystemWatcher(BaseWatcher):
    """
    Watches the Inbox folder for new files.
    
    When a file is detected:
    1. Copy it to Needs_Action folder
    2. Create a metadata .md file with action items
    3. Log the action for audit trail
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the Filesystem Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Track processed file hashes
        self.processed_hashes: set = set()
        
        # File type handlers
        self.file_handlers = {
            '.txt': self._handle_text_file,
            '.md': self._handle_markdown_file,
            '.pdf': self._handle_pdf_file,
            '.doc': self._handle_document_file,
            '.docx': self._handle_document_file,
            '.xls': self._handle_spreadsheet_file,
            '.xlsx': self._handle_spreadsheet_file,
            '.csv': self._handle_csv_file,
            '.jpg': self._handle_image_file,
            '.jpeg': self._handle_image_file,
            '.png': self._handle_image_file,
        }
        
        self.logger.info('Filesystem Watcher ready')
        self.logger.info(f'Watching: {self.inbox}')
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check the Inbox folder for new files.
        
        Returns:
            List of new FileDropItem objects
        """
        new_items = []
        
        try:
            if not self.inbox.exists():
                self.logger.debug('Inbox folder does not exist yet')
                return []
            
            # Get all files in inbox
            for filepath in self.inbox.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    item = FileDropItem(filepath)
                    
                    # Skip if already processed
                    if item.content_hash in self.processed_hashes:
                        self.logger.debug(f'File already processed: {item.name}')
                        continue
                    
                    # Skip if file is being written (size might change)
                    try:
                        current_size = filepath.stat().st_size
                        import time
                        time.sleep(0.1)
                        new_size = filepath.stat().st_size
                        if current_size != new_size:
                            self.logger.debug(f'File still being written: {item.name}')
                            continue
                    except OSError:
                        self.logger.warning(f'Could not verify file stability: {item.name}')
                        continue
                    
                    new_items.append(item)
                    self.logger.info(f'New file detected: {item.name} ({item.size} bytes)')
                    
        except Exception as e:
            self.logger.error(f'Error checking inbox: {e}')
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            item: FileDropItem to process
            
        Returns:
            Path to created action file
        """
        try:
            # Copy file to Needs_Action
            dest_path = self.needs_action / f'FILE_{item.name}'
            shutil.copy2(item.filepath, dest_path)
            self.logger.info(f'Copied file to: {dest_path}')
            
            # Get handler for file type
            handler = self.file_handlers.get(
                item.filepath.suffix.lower(),
                self._handle_unknown_file
            )
            
            # Create metadata action file
            metadata_content = handler(item, dest_path)
            metadata_path = self.needs_action / f'FILE_{item.name}.meta.md'
            self.write_action_file(metadata_path.name, metadata_content)
            
            # Mark as processed
            self.mark_as_processed(item.content_hash)
            
            # Remove original from inbox
            item.filepath.unlink()
            self.logger.info(f'Removed from inbox: {item.name}')
            
            return metadata_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _handle_text_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle plain text files."""
        return self._create_metadata(
            item, dest_path,
            file_type='text',
            suggested_actions=[
                'Review content',
                'Extract key information',
                'Categorize and file',
                'Take action if needed'
            ]
        )
    
    def _handle_markdown_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle Markdown files."""
        return self._create_metadata(
            item, dest_path,
            file_type='markdown',
            suggested_actions=[
                'Review content',
                'Link to related notes',
                'Update index if needed'
            ]
        )
    
    def _handle_pdf_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle PDF files."""
        return self._create_metadata(
            item, dest_path,
            file_type='pdf',
            suggested_actions=[
                'Extract text content',
                'Summarize key points',
                'File in appropriate category',
                'Action any requests or deadlines'
            ]
        )
    
    def _handle_document_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle Word documents."""
        return self._create_metadata(
            item, dest_path,
            file_type='document',
            suggested_actions=[
                'Convert to Markdown for vault',
                'Extract key information',
                'File in appropriate category'
            ]
        )
    
    def _handle_spreadsheet_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle Excel files."""
        return self._create_metadata(
            item, dest_path,
            file_type='spreadsheet',
            suggested_actions=[
                'Review data',
                'Extract summary statistics',
                'Update accounting if financial',
                'File in appropriate category'
            ]
        )
    
    def _handle_csv_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle CSV files."""
        return self._create_metadata(
            item, dest_path,
            file_type='csv',
            suggested_actions=[
                'Parse and review data',
                'Import to relevant system',
                'Generate summary if needed'
            ]
        )
    
    def _handle_image_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle image files."""
        return self._create_metadata(
            item, dest_path,
            file_type='image',
            suggested_actions=[
                'Add alt text description',
                'OCR if contains text',
                'File in appropriate category'
            ]
        )
    
    def _handle_unknown_file(self, item: FileDropItem, dest_path: Path) -> str:
        """Handle unknown file types."""
        return self._create_metadata(
            item, dest_path,
            file_type='unknown',
            suggested_actions=[
                'Identify file type',
                'Determine appropriate action',
                'Convert if possible',
                'File or discard'
            ]
        )
    
    def _create_metadata(
        self,
        item: FileDropItem,
        dest_path: Path,
        file_type: str,
        suggested_actions: List[str]
    ) -> str:
        """
        Create standard metadata content for a file drop.
        
        Args:
            item: The file item
            dest_path: Path to copied file
            file_type: Type classification
            suggested_actions: List of suggested actions
            
        Returns:
            Markdown content string
        """
        actions_list = '\n'.join([f'- [ ] {action}' for action in suggested_actions])
        
        content = f"""---
type: file_drop
file_type: {file_type}
original_name: {item.name}
file_path: {dest_path.name}
size: {self._format_size(item.size)}
size_bytes: {item.size}
content_hash: {item.content_hash}
received: {datetime.now().isoformat()}
status: pending
priority: normal
---

# File Drop: {item.name}

## File Information

| Property | Value |
|----------|-------|
| Original Name | {item.name} |
| Type | {file_type} |
| Size | {self._format_size(item.size)} |
| Received | {datetime.now().strftime('%Y-%m-%d %H:%M')} |
| Content Hash | {item.content_hash} |

## Suggested Actions

{actions_list}

## Notes

*Add any notes or context about this file here*

---
*Created by Filesystem Watcher v0.1*
"""
        return content
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'


def main():
    """Run the Filesystem Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Filesystem Watcher for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds'
    )
    
    args = parser.parse_args()
    
    # Resolve to absolute path
    vault_path = Path(args.vault).resolve()
    
    watcher = FilesystemWatcher(str(vault_path), args.interval)
    watcher.run()


if __name__ == '__main__':
    main()
