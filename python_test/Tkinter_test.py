import tkinter as t
from tkinter import filedialog
import os

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
        
        #variables that are used to show how many documents are
        #uploaded, analysed and ready to compare
        self.total_docs = t.StringVar(value="0")
        self.analysed_docs = t.StringVar(value="0")
        self.ready_to_compare_docs = t.StringVar(value="❌")

# Store uploaded files and example files
        self.files = []

        self.example_files = {
            "sports.txt": "Ice hockey is popular. Football and skiing are common sports.",
            "data.txt": "Data science includes machine learning, statistics, and visualization."
        }

        # Example analysis for sports.txt file
        self.example_analysis = {
            "sports.txt": """Keyword        Relevance

ice hockey        8%
floor ball           5%
skiing                4.5%
bouldering       3%
dancing            2%
football            1.5%
futsal                1%"""
        }

        self.frames = {}

        for F in (Dashboard, FileSelection, Analysis, Compare):
            frame = F(self, self.total_docs, self.analysed_docs, self.ready_to_compare_docs)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(Dashboard) 

    # Swithes between screens "Documents", "Uploads"
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
        btn_frame.pack(pady=20)

        t.Button(btn_frame, text="Documents",
                 width=15,
                 command=self.show_documents).grid(row=0, column=0, padx=10)

        t.Button(btn_frame, text="Uploads",
                 width=15,
                 command=self.show_uploads).grid(row=0, column=1, padx=10)
                 
        self.compare_btn = t.Button(btn_frame, text="Compare",
                 width=15,
                 command=lambda: self.master.show_frame(Compare))
        
        self.compare_btn.grid(row=0, column=2, padx=10)

        # ✅ THIS is where dynamic content goes
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
                 command=lambda: self.master.show_frame(FileSelection)
                 ).pack(pady=10)

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
            self.master.files.append(file)
            print("Saved:", file)
            current = int(self.total_docs.get())
            self.total_docs.set(str(current + 1))
            
            current = int(self.analysed_docs.get())
            self.analysed_docs.set(str(current + 1))
            
            if int(self.analysed_docs.get()) >= 2:
                self.ready_compare.set("✅")

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

    def refresh_files(self):
        for widget in self.file_container.winfo_children():
            widget.destroy()

        t.Label(self.file_container, text="Example Files",
                fg="white", bg="#0b0f3b", font=("Arial", 10, "bold")).pack()

        for name, content in self.master.example_files.items():
            t.Button(self.file_container,
                    text=name,
                    command=lambda c=content, n=name: self.open_analysis_content(n, c)
                    ).pack(pady=3)

        t.Label(self.file_container, text="Uploaded Files",
                fg="white", bg="#0b0f3b", font=("Arial", 10, "bold")).pack(pady=10)

        for file in self.master.files:
            filename = file.split("/")[-1]

            t.Button(self.file_container,
                    text=filename,
                    command=lambda f=file: self.open_analysis(f)
                    ).pack(pady=3)

    def open_analysis(self, file):
        self.master.selected_file = file
        self.master.frames[Analysis].update_analysis(file)
        self.master.show_frame(Analysis)

    def open_analysis_content(self, name, content):
        self.master.frames[Analysis].update_analysis_from_text(name, content)
        self.master.show_frame(Analysis)

# -----ANALYSIS SCREEN----- #
# Displays results of selected file
    
class Analysis(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")

        self.label = t.Label(self, text="Analysis Results",
                             fg="white", bg="#0b0f3b",
                             font=("Arial", 14))
        self.label.pack(pady=10)

        self.result_box = t.Label(self, bg="#1a1f5a", fg="white",
                                 justify="left", padx=20, pady=20)
        self.result_box.pack(pady=20)

        t.Button(self, text="⬅ Back",
                 command=lambda: master.show_frame(FileSelection)
                 ).pack(anchor="nw")

    # Reads file content and updates analysis view
    # To be updated with actual AI analysis logic in future
    def update_analysis(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"

        self.update_analysis_from_text(os.path.basename(filepath), content)

    def update_analysis_from_text(self, filename, text):
        if hasattr(self.master, "example_analysis") and filename in self.master.example_analysis:
            result = f"""File: {filename}

{self.master.example_analysis[filename]}"""
        else:
            words = text.split()
            word_count = len(words)

            result = f"""File: {filename}

        Word count: {word_count}

        Preview:
        {text[:200]}...
        """

        self.result_box.config(text=result)
# -----COMPARE DOCUMENTS SCREEN----- #
# Displays screen that allows user to select documents to compare
class Compare(t.Frame):
    def __init__(self, master, total_docs, analysed_docs, ready_compare):
        super().__init__(master, bg="#0b0f3b")
        
        self.analysed_docs = analysed_docs
        self.total_docs = total_docs
        self.ready_compare = ready_compare
        
        self.label = t.Label(self, text="select documents to compare",
                             fg="white", bg="#0b0f3b",
                             font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.result_box = t.Label(self, bg="#1a1f5a", fg="white",
                                    justify="left", padx=20, pady=20)
        self.result_box.pack(pady=20)
        
        t.Button(self, text="⬅ Back",
            command=lambda: master.show_frame(Dashboard)
            ).pack(anchor="nw")
        
    def refresh(self):
        self.result_box.config(text="")
        if int(self.analysed_docs.get()) < 2:
        
            result = """
            Not enough analysed documents to perform comparison
                    """
            self.result_box.config(text=result)
        
        else:
            result = """
            Choose 2 documents to compare:
                    """
            self.result_box.config(text=result)

        
        
        
# -----RUN APP----- #
app = AityApp()
app.mainloop()
