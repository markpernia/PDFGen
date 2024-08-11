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
