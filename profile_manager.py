import json
import os
from typing import Dict, List, Optional

class ProfileManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.profiles = self._load_profiles()

    def _create_default_settings(self) -> Dict:
        """Create default settings with a basic profile"""
        return {
            "profiles": [
                {
                    "name": "Default Profile",
                    "description": "A balanced profile suitable for general research paper analysis",
                    "constraints": [
                        "Maximum 500 words for summary",
                        "Focus on key findings and methodology",
                        "Include practical implications",
                        "Highlight limitations and future work",
                        "Use clear, accessible language"
                    ],
                    "outputStyle": {
                        "language": "formal",
                        "technicalLevel": "intermediate",
                        "structurePreference": "paragraph",
                        "responseLanguage": "English",
                        "visualAids": True
                    },
                    "selected": True
                }
            ]
        }

    def _load_profiles(self) -> Dict:
        """Load profiles from settings file or create default if not exists"""
        if not os.path.exists(self.settings_file):
            default_settings = self._create_default_settings()
            self._save_profiles(default_settings)
            return default_settings
        
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                # Ensure at least one profile exists
                if not settings.get("profiles"):
                    settings = self._create_default_settings()
                    self._save_profiles(settings)
                # Ensure exactly one profile is selected
                selected_found = False
                for profile in settings["profiles"]:
                    if profile.get("selected", False):
                        if selected_found:
                            profile["selected"] = False
                        else:
                            selected_found = True
                if not selected_found and settings["profiles"]:
                    settings["profiles"][0]["selected"] = True
                return settings
        except json.JSONDecodeError:
            # If settings file is corrupted, create new default settings
            default_settings = self._create_default_settings()
            self._save_profiles(default_settings)
            return default_settings

    def _save_profiles(self, settings: Dict) -> None:
        """Save profiles to settings file"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_all_profiles(self) -> List[Dict]:
        """Get all available profiles"""
        return self.profiles.get("profiles", [])

    def get_profile_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific profile by name"""
        for profile in self.profiles.get("profiles", []):
            if profile["name"] == name:
                return profile
        return None

    def get_active_profile(self) -> Optional[Dict]:
        """Get the currently selected profile"""
        for profile in self.profiles.get("profiles", []):
            if profile.get("selected", False):
                return profile
        return None

    def create_profile(self, profile: Dict) -> None:
        """Create a new profile"""
        if self.get_profile_by_name(profile["name"]):
            raise ValueError(f"Profile '{profile['name']}' already exists")
        
        self.profiles["profiles"].append(profile)
        self._save_profiles(self.profiles)

    def update_profile(self, old_name: str, new_profile: Dict) -> None:
        """Update an existing profile"""
        profiles = self.profiles["profiles"]
        for i, profile in enumerate(profiles):
            if profile["name"] == old_name:
                was_selected = profile.get("selected", False)
                profiles[i] = new_profile
                profiles[i]["selected"] = was_selected
                self._save_profiles(self.profiles)
                return
        raise ValueError(f"Profile '{old_name}' not found")

    def delete_profile(self, name: str) -> None:
        """Delete a profile"""
        profiles = self.profiles["profiles"]
        was_selected = False
        for i, profile in enumerate(profiles):
            if profile["name"] == name:
                was_selected = profile.get("selected", False)
                del profiles[i]
                break
        else:
            raise ValueError(f"Profile '{name}' not found")
        
        # If we deleted the selected profile, select the first remaining profile
        if was_selected and profiles:
            profiles[0]["selected"] = True
        
        self._save_profiles(self.profiles)

    def set_active_profile(self, name: str) -> None:
        """Set a profile as active"""
        found = False
        for profile in self.profiles["profiles"]:
            if profile["name"] == name:
                profile["selected"] = True
                found = True
            else:
                profile["selected"] = False
        
        if not found:
            raise ValueError(f"Profile '{name}' not found")
        
        self._save_profiles(self.profiles)

    def get_profile_constraints(self, name: Optional[str] = None) -> List[str]:
        """Get constraints for a profile"""
        profile = None
        if name:
            profile = self.get_profile_by_name(name)
        else:
            profile = self.get_active_profile()
        
        if profile:
            return profile.get("constraints", [])
        return [] 