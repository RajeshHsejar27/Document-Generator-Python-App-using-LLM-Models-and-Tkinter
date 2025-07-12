# Personal Documentation Assistant

A local, offline-first GUI application for collecting daily notes and images, generating AI-powered summaries using local language models, and exporting beautifully formatted Markdown and PDF reports.

## 🎯 Project Goals

- **Privacy-First**: All processing happens locally - no data leaves your machine
- **Offline Operation**: Works completely offline with local AI models
- **Daily Documentation**: Simple interface for capturing daily activities and insights
- **AI-Powered Summaries**: Automatically generate concise summaries of your notes
- **Multiple Export Formats**: Generate both Markdown and PDF reports
- **Production Ready**: Packaged as a standalone Windows executable

## 🛠️ Tech Stack

- **GUI Framework**: Tkinter (built into Python)
- **Local LLM**: GPT4All with GGUF models (e.g., mistral-7b-openorca.Q4_0.gguf)
- **Image Processing**: Pillow (PIL) for thumbnails and image handling
- **Document Generation**: 
  - markdown2 for Markdown processing
  - ReportLab for PDF generation
- **Packaging**: PyInstaller for standalone executable creation

## 📋 Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Windows 10/11** (for the packaged executable)
- **4GB+ RAM** (for running local LLM models)
- **2GB+ free disk space** (for models and application)

## 🚀 Quick Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd personal-documentation-assistant
pip install -r requirements.txt
```

### 2. Download LLM Model

Download a compatible GGUF model file and place it in the `models/` directory:

**Recommended Model**: [mistral-7b-openorca.Q4_0.gguf](https://gpt4all.io/index.html)

**Used models in this project**:
 - `Meta-Llama-3-8B-Instruct.Q4_0`
 - `nous-hermes-llama2-13b.Q4_0`

Took around 1.5-3 minutes to generate detailed report on a 5-6 brief lines input and 2 input images.
Laptop used for the above run has 16GB Ram, Intel i5 14th Gen Processor.

```bash
# Create models directory
mkdir models

# Download model (example using curl)
curl -L -o models/mistral-7b-openorca.Q4_0.gguf https://gpt4all.io/models/gguf/mistral-7b-openorca.Q4_0.gguf
```

**Alternative Models**:
- `nous-hermes-llama2-13b.Q4_0.gguf` (larger, better quality)
- `orca-mini-3b-gguf2-q4_0.gguf` (smaller, faster)
- `gpt4all-falcon-q4_0.gguf` (good balance)

### 3. Run the Application

```bash
# Development mode
python main.py

# Or run directly
python -m main
```

## 📦 Building Standalone Executable

### Build with PyInstaller (Optional)

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build the application
pyinstaller app.spec

# The executable will be in dist/PersonalDocumentationAssistant/
```

### One-File Executable (Optional)

For a single .exe file (slower startup but easier distribution):

1. Uncomment the one-file configuration in `app.spec`
2. Comment out the directory-based configuration
3. Run `pyinstaller app.spec`

## 📁 Project Structure

```
personal-documentation-assistant/
├── main.py                 # Application entry point
├── ui.py                   # Tkinter GUI implementation
├── llm.py                  # GPT4All integration and summarization
├── reporter.py             # Markdown and PDF report generation
├── requirements.txt        # Python dependencies
├── app.spec               # PyInstaller configuration
├── README.md              # This file
├── models/                # LLM model files (.gguf)
│   └── mistral-7b-openorca.Q4_0.gguf
├── images/                # Sample/uploaded images
├── reports/               # Generated reports
│   ├── daily-log-2024-01-15.md
│   ├── daily-log-2024-01-15.pdf
│   └── images/            # Copied images for reports
└── dist/                  # Built executable (after packaging)
    └── PersonalDocumentationAssistant/
        └── PersonalDocumentationAssistant.exe
```

## 💡 Usage Guide

### Main Interface

1. **Daily Notes**: Enter your daily activities in the text area
   - Use bullet points for better formatting
   - Include key tasks, meetings, accomplishments, challenges

2. **Upload Images**: 
   - Click "📁 Upload Images" to add screenshots, photos, diagrams
   - View thumbnails in the interface
   - Remove individual images with the ✕ button

3. **Report Name**: 
   - Customize the output filename
   - Default format: `daily-log-YYYY-MM-DD`

4. **Generate Report**:
   - Click "Generate Detailed Report"
   - AI will create detailed report and summarize your notes
   - Both .md and .pdf files will be created in `reports/`

### Example Workflow

```
Daily Notes:
• Completed code review for user authentication feature
• Fixed critical bug in payment processing system  
• Attended project planning meeting with stakeholders
• Updated documentation for API endpoints

Images:
- Screenshot of bug fix
- Whiteboard photo from planning meeting

Generated Summary:
"Today focused on code quality improvements with authentication 
feature review and critical payment bug resolution. Participated 
in strategic planning session with stakeholders and enhanced 
technical documentation."
```

## 🔧 Component Details

### 1. GUI (ui.py)
- **Framework**: Tkinter with ttk styling
- **Features**: 
  - Scrollable text area for notes
  - Image thumbnail gallery with horizontal scrolling
  - Progress bars and status updates
  - File dialogs for image selection
  - Responsive layout

### 2. LLM Integration (llm.py)
- **Model Loading**: Automatic detection of .gguf files
- **Summarization**: Focused prompts for concise daily summaries
- **Fallback**: Basic extractive summarization if model unavailable
- **Error Handling**: Graceful degradation with informative messages

### 3. Report Generation (reporter.py)
- **Markdown**: Clean, structured format with emoji headers
- **PDF**: Professional layout with ReportLab
- **Image Handling**: Automatic copying and relative path management
- **File Organization**: Date-based folders and systematic naming

### 4. Packaging (app.spec)
- **Dependencies**: Includes all required libraries
- **Data Files**: Bundles models, images, and configuration
- **Optimization**: Excludes unnecessary packages for smaller size
- **Configuration**: Both directory and one-file build options

## 🐛 Troubleshooting

### Common Issues

**"No model files found"**
- Ensure .gguf model file is in `models/` directory
- Check file permissions and naming
- Verify model file isn't corrupted

**"GPT4All not available"**
- Install GPT4All: `pip install gpt4all`
- Check Python version compatibility (3.10+)

**Slow performance**
- Use smaller model (3B parameters vs 7B/13B)
- Ensure sufficient RAM available
- Close other applications while generating summaries

**PDF generation fails**
- Install ReportLab: `pip install reportlab`
- Check write permissions to reports/ directory
- Verify image files aren't corrupted

### Performance Optimization

1. **Model Selection**: Choose model size based on your hardware
   - 3B models: 4GB RAM minimum
   - 7B models: 8GB RAM recommended  
   - 13B models: 16GB RAM recommended

2. **Image Handling**: Large images are automatically resized for thumbnails

3. **Report Generation**: Progress bars provide feedback during processing

## 🔒 Privacy & Security

- **Fully Offline**: No internet connection required after setup
- **Local Processing**: All AI operations happen on your machine
- **No Telemetry**: No data collection or external communication
- **Data Control**: All files stored locally in your chosen directory

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- **Additional Models**: Support for other local LLM frameworks
- **Export Formats**: HTML, DOCX, or other document formats
- **UI Enhancements**: Dark mode, themes, better layouts
- **Features**: Search functionality, tagging, templates
- **Platform Support**: macOS and Linux packaging

## 📄 License

## License
This project is licensed under the MIT License – see the LICENSE file for details.

## 🙏 Acknowledgments

- **GPT4All**: Excellent local LLM framework
- **ReportLab**: Professional PDF generation
- **Python Community**: Amazing ecosystem of libraries

---

*Built with ❤️ for privacy-conscious productivity enthusiasts*
