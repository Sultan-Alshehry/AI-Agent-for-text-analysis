
import tkinter as t
from tkinter import filedialog, messagebox
import threading
from ai_config import get_mode_display_name, setup_environment
from summary_saver import save_summary
from mode_switch import set_mode, change_API_key
from analysis import json_to_text
from ui.ui_constants import UIConstants as C
from file_reader import read_file, validate_and_read_file
from analysis_formatter import format_analysis_for_ui
from ui.ui_helpers import (
    create_hero_frame, create_centered_label, create_button,
    create_upload_box, create_info_label, create_stat_box
)
import analysis as a
import state


"""
User Interface Module
---------------------
Main GUI application for AI-powered text analysis.

Components:
- AityApp: Main application window and frame management
- Dashboard: Home screen with stats, uploads, and mode switching
- FileSelection: Document browser and selection screen
- Analysis: Analysis results display and export
- Compare: Multi-document comparison (in progress)
"""


class AityApp(t.Tk):
    # Main application window.
    # Manages frame navigation, file storage, and analysis mode switching.

    def __init__(self):
        super().__init__()
        self.title(C.WINDOW_TITLE)
        self.geometry(C.WINDOW_WIDTH)
        self.config(bg=C.BG_COLOR)

        # Initialize analysis mode
        self.analysis_mode = setup_environment()
        self.files = []
        self.frames = {}

        # Document stats
        self.total_docs = t.StringVar(value="0")
        self.analysed_docs = t.StringVar(value="0")
        self.ready_to_compare_docs = t.StringVar(value="❌")

        # Initialize frames 
        for F in (Dashboard, FileSelection, Analysis, Compare):
            frame = F(self, self.total_docs, self.analysed_docs, self.ready_to_compare_docs)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(Dashboard)


    # Switches mode between Gemini and keybert
    def change_mode(self, mode):
        set_mode(mode)
        
        # Update UI with new mode
        self.analysis_mode = state.ANALYSIS_MODE
        dashboard = self.frames.get(Dashboard)
        if dashboard and hasattr(dashboard, "mode_label"):
            dashboard.mode_label.config(text=f"Mode: {self.get_display_mode()}")
            dashboard.show_documents()

        messagebox.showinfo("Mode switched", f"Analysis mode set to {self.get_display_mode()}")

    def get_display_mode(self):
        return get_mode_display_name(self.analysis_mode)


    # Switches between screens "Documents", "Uploads"
    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        if frame_class == FileSelection:
            frame.refresh_files()
        if frame_class == Compare:
            frame.refresh()
        frame.tkraise()


# ---------------- DASHBOARD ---------------- #
class Dashboard(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg=C.BG_COLOR)

        self.total_docs = total_docs
        self.analysed_docs = analysed_docs
        self.ready_compare = ready_compare

        t.Label(self, text=C.LABEL_DASHBOARD,
                fg=C.TEXT_COLOR, bg=C.BG_COLOR,
                font=C.FONT_TITLE).pack(pady=C.PADDING_LARGE)

        # Stats
        stats_frame = t.Frame(self, bg=C.BG_COLOR)
        stats_frame.pack(pady=C.PADDING_MEDIUM)
        self.create_stat(stats_frame, "Total documents", total_docs)
        self.create_stat(stats_frame, "Analyzed", analysed_docs)
        self.create_stat(stats_frame, "Ready to compare", ready_compare)


        # Buttons
        btn_frame = t.Frame(self, bg=C.BG_COLOR)
        btn_frame.pack(pady=C.PADDING_LARGE, anchor='center')

        t.Button(btn_frame, text=C.LABEL_DOCUMENTS, 
                 width=15,
                 command=self.show_documents).grid(row=0, column=0, padx=10)
        
        t.Button(btn_frame, text=C.LABEL_UPLOADS, 
                 width=15,
                 command=self.show_uploads).grid(row=0, column=1, padx=10)
        
        self.compare_btn = t.Button(btn_frame, text=C.LABEL_COMPARE,
                width=15,
                 command=lambda: self.master.show_frame(Compare))
        self.compare_btn.grid(row=0, column=2, padx=10)

        self.mode_label = t.Label(btn_frame, 
                                  text=f"Mode: {self.master.get_display_mode()}", 
                                  fg=C.TEXT_COLOR, bg=C.BG_COLOR)
        self.mode_label.grid(row=1, column=0, columnspan=3)

        mode_frame = t.Frame(btn_frame, bg=C.BG_COLOR)
        mode_frame.grid(row=2, column=0, columnspan=3, pady=C.PADDING_MEDIUM)
       
        t.Button(mode_frame, text=C.BTN_USE_GEMINI,
                width=12,
                command=lambda: self.master.change_mode("genai")).pack(side="left", padx=C.PADDING_MEDIUM)

        t.Button(mode_frame, text=C.BTN_USE_BERTS,
            width=12,
            command=lambda: self.master.change_mode("berts")).pack(side="left", padx=C.PADDING_MEDIUM)
                
        t.Button(mode_frame, text=C.BTN_CHANGE_API_KEY,
                width=12,
                command=lambda: change_API_key()).pack(side="left", padx=C.PADDING_MEDIUM)

        self.content_frame = t.Frame(self, bg=C.BG_COLOR)
        self.content_frame.pack(fill="both", expand=True)
        
        self.show_documents()

    def create_stat(self, parent, title, value):
        """Create a stat display box using helper."""
        create_stat_box(parent, title, value)
            
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


# ---------------- DOCUMENT VIEW ---------------- #
    def show_documents(self):
        self.clear_content()
        
        # Hero section
        hero = create_hero_frame(self.content_frame, height=C.HERO_FRAME_HEIGHT, bg_color=C.BOX_COLOR)
        create_centered_label(hero, C.LABEL_DOCUMENT_HERO, bg_color=C.BOX_COLOR)
        
        # View Documents button
        create_button(self.content_frame, C.BTN_VIEW_DOCUMENTS,
                     command=lambda: self.master.show_frame(FileSelection))
        
        # Status info
        info_text = f"Current mode: {self.master.get_display_mode()} | Uploaded: {len(self.master.files)}"
        info_label = create_info_label(self.content_frame, info_text)
        info_label.pack(pady=C.PADDING_SMALL)


# ---------------- UPLOAD VIEW ---------------- #
    def show_uploads(self):
        self.clear_content()
        
        # Hero section
        hero = create_hero_frame(self.content_frame, height=C.HERO_FRAME_SMALL_HEIGHT, bg_color=C.BOX_COLOR)
        create_centered_label(hero, C.LABEL_UPLOAD_HERO, bg_color=C.BOX_COLOR)
        
        # Upload box with button
        create_upload_box(self.content_frame, C.LABEL_UPLOAD_PROMPT, C.BTN_CHOOSE_FILE, self.upload_file)

    def upload_file(self):
        # Upload and validate a document file.
        file = filedialog.askopenfilename(
            filetypes=[("Text and PDF files", "*.txt *.pdf"), ("All files", "*.*")]
        )
        
        if not file:
            return

        filename = file.split("/")[-1]
        
        # Validate and read file in one operation
        success, result = validate_and_read_file(file)
        if not success:
            messagebox.showerror("Invalid file", result)
            return

        # File is valid and readable, add to application
        self.master.files.append(file)
        messagebox.showinfo("Document Uploaded", f"Successfully uploaded: {filename}")

        # Update statistics
        current = int(self.total_docs.get())
        self.total_docs.set(str(current + 1))

        current = int(self.analysed_docs.get())
        self.analysed_docs.set(str(current + 1))

        if int(self.analysed_docs.get()) >= 2:
            self.ready_compare.set("✅")

        # Refresh UI
        self.master.frames[FileSelection].refresh_files()
        self.master.show_frame(FileSelection)


# ---------------- FILE SELECTION ---------------- #
class FileSelection(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg=C.BG_COLOR)
        self.master = master

        t.Label(self, text="Select Document",
                fg=C.TEXT_COLOR, bg=C.BG_COLOR).pack(pady=C.PADDING_LARGE)
        
        self.file_container = t.Frame(self, bg=C.BG_COLOR)
        self.file_container.pack()

        t.Button(self, text=C.BTN_BACK,
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
                fg=C.TEXT_COLOR, bg=C.BG_COLOR, font=C.FONT_SMALL).pack(pady=C.PADDING_MEDIUM)

        if not self.master.files:
            t.Label(self.file_container,
                    text="No uploaded files yet.",
                    fg=C.TEXT_COLOR, bg=C.BG_COLOR).pack(pady=C.PADDING_SMALL)
        else:
            for file in self.master.files:
                filename = file.replace('\\', '/').split("/")[-1]

                t.Button(self.file_container,
                        text=filename,
                        command=lambda f=file: self.open_analysis(f)
                        ).pack(pady=C.PADDING_SMALL)


# ---------------- ANALYSIS SCREEN ---------------- #
class Analysis(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg=C.BG_COLOR)
        self.current_results = None  
        self.current_filepath = None  

        self.label = t.Label(self, text=C.LABEL_ANALYSIS_RESULTS,
                             fg=C.TEXT_COLOR, bg=C.BG_COLOR,
                             font=C.FONT_HEADER)
        self.label.pack(pady=C.PADDING_MEDIUM)

        self.result_box = t.Label(
            self, bg=C.BOX_COLOR, fg=C.TEXT_COLOR, justify="left", padx=C.PADDING_LARGE, pady=C.PADDING_LARGE, wraplength=500 
        )
        self.result_box.pack(pady=C.PADDING_LARGE)

        # Button frame for Back and Save buttons
        button_frame = t.Frame(self, bg=C.BG_COLOR)
        button_frame.pack(anchor="nw", pady=C.PADDING_MEDIUM)

        t.Button(button_frame, text=C.BTN_BACK,
                 command=lambda: master.show_frame(FileSelection)
                 ).pack(side="left", padx=C.PADDING_SMALL)

        t.Button(button_frame, text=C.BTN_SAVE_RESULTS,
                 command=self.save_results
                 ).pack(side="left", padx=C.PADDING_SMALL)


    def update_analysis(self, filepath):
        # Initiate analysis for the selected file.
        self.current_filepath = filepath
        self.result_box.config(text="Analyzing... Please wait.")
        self.update()  

        def analyze():
            try:
                mode = getattr(self.master, "analysis_mode", "genai")
                summarys_path = a.get_analysis_result(filepath, mode=mode)

                summary, keywords, topics, source_file, mode = json_to_text(summarys_path)
                self.update_analysis_from_text(summary, keywords, topics, source_file=source_file, mode=mode)
            except Exception as e:
                self.result_box.config(text=f"Error during analysis: {str(e)}")

        thread = threading.Thread(target=analyze)
        thread.start()
    
    def update_analysis_from_text(self, summary, keywords, topics, source_file=None, mode=None):
        source_text = None
        if isinstance(source_file, str) and source_file.strip():
            try:
                source_text = read_file(source_file)
            except Exception:
                source_text = None

        display_text = format_analysis_for_ui(summary, keywords, topics, source_text=source_text, mode=mode)
        self.result_box.config(text=display_text)
        
        self.current_results = {
            "summary": summary,
            "keywords": keywords,
            "topics": topics,
            "source_file": source_file,
            "mode": mode,
        }

    def save_results(self):
        # Save analysis results to a custom location using save_summary"""
        if not self.current_results:
            messagebox.showwarning("No Results", "No analysis results to save. Please analyze a document first.")
            return
        
        # Generate default filename based on loaded file
        if self.current_filepath:
            from pathlib import Path
            filename_stem = Path(self.current_filepath).stem
            default_filename = f"{filename_stem}_analysis_results.txt"
        else:
            default_filename = "analysis_results.txt"
        
        # Ask user where to save
        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if output_path:
            try:
                file_format = "txt" if output_path.endswith(".txt") else "json"
                save_summary(self.current_results, output_path, format=file_format)
                messagebox.showinfo("Success", f"Results saved to:\n{output_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")
        

# ---------------- COMPARE SCREEN ---------------- #
class Compare(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg=C.BG_COLOR)
        
        self.analysed_docs = analysed_docs
        self.total_docs = total_docs
        self.ready_compare = ready_compare
        
        
        self.selected_amount = 0
        self.files_to_compare = []
        # self.enough_selected_documents = False
        
        self.label = t.Label(self, text=C.LABEL_SELECT_COMPARE,
                             fg=C.TEXT_COLOR, bg=C.BG_COLOR,
                             font=C.FONT_HEADER)
        self.label.pack(pady=C.PADDING_MEDIUM)

        self.result_box = t.Label(
            self, bg=C.BOX_COLOR, fg=C.TEXT_COLOR, justify="left", padx=C.PADDING_LARGE, pady=C.PADDING_LARGE,
        )

        self.result_box.pack(pady=C.PADDING_LARGE)
        
        self.file_container = t.Frame(self, bg=C.BG_COLOR)
        self.file_container.pack()
        
        self.selected_files = t.Frame(self, bg=C.BG_COLOR)
        self.selected_files.pack(pady=C.PADDING_MEDIUM)
        
        self.selected_box = t.Label(self.selected_files, text="selected documents",
                             fg=C.TEXT_COLOR, bg=C.BG_COLOR,
                             font=C.FONT_NORMAL)
        self.selected_box.pack() 
        
        t.Button(self, text=C.BTN_BACK,
            command=lambda: master.show_frame(Dashboard)
            ).pack(anchor="nw")
        

    def select_document(self, file):
        
        if self.selected_amount < 2:
            t.Label(self.selected_files, text = file.split("/")[-1],
            fg=C.TEXT_COLOR, bg=C.BG_COLOR, font=C.FONT_SMALL).pack(pady=C.PADDING_MEDIUM)
            self.files_to_compare.append(file)
            self.selected_amount = self.selected_amount + 1
            
        
        if self.selected_amount == 2:
            t.Button(self.selected_files,
                    text=C.BTN_COMPARE,
                    command=lambda f=self.files_to_compare: self.perform_comparison(f)
                    ).pack(pady=C.PADDING_SMALL)
            self.selected_amount = self.selected_amount + 1
    

    def perform_comparison(self, files):
        # Execute comparison analysis on selected documents.
        # TODO: Implement document comparison logic
        pass
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
                fg=C.TEXT_COLOR, bg=C.BG_COLOR,
                font=C.FONT_SMALL).pack(pady=C.PADDING_MEDIUM)

        for file in self.master.files:
            filename = file.replace('\\', '/').split("/")[-1]

            t.Button(self.file_container,
                    text=filename,
                    command=lambda f=file: self.select_document(f)
                    ).pack(pady=C.PADDING_SMALL)
        
        
# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app = AityApp()
    app.mainloop()