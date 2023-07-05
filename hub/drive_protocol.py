class DriveProtocol:
    def __init__(self):
        self.byte_array = []

    def add_byte(self, byte_to_add):
        if len(self.byte_array) == 0 or len(self.byte_array) == 3:
            if byte_to_add != b"-" and byte_to_add != b"+" and byte_to_add != b"0":
                return False
        else:
            if byte_to_add < b"0" or byte_to_add > b"9":
                return False
        self.byte_array.append(byte_to_add)
        return True

    def get_bytes(self):
        return self.byte_array

    def clear(self):
        self.byte_array.clear()