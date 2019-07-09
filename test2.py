from esptool_image2elf import LoaderConfig, load_fw, fw_to_elf

args = LoaderConfig("firmware.bin", "esp32")
fw = load_fw(args)


def ptr_sect(sect):
    sect.flags = "r"
    sect.name = "pointers"

def data_sect(sect):
    sect.flags = "r"
    sect.name = "datanstuff"


elf = fw_to_elf(fw, section_funcs={
    0x400d0018: ptr_sect,
    0x3f400020: data_sect
})
elf.write_to_file("firmware.bin_out.elf")
