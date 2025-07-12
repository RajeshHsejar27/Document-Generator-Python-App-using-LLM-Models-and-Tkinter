"""
GUI Module - Tkinter-based User Interface
Handles the main application window, user interactions, and file operations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImageThumbnail:
    """Helper class for managing image thumbnails in the GUI."""
    
    def __init__(self, filepath, thumbnail_size=(100, 100)):
        self.filepath = filepath
        self.thumbnail_size = thumbnail_size
        self.thumbnail = None
        self.tk_image = None
        self._load_thumbnail()
    
    def _load_thumbnail(self):
        """Load and create thumbnail of the image."""
        try:
            with Image.open(self.filepath) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Create thumbnail
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                self.thumbnail = img
                self.tk_image = ImageTk.PhotoImage(img)
                
        except Exception as e:
            logger.error(f"Error loading thumbnail for {self.filepath}: {e}")
            # Create placeholder thumbnail
            placeholder = Image.new('RGB', self.thumbnail_size, (200, 200, 200))
            self.thumbnail = placeholder
            self.tk_image = ImageTk.PhotoImage(placeholder)


class DocumentationApp:
    """Main application class handling the GUI and user interactions."""
    
    def __init__(self, llm_manager, report_generator):
        self.llm_manager = llm_manager
        self.report_generator = report_generator
        self.root = None
        self.uploaded_images = []
        self.image_thumbnails = []
        
        # GUI components
        self.notes_text = None
        self.filename_entry = None
        self.images_frame = None
        self.progress_var = None
        self.progress_bar = None
        self.generate_button = None
        
        self._setup_gui()
    
    def _setup_gui(self):
        """Initialize and configure the main GUI window."""
        self.root = tk.Tk()
        self.root.title("Personal Documentation Assistant")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._create_header(main_frame)
        self._create_notes_section(main_frame)
        self._create_images_section(main_frame)
        self._create_filename_section(main_frame)
        self._create_action_buttons(main_frame)
        self._create_progress_section(main_frame)
        
        # Set default filename
        self._set_default_filename()
    
    def _create_header(self, parent):
        """Create the application header."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="📝 Personal Documentation Assistant",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Capture your daily notes and images, generate AI-powered summaries",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
    
    def _create_notes_section(self, parent):
        """Create the daily notes input section."""
        notes_label = ttk.Label(parent, text="📝 Daily Notes:", font=('Arial', 12, 'bold'))
        notes_label.grid(row=1, column=0, sticky=(tk.W, tk.N), padx=(0, 10), pady=(0, 5))
        
        # Create text area with scrollbar
        notes_frame = ttk.Frame(parent)
        notes_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        
        self.notes_text = scrolledtext.ScrolledText(
            notes_frame,
            wrap=tk.WORD,
            width=50,
            height=12,
            font=('Arial', 11)
        )
        self.notes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add placeholder text
        placeholder_text = (
            "Enter your daily notes here...\n\n"
            "Examples:\n"
            "• Met with the development team to discuss project timeline\n"
            "• Completed code review for the new feature\n"
            "• Attended client presentation meeting\n"
            "• Fixed critical bug in the payment system"
        )
        self.notes_text.insert('1.0', placeholder_text)
        self.notes_text.bind('<FocusIn>', self._clear_placeholder)
    
    def _create_images_section(self, parent):
        """Create the image upload and display section."""
        images_label = ttk.Label(parent, text="🖼️ Images:", font=('Arial', 12, 'bold'))
        images_label.grid(row=2, column=0, sticky=(tk.W, tk.N), padx=(0, 10), pady=(0, 5))
        
        images_container = ttk.Frame(parent)
        images_container.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 20))
        images_container.columnconfigure(1, weight=1)
        
        upload_button = ttk.Button(
            images_container,
            text="📁 Upload Images",
            command=self._upload_images
        )
        upload_button.grid(row=0, column=0, sticky=tk.W)
        
        clear_images_button = ttk.Button(
            images_container,
            text="🗑️ Clear All",
            command=self._clear_images
        )
        clear_images_button.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Scrollable frame for image thumbnails
        canvas_frame = ttk.Frame(images_container)
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        canvas_frame.columnconfigure(0, weight=1)
        
        # Canvas for scrollable content
        self.images_canvas = tk.Canvas(canvas_frame, height=120, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.images_canvas.xview)
        self.images_frame = ttk.Frame(self.images_canvas)
        
        self.images_canvas.configure(xscrollcommand=scrollbar.set)
        self.images_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.images_canvas.create_window((0, 0), window=self.images_frame, anchor="nw")
        self.images_frame.bind("<Configure>", self._on_images_frame_configure)
    
    def _create_filename_section(self, parent):
        """Create the report filename input section."""
        filename_label = ttk.Label(parent, text="📄 Report Name:", font=('Arial', 12, 'bold'))
        filename_label.grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        
        filename_frame = ttk.Frame(parent)
        filename_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 20))
        filename_frame.columnconfigure(0, weight=1)
        
        self.filename_entry = ttk.Entry(filename_frame, font=('Arial', 11))
        self.filename_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(filename_frame, text=".md/.pdf").grid(row=0, column=1)
    
    def _create_action_buttons(self, parent):
        """Create the main action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))
        
        self.generate_button = ttk.Button(
            button_frame,
            text="🚀 Generate Detailed Report",
            command=self._generate_detailed_report_async,
            style='Accent.TButton'
        )
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        view_reports_button = ttk.Button(
            button_frame,
            text="📂 View Reports Folder",
            command=self._open_reports_folder
        )
        view_reports_button.pack(side=tk.LEFT)
    
    def _create_progress_section(self, parent):
        """Create the progress bar and status display."""
        self.progress_var = tk.StringVar(value="Ready to generate detailed report")
        
        status_label = ttk.Label(parent, textvariable=self.progress_var)
        status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            parent,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def _clear_placeholder(self, event):
        """Clear placeholder text when user focuses on the text area."""
        if "Enter your daily notes here..." in self.notes_text.get('1.0', tk.END):
            self.notes_text.delete('1.0', tk.END)
    
    def _set_default_filename(self):
        """Set default filename based on current date."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.filename_entry.delete(0, tk.END)
        self.filename_entry.insert(0, f"daily-log-{today}")
    
    def _upload_images(self):
        """Handle image file selection and upload."""
        filetypes = (
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff'),
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('All files', '*.*')
        )
        
        filenames = filedialog.askopenfilenames(
            title='Select Images',
            initialdir=os.path.expanduser('~'),
            filetypes=filetypes
        )
        
        if filenames:
            for filename in filenames:
                if filename not in self.uploaded_images:
                    self.uploaded_images.append(filename)
            self._update_image_display()
    
    def _clear_images(self):
        """Clear all uploaded images."""
        self.uploaded_images.clear()
        self.image_thumbnails.clear()
        self._update_image_display()
    
    def _update_image_display(self):
        """Update the display of image thumbnails."""
        # Clear existing thumbnails
        for widget in self.images_frame.winfo_children():
            widget.destroy()
        
        # Create new thumbnails
        self.image_thumbnails.clear()
        for i, image_path in enumerate(self.uploaded_images):
            try:
                thumbnail = ImageThumbnail(image_path)
                self.image_thumbnails.append(thumbnail)
                
                # Create thumbnail frame
                thumb_frame = ttk.Frame(self.images_frame)
                thumb_frame.grid(row=0, column=i, padx=5, pady=5)
                
                # Image label
                img_label = ttk.Label(thumb_frame, image=thumbnail.tk_image)
                img_label.grid(row=0, column=0)
                
                # Filename label
                filename = os.path.basename(image_path)
                if len(filename) > 15:
                    filename = filename[:12] + "..."
                
                name_label = ttk.Label(
                    thumb_frame,
                    text=filename,
                    font=('Arial', 8),
                    justify=tk.CENTER
                )
                name_label.grid(row=1, column=0)
                
                # Remove button
                remove_button = ttk.Button(
                    thumb_frame,
                    text="✕",
                    width=3,
                    command=lambda idx=i: self._remove_image(idx)
                )
                remove_button.grid(row=2, column=0, pady=(2, 0))
                
            except Exception as e:
                logger.error(f"Error creating thumbnail for {image_path}: {e}")
        
        # Update canvas scroll region
        self.images_frame.update_idletasks()
        self.images_canvas.configure(scrollregion=self.images_canvas.bbox("all"))
    
    def _remove_image(self, index):
        """Remove an image from the uploaded images list."""
        if 0 <= index < len(self.uploaded_images):
            self.uploaded_images.pop(index)
            self._update_image_display()
    
    def _on_images_frame_configure(self, event):
        """Handle canvas configuration changes."""
        self.images_canvas.configure(scrollregion=self.images_canvas.bbox("all"))
    
    def _generate_detailed_report_async(self):
        """Generate detailed report in a separate thread to avoid blocking the GUI."""
        def generate():
            try:
                self._set_progress("Generating detailed report...", True)
                self._generate_detailed_report()
                self._set_progress("Detailed report generated successfully!", False)
            except Exception as e:
                logger.error(f"Detailed report generation error: {e}")
                self._set_progress(f"Error: {str(e)}", False)
                messagebox.showerror("Error", f"Failed to generate detailed report:\n\n{str(e)}")
        
        # Disable generate button and start progress
        self.generate_button.config(state='disabled')
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        
        # Re-enable button after a delay
        self.root.after(5000, lambda: self.generate_button.config(state='normal'))
    
    def _generate_detailed_report(self):
        """Generate the detailed markdown and PDF reports."""
        # Get user input
        notes = self.notes_text.get('1.0', tk.END).strip()
        filename = self.filename_entry.get().strip()
        
        # Validate input
        if not notes or notes == "Enter your daily notes here...":
            raise ValueError("Please enter some notes before generating a detailed report.")
        
        if not filename:
            raise ValueError("Please enter a filename for the detailed report.")
        
        # Update progress
        self._set_progress("Generating detailed notes with AI...", True)
        
        # Generate detailed notes using LLM
        detailed_notes = self.llm_manager.generate_detailed_notes(notes)
        
        # Update progress
        self._set_progress("Generating AI summary...", True)
        
        # Generate summary using LLM
        summary = self.llm_manager.generate_summary(detailed_notes)
        
        # Update progress
        self._set_progress("Creating detailed report files...", True)
        
        # Generate detailed reports
        self.report_generator.generate_detailed_report(
            original_notes=notes,
            detailed_notes=detailed_notes,
            images=self.uploaded_images,
            summary=summary,
            filename=filename
        )
    
    def _set_progress(self, message, show_progress=False):
        """Update progress display."""
        self.progress_var.set(message)
        if show_progress:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
        self.root.update_idletasks()
    
    def _open_reports_folder(self):
        """Open the reports folder in the system file explorer."""
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        if os.path.exists(reports_dir):
            os.startfile(reports_dir)  # Windows
        else:
            messagebox.showinfo("Info", f"Reports folder not found: {reports_dir}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()