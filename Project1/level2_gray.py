import os
import numpy as np
import basic_image_operations as bio
from lzw_core import LZWCoding
from image_lzw_utils import pack_codes_to_bytes, unpack_bytes_to_codes, write_header_and_payload, read_header_and_payloads
from collections import Counter
import math


def calculate_entropy(data):
    counter = Counter(data)
    total = len(data)
    entropy = 0

    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


def compress_gray_image(image_path, output_path=None):
    img = bio.read_image_file(image_path)
    gray = bio.color_image_to_grayscale(img)

    img_array = bio.image_to_numpy_array(gray)
    height, width = img_array.shape
    flat_pixels = bio.flatten_numpy_array(img_array).tolist()

    entropy = calculate_entropy(flat_pixels)
    print("Entropy:", entropy)

    lzw = LZWCoding("", "image")
    encoded = lzw.encode(flat_pixels)

    payload = pack_codes_to_bytes(encoded, lzw.codelength)

    if output_path is None:
        base = os.path.splitext(image_path)[0]
        output_path = base + "_L2_gray.lzw"

    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "":
        ext = "bmp"

    header = {
        "LEVEL": "2",
        "MODE": "L",
        "WIDTH": width,
        "HEIGHT": height,
        "EXT": ext,
        "PAYLOAD_LEN": len(payload)
    }

    write_header_and_payload(output_path, header, [payload])

    print("Width:", width)
    print("Height:", height)
    print("Encoded length:", len(encoded))
    print("Code length:", lzw.codelength)
    print("Compressed file saved:", output_path)

    compressed_bits = len(payload) * 8
    avg_code_length = compressed_bits / len(flat_pixels)

    return {
        "output_path": output_path,
        "entropy": round(entropy, 6),
        "avg_code_length": round(avg_code_length, 6),
        "encoded_length": len(encoded),
        "code_length": lzw.codelength
    }


def decompress_gray_image(input_path, output_path=None):
    header, payloads = read_header_and_payloads(input_path)

    width = int(header["WIDTH"])
    height = int(header["HEIGHT"])
    ext = header["EXT"]

    encoded, code_length = unpack_bytes_to_codes(payloads[0])

    lzw = LZWCoding("", "image")
    decoded_pixels = lzw.decode(encoded)

    img_array = np.array(decoded_pixels, dtype=np.uint8).reshape((height, width))
    img = bio.numpy_array_to_image(img_array)

    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + "_decompressed." + ext

    bio.write_image_file(img, output_path)

    print("Width:", width)
    print("Height:", height)
    print("Encoded length:", len(encoded))
    print("Code length:", code_length)
    print("Image reconstructed:", output_path)

    return output_path
