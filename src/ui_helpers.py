"""
UI Helpers Module
-----------------
Reusable component builders for Tkinter UI.
Reduces code duplication by providing helper functions for creating common components.
"""

import tkinter as t
from ui_constants import UIConstants as C


def create_hero_frame(parent, height=C.HERO_FRAME_HEIGHT, bg_color=C.BOX_COLOR):
    # Create a hero section frame.
    hero = t.Frame(parent, bg=bg_color, height=height)
    hero.pack(pady=C.PADDING_LARGE, padx=C.PADDING_LARGE, fill="x")
    hero.pack_propagate(False)
    return hero


def create_centered_label(parent, text, font=C.FONT_NORMAL, bg_color=C.BG_COLOR, expand=True):
    # Create a centered label with standard styling.
    label = t.Label(parent, text=text, fg=C.TEXT_COLOR, bg=bg_color, font=font)
    if expand:
        label.pack(expand=True)
    else:
        label.pack()
    return label


def create_button(parent, text, command, width=C.BTN_WIDTH, side="top", padx=0, pady=C.PADDING_MEDIUM):
    # Create a button with standard styling.
    btn = t.Button(parent, text=text, width=width, command=command)
    if side == "top":
        btn.pack(pady=pady)
    else:
        btn.pack(side=side, padx=padx, pady=pady)
    return btn


def create_upload_box(parent, text, button_text, button_command):
    # Create an upload section with title and action button.
    box = t.Frame(parent, bg=C.HERO_COLOR, height=C.UPLOAD_BOX_HEIGHT)
    box.pack(pady=C.PADDING_LARGE, padx=C.PADDING_LARGE, fill="x")
    box.pack_propagate(False)
    
    t.Label(box, text=text, fg=C.TEXT_COLOR, bg=C.HERO_COLOR).pack(pady=C.PADDING_MEDIUM)
    
    btn = t.Button(box, text=button_text, command=button_command)
    btn.pack()
    
    return {"frame": box, "button": btn}


def create_info_label(parent, text, bg_color=C.BG_COLOR):
    # Create a small info/status label.
    return t.Label(parent, text=text, fg=C.TEXT_COLOR, bg=bg_color, font=C.FONT_SMALL)


def create_stat_box(parent, title, value):
    #Create a stat display box.
    box = t.Frame(parent, bg=C.BOX_COLOR, width=C.STAT_BOX_WIDTH, height=C.STAT_BOX_HEIGHT)
    box.pack(side="left", padx=C.PADDING_MEDIUM)
    box.pack_propagate(False)
    
    t.Label(box, text=title, fg=C.TEXT_COLOR, bg=C.BOX_COLOR).pack()
    
    if isinstance(value, t.StringVar):
        t.Label(box, textvariable=value, fg=C.TEXT_COLOR, bg=C.BOX_COLOR, font=C.FONT_SUBHEADER).pack()
    else:
        t.Label(box, text=value, fg=C.TEXT_COLOR, bg=C.BOX_COLOR, font=C.FONT_SUBHEADER).pack()
    
    return box
