import json
import os
import hashlib
from typing import Optional, Dict

class SummaryManager:
    def __init__(self, summaries_file: str = "paper_summaries.json"):
        self.summaries_file = summaries_file
        self.summaries = self._load_summaries()

    def _load_summaries(self) -> Dict:
        """Load summaries from file"""
        if not os.path.exists(self.summaries_file):
            return {}
        
        try:
            with open(self.summaries_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_summaries(self) -> None:
        """Save summaries to file"""
        with open(self.summaries_file, 'w') as f:
            json.dump(self.summaries, f, indent=4)

    def _generate_key(self, content: str, profile_name: Optional[str] = None) -> str:
        """Generate a unique key for the paper content and profile"""
        key_content = content
        if profile_name:
            key_content += profile_name
        return hashlib.md5(key_content.encode()).hexdigest()

    def get_summary(self, content: str, profile_name: Optional[str] = None) -> Optional[str]:
        """Get existing summary for paper content and profile"""
        key = self._generate_key(content, profile_name)
        return self.summaries.get(key)

    def save_summary(self, content: str, summary: str, profile_name: Optional[str] = None) -> None:
        """Save summary for paper content and profile"""
        key = self._generate_key(content, profile_name)
        self.summaries[key] = summary
        self._save_summaries() 