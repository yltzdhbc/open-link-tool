# -*-coding:utf-8-*-
# Copyright (c) 2022 DJI.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib_open_protocol.open_protocol import OpenProto
from ctypes import *
import hashlib
# import dji_crc
import lib_open_protocol.dji_crc as dji_crc
import time
import logging
import math
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, pyqtSlot, QObject

SEND_PACKET_SIZE = 256


def printProgress(iteration, total, prefix="", suffix="", decimals=1, barLength=100):
    import sys

    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = "#" * filledLength + "-" * (barLength - filledLength)
    sys.stdout.write("\r%s |%s| %s%s %s" % (prefix, bar, percent, "%", suffix)),
    if iteration == total:
        sys.stdout.write("\n")
    sys.stdout.flush()


class OpenProtoDataFields(LittleEndianStructure):
    def encode(self):
        return string_at(addressof(self), sizeof(self))

    def decode(self, data):
        data = bytes(data)
        memmove(addressof(self), bytes(data), sizeof(self))
        return len(data)

    @staticmethod
    def to_c_array(data, array_len):
        data = bytes(data)
        return (c_ubyte * array_len)(*bytearray(data))


class CommResponFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [
        ("error", c_uint8),
    ]

    @staticmethod
    def get_rsp_error(data):
        fields = CommResponFields()
        fields.decode(data)
        return fields.error


class QueryVerFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [("loader_ver", c_uint32), ("app_ver", c_uint32), ("hw_id", c_char * 16), ("sn", c_char * 16)]

    CMD = 0x0002


class EnterLoaderFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [
        ("encrypt", c_uint8),
        ("sn_crc16", c_uint32),
    ]
    CMD = 0x00021


class UpgradeInfoFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [
        ("encrypt", c_uint8),
        ("fw_size", c_uint32),
        ("sn_crc16", c_uint16),
        ("hw_id", c_uint8 * 16),
        ("erase_bytes", c_uint32),
    ]
    CMD = 0x00022


class UpgradeDataFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [
        ("encrypt", c_uint8),
        ("pack_idx", c_uint32),
        ("pack_size", c_uint16),
        ("sn_crc16", c_uint16),
        ("m_data", c_uint8 * SEND_PACKET_SIZE),
    ]
    CMD = 0x00023


class UpgradeEndFields(OpenProtoDataFields):
    _pack_ = 1
    _fields_ = [
        ("encrypt", c_uint8),
        ("md5", c_uint8 * 16),
        ("sn_crc16", c_uint16),
    ]
    CMD = 0x00024


class ModuleInfoStruct:
    def __init__(self, loader_ver=0, app_ver=0, hw_id=0, sn="", addr=0):
        self.loader_ver = loader_ver
        self.app_ver = app_ver
        self.hw_id = hw_id
        self.sn = sn
        self.addr = addr
        self.sn_crc16 = OpenProto.CRC16_INIT
        for ch in sn:
            if ch == "\0":
                break
            self.sn_crc16 = dji_crc.get_crc16_check(bytes([ch]), self.sn_crc16)


update_time_1 = 0
update_time_2 = 0


class Upgrade(QObject):
    upgrade_progress_signal = pyqtSignal(float)
    set_str_signal = pyqtSignal(int, str)
    download_info_signal = pyqtSignal(str)

    def __init__(self, proto: OpenProto, logging):
        super().__init__()
        self.proto = proto
        self.firmware = None
        self.erase_num = 0

        self.download_progress = 0
        self.upgrade_step = 0
        self.upgrade_error_str = None

        self.logging = logging

    def query_ver(self):
        global update_time_1
        update_time_1 = time.time()

        self.proto.open()
        ret_packs = self.proto.send_and_recv_ack_pack(0xFFFF, QueryVerFields.CMD, None, True, dst_only_one=False)
        self.proto.close()

        self.logging.debug("Upgrade: Query version start")

        module_list = []
        for pack in ret_packs:
            if pack["cmd"] == QueryVerFields.CMD:
                fields = QueryVerFields()
                fields.decode(pack["data"])

                # sn_crc16 = OpenProto.CRC16_INIT
                # for ch in fields.sn:
                #     if ch == '\0':
                #         break
                #     sn_crc16 = dji_crc.get_crc16_check(bytes([ch]), sn_crc16)

                module = ModuleInfoStruct(fields.loader_ver, fields.app_ver, fields.hw_id, fields.sn, pack["src"])
                module_list.append(module)
                self.logging.debug(
                    "Upgrade: Module Addr:0x%04x, APP:0x%08x, BL:0x%08x, HW_ID:%s, SN:%s"
                    % (module.addr, module.app_ver, module.loader_ver, module.hw_id, module.sn)
                )

        self.logging.debug("Upgrade: Query version end")
        return module_list

    def load_firmware(self, path):
        try:
            f = open(path, "rb")
            self.firmware = f.read()
            f.close()
            return True
        except Exception as e:
            self.logging.debug(e)
            return False

    def download(self, module: ModuleInfoStruct):
        self.logging.debug("Upgrade: start the upgrade")

        if self.firmware is None:
            self.logging.debug("Upgrade: Upgrade failed, firmware not loaded")
            return [False, 0]

        # Step1:进入Loader
        self.download_info_signal.emit("进Loader")
        self.logging.debug("Upgrade: Step1!!! reset to loader")
        self.upgrade_step = 1
        send_fields = EnterLoaderFields(0, module.sn_crc16)
        self.proto.open()
        # self.proto.send_pack(module.addr, EnterLoaderFields.CMD, send_fields.encode(), False)

        # self.proto.close()
        # # 等待3秒让APP切换到Loader，然后再发送一遍指令
        # time.sleep(1)
        # self.proto.open()

        ret_packs = self.proto.send_and_recv_ack_pack(
            module.addr, EnterLoaderFields.CMD, send_fields.encode(), wait_time=0.5, retry=3
        )

        if len(ret_packs) == 0:
            self.logging.debug("Upgrade: The upgrade fails, and there is no response to the Loader command.")
            self.upgrade_error_str = "The upgrade fails, and there is no response to the Loader command."
            self.proto.close()
            return [False, 0]
        ret_err = CommResponFields.get_rsp_error(ret_packs[0]["data"])
        if ret_err != 0:
            self.logging.debug("Upgrade: Upgrade failed, enter Loa der error:0x%02x." % ret_err)
            self.upgrade_error_str = "Upgrade failed, enter Loader error:0x%02x." % ret_err
            self.proto.close()
            return [False, ret_err]

        self.logging.debug("Upgrade: enter Loader success")

        # 等待APP切换到Loader
        time.sleep(2)
        self.download_info_signal.emit("发送信息")

        # Step2:发送待升级的固件信息
        self.erase_num = len(self.firmware)

        self.logging.debug("Upgrade: Step2!!! send firmware info")
        self.logging.debug("Upgrade: Flash erase size:%d(%.2fk)" % (self.erase_num, self.erase_num / 1024))
        self.upgrade_step = 2
        t1 = time.time()
        send_fields = UpgradeInfoFields(
            0, len(self.firmware), module.sn_crc16, OpenProtoDataFields.to_c_array(module.hw_id, 16), self.erase_num
        )
        ret_packs = self.proto.send_and_recv_ack_pack(
            module.addr, UpgradeInfoFields.CMD, send_fields.encode(), wait_time=5, retry=5
        )
        t2 = time.time()

        if len(ret_packs) == 0:
            self.logging.debug("Upgrade: Upgrade failed, no response to sending firmware information.")
            self.upgrade_error_str = "Upgrade failed, no response to sending firmware information."
            self.proto.close()
            return [False, ret_err]
        ret_err = CommResponFields.get_rsp_error(ret_packs[0]["data"])
        if ret_err != 0:
            self.logging.debug("Upgrade: Failed to upgrade, failed to send firmware information:0x%02x." % ret_err)
            self.upgrade_error_str = "Failed to upgrade, failed to send firmware information:0x%02x." % ret_err
            self.proto.close()
            return [False, ret_err]

        self.logging.debug("Upgrade: Send firmware information successfully, Flash erase time:%.4fs" % (t2 - t1))

        # return 0
        self.download_info_signal.emit("发送固件")
        # Step3: 传输固件数据
        self.upgrade_step = 3
        fw_ptr = 0
        fw_pack_idx = 0
        packet_num = math.ceil(len(self.firmware) / SEND_PACKET_SIZE)
        self.logging.debug(
            "Upgrade: send firmware data start, firmware size:%d(%.2fk), packet size:%d(%.2fk), packet num:%d"
            % (len(self.firmware), len(self.firmware) / 1024, SEND_PACKET_SIZE, (SEND_PACKET_SIZE / 1024), packet_num)
        )
        download_cnt = 0
        while fw_ptr < len(self.firmware):
            if len(self.firmware) - fw_ptr >= SEND_PACKET_SIZE:
                fw_pack = self.firmware[fw_ptr : fw_ptr + SEND_PACKET_SIZE]
                fw_pack_size = SEND_PACKET_SIZE
                fw_ptr += SEND_PACKET_SIZE
            else:
                fw_pack = self.firmware[fw_ptr:]
                fw_pack_size = len(self.firmware) - fw_ptr
                fw_pack += bytes([0] * (SEND_PACKET_SIZE - fw_pack_size))
                fw_ptr += fw_pack_size

            send_fields = UpgradeDataFields(
                0, fw_pack_idx, fw_pack_size, module.sn_crc16, OpenProtoDataFields.to_c_array(fw_pack, SEND_PACKET_SIZE)
            )
            ret_packs = self.proto.send_and_recv_ack_pack(
                module.addr, UpgradeDataFields.CMD, send_fields.encode(), wait_time=0.1, retry=5
            )
            if len(ret_packs) == 0:
                self.logging.debug("Upgrade: Upgrade failed, no response to sending firmware data.")
                self.upgrade_error_str = "Upgrade failed, no response to sending firmware data."
                self.proto.close()
                return [False, ret_err]
            ret_err = CommResponFields.get_rsp_error(ret_packs[0]["data"])
            if ret_err != 0:
                self.logging.debug("Upgrade: Failed to upgrade, failed to send firmware data:0x%02x." % ret_err)
                self.upgrade_error_str = "Failed to upgrade, failed to send firmware data:0x%02x." % ret_err
                self.proto.close()
                return [False, ret_err]
            fw_pack_idx += 1
            # self.download_progress = float(fw_ptr)/len(self.firmware)
            # self.logging.debug('Upgrade: Send firmware data successfully, idx:%d (%3.1f%%)' % (fw_pack_idx, 100 * float(fw_ptr)/len(self.firmware)))
            # self.logging.debug('Send idx:%d (%3.1f%%)' % (fw_pack_idx, 100 * float(fw_ptr)/len(self.firmware)))
            download_cnt += 1
            # printProgress(download_cnt, packet_num,
            #               prefix='Upgrade:', suffix=' ', barLength=50)
            self.upgrade_progress_signal.emit(float(download_cnt / packet_num))

        self.download_info_signal.emit("固件发送完成")
        # Step4: 发送传输完成
        self.upgrade_step = 4
        firmware_md5 = hashlib.md5(self.firmware).digest()
        send_fields = UpgradeEndFields(0, OpenProtoDataFields.to_c_array(firmware_md5, 16), module.sn_crc16)
        ret_packs = self.proto.send_and_recv_ack_pack(
            module.addr, UpgradeEndFields.CMD, send_fields.encode(), wait_time=2.0, retry=3
        )
        if len(ret_packs) == 0:
            self.logging.debug(
                "Upgrade: The upgrade failed, no response was sent to the firmware transfer completion command."
            )
            self.upgrade_error_str = (
                "The upgrade failed, no response was sent to the firmware transfer completion command."
            )
            self.proto.close()
            return [False, ret_err]
        ret_err = CommResponFields.get_rsp_error(ret_packs[0]["data"])
        if ret_err != 0:
            self.logging.debug(
                "Upgrade: Upgrade failed, failed to send firmware transfer completion command:0x%02x." % ret_err
            )
            self.upgrade_error_str = (
                "Upgrade failed, failed to send firmware transfer completion command:0x%02x." % ret_err
            )
            self.proto.close()
            return [False, ret_err]

        self.proto.close()
        self.logging.debug("Upgrade: Send firmware transfer complete command successfully")
        self.logging.debug("Upgrade: upgrade successed")

        global update_time_2
        update_time_2 = time.time()
        self.upgrade_step = 5
        return [True, 0]
