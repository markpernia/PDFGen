import os


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
