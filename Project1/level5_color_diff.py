import os
import math
from PIL import Image

from collections import Counter
from lzw_core import LZWCoding
from image_lzw_utils import (
    pack_codes_to_bytes,
    unpack_bytes_to_codes,
    write_header_and_payload,
    read_header_and_payloads
)


def calculate_entropy(data):
    counter = Counter(data)
    total = len(data)
    entropy = 0

    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


def compute_difference_image(pixels):
    diff = [pixels[0]]

    for i in range(1, len(pixels)):
        value = (pixels[i] - pixels[i - 1]) % 256
        diff.append(value)

    return diff


def reconstruct_from_difference(diff):
    pixels = [diff[0]]

    for i in range(1, len(diff)):
        value = (pixels[i - 1] + diff[i]) % 256
        pixels.append(value)

    return pixels


def compress_rgb_diff_image(image_path, output_path=None):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = list(img.getdata())

    r = [p[0] for p in pixels]
    g = [p[1] for p in pixels]
    b = [p[2] for p in pixels]

    dr = compute_difference_image(r)
    dg = compute_difference_image(g)
    db = compute_difference_image(b)

    entropy_r = calculate_entropy(dr)
    entropy_g = calculate_entropy(dg)
    entropy_b = calculate_entropy(db)

    print("Entropy diff R:", entropy_r)
    print("Entropy diff G:", entropy_g)
    print("Entropy diff B:", entropy_b)

    lzw_r = LZWCoding("", "image")
    enc_r = lzw_r.encode(dr)
    r_payload = pack_codes_to_bytes(enc_r, lzw_r.codelength)

    lzw_g = LZWCoding("", "image")
    enc_g = lzw_g.encode(dg)
    g_payload = pack_codes_to_bytes(enc_g, lzw_g.codelength)

    lzw_b = LZWCoding("", "image")
    enc_b = lzw_b.encode(db)
    b_payload = pack_codes_to_bytes(enc_b, lzw_b.codelength)

    if output_path is None:
        base = os.path.splitext(image_path)[0]
        output_path = base + "_L5_rgbdiff.lzw"

    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "":
        ext = "bmp"

    header = {
        "LEVEL": "5",
        "MODE": "RGB_DIFF",
        "WIDTH": width,
        "HEIGHT": height,
        "EXT": ext,
        "R_LEN": len(r_payload),
        "G_LEN": len(g_payload),
        "B_LEN": len(b_payload)
    }

    write_header_and_payload(output_path, header, [r_payload, g_payload, b_payload])

    print("Width:", width)
    print("Height:", height)
    print("Encoded length diff R:", len(enc_r), "Code length R:", lzw_r.codelength)
    print("Encoded length diff G:", len(enc_g), "Code length G:", lzw_g.codelength)
    print("Encoded length diff B:", len(enc_b), "Code length B:", lzw_b.codelength)
    print("Compressed file saved:", output_path)

    avg_r = (len(r_payload) * 8) / len(dr)
    avg_g = (len(g_payload) * 8) / len(dg)
    avg_b = (len(b_payload) * 8) / len(db)

    return {
        "output_path": output_path,
        "entropy": f"R={round(entropy_r, 6)}, G={round(entropy_g, 6)}, B={round(entropy_b, 6)}",
        "avg_code_length": f"R={round(avg_r, 6)}, G={round(avg_g, 6)}, B={round(avg_b, 6)}",
        "encoded_length": f"R={len(enc_r)}, G={len(enc_g)}, B={len(enc_b)}"
    }


def decompress_rgb_diff_image(input_path, output_path=None):
    header, payloads = read_header_and_payloads(input_path)

    width = int(header["WIDTH"])
    height = int(header["HEIGHT"])
    ext = header["EXT"]

    r_codes, r_codelen = unpack_bytes_to_codes(payloads[0])
    g_codes, g_codelen = unpack_bytes_to_codes(payloads[1])
    b_codes, b_codelen = unpack_bytes_to_codes(payloads[2])

    lzw = LZWCoding("", "image")
    dr = lzw.decode(r_codes)
    dg = lzw.decode(g_codes)
    db = lzw.decode(b_codes)

    r = reconstruct_from_difference(dr)
    g = reconstruct_from_difference(dg)
    b = reconstruct_from_difference(db)

    pixels = list(zip(r, g, b))

    img = Image.new("RGB", (width, height))
    img.putdata(pixels)

    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + "_decompressed." + ext

    img.save(output_path)

    print("Width:", width)
    print("Height:", height)
    print("Encoded length diff R:", len(r_codes), "Code length R:", r_codelen)
    print("Encoded length diff G:", len(g_codes), "Code length G:", g_codelen)
    print("Encoded length diff B:", len(b_codes), "Code length B:", b_codelen)
    print("Image reconstructed:", output_path)

    return output_path
