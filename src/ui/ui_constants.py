"""
UI Constants Module
-------------------
Centralized UI configuration for consistent styling and text.
"""

class UIConstants:
    # Colors
    BG_COLOR = "#0b0f3b"           # Main background
    BOX_COLOR = "#1a1f5a"          # Stats box background
    HERO_COLOR = "#2a2f6a"         # Hero section background
    TEXT_COLOR = "white"
    
    # Fonts
    FONT_TITLE = ("Arial", 18, "bold")     # Main titles
    FONT_HEADER = ("Arial", 14, "bold")    # Section headers
    FONT_SUBHEADER = ("Arial", 12, "bold") # Subheaders
    FONT_SMALL = ("Arial", 10, "bold")     # Small text bold
    FONT_NORMAL = ("Arial", 12)            # Normal text
    
    # Window settings
    WINDOW_WIDTH = "600x600"
    WINDOW_TITLE = "AITY AI Agent for text analysing"
    
    # Grid and spacing
    STAT_BOX_WIDTH = 120
    STAT_BOX_HEIGHT = 60
    PADDING_LARGE = 20
    PADDING_MEDIUM = 10
    PADDING_SMALL = 5
    
    # Frame dimensions
    HERO_FRAME_HEIGHT = 150
    HERO_FRAME_SMALL_HEIGHT = 80
    UPLOAD_BOX_HEIGHT = 150
    
    # Button defaults
    BTN_WIDTH = 15
    BTN_SMALL_WIDTH = 12
    
    # Labels
    LABEL_DASHBOARD = "AITY Dashboard"
    LABEL_DOCUMENTS = "Documents"
    LABEL_UPLOADS = "Uploads"
    LABEL_COMPARE = "Compare"
    LABEL_TOTAL_DOCS = "Total documents"
    LABEL_ANALYZED = "Analyzed"
    LABEL_READY_COMPARE = "Ready to compare"
    LABEL_ANALYSIS_RESULTS = "Analysis Results"
    LABEL_SELECT_COMPARE = "select documents to compare"
    LABEL_UPLOAD_HERO = "Upload Document\nAdd a new document for AI-powered text analysis"
    LABEL_DOCUMENT_HERO = "Upload a document to get started with analysing\n\nSelect Uploads and add a document"
    LABEL_UPLOAD_PROMPT = "Upload a document (.pdf or .txt)"
    
    # Button texts
    BTN_VIEW_DOCUMENTS = "View Documents"
    BTN_CHOOSE_FILE = "Choose file"
    BTN_USE_GEMINI = "Use Gemini"
    BTN_USE_HYBRID = "Use KeyBERT + BERTopic"
    BTN_BACK = "⬅ Back"
    BTN_SAVE_RESULTS = "💾 Save Results"
    BTN_COMPARE = "Compare results"
    BTN_CHANGE_API_KEY = "Change API key"
