# SciSift: Scientific Paper Analysis Agent

SciSift is an intelligent agent that analyzes and summarizes scientific articles based on customizable profiles and constraints. It helps researchers and academics efficiently extract relevant information and create targeted summaries of research papers.

## Features

- **Dual Interface**: Access via both GUI (graphical user interface) and CLI (command-line interface)
- **Profile Management**: Create and customize analysis profiles with specific parameters
- **Paper Analysis**: Process and analyze scientific papers (including PDFs)
- **Customizable Outputs**: Configure response styles and languages
- **Interactive Chat**: Engage with the AI to discuss and analyze papers

## Dependencies

The project requires the following Python packages:
- `requests`: HTTP library for API requests
- `beautifulsoup4`: Library for parsing HTML and XML documents
- `PyPDF2`: PDF processing library
- `python-dotenv`: Environment variable management
- `openai`: OpenAI API client
- `ttkbootstrap`: Modern themed widgets for tkinter

These can be installed automatically using the requirements.txt file as shown in the Installation section.

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd scisift
```

2. Create a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API credentials:
```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_URL=https://openrouter.ai/api/v1
```

## Usage

### GUI Mode
Run the graphical interface:
```bash
python main.py --gui
```

The GUI provides:
- Profile creation and management
- Paper upload and analysis
- Interactive chat interface
- Real-time analysis progress tracking

### CLI Mode
Run the command-line interface:
```bash
python main.py
```

CLI commands include:
- Managing profiles
- Analyzing papers
- Configuring settings
- Chatting with the AI

## Project Structure

- `main.py`: Entry point of the application
- `gui_app.py`: GUI implementation using tkinter and ttkbootstrap
- `cli_app.py`: Command-line interface implementation
- `ai_service.py`: Core AI service functionality
- `profile_manager.py`: Profile management system
- `settings.json`: Configuration settings
- `papers/`: Directory for paper storage
- `requirements.txt`: Python dependencies

## Configuration

Profiles can be customized with:
- Response language
- Output style
- Analysis constraints
- Custom prompts
- Paper processing preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License