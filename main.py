import struct
import argparse
import shlex

class Archive(object):

    class File(object):
        def __init__(self, f):
            self.name_table_offset,\
            self.offset,\
            self.unk1,\
            self.size1,\
            self.unk2,\
            self.size2,\
            self.unk3,\
            self.unk4 = struct.unpack('8I', f.read(32))

    class Directory(object):
        def __init__(self, f):
            self.name_offset,\
            self.children_start_index,\
            self.unknown,\
            self.file_count = struct.unpack('4i', f.read(16))

    def __init__(self, f):
        magic = f.read(4)
        if magic != b'LTAR':
            raise Exception('Invalid file format')
        version = struct.unpack('I', f.read(4))[0]
        if version != 3:
            raise Exception('Invalid archive version (expected {0}, found {1})'.format(3, version))
        name_table_size = struct.unpack('I', f.read(4))[0]
        directory_count = struct.unpack('I', f.read(4))[0]
        file_count = struct.unpack('I', f.read(4))[0]
        unknown4 = struct.unpack('I', f.read(4))[0]
        unknown5 = struct.unpack('I', f.read(4))[0]
        unknown6 = struct.unpack('I', f.read(4))[0]
        unknown7 = struct.unpack('I', f.read(4))[0]
        unknown8 = struct.unpack('I', f.read(4))[0]
        offset = struct.unpack('I', f.read(4))[0]  # some sort of offset to something, or a hash, perhaps
        data_size = struct.unpack('I', f.read(4))[0]  # probably the size of the data block (doesn't match filesize)
        print(unknown4, unknown5, unknown6, unknown7, unknown8)
        print(offset, data_size)
        self._name_table = f.read(name_table_size)
        self._files = [Archive.File(f) for _ in range(0, file_count)]
        self._directories = [Archive.Directory(f) for _ in range(0, directory_count)]

        # TODO: inspect if file sizes ever mismatch
        for file in self._files:
            if file.size1 != file.size2:
                print(file.size1, file.size2)


    def _get_file_index(self, name):
        offset = self._get_name_offset(name)
        if offset == -1:
            return -1
        for i, f in enumerate(self._files):
            if f.name_table_offset == offset:
                return i
        return -1

    def _get_name_offset(self, name):
        return self._name_table.find(name.encode('ascii'))

    def _get_name(self, offset):
        if offset == 0:
            return ''
        itr = iter(self._name_table[offset:])
        s = ''
        while True:
            c = chr(next(itr))
            if c == '\0':
                break
            s += c
        return s

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    args = parser.parse_args(['D:\GOG Galaxy\Games\F.E.A.R. Platinum Collection\FEARXP2\FEAR_XP.Arch00'])

    with open(args.file, 'rb') as f:
        archive = Archive(f)

    while True:
        args = input('>')
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='subparser')
        export = subparsers.add_parser('export')
        inspect = subparsers.add_parser('inspect')
        inspect.add_argument('cmd', choices=['name', 'rname', 'file'])
        inspect.add_argument('arg')
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            print(e)
            continue
        if args.subparser == 'inspect':
            if args.cmd == 'rname':
                offset = archive._get_name_offset(args.arg)
                print('{0} ({1})'.format(offset, hex(offset)))
            elif args.cmd == 'file':
                index = archive._get_file_index(args.arg)
                print('{0} ({1})'.format(index, hex(index)))
            elif args.cmd == 'name':
                offset = int(args.arg, 0)
                name = archive._get_name(offset)
                print(name)
