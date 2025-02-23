import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ttkbootstrap as ttk
from dotenv import load_dotenv
from os.path import isfile, join
from os import listdir, makedirs
from ai_service import chat_with_ai, explain_paper, profile_manager
import threading
from typing import List, Dict, Optional

# Ensure papers directory exists
papers_dir = "papers"
makedirs(papers_dir, exist_ok=True)

class LoaderDialog:
    def __init__(self, parent, message="Processing..."):
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Remove window decorations
        self.top.overrideredirect(True)
        
        # Center the dialog
        window_width = 200
        window_height = 50
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Add message and progress bar
        ttk.Label(self.top, text=message).pack(pady=5)
        self.progress = ttk.Progressbar(
            self.top, mode='indeterminate', length=180
        )
        self.progress.pack(pady=5)
        self.progress.start()
    
    def destroy(self):
        self.top.destroy()

class SciSiftGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SciSift")
        self.root.geometry("1000x700")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('darkly')
        
        # Chat conversation history
        self.conversation_history: List[Dict] = []
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.chat_frame = ttk.Frame(self.notebook)
        self.paper_frame = ttk.Frame(self.notebook)
        self.profile_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.chat_frame, text='Chat')
        self.notebook.add(self.paper_frame, text='Papers')
        self.notebook.add(self.profile_frame, text='Profiles')
        
        # Initialize all tabs
        self._init_chat_tab()
        self._init_paper_tab()
        self._init_profile_tab()
        
        # Show active profile
        self._update_active_profile_label()

    def _init_chat_tab(self):
        # Top control panel
        control_frame = ttk.Frame(self.chat_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Profile toggle
        self.use_profile_var = tk.BooleanVar(value=False)
        self.profile_toggle = ttk.Checkbutton(
            control_frame,
            text="Use Profile",
            variable=self.use_profile_var
        )
        self.profile_toggle.pack(side='left', padx=5)
        
        # Reset conversation button
        self.reset_button = ttk.Button(
            control_frame,
            text="Reset Conversation",
            command=self._reset_conversation,
            style='secondary.TButton'
        )
        self.reset_button.pack(side='right', padx=5)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            self.chat_frame, wrap=tk.WORD, height=25,
            font=('Segoe UI', 10)
        )
        self.chat_history.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Message input area
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        self.message_input = ttk.Entry(
            input_frame, font=('Segoe UI', 10)
        )
        self.message_input.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        self.send_button = ttk.Button(
            input_frame, text="Send",
            command=self._send_message,
            style='primary.TButton'
        )
        self.send_button.pack(side='right')
        
        # Bind Enter key to send message
        self.message_input.bind('<Return>', lambda e: self._send_message())

    def _init_paper_tab(self):
        # Paper source selection
        self.paper_source_frame = ttk.LabelFrame(
            self.paper_frame, text="Paper Source"
        )
        self.paper_source_frame.pack(fill='x', padx=10, pady=5)
        
        self.source_var = tk.StringVar(value="file")
        ttk.Radiobutton(
            self.paper_source_frame, text="Local File", 
            variable=self.source_var, value="file"
        ).pack(side='left', padx=10)
        ttk.Radiobutton(
            self.paper_source_frame, text="URL", 
            variable=self.source_var, value="url"
        ).pack(side='left', padx=10)
        
        # File/URL input
        self.paper_input_frame = ttk.Frame(self.paper_frame)
        self.paper_input_frame.pack(fill='x', padx=10, pady=5)
        
        # Create both input types
        self.file_input = ttk.Combobox(
            self.paper_input_frame,
            state="readonly"
        )
        self.url_input = ttk.Entry(
            self.paper_input_frame,
            font=('Segoe UI', 10)
        )
        
        # Initially show file input
        self.file_input.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        # Button frame for analyze and clear
        button_frame = ttk.Frame(self.paper_input_frame)
        button_frame.pack(side='right')
        
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_paper_results,
            style='secondary.TButton'
        )
        self.clear_button.pack(side='left', padx=5)
        
        self.analyze_button = ttk.Button(
            button_frame,
            text="Analyze",
            command=self._analyze_paper,
            style='primary.TButton'
        )
        self.analyze_button.pack(side='left')
        
        # Results frame with copy button
        results_frame = ttk.Frame(self.paper_frame)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        results_header = ttk.Frame(results_frame)
        results_header.pack(fill='x', pady=(0, 5))
        
        ttk.Label(
            results_header,
            text="Analysis Results",
            font=('Segoe UI', 10, 'bold')
        ).pack(side='left')
        
        self.copy_button = ttk.Button(
            results_header,
            text="Copy",
            command=self._copy_results,
            style='secondary.TButton'
        )
        self.copy_button.pack(side='right')
        
        # Results text area
        self.paper_results = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=15,
            font=('Segoe UI', 10)
        )
        self.paper_results.pack(fill='both', expand=True)
        
        # Update paper list when source changes
        self.source_var.trace('w', lambda *args: self._update_paper_source())
        self._update_paper_source()

    def _init_profile_tab(self):
        # Split into two frames
        list_frame = ttk.Frame(self.profile_frame)
        list_frame.pack(side='left', fill='y', padx=10, pady=5, expand=True)
        
        details_frame = ttk.Frame(self.profile_frame)
        details_frame.pack(side='right', fill='both', padx=10, pady=5, expand=True)
        
        # Profile list section
        list_label_frame = ttk.LabelFrame(list_frame, text="Available Profiles")
        list_label_frame.pack(fill='both', expand=True)
        
        self.profile_listbox = tk.Listbox(
            list_label_frame, height=15,
            font=('Segoe UI', 10)
        )
        self.profile_listbox.pack(fill='both', padx=5, pady=5, expand=True)
        
        # Profile actions
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            actions_frame, text="New Profile",
            command=self._create_profile,
            style='primary.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            actions_frame, text="Edit Profile",
            command=self._edit_profile,
            style='secondary.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            actions_frame, text="Set Active",
            command=self._set_active_profile,
            style='success.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            actions_frame, text="Delete",
            command=self._delete_profile,
            style='danger.TButton'
        ).pack(side='left', padx=5)
        
        # Profile details section
        details_label = ttk.Label(
            details_frame, text="Profile Details",
            font=('Segoe UI', 12, 'bold')
        )
        details_label.pack(pady=5)
        
        self.profile_details = scrolledtext.ScrolledText(
            details_frame, wrap=tk.WORD, height=20,
            font=('Segoe UI', 10)
        )
        self.profile_details.pack(fill='both', expand=True)
        
        # Update profile list
        self._update_profile_list()
        
        # Bind selection event
        self.profile_listbox.bind('<<ListboxSelect>>', self._show_profile_details)

    def _reset_conversation(self):
        if messagebox.askyesno("Reset Conversation", "Are you sure you want to reset the conversation history?"):
            self.conversation_history.clear()
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.insert(tk.END, "Conversation reset.\n\n")

    def _send_message(self):
        message = self.message_input.get().strip()
        if not message:
            return
        
        self.chat_history.insert(tk.END, f"You: {message}\n")
        self.message_input.delete(0, tk.END)
        self.chat_history.see(tk.END)
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Disable input while processing
        self.message_input.configure(state='disabled')
        self.send_button.configure(state='disabled')
        
        # Show loader
        loader = LoaderDialog(self.root, "Getting AI response...")
        
        def get_ai_response():
            try:
                response = chat_with_ai(
                    message,
                    use_profile=self.use_profile_var.get(),
                    conversation_history=self.conversation_history
                )
                
                # Add AI response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Update UI in main thread
                self.root.after(0, lambda: self._update_chat_with_response(response))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get AI response: {str(e)}"))
            finally:
                # Clean up in main thread
                self.root.after(0, lambda: self._cleanup_after_response(loader))
        
        # Start AI request in background
        threading.Thread(target=get_ai_response, daemon=True).start()

    def _update_chat_with_response(self, response):
        self.chat_history.insert(tk.END, f"AI: {response}\n\n")
        self.chat_history.see(tk.END)

    def _cleanup_after_response(self, loader):
        self.message_input.configure(state='normal')
        self.send_button.configure(state='normal')
        self.message_input.focus()
        loader.destroy()

    def _clear_paper_results(self):
        """Clear the paper analysis results"""
        self.paper_results.delete(1.0, tk.END)
        if self.source_var.get() == "file":
            self.file_input.set("Select a paper file...")
        else:
            self.url_input.delete(0, tk.END)
            self.url_input.insert(0, "Enter paper URL...")

    def _copy_results(self):
        """Copy paper analysis results to clipboard"""
        results = self.paper_results.get(1.0, tk.END).strip()
        if results:
            self.root.clipboard_clear()
            self.root.clipboard_append(results)
            messagebox.showinfo("Success", "Results copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No results to copy")

    def _analyze_paper(self):
        source = self.source_var.get()
        paper_input = self.file_input.get() if source == "file" else self.url_input.get()
        
        if not paper_input or paper_input in ["Select a paper file...", "Enter paper URL..."]:
            messagebox.showwarning("Warning", "Please select a paper or enter a URL")
            return
        
        # Disable inputs while processing
        self.file_input.configure(state='disabled')
        self.url_input.configure(state='disabled')
        self.analyze_button.configure(state='disabled')
        self.clear_button.configure(state='disabled')
        self.copy_button.configure(state='disabled')
        
        # Show loader
        loader = LoaderDialog(self.root, "Analyzing paper...")
        
        def analyze():
            try:
                if source == "file":
                    paper_path = join(papers_dir, paper_input)
                    result = explain_paper("file", paper_path=paper_path)
                else:
                    result = explain_paper("url", url=paper_input)
                
                if result is None:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to get analysis result"))
                    return
                    
                # Update UI in main thread
                self.root.after(0, lambda: self._update_paper_results(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to analyze paper: {str(e)}"))
            finally:
                # Clean up in main thread
                self.root.after(0, lambda: self._cleanup_after_analysis(loader))
        
        # Start analysis in background
        threading.Thread(target=analyze, daemon=True).start()

    def _update_paper_results(self, result):
        """Update the paper results text area"""
        self.paper_results.delete(1.0, tk.END)
        self.paper_results.insert(tk.END, str(result))

    def _cleanup_after_analysis(self, loader):
        """Clean up after paper analysis"""
        if self.source_var.get() == "file":
            self.file_input.configure(state='readonly')
        else:
            self.url_input.configure(state='normal')
        self.analyze_button.configure(state='normal')
        self.clear_button.configure(state='normal')
        self.copy_button.configure(state='normal')
        loader.destroy()

    def _update_paper_source(self):
        if self.source_var.get() == "file":
            # Switch to file input
            self.url_input.pack_forget()
            self.file_input.pack(side='left', expand=True, fill='x', padx=(0, 5))
            # List files in papers directory
            papers = [f for f in listdir(papers_dir) if isfile(join(papers_dir, f))]
            self.file_input['values'] = papers
            self.file_input.set("Select a paper file...")
        else:
            # Switch to URL input
            self.file_input.pack_forget()
            self.url_input.pack(side='left', expand=True, fill='x', padx=(0, 5))
            self.url_input.delete(0, tk.END)
            self.url_input.insert(0, "Enter paper URL...")
            self.url_input.bind('<FocusIn>', lambda e: self._on_url_focus_in())
            self.url_input.bind('<FocusOut>', lambda e: self._on_url_focus_out())

    def _on_url_focus_in(self):
        if self.url_input.get() == "Enter paper URL...":
            self.url_input.delete(0, tk.END)

    def _on_url_focus_out(self):
        if not self.url_input.get().strip():
            self.url_input.insert(0, "Enter paper URL...")

    def _update_profile_list(self):
        self.profile_listbox.delete(0, tk.END)
        for profile in profile_manager.get_all_profiles():
            self.profile_listbox.insert(tk.END, profile['name'])
            if profile.get('selected', False):
                self.profile_listbox.itemconfig(tk.END, {'bg': '#2ecc71'})

    def _show_profile_details(self, event=None):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
        
        profile_name = self.profile_listbox.get(selection[0])
        profile = profile_manager.get_profile_by_name(profile_name)
        
        if not profile:
            return
        
        details = f"Name: {profile['name']}\n"
        details += f"Description: {profile['description']}\n\n"
        details += "Constraints:\n"
        for constraint in profile.get('constraints', []):
            details += f"  • {constraint}\n"
        details += "\nOutput Style:\n"
        for key, value in profile.get('outputStyle', {}).items():
            details += f"  • {key}: {value}\n"
        
        self.profile_details.delete(1.0, tk.END)
        self.profile_details.insert(tk.END, details)

    def _create_profile(self):
        dialog = ProfileDialog(self.root, "Create Profile")
        if dialog.result:
            try:
                profile_manager.create_profile(dialog.result)
                self._update_profile_list()
                self._update_active_profile_label()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _edit_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to edit")
            return
        
        profile_name = self.profile_listbox.get(selection[0])
        profile = profile_manager.get_profile_by_name(profile_name)
        
        dialog = ProfileDialog(self.root, "Edit Profile", profile)
        if dialog.result:
            try:
                profile_manager.update_profile(profile_name, dialog.result)
                self._update_profile_list()
                self._update_active_profile_label()
                self._show_profile_details()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _set_active_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to set as active")
            return
        
        profile_name = self.profile_listbox.get(selection[0])
        profile_manager.set_active_profile(profile_name)
        self._update_profile_list()
        self._update_active_profile_label()

    def _delete_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to delete")
            return
        
        profile_name = self.profile_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?"):
            profile_manager.delete_profile(profile_name)
            self._update_profile_list()
            self._update_active_profile_label()
            self.profile_details.delete(1.0, tk.END)

    def _update_active_profile_label(self):
        active_profile = profile_manager.get_active_profile()
        title = f"SciSift - {active_profile['name'] if active_profile else 'No Active Profile'}"
        self.root.title(title)

class ProfileDialog:
    def __init__(self, parent, title, profile=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x800")  # Larger window
        
        # Initialize result
        self.result = None
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Main container
        main_container = ttk.Frame(self.dialog)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Add mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=560)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Basic Info Section
        basic_frame = ttk.LabelFrame(self.scrollable_frame, text="Basic Information")
        basic_frame.pack(fill='x', pady=5)
        
        ttk.Label(basic_frame, text="Name:").pack(padx=10, pady=(10, 0))
        self.name_entry = ttk.Entry(basic_frame)
        self.name_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(basic_frame, text="Description:").pack(padx=10, pady=(10, 0))
        self.desc_entry = ttk.Entry(basic_frame)
        self.desc_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        # Response Language
        ttk.Label(basic_frame, text="Response Language:").pack(padx=10, pady=(10, 0))
        self.language_combo = ttk.Combobox(
            basic_frame,
            values=["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Chinese", "Korean"],
            state="readonly"
        )
        self.language_combo.pack(fill='x', padx=10, pady=(0, 10))
        
        # Constraints Section
        constraints_frame = ttk.LabelFrame(self.scrollable_frame, text="Constraints")
        constraints_frame.pack(fill='x', pady=5)
        
        ttk.Label(constraints_frame, text="Enter constraints (one per line):").pack(padx=10, pady=(10, 0))
        self.constraints_text = scrolledtext.ScrolledText(constraints_frame, height=5)
        self.constraints_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Output Style Section
        style_frame = ttk.LabelFrame(self.scrollable_frame, text="Output Style")
        style_frame.pack(fill='x', pady=5)
        
        # Language Style
        style_container = ttk.Frame(style_frame)
        style_container.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(style_container, text="Language Style:").pack(side='left')
        self.style_var = tk.StringVar()
        ttk.Radiobutton(style_container, text="Formal", variable=self.style_var, value="formal").pack(side='left', padx=10)
        ttk.Radiobutton(style_container, text="Conversational", variable=self.style_var, value="conversational").pack(side='left', padx=10)
        
        # Technical Level
        tech_container = ttk.Frame(style_frame)
        tech_container.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(tech_container, text="Technical Level:").pack(side='left')
        self.tech_level = ttk.Combobox(
            tech_container,
            values=["basic", "intermediate", "advanced"],
            state="readonly",
            width=15
        )
        self.tech_level.pack(side='left', padx=10)
        
        # Structure
        struct_container = ttk.Frame(style_frame)
        struct_container.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(struct_container, text="Structure:").pack(side='left')
        self.structure_var = tk.StringVar()
        ttk.Radiobutton(struct_container, text="Paragraph", variable=self.structure_var, value="paragraph").pack(side='left', padx=10)
        ttk.Radiobutton(struct_container, text="Bullet Points", variable=self.structure_var, value="bullet-points").pack(side='left', padx=10)
        
        # Visual Aids
        visual_container = ttk.Frame(style_frame)
        visual_container.pack(fill='x', padx=10, pady=5)
        
        self.visual_aids_var = tk.BooleanVar()
        ttk.Checkbutton(
            visual_container,
            text="Include Visual Aids",
            variable=self.visual_aids_var
        ).pack(side='left')
        
        # Buttons - Fixed at bottom
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10, side='bottom')
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            style='secondary.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._save,
            style='primary.TButton'
        ).pack(side='right', padx=5)
        
        # Set values if editing
        if profile:
            self.name_entry.insert(0, profile['name'])
            self.desc_entry.insert(0, profile['description'])
            self.constraints_text.insert('1.0', '\n'.join(profile.get('constraints', [])))
            
            output_style = profile.get('outputStyle', {})
            self.language_combo.set(output_style.get('responseLanguage', 'English'))
            self.style_var.set(output_style.get('language', 'formal'))
            self.tech_level.set(output_style.get('technicalLevel', 'basic'))
            self.structure_var.set(output_style.get('structurePreference', 'paragraph'))
            # Convert visualAids to boolean - treat "recommended" as True
            visual_aids = output_style.get('visualAids', False)
            self.visual_aids_var.set(True if visual_aids in [True, "recommended"] else False)
        else:
            # Set defaults for new profile
            self.language_combo.set('English')
            self.style_var.set('formal')
            self.tech_level.set('basic')
            self.structure_var.set('paragraph')
            self.visual_aids_var.set(False)
        
        # Wait for dialog
        self.dialog.wait_window()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _save(self):
        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Profile name is required")
            return
            
        constraints = [c.strip() for c in self.constraints_text.get('1.0', tk.END).split('\n') if c.strip()]
        
        self.result = {
            "name": name,
            "description": self.desc_entry.get().strip(),
            "constraints": constraints,
            "outputStyle": {
                "language": self.style_var.get(),
                "technicalLevel": self.tech_level.get(),
                "structurePreference": self.structure_var.get(),
                "visualAids": self.visual_aids_var.get(),
                "responseLanguage": self.language_combo.get()
            }
        }
        self.dialog.destroy()

    def _cancel(self):
        self.result = None
        self.dialog.destroy()

def run_gui():
    load_dotenv()
    root = ttk.Window()
    app = SciSiftGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui() 