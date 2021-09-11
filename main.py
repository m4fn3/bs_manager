from pathlib import Path
import os, stat, subprocess, time

bs_data_dir = Path(r"C:\ProgramData\BlueStacks_nxt")
bs_program_dir = Path(r"C:\Program Files\BlueStacks_nxt")
adb_executable = f'\"{bs_program_dir / "HD-Adb.exe"}\"'
conf_path = bs_data_dir / "bluestacks.conf"


def cmd(cmd_, shell=True, popen=False):
    if popen:
        subprocess.Popen(cmd_, stdout=subprocess.PIPE, shell=True)
    elif shell:
        r = subprocess.run(cmd_, stdout=subprocess.PIPE, shell=True)
        return str(r.stdout)
    else:
        r = subprocess.run(cmd_.split(), stdout=subprocess.PIPE)
        return str(r.stdout)


class BSConf:
    def __init__(self, path):
        self.path = path
        with open(path, "r") as file:
            self.conf = {}
            for line in file:
                meta = line.split("=", 1)
                self.conf[meta[0]] = meta[1].replace("\n", "")
            self.instance = {
                key.replace("bst.instance.", "").replace(".display_name", ""): self.conf[key] \
                for key in self.search_key("display_name")
            }

    def search_key(self, name):
        return [key for key in self.conf if name in key]

    def save(self):
        if not os.access(self.path, os.W_OK):
            os.chmod(self.path, stat.S_IWRITE)
        text = ""
        for opt in self.conf:
            text += f"{opt}={self.conf[opt]}\n"
        with open(self.path, "w", newline="\n") as f:
            f.write(text)
        if os.access(self.path, os.W_OK):
            os.chmod(self.path, stat.S_IREAD)

    def get_root_status(self, instance):
        status = self.conf[f"bst.instance.{instance}.enable_root_access"]
        if status == '"1"':
            return True
        else:
            return False

    def set_root_status(self, instance, root):
        status = '"1"' if root else '"0"'
        self.conf[f"bst.instance.{instance}.enable_root_access"] = status
        self.save()

    def is_read_only(self):
        """True - read-only, False -> writable"""
        if os.access(self.path, os.W_OK):
            return False
        else:
            return True

    def set_read_write(self, perm):
        """True to set writable, False to set read-only"""
        if perm:
            os.chmod(self.path, stat.S_IWRITE)
        else:
            os.chmod(self.path, stat.S_IREAD)

    def get_adb_address(self, instance):
        return int(self.conf[f"bst.instance.{instance}.adb_port"].replace('"', ""))

    def __getitem__(self, item):
        return self.conf[item]

    def __setitem__(self, key, value):
        self.conf[key] = value


class ADB:
    def __init__(self, conf: BSConf):
        self.instance = {}
        for i in conf.instance:
            self.instance[i] = conf.get_adb_address(i)

    def connect(self, instance):
        address = self.instance[instance]
        r = cmd(f"{adb_executable} connect 127.0.0.1:{address}")
        output = r.replace("\n", "")
        if "empty host name" in output:
            subprocess.run(f"{adb_executable} kill-server", stdout=subprocess.PIPE)
            subprocess.run(f"{adb_executable} start-server", stdout=subprocess.PIPE)
            self.connect(address)
        elif "unable to connect to" in output:
            return False
        elif "connected to" in output:
            return True
        else:
            return False

    def shell(self, instance, cmd_):
        self.connect(instance)
        address = self.instance[instance]
        cmd(f"{adb_executable} -s 127.0.0.1:{address} shell {cmd_}")

    def reboot(self, instance):
        self.stop(instance)
        time.sleep(3)
        self.start(instance)

    def start(self, instance):
        cmd(f"\"{bs_program_dir / 'HD-Player.exe'}\" --instance {instance}", popen=True)

    def stop(self, instance):
        self.shell(instance, "reboot -p")

    def start_shell(self, instance):
        self.connect(instance)
        cmd(f"start cmd /k {adb_executable} -s 127.0.0.1:{self.instance[instance]} shell", popen=True)


def clear_screen():
    os.system("cls")


def instance_menu(conf):
    select_i_menu = "---Select the instance---\nPlease select from the list below and enter the number."
    instance_key = []
    for i, n in enumerate(conf.instance):
        instance_key.append(n)
        select_i_menu += f"\n {i + 1}. {conf.instance[n]}"
    select_i_menu += "\n(type anything else to exit)"
    r = input(select_i_menu)
    if r.rstrip().isdigit() and 1 <= int(r) <= len(instance_key) + 1:
        return instance_key[int(r) - 1]
    else:
        return None


def main():
    conf = BSConf(conf_path)
    adb = ADB(conf)
    while True:
        clear_screen()
        instance = instance_menu(conf)
        if instance is None:
            break

        while True:
            clear_screen()
            root_flag = "Rooted" if conf.get_root_status(instance) else "Not Rooted"
            rw_flag = "Read-only" if conf.is_read_only() else "Writable"
            select_a_menu = f"---Select the action for {conf.instance[instance]}---\n" \
                            f"Please select from 1 to 4 below\n" \
                            f" 1. Root/UnRoot ({root_flag})\n" \
                            f" 2. Read/Write ({rw_flag})\n" \
                            f" 3. Start/Stop/Restart\n" \
                            f" 4. Open adb shell\n" \
                            "(type anything else to back)"
            r = input(select_a_menu)
            if r == "1":
                status = not conf.get_root_status(instance)
                conf.set_root_status(instance, status)
                if adb.connect(instance):
                    adb.reboot(instance)
                input("Successfully {}!!\n(type any key to continue)".format(
                    "Rooted" if conf.get_root_status(instance) else "UnRooted"))
            elif r == "2":
                status = conf.is_read_only()
                conf.set_read_write(status)
                input("Now conf file is {}!!\n(type any key to continue)".format(
                    "Read-only" if conf.is_read_only() else "Writable"))
            elif r == "3":
                clear_screen()
                select_o_menu = "---Select the operation---\n" \
                                "Please select from 1 to 3 below\n" \
                                " 1. Start\n" \
                                " 2. Stop\n" \
                                " 3. Restart\n" \
                                "(type anything else to back)"
                r = input(select_o_menu)
                if r == "1":
                    adb.start(instance)
                elif r == "2":
                    adb.stop(instance)
                elif r == "3":
                    adb.reboot(instance)
            elif r == "4":
                if not adb.connect(instance):
                    adb.start(instance)
                    input("Waiting for BlueStacks to start. Press any key after BlueStacks has finished launching.")
                adb.start_shell(instance)
            else:
                break


if __name__ == "__main__":
    main()
