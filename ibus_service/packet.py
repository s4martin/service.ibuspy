import time


class IBUSPacket(object):

    # instance variables
    source_id = None
    length = None
    destination_id = None
    data = None
    xor_checksum = None
    raw = None
    timestamp = None

    def __init__(self, source_id, length, destination_id, data, xor_checksum, raw=None):
        """
        Initializes packet object
        """
        self.source_id = source_id
        self.length = length
        self.destination_id = destination_id
        self.data = data
        self.xor_checksum = xor_checksum
        self.raw = raw
        self.timestamp = str(int(time.time() * 1000))
        return

    def as_dict(self):
        """
        Returns dict() representation of object
        """
        return dict(source_id=self.source_id,
                    length=self.length,
                    destination_id=self.destination_id,
                    data=self.data,
                    xor_checksum=self.xor_checksum,
                    raw=self.raw,
                    timestamp=self.timestamp)

    def is_valid(self):
        """
        Verifies packet information & XOR checksum
        """
        if self.source_id is None or self.destination_id is None \
                or self.data is None or self.xor_checksum is None:
            return False

        # XOR checksum calculation
        return self.xor_checksum == self.calculate_xor_checksum()

    def __str__(self):
        """
        Human-readable string representing packet data
        """
        return "IBUSPacket\nRaw = " + self.raw + "\n"\
               + "Source = " + self.get_device_name(self.source_id) + "\n"\
               + "Destination = " + self.get_device_name(self.destination_id) + "\n"\
               + "Data = " + self.data.decode("hex") + "\n"

    @staticmethod
    def get_device_name(device_id):
        """
        Returns device name for provided id
        i.e. 50 - MFL Multi Functional Steering Wheel Buttons
        """
        device_names = {
            "00": "GM Body module", # Was Broadcast
            "08": "Sunroof Control",
            "18": "CDW - CDC CD-Player",
            "30": "Check Control Module",
            "3b": "NAV Navigation/Video Module",
            "3f": "DIS",
            "40": "Remote control central locking",
            "43": "Menu Screen",
            "44": "Immobiliser",
            "50": "MFL Multi Functional Steering Wheel Buttons",
            "51": "Mirror memory",
            "5b": "Integrated heating and air conditioning",
            "60": "PDC Park Distance Control",
            "68": "RAD Radio",
            "6a": "DSP Digital Sound Processor",
            "72": "Seat memory",
            "73": "Sirius Radio",
            "76": "CD changer, DIN size",
            "7f": "GPS module",
            "80": "IKE Instrument Kombi Electronics",
            "9b": "Mirror memory",
            "9c": "Mirror memory",
            "a0": "Rear multi-info display",
            "a4": "Air bag module",
            "a8": "KAM",
            "ac": "ASP",
            "b0": "Speed recognition system",
            "bb": "TV Module",
            "bf": "Global, broadcast address", # "LCM Light Control Module",
            "c0": "MID Multi-Information Display Buttons",
            "c8": "TEL Telephone",
            "d0": "LCM Light Control Module", # "Navigation Location",
            "e7": "OBC Text Bar",
            "e8": "Rain/Light Sensor",
            "ed": "Lights, Wipers, Seat Memory",
            "f0": "BMB Board Monitor Buttons",
            "ff": "Broadcast",
        }
        try:
            return device_names[device_id]
        except KeyError:
            return "Unknown"

    def calculate_xor_checksum(self):
        """
        Calculates XOR value for packet
        """
        """
        b_source = IBUSPacket.hex_to_bin(self.source_id)
        b_length = IBUSPacket.hex_to_bin(self.length)
        b_destination = IBUSPacket.hex_to_bin(self.destination_id)
        b_data = IBUSPacket.hex_to_bin(self.data)
        """
        # TODO return calculated value
        return self.xor_checksum