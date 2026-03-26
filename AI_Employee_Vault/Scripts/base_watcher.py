"""
Base Watcher Module

Abstract base class for all Watcher scripts in the AI Employee system.
Watchers monitor various inputs (Gmail, WhatsApp, filesystems) and create
actionable .md files in the Needs_Action folder.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all Watcher implementations.
    
    All Watchers follow the same pattern:
    1. Continuously monitor a data source
    2. Detect new/updated items
    3. Create .md action files in the Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f'{self.__class__.__name__} initialized')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {check_interval}s')
    
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_file = self.logs / f'watcher_{datetime.now().strftime("%Y%m%d")}.log'
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new or updated items.
        
        Returns:
            List of items that need processing
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError(
            "Subclasses must implement check_for_updates()"
        )
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if failed
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError(
            "Subclasses must implement create_action_file()"
        )
    
    def run(self):
        """
        Main run loop for the Watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Watching for changes every {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new items')
                    
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            self.logger.info(f'{self.__class__.__name__} shutting down')
    
    def is_already_processed(self, item_id: str) -> bool:
        """
        Check if an item has already been processed.
        
        Args:
            item_id: Unique identifier for the item
            
        Returns:
            True if already processed, False otherwise
        """
        return item_id in self.processed_ids
    
    def mark_as_processed(self, item_id: str):
        """
        Mark an item as processed.
        
        Args:
            item_id: Unique identifier for the item
        """
        self.processed_ids.add(item_id)
        self.logger.debug(f'Marked item as processed: {item_id}')
    
    def get_existing_files(self) -> set:
        """
        Get set of existing action file names to avoid overwriting.
        
        Returns:
            Set of existing file names in Needs_Action folder
        """
        return {f.name for f in self.needs_action.iterdir() if f.is_file()}
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: Type prefix (e.g., 'EMAIL', 'FILE', 'TASK')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
    
    def write_action_file(self, filename: str, content: str) -> Path:
        """
        Write content to an action file.
        
        Args:
            filename: Name of the file to create
            content: Markdown content to write
            
        Returns:
            Path to the created file
        """
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def create_standard_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create standard YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, file, task, etc.)
            **kwargs: Additional frontmatter fields
            
        Returns:
            YAML frontmatter string
        """
        frontmatter = f"""---
type: {item_type}
created: {datetime.now().isoformat()}
status: pending
priority: normal
"""
        # Add additional fields
        for key, value in kwargs.items():
            frontmatter += f'{key}: {value}\n'
        
        frontmatter += '---\n\n'
        return frontmatter
