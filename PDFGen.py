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


def create_pdf(directory, fig_filename, image_files):
    """Create a PDF from images with text annotations."""
    images_with_text = [process_image(img_path) for img_path in image_files]
    pdf_filename = os.path.join(directory, f"{fig_filename}.pdf")

    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    images_with_text[0].save(pdf_filename, save_all=True, append_images=images_with_text[1:], resolution=300.0,
                             quality=95)
    # messagebox.showinfo("Success", f"PDF generated successfully as {pdf_filename}")

    # Extract just the filename from the full path
    filename_only = os.path.basename(pdf_filename)

    # Show the success message with only the filename
    messagebox.showinfo("Success", f"PDF generated successfully as {filename_only}")


def process_image(img_path):
    """Process an individual image by adding text annotation below it."""
    img = Image.open(img_path)

    # Check if the image has transparency (mode 'RGBA')
    if img.mode == 'RGBA':
        # Create a white background image
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Paste using the alpha channel as mask
        img = background

    # Proceed with the rest of the processing
    img = img.convert('RGB')
    font_size = min(int(img.width * 0.03), 300)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(img)
    text = os.path.basename(img_path)
    text_width, text_height = get_text_size(draw, text, font)

    padding = 20  # Padding between the image and the label
    rectangle_padding = 10
    rectangle_height = text_height + 2 * rectangle_padding  # Text height + padding above and below

    new_img_height = img.height + rectangle_height + padding
    new_img = Image.new("RGB", (img.width, new_img_height), "white")
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    rectangle_y1 = new_img.height - rectangle_height  # Position rectangle at the very bottom
    rectangle_y2 = new_img.height
    draw.rectangle([0, rectangle_y1, img.width, rectangle_y2], fill="white")

    text_position = ((new_img.width - text_width) / 2, rectangle_y1 + rectangle_padding)
    draw.text(text_position, text, font=font, fill="black")

    return new_img.convert('RGB')


def get_text_size(draw, text, font):
    """Get the size of the text for positioning."""
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    return draw.textsize(text, font=font)


def browse_directory():
    """Open a file dialog to select a directory."""
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, 'end')
        entry_directory.insert(0, directory)


def start_processing():
    """Start the PDF generation process based on user input."""
    directory = entry_directory.get().strip()
    if not os.path.isdir(directory):
        messagebox.showerror("Error", "The specified directory does not exist. Please check the path and try again.")
        return

    include_subdirs = include_subdirs_var.get() == 1
    include_jpg = include_jpg_var.get() == 1
    include_png = include_png_var.get() == 1

    if not (include_jpg or include_png):
        messagebox.showwarning("Warning", "No image file type selected. Please select at least one image file type.")
        return

    generate_pdf(directory, include_subdirs, include_jpg, include_png)


def setup_ui():
    """Set up the main window UI."""
    Label(app_window, text="Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    entry_directory.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
    Button(app_window, text="Browse", command=browse_directory).grid(row=0, column=2, padx=10, pady=5)

    Checkbutton(app_window, text="Include images from subdirectories", variable=include_subdirs_var).grid(row=1,
                                                                                                          column=0,
                                                                                                          columnspan=3,
                                                                                                          padx=10,
                                                                                                          pady=5,
                                                                                                          sticky='w')

    Checkbutton(app_window, text="jpg/jpeg", variable=include_jpg_var).grid(row=2, column=0, padx=10, pady=5,
                                                                                    sticky='w')

    Checkbutton(app_window, text="png", variable=include_png_var).grid(row=2, column=1, padx=10, pady=5,
                                                                              sticky='w')

    Button(app_window, text="Generate PDF", command=start_processing).grid(row=3, column=0, columnspan=3, padx=10,
                                                                           pady=20)


# Create the main window
app_window = Tk()
app_window.title("PDF Generator v0.1")

# Set the window icon
icon_path = 'icon.ico'
if os.path.isfile(icon_path):
    app_window.iconbitmap(icon_path)

# Layout configuration
app_window.grid_rowconfigure(0, weight=1)
app_window.grid_rowconfigure(1, weight=1)
app_window.grid_rowconfigure(2, weight=1)
app_window.grid_rowconfigure(3, weight=1)
app_window.grid_columnconfigure(1, weight=1)

# Directory input
entry_directory = Entry(app_window, width=50)

# Variables for checkboxes
include_subdirs_var = IntVar()
include_jpg_var = IntVar()
include_png_var = IntVar()

# Set up the UI elements
setup_ui()

# Run the application
app_window.mainloop()
