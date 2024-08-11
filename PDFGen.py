import os
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont


def collect_images(directory, include_subdirs, file_types):
    """Collect image files based on user selections."""
    image_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if any(filename.lower().endswith(ext) for ext in file_types):
                image_files.append(os.path.join(root, filename))
        if not include_subdirs:
            break
    return image_files


def generate_pdf(directory, include_subdirs, include_jpg, include_png):
    """Generate a PDF from selected images in the directory."""
    fig_filename = next((os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith('.fig')), None)
    file_types = (['.jpg', '.jpeg'] if include_jpg else []) + (['.png'] if include_png else [])
    image_files = collect_images(directory, include_subdirs, file_types)

    warnings = check_warnings(fig_filename, image_files, file_types, directory)
    if warnings:
        messagebox.showwarning("Warning", "\n".join(warnings))
        return

    if fig_filename and image_files:
        create_pdf(directory, fig_filename, image_files)
    else:
        messagebox.showwarning("Warning", "No .fig file found or no images found.")