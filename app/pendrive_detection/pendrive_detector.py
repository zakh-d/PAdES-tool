import os
import sys
from typing import Optional

if sys.platform == "linux":
    import pyudev
    import psutil

if sys.platform == "win32":
    import wmi


class PenDriveFinder:
    """
    A utility class to detect pen drives and locate private key files (*.pem) stored
    on them on various operating systems(Windows, Linux, macOS).
    """

    def __init__(self):
        self._wmi_client = None

    def find_all_pen_drives(self) -> list[str]:
        """
        Detects and lists all connected pen drives across different operating systems (Linux, Windows, macOS).
        It determines the current operating system and delegates the task to an OS-specific function.
        :return:
            list - A list of detected pen drive mount points (partitions or whole drives).
            An empty list is returned if no pen drives are detected.
        """
        if sys.platform == "linux":
            return self.__find_all_pen_drives_linux()
        elif sys.platform == "win32":
            return self.__find_all_pen_drives_win()
        elif sys.platform == "darwin":
            pass  # TODO implement macos function
        return []

    @staticmethod
    def __find_all_pen_drives_linux() -> list[str]:
        """
        Scans all connected and mounted drives to detect all pen drives on Linux systems.
        :return:
            list - A list of detected pen drive mount points (partitions or whole drives).
            An empty list is returned if no pen drives are detected.
        """
        context = pyudev.Context()
        pen_drives = []

        partition_mounts = {p.device: p.mountpoint for p in psutil.disk_partitions()}

        for device in context.list_devices(subsystem="block", DEVTYPE="disk"):
            if device.attributes.asstring("removable") == "1":
                mount_point = partition_mounts.get(device.device_node)
                if mount_point:
                    pen_drives.append(mount_point)
                else:
                    for part in context.list_devices(
                        subsystem="block", DEVTYPE="partition", parent=device
                    ):
                        mount_point = partition_mounts.get(part.device_node)
                        if mount_point:
                            pen_drives.append(mount_point)

        return pen_drives

    def __find_all_pen_drives_win(self) -> list[str]:
        """
        Scans all connected and mounted drives to detect all pen drives on Windows systems.
        :return:
            list - A list of detected pen drive mount points (partitions or whole drives).
            An empty list is returned if no pen drives are detected.
        """
        if self._wmi_client is None:
            self._wmi_client = wmi.WMI()

        pen_drives = []

        for drive in self._wmi_client.Win32_DiskDrive():
            if drive.InterfaceType == "USB":
                for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
                    for logical_disk in partition.associators(
                        "Win32_LogicalDiskToPartition"
                    ):
                        pen_drives.append(logical_disk.DeviceID)

        return pen_drives

    @staticmethod
    def find_pen_drive_with_private_key(pen_drives: list[str]) -> Optional[str]:
        """
        Scans all connected and mounted drives to detect a pen drive containing a private key (*.pem) file.
        :param:
            pen_drives: list - A list of detected pen drive mount points (partitions or whole drives).
        :return:
            str - Mount point of the partition containing the `.pem` private key file, or
            None - If no partition with a `.pem` file is found.
        """
        for pen_drive in pen_drives:
            for entry in os.scandir(pen_drive):
                if entry.name.endswith(".pem") and entry.is_file():
                    return pen_drive
        return None

    @staticmethod
    def get_private_key_path(pen_drive_path: str) -> Optional[str]:
        """
        Searches the specified pen drive (mount point) for a private key (*.pem) file.
        :param pen_drive_path: str - The mount point of the pen drive to scan.
        :return:
            str - Full path to the `.pem` private key file if found, or
            None - If no `.pem` file is found on the provided pen drive path.
        """
        for entry in os.scandir(pen_drive_path):
            if entry.name.endswith(".pem") and entry.is_file():
                return entry.path
