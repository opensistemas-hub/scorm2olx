import tarfile
import tempfile
import shutil
import os

class TarFS(object):

    def __init__(self, tarname, write=True):
        super(TarFS, self).__init__()
        self.tarname = tarname
        self.write = write


    def __enter__(self):
        self.__dirname__ = tempfile.mkdtemp()
        return self

    def __exit__(self, *args, **kwargs):
        try:
            tf = tarfile.open(self.tarname, mode='w:gz')
            tf.add(u'{}/'.format(self.__dirname__), arcname='')
            tf.close()
        finally:
            shutil.rmtree(self.__dirname__)

    def makedirs(self, dir):
        os.makedirs(self.safe_join(self.__dirname__, dir))

    def settext(self, filename, content=None):
        with open(self.safe_join(self.__dirname__, filename), 'w') as f:
            if content:
                f.write(content.encode('utf-8'))

    def touch(self, filename):
        return self.settext(filename)

    def copy(self, source, destination):
        shutil.copyfile(source, self.safe_join(self.__dirname__, destination))

    @staticmethod
    def safe_join(a, b):
        if os.path.isabs(b):
            return '{0}{1}'.format(a, b)
        else:
            return '{0}/{1}'.format(a, b)



