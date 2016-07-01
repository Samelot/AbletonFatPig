import os
import struct

import Live

LIVE_CHANNEL = 8
NOVO_OCTAVE_FILENAMES = [
    "NovationOctave1.syx",
    "NovationOctave2.syx",
    "NovationOctave3.syx",
    "NovationOctave4.syx",
]
PRODUCT_ID_BYTES = (0, 32, 41, 97)
SEND_UP_CC = 104
SYSEX_IDENTITY_REQUEST = (240, 126, 0, 6, 1, 247)
PREFIX_TEMPLATE_SYSEX = (240, 0, 32, 41, 2, 17, 119)
LIVE_TEMPLATE_SYSEX = PREFIX_TEMPLATE_SYSEX + (LIVE_CHANNEL, 247)

class FatPig(object):
    _octave_bytes = []
    _octave_idx = -1

    def __init__(self, c_instance):
        self._c_instance = c_instance
        self._device = None
        self._identified = False
        self._identity_request_sent = False
        c_instance.log_message("FatPig.FatPig#__init__[loading octave]")

        for idx in range(0, len(NOVO_OCTAVE_FILENAMES)):
            octave_filename = NOVO_OCTAVE_FILENAMES[idx]
            octave_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    octave_filename)
            octave_bytes = ()
            with open(octave_path, "rb") as octave_fp:
                byte_string = octave_fp.read(1)
                while byte_string != "":
                    octave_bytes = octave_bytes + struct.unpack('B', byte_string)
                    byte_string = octave_fp.read(1)
            self._octave_bytes.insert(idx, octave_bytes)

        c_instance.log_message("FatPig.FatPig#__init__[loading %d octaves]" % len(self._octave_bytes))
         

    def build_midi_map(self, midi_map_handle):
        self._c_instance.log_message("FatPig.FatPig#build_midi_map")
        Live.MidiMap.forward_midi_cc(self._c_instance.handle(),
                midi_map_handle, LIVE_CHANNEL, SEND_UP_CC)

    def can_lock_to_devices(self):
        self._c_instance.log_message("FatPig.FatPig#can_lock_to_devices")
        return True

    def connect_script_instances(self, instantiated_scripts):
        self._c_instance.log_message("FatPig.FatPig#connect_script_instances")

    def disconnect(self):
        self._c_instance.log_message("FatPig.FatPig#disconnect")

    def lock_to_device(self, device):
        self._c_instance.log_message("FatPig.FatPig#lock_to_device")
        self._device = device

    def port_settings_changed(self):
        self._c_instance.log_message("FatPig.FatPig#port_settings_changed")

    def receive_midi(self, midi_bytes):
        self._c_instance.log_message("FatPig.FatPig#receive_midi")
        if midi_bytes[3:5] == (6, 2): # Handle identity response
            self._c_instance.log_message("FatPig.FatPig#receive_midi[handle identity response]")
            product_id_bytes = midi_bytes[5:5 + len(PRODUCT_ID_BYTES)]
            if product_id_bytes == PRODUCT_ID_BYTES:
                self._c_instance.log_message("FatPig.FatPig#update_display[sending template request]")
                #self._c_instance.send_midi(LIVE_TEMPLATE_SYSEX)
        elif midi_bytes[:7] == PREFIX_TEMPLATE_SYSEX: # Handle template response
            self._c_instance.log_message("FatPig.FatPig#receive_midi[handle template response]")
            if midi_bytes[7] == LIVE_CHANNEL:
                self._c_instance.log_message("FatPig.FatPig#receive_midi[handle template response, on the live channel]")
            else:
                self._c_instance.log_message("FatPig.FatPig#receive_midi[handle template response, on channel %d]" % midi_bytes[7])
        elif midi_bytes[1:] == (SEND_UP_CC, 127):
            self._c_instance.log_message("FatPig.FatPig#receive_midi[raising octave]")
            if self._octave_idx < 0 or self._octave_idx >= len(self._octave_bytes) - 1:
                self._octave_idx = 0
            else:
                self._octave_idx = 1 + self._octave_idx
            self._c_instance.send_midi(self._octave_bytes[self._octave_idx])
        else:
            self._c_instance.log_message("FatPig.FatPig#receive_midi[handle bytes %s]" % ",".join(map(str,midi_bytes)))

    def refresh_state(self):
        self._c_instance.log_message("FatPig.FatPig#refresh_state")

    def restore_bank(self):
        self._c_instance.log_message("FatPig.FatPig#restore_bank")

    def suggest_input_port(self):
        self._c_instance.log_message("FatPig.FatPig#suggest_input_port")
        return None

    def suggest_map_mode(self, cc_no, channel):
        self._c_instance.log_message("FatPig.FatPig#suggest_map_mode")
        return -1

    def suggest_needs_takeover(self, cc_no, channel):
        self._c_instance.log_message("FatPig.FatPig#suggest_needs_takeover")
        return True

    def suggest_output_port(self):
        self._c_instance.log_message("FatPig.FatPig#suggest_output_port")
        return None

    def update_display(self):
        if not self._identity_request_sent:
            self._c_instance.log_message("FatPig.FatPig#update_display[sending identity request]")
            self._c_instance.send_midi(SYSEX_IDENTITY_REQUEST)
            self._identity_request_sent = True
