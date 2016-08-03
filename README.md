# libc Trip in Memoryland

## Description

This script is a fun experimentation playing with Virtual Memory, Physical Mapping and proof of the Copy On Write behavior of fork().

The script lists all pids, retrieves the virtual address of the libc, translates the virtual address for each pid to a physical address and dumps the unique instances to /tmp folder.

This could be a useful PoC playing with /proc memory files like mem, pagemap and maps.

## Dependencies

The script works on Python 2.x. No other dependencies are required.

## Usage

The script accesses privileged files and needs to be run with root privileges:

```shell
[*] listing PID ...
[*] retrieving libc addresses ...
[+] PID     : Physical            Virtual          (Name)
[+] 1       : 0x0000000045f0b1 -> 0x007f1c6f985000 (init)
[+] 1537    : 0x0000000045f0b1 -> 0x007f66423f2000 (libvirtd)
[+] 2059    : 0x0000000045f0b1 -> 0x007ff3eb870000 (master)
[+] 1040    : 0x0000000045f0b1 -> 0x007f63b6b9f000 (rpc.statd)
...
[+] 4094    : 0x0000000045f0b1 -> 0x007fea9860c000 (fsnotifier64)
[*] dump 2 libc files ...
[*] dumping libc at physical address 0x0000000045f0b1 ...
[+] md5sum: 9089dd6bd629aeae4ae17d5566b4aeb3
[*] dumping libc at physical address 0x00000000430d59 ...
[+] md5sum: 786d2647168718d9e4c82e5102209504


```