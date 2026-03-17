from lzw_core import LZWCoding

def compress_text(filename):
    lzw = LZWCoding(filename, "text")
    return lzw.compress_text_file()

def decompress_text(filename):
    lzw = LZWCoding(filename, "text")
    return lzw.decompress_text_file()



#TEST
"""if __name__ == "__main__":

    test_text = "ABRACADABRA"

    from lzw_core import LZWCoding

    lzw = LZWCoding("temp", "text")

    encoded = lzw.encode(test_text)
    print("Encoded:", encoded)

    decoded = lzw.decode(encoded.copy())
    print("Decoded:", decoded)"""
