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

from file_reader import validate_and_read_file
from analysis import get_analysis_result, json_to_text
from analysis_formatter import format_analysis_for_ui
from summary_saver import save_summary
from mode_switch import set_mode
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
        messagebox.showinfo("Mode switched", f"Analysis mode set to {app_instance.analysis_mode}")

    @staticmethod
    def handle_analysis(filepath, analysis_callback):
        def analyze():
            try:
                mode = state.ANALYSIS_MODE
                summarys_path = get_analysis_result(filepath, mode=mode)
                summary, keywords, topics = json_to_text(summarys_path)
                analysis_callback(summary, keywords, topics)
            except Exception as e:
                analysis_callback(None, None, f"Error during analysis: {str(e)}")

        thread = threading.Thread(target=analyze, daemon=True)
        thread.start()

    @staticmethod
    def format_analysis_results(summary, keywords, topics):
        if summary is None:  
            return keywords  
        
        return format_analysis_for_ui(summary, keywords, topics)

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
    def perform_document_comparison(file1_path, file2_path):
        try:
            # TODO: Implement actual comparison logic
            # For now, return placeholder
            return {
                "status": "success",
                "message": "Comparison feature coming soon",
                "file1": file1_path,
                "file2": file2_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
