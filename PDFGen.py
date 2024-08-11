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


def check_warnings(fig_filename, image_files, file_types, directory):
    """Check for any warnings based on user selections and collected images."""
    warnings = []
    if not fig_filename:
        warnings.append("No .fig file found.")

    if not image_files:
        missing_types = [ext for ext in file_types if
                         not any(f.endswith(ext) for f in collect_images(directory, True, [ext]))]
        for ext in missing_types:
            warnings.append(f"No {ext} files found.")
    elif not file_types:
        warnings.append("No image file types selected.")

    return warnings
