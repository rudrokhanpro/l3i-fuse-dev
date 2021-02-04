import os
import sys
import stat
import errno
from logger import log  # custom fn to log

# import fuse
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse

# use newer API
fuse.fuse_python_api = (0, 2)
# assert fuse library has 'stateful_files' & 'has_init'
fuse.feature_assert('stateful_files', 'has_init')

# variables
home = os.environ['HOME']
desktop_path = home + '/Desktop'
myfuse_dirname = 'mydrive'
myfuse_source_path = desktop_path + '/' + myfuse_dirname


class MyFuse(fuse.Fuse):
    # init FUSE
    def __init__(self, *args, **kw):
        log("[__init__]")
        fuse.Fuse.__init__(self, *args, **kw)
        self.root = myfuse_source_path

    def fsinit(self):
        log("[fsinit]")
        os.chdir(self.root)

    def main(self, *args, **kw):
        log("[main]")
        self.file_class = self.MyFile
        return fuse.Fuse.main(self, *args, **kw)

    # get file (or directory) attributes
    def getattr(self, path):
        log("[getattr] (path=%s)" % path)
        return os.lstat("." + path)

    # read files in a directory
    def readdir(self, path, offset):
        log("[readdir] (path=%s)" % path)
        for e in os.listdir("." + path):
            yield fuse.Direntry(e)

    # remove a directory
    def rmdir(self, path):
        log("[rmdir] (path=%s)" % path)
        os.rmdir("." + path)

    # rename a directory
    def rename(self, path, path1):
        log("[rename] (path=%s, path1=%s)" % (path, path1))
        os.rename("." + path, "." + path1)

    class MyFile(object):
        def __init__(self, path, flags, *mode):
            log("[MyFile.__init__]")
            self.file = os.fdopen(os.open("." + path, flags, *mode),
                                  self.flag2mode(flags))
            self.fd = self.file.fileno()

        # return a file's content uppercased
        def read(self, length, offset):
            log("[MyFile.read]")
            self.file.seek(offset)
            contents = self.file.read(length)

            return contents.upper()

        # get a file's attributes
        def fgetattr(self):
            log("[MyFile.fgetattr]")
            return os.fstat(self.fd)

        def flag2mode(self, flags):
            md = {os.O_RDONLY: 'rb', os.O_WRONLY: 'wb', os.O_RDWR: 'wb+'}
            m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

            if flags | os.O_APPEND:
                m = m.replace('w', 'a', 1)

            log("[MyFile.flag2mode] (flags=%d) %s" % (flags, m))

            return m


def main():
    # make a directory if it doesnt exist
    if not os.path.exists(myfuse_source_path):
        os.mkdir(myfuse_source_path)

    server = MyFuse(version="%prog" + fuse.__version__)
    server.parser.add_option(mountopt="root")
    server.parse(values=server, errex=1)

    # try to start fuse
    try:
        if server.fuse_args.mount_expected():
            os.chdir(server.root)
    except OSError:
        print("can't enter root of underlying filesystem", file=sys.stderr)
        sys.exit(1)

    server.main()


if __name__ == '__main__':
    main()
