from dotenv import load_dotenv
from os.path import isfile, join
from os import listdir, makedirs
from ai_service import chat_with_ai, explain_paper, profile_manager

# Ensure papers directory exists
papers_dir = "papers"
makedirs(papers_dir, exist_ok=True)

def line_break(empty=False):
    if empty:
        print("\n")
    else:
        print("===================")

def normal_chat():
    line_break(True)
    active_profile = profile_manager.get_active_profile()
    use_profile = False
    
    if active_profile:
        print(f"Active Profile: {active_profile['name']}")
        print("Would you like to use this profile for responses? (yes/no):")
        use_profile = input().strip().lower() == 'yes'
        if use_profile:
            print("Using profile for responses. You can toggle this with the 'profile' command.")
        else:
            print("Not using profile. You can toggle this with the 'profile' command.")
    
    print("\nEnter your message (or 'exit' to return to main menu, 'profile' to toggle profile):")
    while True:
        message = input().strip()
        if message.lower() == 'exit':
            break
        elif message.lower() == 'profile':
            use_profile = not use_profile
            print(f"\nProfile usage {'enabled' if use_profile else 'disabled'}")
            print("\nEnter your message:")
            continue
            
        if message:
            print("\nAI:", chat_with_ai(message, use_profile=use_profile))
        line_break(True)
        print("Enter your message (or 'exit' to return to main menu, 'profile' to toggle profile):")

def explain_paper_chat():
    while True:
        line_break(True)
        print("1. Choose a paper from papers folder")
        print("2. Enter a URL")
        print("3. Back to main menu")
        print("Enter 1, 2, or 3:")
        
        try:
            choice = int(input())
        except ValueError:
            print("Please enter a valid number")
            continue

        line_break(True)
        
        if choice == 1:
            papers = [f for f in listdir(papers_dir) if isfile(join(papers_dir, f))]
            if not papers:
                print("No papers found in papers directory")
                continue
                
            print("Available papers:")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper}")
            print("\nEnter the number of the paper to analyze (or 0 to cancel):")
            
            try:
                paper_index = int(input())
                if paper_index == 0:
                    continue
                if paper_index < 1 or paper_index > len(papers):
                    print("Invalid paper number")
                    continue
                    
                paper_path = join(papers_dir, papers[paper_index - 1])
                print(f"\nAnalyzing paper {paper_path}...")
                line_break(True)
                result = explain_paper("file", paper_path=paper_path)
                if result:
                    print(result)
                else:
                    print("Failed to analyze paper")
            except ValueError:
                print("Please enter a valid number")
                
        elif choice == 2:
            print("Enter the URL of the paper (or empty to cancel):")
            url = input().strip()
            if not url:
                continue
                
            print(f"\nAnalyzing paper from {url}...")
            line_break(True)
            result = explain_paper("url", url=url)
            if result:
                print(result)
            else:
                print("Failed to analyze paper")
                
        elif choice == 3:
            break
        else:
            print("Invalid choice")

def manage_profiles():
    while True:
        line_break(True)
        print("Profile Management")
        print("1. View all profiles")
        print("2. Create new profile")
        print("3. Update existing profile")
        print("4. Set active profile")
        print("5. Delete profile")
        print("6. Back to main menu")
        print("Enter your choice (1-6):")
        
        try:
            choice = int(input())
        except ValueError:
            print("Please enter a valid number")
            continue

        line_break(True)
        
        if choice == 1:
            profiles = profile_manager.get_all_profiles()
            if not profiles:
                print("No profiles found.")
            else:
                for profile in profiles:
                    print(f"Name: {profile['name']}")
                    print(f"Description: {profile['description']}")
                    print(f"Active: {'Yes' if profile.get('selected', False) else 'No'}")
                    print("Constraints:")
                    for constraint in profile.get('constraints', []):
                        print(f"  - {constraint}")
                    print("Output Style:")
                    for key, value in profile.get('outputStyle', {}).items():
                        print(f"  - {key}: {value}")
                    print()
        
        elif choice == 2:
            print("Enter profile name:")
            name = input().strip()
            if not name:
                print("Profile name cannot be empty")
                continue
                
            print("Enter profile description:")
            description = input().strip()
            
            print("Enter constraints (one per line, empty line to finish):")
            constraints = []
            while True:
                constraint = input().strip()
                if not constraint:
                    break
                constraints.append(constraint)
            
            print("\nOutput Style Settings")
            print("Language (formal/conversational):")
            language = input().strip().lower()
            if language not in ['formal', 'conversational']:
                language = 'formal'
            
            print("Technical level (basic/intermediate/advanced):")
            tech_level = input().strip().lower()
            if tech_level not in ['basic', 'intermediate', 'advanced']:
                tech_level = 'basic'
            
            print("Structure preference (paragraph/bullet-points):")
            structure = input().strip().lower()
            if structure not in ['paragraph', 'bullet-points']:
                structure = 'paragraph'
            
            print("Include visual aids? (yes/no):")
            visual_aids = input().strip().lower() == 'yes'
            
            profile_data = {
                "name": name,
                "description": description,
                "constraints": constraints,
                "outputStyle": {
                    "language": language,
                    "technicalLevel": tech_level,
                    "structurePreference": structure,
                    "visualAids": visual_aids
                }
            }
            
            try:
                profile_manager.create_profile(profile_data)
                print("Profile created successfully!")
            except ValueError as e:
                print(f"Error: {str(e)}")
        
        elif choice == 3:
            profiles = profile_manager.get_all_profiles()
            if not profiles:
                print("No profiles found.")
                continue
            
            print("Available profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile['name']}")
            
            print("\nEnter profile number to update (or 0 to cancel):")
            try:
                profile_idx = int(input())
                if profile_idx == 0:
                    continue
                if profile_idx < 1 or profile_idx > len(profiles):
                    print("Invalid profile number")
                    continue
                
                profile = profiles[profile_idx - 1]
                print(f"\nUpdating profile: {profile['name']}")
                
                print("Enter new description (or press Enter to keep current):")
                description = input().strip()
                if description:
                    profile['description'] = description
                
                print("Update constraints? (yes/no):")
                if input().strip().lower() == 'yes':
                    print("Enter new constraints (one per line, empty line to finish):")
                    constraints = []
                    while True:
                        constraint = input().strip()
                        if not constraint:
                            break
                        constraints.append(constraint)
                    profile['constraints'] = constraints
                
                print("Update output style? (yes/no):")
                if input().strip().lower() == 'yes':
                    print("Language (formal/conversational):")
                    language = input().strip().lower()
                    if language in ['formal', 'conversational']:
                        profile['outputStyle']['language'] = language
                    
                    print("Technical level (basic/intermediate/advanced):")
                    tech_level = input().strip().lower()
                    if tech_level in ['basic', 'intermediate', 'advanced']:
                        profile['outputStyle']['technicalLevel'] = tech_level
                    
                    print("Structure preference (paragraph/bullet-points):")
                    structure = input().strip().lower()
                    if structure in ['paragraph', 'bullet-points']:
                        profile['outputStyle']['structurePreference'] = structure
                    
                    print("Include visual aids? (yes/no):")
                    profile['outputStyle']['visualAids'] = input().strip().lower() == 'yes'
                
                profile_manager.update_profile(profile['name'], profile)
                print("Profile updated successfully!")
            except ValueError as e:
                print(f"Error: {str(e)}")
        
        elif choice == 4:
            profiles = profile_manager.get_all_profiles()
            if not profiles:
                print("No profiles found.")
                continue
            
            print("Available profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile['name']}")
            
            print("\nEnter profile number to set as active (or 0 to cancel):")
            try:
                profile_idx = int(input())
                if profile_idx == 0:
                    continue
                if profile_idx < 1 or profile_idx > len(profiles):
                    print("Invalid profile number")
                    continue
                
                profile_manager.set_active_profile(profiles[profile_idx - 1]['name'])
                print(f"Active profile set to: {profiles[profile_idx - 1]['name']}")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == 5:
            profiles = profile_manager.get_all_profiles()
            if not profiles:
                print("No profiles found.")
                continue
            
            print("Available profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile['name']}")
            
            print("\nEnter profile number to delete (or 0 to cancel):")
            try:
                profile_idx = int(input())
                if profile_idx == 0:
                    continue
                if profile_idx < 1 or profile_idx > len(profiles):
                    print("Invalid profile number")
                    continue
                
                profile_name = profiles[profile_idx - 1]['name']
                print(f"\nAre you sure you want to delete profile '{profile_name}'? (yes/no):")
                if input().strip().lower() == 'yes':
                    if profile_manager.delete_profile(profile_name):
                        print(f"Profile '{profile_name}' deleted successfully!")
                    else:
                        print(f"Failed to delete profile '{profile_name}'")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == 6:
            break
        else:
            print("Invalid choice")

def main_menu():
    while True:
        line_break()
        print("Welcome to SciSift!")
        active_profile = profile_manager.get_active_profile()
        if active_profile:
            print(f"Active Profile: {active_profile['name']}")
        else:
            print("No active profile selected")
            
        print("\n1. Chat with AI")
        print("2. Analyze scientific paper")
        print("3. Manage profiles")
        print("4. Exit")
        print("\nEnter your choice (1-4):")
        
        try:
            choice = int(input())
        except ValueError:
            print("Please enter a valid number")
            continue

        if choice == 1:
            normal_chat()
        elif choice == 2:
            explain_paper_chat()
        elif choice == 3:
            manage_profiles()
        elif choice == 4:
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice")

def run_cli():
    load_dotenv()
    main_menu() 