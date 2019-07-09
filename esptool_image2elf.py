from dataclasses import dataclass
import os

from xtensa_elf import XtensaElf, ElfSection
import esptool


@dataclass
class LoaderConfig:
    '''Settings for esptool's firmware loader'''
    filename: str
    chip: str = 'auto'  # 'auto' / 'esp32' / 'esp8266'


def load_fw(args):
    esptool.image_info(args)
    fw = esptool.LoadFirmwareImage(args.chip, args.filename)

    segsum = sum([len(seg.data) for seg in fw.segments])
    fsize = os.stat(args.filename).st_size
    print(f"Segment data bytes: {segsum} / {fsize} ({segsum/fsize*100:.02f}%)")
    if segsum / fsize < 0.5:
        print("[WARN] ELF will be significantly shorter than image")

    return fw


def fw_to_elf(fw, section_funcs={}):
    elf = XtensaElf(fw.entrypoint)
    for i, section in enumerate(fw.segments):
        elf_section = ElfSection(f"sect{i}", section.addr, section.data)

        if section.addr in section_funcs:
            print("running section func")
            section_funcs[section.addr](elf_section)
        elf.add_section(elf_section)

    elf.elf.__bytes__()  # update ELF offsets FIXME this is gross
    offset = {}
    for sect in elf.elf.Elf.Shdr_table:
        offset[sect.sh_addr] = sect.sh_offset
    for ld in elf.elf.Elf.Phdr_table:
        print(ld)
        ld.p_offset = offset[ld.p_vaddr]
    return elf
