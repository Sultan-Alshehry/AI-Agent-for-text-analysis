"""
UI Service Module
-----------------
Service layer for UI callbacks and business logic.
Separates UI presentation from application logic.

Handles:
- File upload validation and stats updates
- Analysis execution and result management
- Mode switching with dialog prompting
- Document comparison logic
"""

import tkinter as t
from tkinter import filedialog, messagebox
import threading

from ai_config import get_mode_display_name
from file_reader import read_file, validate_and_read_file
from analysis import get_analysis_result, json_to_text
from analysis_formatter import format_analysis_for_ui
from summary_saver import save_summary
from mode_switch import set_mode
from comparison import compare_results
import state


class UIService:
    # Service class for UI-related business logic.
    @staticmethod
    def handle_file_upload(app_instance):
        file = filedialog.askopenfilename(
            filetypes=[("Text and PDF files", "*.txt *.pdf"), ("All files", "*.*")]
        )
        
        if not file:
            return False

        filename = file.split("/")[-1]
        
        # Validate and read file
        success, result = validate_and_read_file(file)
        if not success:
            messagebox.showerror("Invalid file", result)
            return False

        # File is valid - add to app
        app_instance.files.append(file)
        
        # Update statistics
        current = int(app_instance.total_docs.get())
        app_instance.total_docs.set(str(current + 1))

        current = int(app_instance.analysed_docs.get())
        app_instance.analysed_docs.set(str(current + 1))

        if int(app_instance.analysed_docs.get()) >= 2:
            app_instance.ready_to_compare_docs.set("✅")

        messagebox.showinfo("Document Uploaded", f"Successfully uploaded: {filename}")
        return True

    @staticmethod
    def handle_mode_change(app_instance, mode):
        set_mode(mode)
        app_instance.analysis_mode = state.ANALYSIS_MODE
        messagebox.showinfo(
            "Mode switched",
            f"Analysis mode set to {get_mode_display_name(app_instance.analysis_mode)}"
        )

    @staticmethod
    def handle_analysis(filepath, analysis_callback):
        def analyze():
            try:
                mode = state.ANALYSIS_MODE
                summarys_path = get_analysis_result(filepath, mode=mode)
                summary, keywords, topics, source_file, analysis_mode = json_to_text(summarys_path)
                analysis_callback(summary, keywords, topics, source_file, analysis_mode)
            except Exception as e:
                analysis_callback(None, None, f"Error during analysis: {str(e)}")

        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()

    @staticmethod
    def format_analysis_results(summary, keywords, topics, source_file=None, mode=None):
        if summary is None:  
            return keywords  

        source_text = None
        if isinstance(source_file, str) and source_file.strip():
            try:
                source_text = read_file(source_file)
            except Exception:
                source_text = None

        return format_analysis_for_ui(summary, keywords, topics, source_text=source_text, mode=mode)

    @staticmethod
    def handle_save_results(results_dict, filepath=None):
        if not results_dict:
            messagebox.showwarning("No Results", "No analysis results to save.")
            return False

        # Generate default filename based on loaded file
        if filepath:
            from pathlib import Path
            filename_stem = Path(filepath).stem
            default_filename = f"{filename_stem}_analysis_results.txt"
        else:
            default_filename = "analysis_results.txt"

        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if output_path:
            try:
                file_format = "txt" if output_path.endswith(".txt") else "json"
                save_summary(results_dict, output_path, format=file_format)
                messagebox.showinfo("Success", f"Results saved to:\n{output_path}")
                return True
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")
                return False
        
        return False

    @staticmethod
    def handle_compare_selection(selected_documents):
        if len(selected_documents) < 2:
            return {"valid": False, "message": "Select 2 documents to compare"}
        
        if len(selected_documents) > 2:
            return {"valid": False, "message": "Maximum 2 documents allowed"}
        
        return {"valid": True, "message": "Ready to compare"}

    @staticmethod
    def perform_document_comparison(filepaths):
        try:
            return compare_results(filepaths)
        except FileNotFoundError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
