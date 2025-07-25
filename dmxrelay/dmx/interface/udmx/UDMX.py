# pyudmx.py - Anyma (and clones) uDMX interface module
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE file).  If not, see <http://www.gnu.org/licenses/>.
#
# This module is based on the Python uDMX utility written by Dave Hocker.
# See https://github.com/dhocker/udmx-pyusb for more on this good work.
#
# This module is based on the C++ uDMX utility written by Markus Baertschi.
# See https://github.com/markusb/uDMX-linux.git for more on this good work.
#
from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice
from typing import Union, List  # support type hinting

USB_AVAILABLE = False
try:
    import usb
    USB_AVAILABLE = True
except:
    USB_AVAILABLE = False

if USB_AVAILABLE:
    class UDMXDevice(IDMXDevice):

        def __init__(self):
            self._dev = None

        def initDevice(self, usb_vendor_id: int = 0x16c0, usb_product_id: int = 0x5dc,
                       usb_bus: int = None, usb_address: int = None, **kwargs) -> bool:
            super().initDevice(**kwargs)
            """
            Open the first device that matches the search criteria. Th default parameters
            are set up for the likely most common case of a single uDMX interface.
            However, for the case of multiple uDMX interfaces, you can use the
            bus and address paramters to further specifiy the uDMX interface
            to be opened.
            :param port: For Compatibility reasons, unused
            :param usb_vendor_id:
            :param usb_product_id:
            :param usb_bus: USB bus number 1-n
            :param usb_address: USB device address 1-n
            :return: Returns true if a device was opened. Otherwise, returns false.
            """
            args = {}
            if usb_vendor_id < 0:
                usb_vendor_id = 0x16c0
            if usb_product_id < 0:
                usb_product_id = 0x5dc

            if usb_vendor_id:
                args["idVendor"] = usb_vendor_id
            if usb_product_id:
                args["idProduct"] = usb_product_id
            if usb_bus and usb_bus >= 0:
                args["bus"] = usb_bus
            if usb_address and usb_address >= 0:
                args["address"] = usb_address
            # Find the uDMX interface
            self._dev = usb.core.find(**args)
            return self._dev is not None

        def _send_control_message(self, cmd: int, value_or_length: int = 1, channel: int = 1,
                                  data_or_length: Union[int, bytearray] = 1) -> int:
            """
            Sends a control transfer to the current device.
            :param cmd: 1 for single value transfer, 2 for multi-value transfer
            :param value_or_length: for single value transfer, the value. For multi-value transfer,
                the length of the data bytearray.
            :param channel: DMX channel number, 1- 512
            :param data_or_length: for a single value transfer it should be 1.
                For a multi-value transfer, a bytearray containing the values.
            :return: number of bytes sent.
            """

            if self._dev is None:
                raise ValueError("No usb device opened")

            # All data transfers use this request type. This is more for
            # the PyUSB package than for the uDMX as the uDMX does not
            # use it..
            bmRequestType = usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE | usb.util.CTRL_OUT

            """
            usb request for SetSingleChannel:
                Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
                Request:        1
                Value:          value to set [0 .. 255]
                Index:          channel index to set [0 .. 511], not the human known value of 1-512
                Length:         ignored, but returned as the number of byte values transfered
            usb request for SetMultiChannel:
                Request Type:   ignored by device, should be USB_TYPE_VENDOR | USB_RECIP_DEVICE | USB_ENDPOINT_OUT
                Request:        2
                Value:          number of channels to set [1 .. 512-wIndex]
                Index:          index of first channel to set [0 .. 511], not the human known value of 1-512
                Data:           iterable object containing values (we use a bytearray)
            """

            n = self._dev.ctrl_transfer(bmRequestType, cmd, wValue=value_or_length, wIndex=channel - 1,
                                        data_or_wLength=data_or_length)

            # For a single value transfer the return value is the data_or_length value.
            # For a multi-value transfer the return value is the number of values transfer
            # which should be the number of values in the data_or_length bytearray.
            return n

        def send_single_value(self, channel: int, value: int) -> int:
            """
            Send a single value to the uDMX
            :param channel: DMX channel number, 1-512
            :param value: Value to be sent to channel, 0-255
            :return: number of bytes actually sent
            """
            SetSingleChannel = 1
            n = self._send_control_message(SetSingleChannel, value_or_length=value, channel=channel, data_or_length=1)
            return n

        def send_multi_value(self, channel: int, values: Union[List[int], bytearray]) -> int:
            """
            Send multiple consecutive bytes to the uDMX
            :param channel: The starting DMX channel number, 1-512
            :param values: any sequence of integer values that can be converted
            to a bytearray (e.g a list). Each value 0-255.
            :return: number of bytes actually sent
            """
            SetMultiChannel = 2
            if isinstance(values, bytearray):
                ba = values
            else:
                ba = bytearray(values)
            n = self._send_control_message(SetMultiChannel, value_or_length=len(ba),
                                           channel=channel, data_or_length=ba)
            return n

        def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
            self.send_multi_value(1, data)

        def closeDevice(self):
            """
            Close and release the current usb device.
            :return: None
            """
            # This may not be absolutely necessary, but it is safe.
            # It's the closest thing to a close() method.
            if self._dev is not None:
                usb.util.dispose_resources(self._dev)
                self._dev = None