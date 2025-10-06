def decode_asn1_tlv(data, start=0, end=None):
    if end is None:
        end = len(data)

    i = start
    decoded = []

    while i < end:
        # --- Decode Tag ---
        first_tag_byte = data[i]
        i += 1

        tag_class = (first_tag_byte & 0b11000000) >> 6
        constructed = (first_tag_byte & 0b00100000) >> 5
        tag_number = first_tag_byte & 0b00011111

        # If tag_number == 31 (0x1F), extended tag number follows
        if tag_number == 0x1F:
            tag_number = 0
            while True:
                b = data[i]
                i += 1
                tag_number = (tag_number << 7) | (b & 0x7F)
                if not (b & 0x80):
                    break

        # --- Decode Length ---
        length_byte = data[i]
        i += 1

        if length_byte & 0x80 == 0:  # Short form
            length = length_byte & 0x7F
        else:  # Long form
            num_length_bytes = length_byte & 0x7F
            length = 0
            for _ in range(num_length_bytes):
                length = (length << 8) | data[i]
                i += 1

        # --- Extract Value ---
        value_start = i
        value_end = i + length
        value = data[value_start:value_end]
        i = value_end

        # --- Recursive decode if constructed ---
        if constructed:
            nested = decode_asn1_tlv(value, 0, len(value))
            decoded.append({
                'tag_class': tag_class,
                'constructed': True,
                'tag_number': tag_number,
                'length': length,
                'value': nested
            })
        else:
            decoded.append({
                'tag_class': tag_class,
                'constructed': False,
                'tag_number': tag_number,
                'length': length,
                'value': value
            })

    return decoded


# --- Example ASN.1 BER encoded data ---

# Example: Sequence (constructed tag 0x30), length 6
# Contains two INTEGERs: 0x02 0x01 0x01 (integer 1), 0x02 0x01 0x02 (integer 2)
example_data = bytes([
    0x30, 0x06,  # Sequence, length 6
    0x02, 0x01, 0x01,  # Integer 1
    0x02, 0x01, 0x02  # Integer 2
])

decoded = decode_asn1_tlv(example_data)

import pprint

pprint.pprint(decoded)
