import os
from lzw_core import LZWCoding


def pack_codes_to_bytes(encoded_codes, code_length):
    lzw = LZWCoding("", "text")
    lzw.codelength = code_length

    bit_string = lzw.int_list_to_binary_string(encoded_codes)
    bit_string = lzw.add_code_length_info(bit_string)
    padded = lzw.pad_encoded_data(bit_string)
    byte_array = lzw.get_byte_array(padded)

    return bytes(byte_array)


def unpack_bytes_to_codes(byte_data):
    lzw = LZWCoding("", "text")

    bit_string = ""
    for byte in byte_data:
        bit_string += bin(byte)[2:].rjust(8, "0")

    bit_string = lzw.remove_padding(bit_string)
    bit_string = lzw.extract_code_length_info(bit_string)
    encoded_codes = lzw.binary_string_to_int_list(bit_string)

    return encoded_codes, lzw.codelength


def write_header_and_payload(output_path, header_dict, payloads):
    with open(output_path, "wb") as f:
        for key, value in header_dict.items():
            line = f"{key}:{value}\n"
            f.write(line.encode("utf-8"))

        f.write(b"ENDHDR\n")

        for payload in payloads:
            f.write(payload)


def read_header_and_payloads(input_path):
    header = {}

    with open(input_path, "rb") as f:
        while True:
            line = f.readline()
            if not line:
                raise ValueError("Invalid compressed file: ENDHDR not found.")

            if line == b"ENDHDR\n":
                break

            line = line.decode("utf-8").strip()
            key, value = line.split(":", 1)
            header[key] = value

        payloads = []

        if "PAYLOAD_LEN" in header:
            length = int(header["PAYLOAD_LEN"])
            payloads.append(f.read(length))
        else:
            r_len = int(header["R_LEN"])
            g_len = int(header["G_LEN"])
            b_len = int(header["B_LEN"])

            payloads.append(f.read(r_len))
            payloads.append(f.read(g_len))
            payloads.append(f.read(b_len))

    return header, payloads
