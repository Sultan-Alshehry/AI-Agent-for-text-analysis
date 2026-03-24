import tkinter as t
from tkinter import filedialog, messagebox, simpledialog
import os
import main as m
import json
from PyPDF2 import PdfReader
from ai_config import setup_environment, set_analysis_mode, set_gemini_api_key
from summary_saver import save_summary
import threading

# AITY - AI Text Analysis Prototype
# --------------------------------
# This app allows users to:
# 1. Upload documents
# 2. View documents
# 3. Analyze text (keywords, relevance, topics, etc.)
# 4. Compare documents (future feature)

# Main app class (controls navigation)
class AityApp(t.Tk):
    def __init__(self):
        super().__init__()
        self.title("AITY AI Agent for text analysing")
        self.geometry("600x600")
        self.config(bg="#0b0f3b")

        # Initialize analysis mode via setup_environment
        self.analysis_mode = setup_environment()

        # variables that are used to show how many documents are
        # uploaded, analysed and ready to compare
        self.total_docs = t.StringVar(value="0")
        self.analysed_docs = t.StringVar(value="0")
        self.ready_to_compare_docs = t.StringVar(value="❌")

        # Store uploaded files and example files
        self.files = []

        self.frames = {}

        for F in (Dashboard, FileSelection, Analysis, Compare):
            frame = F(self, self.total_docs, self.analysed_docs, self.ready_to_compare_docs)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(Dashboard)

    # Switches mode between Gemini and keybert
    def change_mode(self, mode):
        if mode == "genai":
            if not os.environ.get("GEMINI_API_KEY"):
                key = simpledialog.askstring("Gemini API Key", "Enter GEMINI_API_KEY:")
                if not key:
                    messagebox.showwarning("Gemini required", "Gemini API key required to use Gemini mode. Falling back to KeyBERT if available.")
                    # Try fallback to keybert
                    try:
                        import keybert
                        self.change_mode("keybert")
                    except ImportError:
                        messagebox.showerror("No engine available", "Neither Gemini nor KeyBERT is available. Please install KeyBERT or provide a Gemini API key.")
                    return
                set_gemini_api_key(key)
        elif mode == "keybert":
            try:
                import keybert
            except ImportError:
                messagebox.showwarning("KeyBERT not installed", "KeyBERT is not installed. Please install it with: pip install keybert sentence-transformers")
                return

        set_analysis_mode(mode)
        self.analysis_mode = mode
        print(f"Switched to mode: {mode}")

        dashboard = self.frames.get(Dashboard)
        if dashboard and hasattr(dashboard, "mode_label"):
            dashboard.mode_label.config(text=f"Mode: {mode}")
            # Refresh the content view to show updated mode in bottom label
            dashboard.show_documents()

        messagebox.showinfo("Mode switched", f"Analysis mode set to {mode}")

    # Switches between screens "Documents", "Uploads"
    def show_frame(self, frame_class):
        frame = self.frames[frame_class]

        if frame_class == FileSelection:
            frame.refresh_files()
        if frame_class == Compare:
            frame.refresh()

        frame.tkraise()

# -----DASHBOARD SCREEN----- #
# Contains stats, navigation buttons etc.

class Dashboard(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")
        
        self.analysed_docs = analysed_docs
        self.total_docs = total_docs
        self.ready_compare = ready_compare
        # Title
        t.Label(self, text="AITY Dashboard",
                fg="white", bg="#0b0f3b",
                font=("Arial", 18, "bold")).pack(pady=20)

        # ---- STATS BAR ----
        # In future should update dynamically
        stats_frame = t.Frame(self, bg="#0b0f3b")
        stats_frame.pack(pady=10)

        self.create_stat(stats_frame, "Total documents", total_docs)
        self.create_stat(stats_frame, "Analyzed", analysed_docs)
        self.create_stat(stats_frame, "Ready to compare", ready_compare)

        # ---- BUTTONS ----
        btn_frame = t.Frame(self, bg="#0b0f3b")
        btn_frame.pack(pady=20, anchor='center')

        t.Button(btn_frame, text="Documents",
                 width=15,
                 command=self.show_documents).grid(row=0, column=0, padx=10)

        t.Button(btn_frame, text="Uploads",
                 width=15,
                 command=self.show_uploads).grid(row=0, column=1, padx=10)

        self.mode_label = t.Label(btn_frame, text=f"Mode: {self.master.analysis_mode}", fg="white", bg="#0b0f3b")
        self.mode_label.grid(row=1, column=0, columnspan=3)

        mode_frame = t.Frame(btn_frame, bg="#0b0f3b")
        mode_frame.grid(row=2, column=0, columnspan=3, pady=10)

        t.Button(mode_frame, text="Use Gemini",
                width=12,
                command=lambda: self.master.change_mode("genai")).pack(side="left", padx=10)

        t.Button(mode_frame, text="Use KeyBERT",
                width=12,
                command=lambda: self.master.change_mode("keybert")).pack(side="left", padx=10)

        self.compare_btn = t.Button(btn_frame, text="Compare",
                 width=15,
                 command=lambda: self.master.show_frame(Compare))
        
        self.compare_btn.grid(row=0, column=2, padx=10)

        self.content_frame = t.Frame(self, bg="#0b0f3b")
        self.content_frame.pack(fill="both", expand=True)

        # show default view
        self.show_documents()

    # -------- helper --------
    def create_stat(self, parent, title, value):
        box = t.Frame(parent, bg="#1a1f5a", width=120, height=60)
        box.pack(side="left", padx=10)
        box.pack_propagate(False)

        t.Label(box, text=title, fg="white", bg="#1a1f5a").pack()
        if isinstance(value, t.StringVar):
            t.Label(box, textvariable=value, fg="white", bg="#1a1f5a",
            font=("Arial", 12, "bold")).pack()
        else:
            t.Label(box, text=value, fg="white", bg="#1a1f5a",
            font=("Arial", 12, "bold")).pack()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # -------- DOCUMENT VIEW --------
    # Shows instructions to file selection
    def show_documents(self):
        self.clear_content()

        hero = t.Frame(self.content_frame, bg="#1a1f5a", height=150)
        hero.pack(pady=40, padx=40, fill="x")
        hero.pack_propagate(False)

        t.Label(hero,
                text="Upload a document to get started with analysing\n\nSelect Uploads and add a document",
                fg="white", bg="#1a1f5a").pack(expand=True)

        t.Button(self.content_frame,
                text="View Documents",
                command=lambda: self.master.show_frame(FileSelection)).pack(pady=10)

        # show current selection mode and file count
        t.Label(self.content_frame,
                text=f"Current mode: {self.master.analysis_mode} | Uploaded: {len(self.master.files)}",
                fg="white", bg="#0b0f3b").pack(pady=5)

    # -------- UPLOAD VIEW --------
    # Shows file upload UI
    def show_uploads(self):
        self.clear_content()

        hero = t.Frame(self.content_frame, bg="#1a1f5a", height=80)
        hero.pack(pady=20, padx=40, fill="x")
        hero.pack_propagate(False)

        t.Label(hero,
                text="Upload Document\nAdd a new document for AI-powered text analysis",
                fg="white", bg="#1a1f5a").pack(expand=True)

        upload_box = t.Frame(self.content_frame, bg="#2a2f6a", height=150)
        upload_box.pack(pady=20, padx=40, fill="x")
        upload_box.pack_propagate(False)

        t.Label(upload_box,
                text="Upload a document (.pdf or .txt)",
                fg="white", bg="#2a2f6a").pack(pady=10)

        t.Button(upload_box,
                 text="Choose file",
                 command=self.upload_file).pack()
                 

    # -------- FILE UPLOAD LOGIC --------
    # Opens file dialog and stores selected file
    def upload_file(self):
        file = filedialog.askopenfilename()
        if file:
            filename = file.split("/")[-1]
            
            # Validate PDF files before uploading
            if filename.lower().endswith('.pdf'):
                try:
                    PdfReader(file)  # Verify PDF is readable
                except Exception as e:
                    messagebox.showerror("Invalid PDF", f"Cannot read PDF file: {str(e)}")
                    return
            
            self.master.files.append(file)
            print("Saved:", file)
            messagebox.showinfo("Document Uploaded", f"Successfully uploaded: {filename}")
            current = int(self.total_docs.get())
            self.total_docs.set(str(current + 1))
            
            current = int(self.analysed_docs.get())
            self.analysed_docs.set(str(current + 1))
            
            if int(self.analysed_docs.get()) >= 2:
                self.ready_compare.set("✅")

            # Immediately show the file selection so user can see new file
            self.master.frames[FileSelection].refresh_files()
            self.master.show_frame(FileSelection)


# -----FILE SELECTION SCREEN----- #
# Shows both example files and uploaded files

class FileSelection(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")

        self.master = master

        t.Label(self, text="Select Document",
                fg="white", bg="#0b0f3b").pack(pady=20)

        self.file_container = t.Frame(self, bg="#0b0f3b")
        self.file_container.pack()

        t.Button(self, text="⬅ Back",
                 command=lambda: master.show_frame(Dashboard)
                 ).pack(anchor="nw")

    def open_analysis(self, file):
        self.master.selected_file = file
        self.master.frames[Analysis].update_analysis(file)
        self.master.show_frame(Analysis)

    def refresh_files(self):
        for widget in self.file_container.winfo_children():
            widget.destroy()

        t.Label(self.file_container, text="Uploaded Files",
                fg="white", bg="#0b0f3b", font=("Arial", 10, "bold")).pack(pady=10)

        if not self.master.files:
            t.Label(self.file_container,
                    text="No uploaded files yet.",
                    fg="white", bg="#0b0f3b").pack(pady=5)
        else:
            for file in self.master.files:
                filename = file.replace('\\', '/').split("/")[-1]

                t.Button(self.file_container,
                        text=filename,
                        command=lambda f=file: self.open_analysis(f)
                        ).pack(pady=3)

# -----ANALYSIS SCREEN----- #
# Displays results of selected file
    
class Analysis(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")

        self.current_results = None  # Store current results for saving
        self.current_filepath = None  # Store current filepath for saving

        self.label = t.Label(self, text="Analysis Results",
                             fg="white", bg="#0b0f3b",
                             font=("Arial", 14))
        self.label.pack(pady=10)

        self.result_box = t.Label(
            self, bg="#1a1f5a", fg="white", justify="left", padx=20, pady=20, wraplength=500 
        )

        self.result_box.pack(pady=20)

        # Button frame for Back and Save buttons
        button_frame = t.Frame(self, bg="#0b0f3b")
        button_frame.pack(anchor="nw", pady=10)

        t.Button(button_frame, text="⬅ Back",
                 command=lambda: master.show_frame(FileSelection)
                 ).pack(side="left", padx=5)

        t.Button(button_frame, text="💾 Save Results",
                 command=self.save_results
                 ).pack(side="left", padx=5)

    # Reads file content and updates analysis view
    # uses gemini or keybert based on selected mode
    def update_analysis(self, filepath):
        print(filepath)
        self.current_filepath = filepath

        self.result_box.config(text="Analyzing... Please wait.")
        self.update()  # Force UI update

        def analyze():
            try:
                mode = getattr(self.master, "analysis_mode", "genai")
                summarys_path = m.get_analysis_result(filepath, mode=mode)

                summary, keywords, topics = self.json_to_text(summarys_path)
                self.update_analysis_from_text(summary, keywords, topics)
            except Exception as e:
                self.result_box.config(text=f"Error during analysis: {str(e)}")

        thread = threading.Thread(target=analyze)
        thread.start()

    # NOTE: PDF conversion is handled by file_reader.read_file now, so this is no longer used
    def convert_pdf_to_text(self, filepath):
        raise NotImplementedError("PDF conversion is done via file_reader.read_file in main.get_analysis_result")
        
    def json_to_text(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        summary = data.get("summary", "")
        keywords = data.get("keywords", "")
        topics = data.get("topics", "")
        
        return summary, keywords, topics

    def update_analysis_from_text(self, summary, keywords, topics):
        # Normalize lists/dicts
        def normalize(items):
            if items is None:
                return []
            if isinstance(items, list):
                return items
            return [items]

        keywords_list = normalize(keywords)
        topics_list = normalize(topics)

        if keywords_list and isinstance(keywords_list[0], dict):
            keywords_text = "\n".join(
                f"- {item.get('keyword', item.get('key', str(item)))} ({item.get('score', '')})"
                for item in keywords_list
            )
        else:
            keywords_text = "\n".join(str(item) for item in keywords_list)

        topics_text = "\n".join(str(item) for item in topics_list)

        display_text = (
            f"Summary:\n{summary}\n\n"
            f"Keywords:\n{keywords_text}\n\n"
            f"Topics:\n{topics_text}"
        )

        self.result_box.config(text=display_text)
        
        # Store results for potential saving
        self.current_results = {
            "summary": summary,
            "keywords": keywords,
            "topics": topics
        }
    
    def save_results(self):
        """Save analysis results to a custom location using save_summary"""
        if not self.current_results:
            messagebox.showwarning("No Results", "No analysis results to save. Please analyze a document first.")
            return
        
        # Ask user where to save
        output_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"analysis_results.json"
        )
        
        if output_path:
            try:
                save_summary(self.current_results, output_path)
                messagebox.showinfo("Success", f"Results saved to:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")
        
# -----COMPARE DOCUMENTS SCREEN----- #
# Displays screen that allows user to select documents to compare and excecutes comparison
class Compare(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")
        
        self.analysed_docs = analysed_docs
        self.total_docs = total_docs
        self.ready_compare = ready_compare
        
        
        self.selected_amount = 0
        self.files_to_compare = []
        #self.enough_selected_documents = False
        
        self.label = t.Label(self, text="select documents to compare",
                             fg="white", bg="#0b0f3b",
                             font=("Arial", 14))
        self.label.pack(pady=10)

        self.result_box = t.Label(
            self, bg="#1a1f5a", fg="white", justify="left", padx=20, pady=20,
        )

        self.result_box.pack(pady=20)
        
        self.file_container = t.Frame(self, bg="#0b0f3b")
        self.file_container.pack()
        
        self.selected_files = t.Frame(self, bg="#0b0f3b")
        self.selected_files.pack(pady=10)
        
        self.selected_box = t.Label(self.selected_files, text="selected documents",
                             fg="white", bg="#0b0f3b",
                             font=("Arial", 12))
        self.selected_box.pack() 
        
        t.Button(self, text="⬅ Back",
            command=lambda: master.show_frame(Dashboard)
            ).pack(anchor="nw")
        
    #method used when selecting documents for comparing
    def select_document(self, file):
        
        if self.selected_amount < 2:
            t.Label(self.selected_files, text = file.split("/")[-1],
            fg="white", bg="#0b0f3b", font=("Arial", 10, "bold")).pack(pady=10)
            self.files_to_compare.append(file)
            self.selected_amount = self.selected_amount + 1
            
        
        if self.selected_amount == 2:
            t.Button(self.selected_files,
                    text="Compare results",
                    command=lambda f=self.files_to_compare: self.perform_comparison(f)
                    ).pack(pady=3)
            self.selected_amount = self.selected_amount + 1
    
    #this is where comparison is going to be implemented in future
    def perform_comparison(self, files):
        print(files)
        
    def refresh(self):
        for widget in self.file_container.winfo_children():
            widget.destroy()

        for widget in self.selected_files.winfo_children():
            if widget != self.selected_box:
                widget.destroy()

        self.selected_amount = 0
        self.files_to_compare = []

        if int(self.analysed_docs.get()) < 2:
            self.result_box.config(text="Not enough analysed documents to perform comparison")
            return

        self.result_box.config(text="Choose 2 documents to compare:")

        t.Label(self.file_container, text="Uploaded Files",
                fg="white", bg="#0b0f3b",
                font=("Arial", 10, "bold")).pack(pady=10)

        for file in self.master.files:
            filename = file.replace('\\', '/').split("/")[-1]

            t.Button(self.file_container,
                    text=filename,
                    command=lambda f=file: self.select_document(f)
                    ).pack(pady=3)
        
        
# -----RUN APP----- #
app = AityApp()
app.mainloop()