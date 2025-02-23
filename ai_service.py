from openai import OpenAI
import os
from profile_manager import ProfileManager
from summary_manager import SummaryManager
from PyPDF2 import PdfReader
import mimetypes

client = OpenAI(
  base_url=os.getenv("OPENROUTER_API_URL"),
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

profile_manager = ProfileManager()
summary_manager = SummaryManager()

def _get_profile_context():
    active_profile = profile_manager.get_active_profile()
    if not active_profile:
        return ""
    
    context = f"""Please provide your response according to the following profile:
                Name: {active_profile['name']}
                Description: {active_profile['description']}
                Constraints:
                {chr(10).join('- ' + c for c in active_profile['constraints'])}
                Output Style:
                {chr(10).join('- ' + k + ': ' + str(v) for k, v in active_profile['outputStyle'].items())}

                """
    return context

def _read_file_content(file_path):
    """Read and return file content based on file type"""
    mime_type, _ = mimetypes.guess_type(file_path)
    
    try:
        # Handle PDF files
        if mime_type == 'application/pdf':
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
            return content
        
        # Handle text files
        elif mime_type and mime_type.startswith('text/'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Try reading as text if mime type is unknown
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
    except UnicodeDecodeError:
        return "Error: File format not supported. Please provide a text or PDF file."
    except Exception as e:
        return f"Error: Failed to read file: {str(e)}"

def chat_with_ai(message, file_path=None, model="google/gemini-2.0-flash-001", use_profile=False, conversation_history=None):
    # Handle file content
    file_content = ""
    if file_path:
        file_content = _read_file_content(file_path)
        if file_content.startswith("Error:"):
            return file_content
        message = f"Here is the content of the file:\n\n{file_content}\n\n{message}"

    full_message = (_get_profile_context() + message) if use_profile else message

    # Build messages list with conversation history
    messages = []
    if conversation_history:
        messages.extend([
            {
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            }
            for msg in conversation_history[:-1]  # Exclude the last message as it's the current one
        ])
    
    # Add the current message
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": full_message
            }
        ]
    })

    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content

def explain_paper(type, paper_path=None, url=None, model="google/gemini-2.0-flash-001"):
    active_profile = profile_manager.get_active_profile()
    profile_name = active_profile['name'] if active_profile else None

    if type == "file":
        message = "Please analyze and explain the following paper:"
        file_content = _read_file_content(paper_path)
        if file_content.startswith("Error:") or not isinstance(file_content, str):
            return file_content

        # Check for existing summary
        existing_summary = summary_manager.get_summary(file_content, profile_name)
        if existing_summary:
            return existing_summary

        # Generate new summary
        summary = chat_with_ai(message, file_path=paper_path, model=model, use_profile=True)
        if summary:
            summary_manager.save_summary(file_content, summary, profile_name)
        return summary
    else:
        if not url:
            return "Error: URL is required for URL-based paper analysis"
            
        message = f"Please analyze and explain the paper at this URL: {url}"
        # For URLs, we'll use the URL itself as the content key
        existing_summary = summary_manager.get_summary(url, profile_name)
        if existing_summary:
            return existing_summary

        # Generate new summary
        summary = chat_with_ai(message, model=model, use_profile=True)
        if summary:
            summary_manager.save_summary(url, summary, profile_name)
        return summary