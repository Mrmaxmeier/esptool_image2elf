from makeelf.elf import *


class XtensaElf(object):
    def __init__(self, entry_addr):
        self.elf = ELF(
            e_class=ELFCLASS.ELFCLASS32,
            e_machine=EM.EM_XTENSA,
            e_data=ELFDATA.ELFDATA2LSB,
            e_type=ET.ET_EXEC,
        )
        self.elf.Elf.Ehdr.e_entry = entry_addr
        self.elf.Elf.Ehdr.e_flags = 0x300

    def add_section(self, esp_section):
        print("add_section", esp_section.name,
              hex(esp_section.addr), len(esp_section.data))
        sec_id = self.elf.append_section(sec_name=esp_section.name,
                                         sec_data=esp_section.data,
                                         sec_addr=esp_section.addr)
        flags = esp_section.flags

        Shdr = self.elf.Elf.Shdr_table[sec_id]

        ptype = PT.PT_LOAD
        vaddr = Shdr.sh_addr
        paddr = vaddr
        mem_size = Shdr.sh_size
        file_size = Shdr.sh_size
        offset = 0x13371337  # resolved later

        Phdr = Elf32_Phdr(p_type=ptype, p_offset=offset, p_vaddr=vaddr,
                          p_paddr=paddr, p_filesz=file_size, p_memsz=mem_size,
                          p_flags=flags, p_align=1, little=self.elf.little)

        self.elf.Elf.Phdr_table.append(Phdr)

    def write_to_file(self, filename_to_write):
        # print(repr(self.elf))
        with open(filename_to_write, 'wb') as f:
            f.write(bytes(self.elf))


class ElfSection(object):
    def __init__(self, section_name, section_address, section_bytes):
        self.name = section_name
        self.addr = section_address
        self.data = section_bytes
        self.flags = "rwx"

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, fs):
        self._flags = 0
        if "r" in fs:
            self._flags |= PF.PF_R
        if "w" in fs:
            self._flags |= PF.PF_W
        if "x" in fs:
            self._flags |= PF.PF_X
