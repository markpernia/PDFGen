import os
from tkinter import Tk, Label, Button, Entry, Checkbutton, IntVar, filedialog, messagebox, simpledialog
from tkinter import ttk  # For the progress bar
from PIL import Image, ImageDraw, ImageFont


def collect_images(directory, include_subdirs, file_types):
    """Collect image files based on user selections."""
    file_types_set = set(ext.lower() for ext in file_types)
    image_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(tuple(file_types_set)):
                image_files.append(os.path.join(root, filename))
        if not include_subdirs:
            break
    return image_files


def generate_pdf(directory, include_subdirs, include_jpg, include_png):
    """Generate a PDF from selected images in the directory."""
    fig_files = [f for f in os.listdir(directory) if f.endswith('.fig')]

    if len(fig_files) == 0:
        messagebox.showwarning("Warning", "No .fig file found in the directory.")
        return  # Exit the function since no .fig file is available

    elif len(fig_files) == 1:
        fig_filename = os.path.splitext(fig_files[0])[0]

    else:
        fig_filename = simpledialog.askstring(
            "Input",
            f"Multiple .fig files found:\n\n{', '.join(fig_files)}\n\nPlease enter a custom name for the PDF file:"
        )
        if not fig_filename:
            return  # User cancelled the operation

    file_types = (['.jpg', '.jpeg'] if include_jpg else []) + (['.png'] if include_png else [])
    image_files = collect_images(directory, include_subdirs, file_types)

    warnings = check_warnings(fig_filename, image_files, file_types)
    if warnings:
        messagebox.showwarning("Warning", "\n".join(warnings))
        return

    if image_files:
        create_pdf(directory, fig_filename, image_files)
    else:
        messagebox.showwarning("Warning", "No images found.")


def select_fig_file(fig_files):
    """Prompt the user to select or enter the desired .fig file."""
    fig_filename = simpledialog.askstring(
        "Select FIG File",
        f"Multiple .fig files found:\n\n{', '.join(fig_files)}\n\nPlease enter the desired .fig file name (without extension):"
    )
    if fig_filename:
        # Check if the entered filename matches any of the available .fig files
        if any(fig_filename == os.path.splitext(f)[0] for f in fig_files):
            return fig_filename
        else:
            messagebox.showerror("Error", "Invalid file name entered. Please try again.")
            return select_fig_file(fig_files)  # Retry if the user entered an invalid name
    else:
        return None  # User cancelled the operation


def check_warnings(fig_filename, image_files, file_types):
    """Check for any warnings based on user selections and collected images."""
    warnings = []

    # Check for missing .fig file (shouldn't happen after user selection)
    if not fig_filename:
        warnings.append("No .fig file found.")

    # Check if no images are found
    if not image_files:
        if not file_types:
            warnings.append("No image file types selected.")
        else:
            missing_types = []
            for ext in file_types:
                if not any(img.lower().endswith(ext) for img in image_files):
                    missing_types.append(ext)
            if missing_types:
                missing_types_str = ', '.join([f"No {ext} files found" for ext in missing_types])
                warnings.append(missing_types_str)
    else:
        if not file_types:
            warnings.append("No image file types selected.")

    return warnings


def create_pdf(directory, fig_filename, image_files):
    """Create a PDF from images with text annotations."""
    total_images = len(image_files)
    progress_bar["maximum"] = total_images

    images_with_text = []
    for idx, img_path in enumerate(image_files):
        images_with_text.append(process_image(img_path))
        progress_bar["value"] = idx + 1

        # Update percentage
        percentage = int((idx + 1) / total_images * 100)
        percentage_label.config(text=f"{percentage}%")
        progress_bar.update()

    pdf_filename = os.path.join(directory, f"{fig_filename}.pdf")

    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    images_with_text[0].save(pdf_filename, save_all=True, append_images=images_with_text[1:], resolution=300.0,
                             quality=95)

    filename_only = os.path.basename(pdf_filename)
    messagebox.showinfo("Success", f"PDF generated successfully as {filename_only}")
    progress_bar["value"] = 0  # Reset progress bar after completion
    percentage_label.config(text="0%")  # Reset percentage label


def process_image(img_path):
    """Process an individual image by adding text annotation below it."""
    img = Image.open(img_path)

    if img.mode == 'RGBA':
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background

    img = img.convert('RGB')
    font_size = min(int(img.width * 0.03), 300)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(img)
    text = os.path.basename(img_path)
    text_width, text_height = get_text_size(draw, text, font)

    padding = 20
    rectangle_padding = 10
    rectangle_height = text_height + 2 * rectangle_padding

    new_img_height = img.height + rectangle_height + padding
    new_img = Image.new("RGB", (img.width, new_img_height), "white")
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    rectangle_y1 = new_img.height - rectangle_height
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
    else:
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

    Button(app_window, text="Create PDF", command=start_processing).grid(row=3, column=0, columnspan=3, padx=10,
                                                                         pady=20)

    progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # Add a Label to display the percentage
    percentage_label.grid(row=4, column=2, padx=10, pady=10, sticky='e')


# Create the main window
app_window = Tk()
app_window.title("ImgToPDF")

# Set the window icon
icon_path = 'PDFGen.ico'
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

# Progress bar widget
progress_bar = ttk.Progressbar(app_window, orient="horizontal", mode="determinate")

# Label to display the percentage
percentage_label = Label(app_window, text="0%")

# Set up the UI elements
setup_ui()

# Run the application
app_window.mainloop()  # Start the Tkinter event loop
