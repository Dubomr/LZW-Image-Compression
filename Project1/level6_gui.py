import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PIL import Image, ImageTk
import numpy as np

from lzw_core import LZWCoding

from level2_gray import compress_gray_image, decompress_gray_image
from level3_diff import compress_gray_diff_image, decompress_gray_diff_image
from level4_color import compress_rgb_image, decompress_rgb_image
from level5_color_diff import compress_rgb_diff_image, decompress_rgb_diff_image


# ------------------------ Helpers ------------------------

def human_bytes(n):
    if n is None:
        return "-"
    n = float(n)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def file_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return None


def compare_text_files(path_a, path_b):
    with open(path_a, "rb") as fa, open(path_b, "rb") as fb:
        return fa.read() == fb.read()


def compare_image_files(path_a, path_b):
    img_a = Image.open(path_a)
    img_b = Image.open(path_b)

    arr_a = np.array(img_a)
    arr_b = np.array(img_b)

    return arr_a.shape == arr_b.shape and np.array_equal(arr_a, arr_b)


# ------------------------ Level 1 path-based helpers ------------------------

def level1_compress_path(txt_path, out_bin_path):
    with open(txt_path, "rb") as f:
        raw = f.read()

    text = raw.decode("utf-8", errors="replace")

    lzw = LZWCoding("", "text")

    encoded_ints = lzw.encode(text)
    bitstring = lzw.int_list_to_binary_string(encoded_ints)
    bitstring = lzw.add_code_length_info(bitstring)
    padded = lzw.pad_encoded_data(bitstring)
    byte_array = lzw.get_byte_array(padded)

    with open(out_bin_path, "wb") as f:
        f.write(bytes(byte_array))


def level1_decompress_path(bin_path, out_txt_path):
    lzw = LZWCoding("", "text")

    with open(bin_path, "rb") as f:
        data = f.read()

    bits = []
    for b in data:
        bits.append(bin(b)[2:].rjust(8, "0"))
    bit_string = "".join(bits)

    bit_string = lzw.remove_padding(bit_string)
    bit_string = lzw.extract_code_length_info(bit_string)
    encoded_ints = lzw.binary_string_to_int_list(bit_string)

    decoded_text = lzw.decode(encoded_ints)

    with open(out_txt_path, "wb") as f:
        f.write(decoded_text.encode("utf-8", errors="replace"))


# ------------------------ GUI ------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("COMP204 Project 1 - LZW GUI (Levels 1-5)")
        self.geometry("1260x800")

        self.selected_file = tk.StringVar(value="")
        self.selected_output = tk.StringVar(value="")
        self.original_file_for_compare = tk.StringVar(value="")

        self.level_var = tk.StringVar(value="2")
        self.op_var = tk.StringVar(value="compress")

        self.original_size_var = tk.StringVar(value="-")
        self.compressed_size_var = tk.StringVar(value="-")
        self.decompressed_size_var = tk.StringVar(value="-")
        self.delta_var = tk.StringVar(value="-")
        self.equal_var = tk.StringVar(value="-")
        self.entropy_var = tk.StringVar(value="-")
        self.avg_code_length_var = tk.StringVar(value="-")
        self.difference_var = tk.StringVar(value="-")

        self._preview_imgtk = None
        self.preview_path = None

        self.last_original_path = None
        self.last_compressed_path = None
        self.last_decompressed_path = None

        self._build_ui()
        self._update_suggested_output()

    # ---------------- UI ----------------

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Input file:").pack(side="left")
        ttk.Entry(top, textvariable=self.selected_file, width=78).pack(side="left", padx=8)
        ttk.Button(top, text="Browse...", command=self.browse_file).pack(side="left")
        ttk.Button(top, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=8)

        compare_frame = ttk.Frame(self, padding=10)
        compare_frame.pack(fill="x")

        ttk.Label(compare_frame, text="Original file (for comparison):").pack(side="left")
        ttk.Entry(compare_frame, textvariable=self.original_file_for_compare, width=62).pack(side="left", padx=8)
        ttk.Button(compare_frame, text="Browse Original...", command=self.browse_original_file).pack(side="left")

        mid = ttk.Frame(self, padding=10)
        mid.pack(fill="x")

        ttk.Label(mid, text="Level:").pack(side="left")
        level_cb = ttk.Combobox(
            mid,
            textvariable=self.level_var,
            width=5,
            state="readonly",
            values=["1", "2", "3", "4", "5"]
        )
        level_cb.pack(side="left", padx=8)
        level_cb.bind("<<ComboboxSelected>>", lambda e: self._update_suggested_output())

        ttk.Label(mid, text="Operation:").pack(side="left")
        op_cb = ttk.Combobox(
            mid,
            textvariable=self.op_var,
            width=12,
            state="readonly",
            values=["compress", "decompress"]
        )
        op_cb.pack(side="left", padx=8)
        op_cb.bind("<<ComboboxSelected>>", lambda e: self._update_suggested_output())

        ttk.Button(mid, text="Choose Output...", command=self.choose_output).pack(side="left", padx=8)
        ttk.Label(mid, text="Output:").pack(side="left", padx=(10, 0))
        ttk.Entry(mid, textvariable=self.selected_output, width=52).pack(side="left", padx=8)

        ttk.Button(mid, text="Run", command=self.run_clicked).pack(side="left", padx=8)
        ttk.Button(mid, text="Clear Log", command=self.clear_log).pack(side="left")

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # Log frame
        log_frame = ttk.Labelframe(main, text="Log", padding=8)
        log_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.log_text = tk.Text(log_frame, height=24, wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # Right panel
        right = ttk.Frame(main)
        right.pack(side="left", fill="y")

        prev_frame = ttk.Labelframe(right, text="Output Preview", padding=8)
        prev_frame.pack(fill="both")

        self.preview_label = ttk.Label(prev_frame, text="No image yet.", width=45)
        self.preview_label.pack()

        ttk.Button(prev_frame, text="Refresh Preview", command=self.refresh_preview).pack(pady=8)

        stats = ttk.Labelframe(right, text="Run Summary", padding=8)
        stats.pack(fill="x", pady=(10, 0))

        def row(label, var):
            r = ttk.Frame(stats)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=label, width=22).pack(side="left")
            ttk.Label(r, textvariable=var, wraplength=340, justify="left").pack(side="left")

        row("Original size:", self.original_size_var)
        row("Compressed size:", self.compressed_size_var)
        row("Decompressed size:", self.decompressed_size_var)
        row("Size differences:", self.delta_var)
        row("Original == Decomp?:", self.equal_var)
        row("Entropy:", self.entropy_var)
        row("Average code length:", self.avg_code_length_var)
        row("Difference:", self.difference_var)

        notes = (
            "Notes:\n"
            "- Level 1 expects a .txt input.\n"
            "- Levels 2-5 expect an image input for compress, and a .lzw for decompress.\n"
            "- Use 'Original file (for comparison)' for correct equality checking after decompress.\n"
            "- Level 2/3 convert images to grayscale, so equality with a color original may be NO.\n"
            "- Level 4/5 should reconstruct the original color BMP exactly.\n"
            "- Use 'Choose Output...' to save where you want.\n"
        )
        ttk.Label(right, text=notes, justify="left").pack(anchor="w", pady=10)

        self._log("GUI ready. Choose input, level, operation, output path, then Run.")

    # ---------------- Logging ----------------

    def _log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.delete("1.0", "end")

    # ---------------- File Browsing ----------------

    def browse_file(self):
        filetypes = [
            ("All supported", "*.txt *.png *.jpg *.jpeg *.bmp *.lzw *.bin"),
            ("Text files", "*.txt"),
            ("Images", "*.png *.jpg *.jpeg *.bmp"),
            ("Compressed files", "*.lzw *.bin"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if path:
            self.selected_file.set(path)
            self._log(f"Selected input: {path}")
            self._update_suggested_output()

    def browse_original_file(self):
        filetypes = [
            ("All supported", "*.txt *.png *.jpg *.jpeg *.bmp"),
            ("Text files", "*.txt"),
            ("Images", "*.png *.jpg *.jpeg *.bmp"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Select original file for comparison", filetypes=filetypes)
        if path:
            self.original_file_for_compare.set(path)
            self._log(f"Selected original for comparison: {path}")

    def open_output_folder(self):
        folder = os.path.dirname(self.selected_output.get().strip()) or os.getcwd()
        try:
            os.startfile(folder)
        except Exception:
            messagebox.showinfo("Output folder", folder)

    # ---------------- Output Suggestion ----------------

    def _update_suggested_output(self):
        in_path = self.selected_file.get().strip()
        level = self.level_var.get().strip()
        op = self.op_var.get().strip()

        if not in_path:
            self.selected_output.set("")
            return

        in_dir = os.path.dirname(in_path)
        base, ext = os.path.splitext(os.path.basename(in_path))

        if level == "1":
            if op == "compress":
                out = os.path.join(in_dir, f"{base}_compressed.bin")
            else:
                out = os.path.join(in_dir, f"{base}_decompressed.txt")

        elif level == "2":
            if op == "compress":
                out = os.path.join(in_dir, f"{base}_L2_gray.lzw")
            else:
                out = os.path.join(in_dir, f"{base}_L2_gray_decompressed.bmp")

        elif level == "3":
            if op == "compress":
                out = os.path.join(in_dir, f"{base}_L3_graydiff.lzw")
            else:
                out = os.path.join(in_dir, f"{base}_L3_graydiff_decompressed.bmp")

        elif level == "4":
            if op == "compress":
                out = os.path.join(in_dir, f"{base}_L4_rgb.lzw")
            else:
                out = os.path.join(in_dir, f"{base}_L4_rgb_decompressed.bmp")

        elif level == "5":
            if op == "compress":
                out = os.path.join(in_dir, f"{base}_L5_rgbdiff.lzw")
            else:
                out = os.path.join(in_dir, f"{base}_L5_rgbdiff_decompressed.bmp")

        else:
            out = os.path.join(in_dir, f"{base}_output")

        self.selected_output.set(out)

    def choose_output(self):
        in_path = self.selected_file.get().strip()
        if not in_path:
            messagebox.showwarning("No input", "Please select an input file first.")
            return

        level = self.level_var.get().strip()
        op = self.op_var.get().strip()
        suggested = self.selected_output.get().strip()

        if level == "1":
            if op == "compress":
                defext, ft = ".bin", [("BIN files", "*.bin"), ("All files", "*.*")]
            else:
                defext, ft = ".txt", [("Text files", "*.txt"), ("All files", "*.*")]
        else:
            if op == "compress":
                defext, ft = ".lzw", [("LZW files", "*.lzw"), ("All files", "*.*")]
            else:
                defext, ft = ".bmp", [("BMP files", "*.bmp"), ("PNG files", "*.png"), ("All files", "*.*")]

        path = filedialog.asksaveasfilename(
            title="Choose output file",
            initialfile=os.path.basename(suggested),
            initialdir=os.path.dirname(suggested),
            defaultextension=defext,
            filetypes=ft
        )

        if path:
            self.selected_output.set(path)
            self._log(f"Selected output: {path}")

    # ---------------- Run ----------------

    def run_clicked(self):
        in_path = self.selected_file.get().strip()
        out_path = self.selected_output.get().strip()

        if not in_path:
            messagebox.showwarning("No input", "Please select an input file.")
            return

        if not out_path:
            messagebox.showwarning("No output", "Please choose an output file.")
            return

        level = self.level_var.get().strip()
        op = self.op_var.get().strip()

        t = threading.Thread(target=self._run_task, args=(level, op, in_path, out_path), daemon=True)
        t.start()

    def _run_task(self, level, op, in_path, out_path):
        try:
            self._log(f"\n--- RUN --- Level {level} | {op}")
            self._log(f"Input:  {in_path}")
            self._log(f"Output: {out_path}")

            compare_original = self.original_file_for_compare.get().strip()

            if op == "compress":
                self.last_original_path = in_path
            elif compare_original:
                self.last_original_path = compare_original

            self.last_compressed_path = None
            self.last_decompressed_path = None
            self.preview_path = None

            self.entropy_var.set("-")
            self.avg_code_length_var.set("-")
            self.difference_var.set("-")

            # ---------------- Level 1 ----------------
            if level == "1":
                if op == "compress":
                    if not in_path.lower().endswith(".txt"):
                        raise ValueError("Level 1 compress expects a .txt file.")
                    level1_compress_path(in_path, out_path)
                    self.last_compressed_path = out_path
                    self._log("Level1 compression done.")
                else:
                    if not (in_path.lower().endswith(".bin") or in_path.lower().endswith(".lzw")):
                        raise ValueError("Level 1 decompress expects a .bin file.")
                    level1_decompress_path(in_path, out_path)
                    self.last_decompressed_path = out_path
                    self._log("Level1 decompression done.")

            # ---------------- Level 2 ----------------
            elif level == "2":
                if op == "compress":
                    result = compress_gray_image(in_path, out_path)
                    self.last_compressed_path = result["output_path"]
                    self.entropy_var.set(str(result["entropy"]))
                    self.avg_code_length_var.set(str(result["avg_code_length"]))
                    self._log("Level2 compression done.")
                else:
                    produced_img = decompress_gray_image(in_path, out_path)
                    self.last_decompressed_path = produced_img
                    self.preview_path = produced_img
                    self._log("Level2 decompression done.")

            # ---------------- Level 3 ----------------
            elif level == "3":
                if op == "compress":
                    result = compress_gray_diff_image(in_path, out_path)
                    self.last_compressed_path = result["output_path"]
                    self.entropy_var.set(str(result["entropy"]))
                    self.avg_code_length_var.set(str(result["avg_code_length"]))
                    self._log("Level3 compression done.")
                else:
                    produced_img = decompress_gray_diff_image(in_path, out_path)
                    self.last_decompressed_path = produced_img
                    self.preview_path = produced_img
                    self._log("Level3 decompression done.")

            # ---------------- Level 4 ----------------
            elif level == "4":
                if op == "compress":
                    result = compress_rgb_image(in_path, out_path)
                    self.last_compressed_path = result["output_path"]
                    self.entropy_var.set(str(result["entropy"]))
                    self.avg_code_length_var.set(str(result["avg_code_length"]))
                    self._log("Level4 compression done.")
                else:
                    produced_img = decompress_rgb_image(in_path, out_path)
                    self.last_decompressed_path = produced_img
                    self.preview_path = produced_img
                    self._log("Level4 decompression done.")

            # ---------------- Level 5 ----------------
            elif level == "5":
                if op == "compress":
                    result = compress_rgb_diff_image(in_path, out_path)
                    self.last_compressed_path = result["output_path"]
                    self.entropy_var.set(str(result["entropy"]))
                    self.avg_code_length_var.set(str(result["avg_code_length"]))
                    self._log("Level5 compression done.")
                else:
                    produced_img = decompress_rgb_diff_image(in_path, out_path)
                    self.last_decompressed_path = produced_img
                    self.preview_path = produced_img
                    self._log("Level5 decompression done.")

            else:
                raise ValueError("Invalid level selected.")

            # ---------------- Summary ----------------
            orig_path = self.last_original_path
            orig_sz = file_size(orig_path) if orig_path else None
            comp_sz = file_size(self.last_compressed_path) if self.last_compressed_path else None
            decomp_sz = file_size(self.last_decompressed_path) if self.last_decompressed_path else None

            self.original_size_var.set(human_bytes(orig_sz))
            self.compressed_size_var.set(human_bytes(comp_sz) if comp_sz is not None else "-")
            self.decompressed_size_var.set(human_bytes(decomp_sz) if decomp_sz is not None else "-")

            diffs = []
            if orig_sz is not None and comp_sz is not None:
                diffs.append(f"Orig→Comp: {human_bytes(orig_sz)} → {human_bytes(comp_sz)}")
            if orig_sz is not None and decomp_sz is not None:
                diffs.append(f"Orig→Decomp: {human_bytes(orig_sz)} → {human_bytes(decomp_sz)}")
            self.delta_var.set(" | ".join(diffs) if diffs else "-")

            if orig_sz is not None and comp_sz is not None:
                diff_value = orig_sz - comp_sz
                self.difference_var.set(
                    f"{human_bytes(orig_sz)} - {human_bytes(comp_sz)} = {human_bytes(diff_value)}"
                )
            else:
                self.difference_var.set("-")

            eq = "-"
            if orig_path and self.last_decompressed_path:
                try:
                    if level == "1":
                        eq = "YES" if compare_text_files(orig_path, self.last_decompressed_path) else "NO"
                    else:
                        eq = "YES" if compare_image_files(orig_path, self.last_decompressed_path) else "NO"
                except Exception as e:
                    eq = f"N/A ({e})"

            self.equal_var.set(eq)

            self._log("--- DONE ---")
            self.after(0, self.refresh_preview)

        except Exception as e:
            self._log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))

    # ---------------- Preview ----------------

    def refresh_preview(self):
        if not self.preview_path or not os.path.exists(self.preview_path):
            self.preview_label.configure(text="No image to preview.")
            self._preview_imgtk = None
            return

        try:
            img = Image.open(self.preview_path)
            img.thumbnail((450, 450))
            imgtk = ImageTk.PhotoImage(img)
            self._preview_imgtk = imgtk
            self.preview_label.configure(image=imgtk, text="")
            self._log(f"Preview loaded: {self.preview_path}")
        except Exception as e:
            self.preview_label.configure(text=f"Failed to preview image.\n{e}")
            self._preview_imgtk = None


if __name__ == "__main__":
    app = App()
    app.mainloop()
