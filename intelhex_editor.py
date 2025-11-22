# Copyright (c) 2025 Alex Papdi
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Union, Dict

# Type alias for HEX-like input
HexLike = Union[str, int]

class IntelHexFile:
    def __init__(self):
        self.data: Dict[int, int] = {}
        self.start_address: Union[int, None] = None

    @staticmethod
    def parse_line(line: str):
        """
        Parses a single line from the Intel HEX file.
        Validates checksum and returns record type, address, and data bytes.

        :param line: Single line to parse
        """
        if not line.startswith(':'):
            raise ValueError("Invalid Intel HEX line")

        line = line[1:]
        byte_count = int(line[0:2], 16)
        address = int(line[2:6], 16)
        record_type = int(line[6:8], 16)
        data = bytes.fromhex(line[8:8 + byte_count * 2])
        checksum = int(line[8 + byte_count * 2:10 + byte_count * 2], 16)

        # Checksum validation
        total = byte_count + (address >> 8) + (address & 0xFF) + record_type + sum(data)
        computed_checksum = (-total) & 0xFF
        if computed_checksum != checksum:
            raise ValueError(f"Checksum mismatch: expected {checksum:02X}, got {computed_checksum:02X}")

        return record_type, address, data

    def load_file(self, filepath: str):
        """
        Loads and parses an Intel HEX file

        :param filepath: Path of the Intel HEX file
        """
        extended_address = 0
        first_data_address = None

        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                record_type, address, data = self.parse_line(line)

                if record_type == 0x00:  # Data record
                    full_address = extended_address | address
                    if first_data_address is None:
                        first_data_address = full_address
                    for i, byte in enumerate(data):
                        self.data[full_address + i] = byte

                elif record_type == 0x01:  # End of file
                    break

                elif record_type == 0x04:  # Extended Linear Address
                    extended_address = int.from_bytes(data, 'big') << 16

                elif record_type == 0x05:  # Start Linear Address
                    self.start_address = int.from_bytes(data, 'big')

        # Fallback to first data address if no explicit start address
        if self.start_address is None:
            self.start_address = first_data_address

    def read_memory(self, address: HexLike, length: HexLike = 1) -> str:
        """
        Reads a sequence of bytes from memory starting at the given address

        :param address: Memory address of the data to read
        :param length: Length of the data to read
        :return: Returns the read memory data
        """
        addr = int(address, 16) if isinstance(address, str) else address
        length = int(length, 16) if isinstance(length, str) else length
        return ''.join(f'{self.data.get(addr + i, 0xFF):02X}' for i in range(length))

    def write_memory(self, address: HexLike, data: HexLike):
        """
        Writes a sequence of bytes to memory at the given address

        :param address: Memory address of the data to overwrite
        :param data: Data to overwrite with
        """
        addr = int(address, 16) if isinstance(address, str) else address

        if isinstance(data, int):
            hex_str = f'{data:X}'
        elif isinstance(data, str):
            hex_str = data.lstrip('0x').upper()
        else:
            raise TypeError("Data must be str or int")

        # Convert hex string to byte list
        bytes_data = [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]
        for i, byte in enumerate(bytes_data):
            self.data[addr + i] = byte

    def save_file(self, filepath: str):
        """
        Saves the current memory map to an Intel HEX file.
        Writes data in 32-byte chunks with extended address records.

        :param filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as file:
            addresses = sorted(self.data.keys())
            current_ext_addr = None

            for base in range(addresses[0], addresses[-1] + 1, 32):
                chunk = [self.data.get(base + i, 0xFF) for i in range(32)]
                linear_addr = base >> 16

                # Write extended address record if needed
                if linear_addr != current_ext_addr:
                    current_ext_addr = linear_addr
                    high = current_ext_addr & 0xFFFF
                    checksum = (-2 - 4 - (high >> 8) - (high & 0xFF)) & 0xFF
                    file.write(f":02000004{high:04X}{checksum:02X}\n")

                # Write data record
                addr_field = f"{base & 0xFFFF:04X}"
                data_field = ''.join(f"{b:02X}" for b in chunk)
                byte_count = len(chunk)
                checksum = byte_count + (base >> 8) + (base & 0xFF) + 0x00 + sum(chunk)
                checksum = (-checksum) & 0xFF
                file.write(f":{byte_count:02X}{addr_field}00{data_field}{checksum:02X}\n")

            # Write end-of-file record
            file.write(":00000001FF\n")


@dataclass
class HexEditor:
    file: str

    def __post_init__(self):
        self.parser = IntelHexFile()
        self.parser.load_file(self.file)

    @property
    def start_address(self) -> str:
        """
        :return: Returns the start address of the Intel HEX file
        """
        return f'0x{self.parser.start_address:08X}'

    @property
    def length(self) -> int:
        """
        :return: Returns the total length of the memory block in bytes
        """
        if not self.parser.data:
            return 0
        addresses = self.parser.data.keys()
        return max(addresses) - min(addresses) + 1

    def read(self, address: HexLike, length: HexLike = 1) -> str:
        """
        Reads memory content from the given address

        :param address: Memory address of the data to read
        :param length: Length of the data to read
        :return: Returns the read memory data
        """
        return self.parser.read_memory(address, length)

    def write(self, address: HexLike, data: HexLike, output: str = None):
        """
        Writes data to memory and saves the result to a new HEX file

        :param address: Memory address of the data to overwrite
        :param data: Data to overwrite with
        :param output: Output file path
        """
        self.parser.write_memory(address, data)
        self.parser.save_file(output if output is not None else self.file)


if __name__ == '__main__':
    hex_parser = HexEditor('Sample.hex')

    print("Start address:", hex_parser.start_address)
    print("Length:", hex_parser.length)
    print("Read:", hex_parser.read('0x803000A0', 0x10))

    hex_parser.write(
        address='0x803000A0',
        data='B0C1F0C1B0C1C1CADEADBEEF1EE7FEE7',
        output='Sample_modified.hex'
    )
