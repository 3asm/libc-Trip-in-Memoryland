__author__ = "Alaeddine Mesbahi"
__license__ = "GPL"
__version__ = "3.0"


import os
import re
import struct
import hashlib

PROC_PATH = '/proc'
LIBC_PATH_PREFIX = 'libc-2.19.so'
PROC_MAPS_PATH = '/proc/{}/maps'
PROC_COMM_PATH = '/proc/{}/comm'
PROC_PAGEMAP_PATH = '/proc/{}/pagemap'
PROC_MEM_PATH = '/proc/{}/mem'


def info(text):
    print "[*] {} ...".format(text)


def success(text):
    print "[+] {}".format(text)


def md5sum(blob):
    m = hashlib.md5()
    m.update(blob)
    return m.hexdigest()


def proc_name(pid):
    path = PROC_COMM_PATH.format(pid)
    if os.path.isfile(path):
        with open(path, 'r') as cmd:
            return cmd.read()[:-1]
    return ''


def parse_proc_maps(pid):
    with open(PROC_MAPS_PATH.format(pid), 'r') as maps_file:
        for l in maps_file.readlines():
            m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([rwxp-]{4}) ([0-9A-Fa-f]+) ([0-9:]+) ([0-9]+)\s+(.*)', l)
            if m:
                yield m.groups()


def vertical_to_physical(memory_adress, pid):
    maps_path = PROC_PAGEMAP_PATH.format(pid)
    page_size = os.sysconf("SC_PAGE_SIZE")
    pagemap_entry_size = 8
    if os.path.isfile(maps_path):
        offset = (memory_adress / page_size) * pagemap_entry_size
        with open(maps_path, 'r') as f:
            f.seek(offset, 0)
            entry = struct.unpack('Q', f.read(pagemap_entry_size))[0]
        return entry & 0x7FFFFFFFFFFFFF


def dump_memory(pid, offset, size, output_file):
    with open(PROC_MEM_PATH.format(pid), 'rb') as mem_file:
        mem_file.seek(offset)  # seek to region start
        chunk = mem_file.read(size)  # read region contents
        with open(output_file, 'wb') as dump_libc_file:
            dump_libc_file.write(chunk)
            return chunk

if __name__ == '__main__':

    pids = list()
    info('listing PID')

    for path in os.listdir(PROC_PATH):
        if re.match('[0-9]+'.format(PROC_PATH), path):
            if os.path.isfile('{}/{}/maps'.format(PROC_PATH, path)):
                pids.append(int(path))

    info('retrieving libc addresses')
    unique_libc_addrs = dict()
    libc_mappings = dict()

    for pid in pids:
        for entry in parse_proc_maps(pid):
            if LIBC_PATH_PREFIX in entry[6]:
                offset = int(entry[0], 16)
                size = int(entry[1], 16) - offset
                physical_offset = vertical_to_physical(offset, pid)
                unique_libc_addrs[physical_offset] = (offset, size, pid)
                libc_mappings[pid] = (physical_offset, offset, size)
                #  take first entry only corresponding to .text code section
                break

    success("{0:<8}: {1:<19} {2:<16} ({3:})".format("PID", "Physical", "Virtual", "Name"))
    for pid, offsets in libc_mappings.items():
        success("{0:<8}: {1:#016x} -> {2:#016x} ({3:})".format(pid, offsets[0], offsets[1], proc_name(pid)))

    info('dump {} libc files'.format(len(unique_libc_addrs)))
    for physical, (offset, size, pid) in unique_libc_addrs.items():
        info('dumping libc at physical address {:#016x}'.format(physical))
        chunk = dump_memory(pid, offset, size, '/tmp/libc_{}'.format(pid))
        success("md5sum: {}".format(md5sum(chunk)))


