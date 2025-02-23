import json
import os
from typing import Dict, List, Optional

class ProfileManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.profiles = self._load_profiles()

    def _load_profiles(self) -> Dict:
        """Load profiles from settings file"""
        if not os.path.exists(self.settings_file):
            return {"profiles": []}
        
        with open(self.settings_file, 'r') as f:
            return json.load(f)

    def _save_profiles(self) -> None:
        """Save profiles to settings file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.profiles, f, indent=4)

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

    def create_profile(self, profile_data: Dict) -> bool:
        """Create a new profile"""
        if not profile_data.get("name"):
            raise ValueError("Profile must have a name")

        if self.get_profile_by_name(profile_data["name"]):
            raise ValueError(f"Profile with name '{profile_data['name']}' already exists")

        # Ensure required fields with correct structure
        profile_data.setdefault("description", "")
        profile_data.setdefault("constraints", [])
        profile_data.setdefault("selected", False)
        
        # Ensure outputStyle exists with default values
        output_style = profile_data.setdefault("outputStyle", {})
        output_style.setdefault("responseLanguage", "English")
        output_style.setdefault("language", "formal")
        output_style.setdefault("technicalLevel", "basic")
        output_style.setdefault("structurePreference", "paragraph")
        output_style.setdefault("visualAids", False)

        self.profiles.setdefault("profiles", []).append(profile_data)
        self._save_profiles()
        return True

    def update_profile(self, name: str, updated_data: Dict) -> bool:
        """Update an existing profile"""
        profiles = self.profiles.get("profiles", [])
        for i, profile in enumerate(profiles):
            if profile["name"] == name:
                profiles[i].update(updated_data)
                self._save_profiles()
                return True
        return False

    def set_active_profile(self, name: str) -> bool:
        """Set a profile as the active one"""
        found = False
        for profile in self.profiles.get("profiles", []):
            if profile["name"] == name:
                profile["selected"] = True
                found = True
            else:
                profile["selected"] = False
        
        if found:
            self._save_profiles()
        return found

    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        profiles = self.profiles.get("profiles", [])
        for i, profile in enumerate(profiles):
            if profile["name"] == name:
                del profiles[i]
                self._save_profiles()
                return True
        return False

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