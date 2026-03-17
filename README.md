# Project 1 - LZW Compression for Text and Images

This project was developed for **COMP204 – Programming Studio**.
It implements **Lempel-Ziv-Welch (LZW)** compression and decompression for text files and image files, and provides a **Tkinter-based graphical user interface (GUI)** to test all implemented levels.

## Project Overview

The project consists of five functional levels and one GUI level:

- **Level 1:** LZW compression and decompression for text files
- **Level 2:** LZW compression and decompression for grayscale images
- **Level 3:** LZW compression and decompression for grayscale difference images
- **Level 4:** LZW compression and decompression for RGB color images
- **Level 5:** LZW compression and decompression for RGB difference images
- **Level 6:** Graphical User Interface (GUI) for running all levels

The aim of the project is to understand how **dictionary-based lossless compression** works, how image data can be transformed into compressible sequences, and how preprocessing methods such as **difference images** affect compression performance.

---

## Features

- Text file compression and decompression using LZW
- Grayscale image compression and decompression
- Difference-image based compression for grayscale images
- RGB channel-based compression and decompression
- Difference-image based compression for RGB images
- GUI for selecting:
  - file
  - compression level
  - compress/decompress operation
  - output path
- File size comparison support through the GUI
- Original vs decompressed file checking
- BMP-based restoration support for image levels

---

## File Descriptions

- **lzw_core.py:**
Core LZW compression/decompression implementation.
Includes encoding, decoding, bit-packing, padding, and binary conversion utilities.

- **image_lzw_utils.py:**
Utility functions for packing encoded LZW codes into byte streams, unpacking them, and writing/reading custom headers for compressed image files.

- **basic_image_operations.py:**
Basic image processing functions such as reading, writing, grayscale conversion, flattening, and reshaping arrays.

- **image_tools.py:**
Additional helper functions for image reading and channel operations.

- **level1_text.py:**
Implements Level 1 text compression and decompression.

- **level2_gray.py:**
Implements grayscale image compression and decompression.

- **level3_diff.py:** 
Implements grayscale difference-image compression and decompression.

- **level4_color.py:**
Implements RGB image compression and decompression by compressing each color channel separately.

- **level5_color_diff.py:**
Implements RGB difference-image compression and decompression.

- **level6_gui.py:**
Tkinter-based graphical user interface to run all levels interactively.

---

## Requirements

The project uses Python and the following libraries:

- **Pillow**

- **numpy**

- **tkinter**

Install required libraries with:

```text
pip install pillow numpy
```

---

## How to Run

Run the GUI

```text
cd Project1
python level6_gui.py
```

---

## Project Structure

```text
Project1/
│
├── lzw_core.py
├── image_lzw_utils.py
├── basic_image_operations.py
├── image_tools.py
│
├── level1_text.py
├── level2_gray.py
├── level3_diff.py
├── level4_color.py
├── level5_color_diff.py
├── level6_gui.py
│
└── README.md
```
---

## Learning Outcomes

This project helped demonstrate:

- **how dictionary-based compression works**

- **how bit-packing affects compressed file size**

- **how image data can be transformed for compression**

- **how grayscale and RGB data differ in representation**

- **how preprocessing techniques such as difference coding affect redundancy**

- **how to build a GUI for testing and demonstrating algorithms**

---
