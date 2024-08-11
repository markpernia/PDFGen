PDFGen a standalone executable built with PyInstaller, offering a straightforward solution for generating PDFs from images.

## Features

- Image Format Selection: Choose from `.jpg` / `.jpeg`, or `.png` formats to include in your PDF.
- Subfolder Inclusion: Optionally include images from subdirectories within your specified directory to better manage and organize your image sources.
- Automatic PDF Naming: The generated PDF is automatically named based on the Figma `.fig` file found in the directory, streamlining the naming process.
- Page Labeling: Each page of the generated PDF includes a label at the bottom with the original image filename.

## Getting Started
Download: Obtain the latest standalone executable from the [releases page](https://github.com/markpernia/PDFGen/releases/edit/untagged-2522159e0ebed37cacbd#).
Installation: Simply run the downloaded executable. No additional installation or Python setup is required due to the PyInstaller packaging.

## Usage:

Place your images (`.jpg` / `.jpeg`, or `.png`) and a `.fig` file in the same directory.
Run the executable and specify the directory containing your images.
PDFGen will process the images and generate a PDF named after the `.fig` file.
Configuration: Customize your PDF generation by selecting image formats and deciding whether to include images from subdirectories.