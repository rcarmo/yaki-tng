# PickleQueue -- persistent queue using cPickle

import Queue, cPickle

class PickleQueue(Queue.Queue):
    """A multi-producer, multi-consumer, persistent queue."""

    def __init__(self, filename, maxsize=0):
        """Initialize a persistent queue with a filename and maximum size.

        The filename is used as a persistent data store for the queue.
        If maxsize <= 0, the queue size is infinite.
        """
        self.filename = filename
        Queue.Queue.__init__(self, maxsize)

    def _init(self, maxsize):
        # Implements Queue protocol _init for persistent queue.
        # Sets up the pickle files.
        self.maxsize = maxsize
        try:
            self.readfile = file(self.filename, 'r')
            self.queue = cPickle.load(self.readfile)
            self.readfile.close()
        except IOError, err:
            if err.errno == 2:
                # File doesn't exist, continue ...
                self.queue = []
            else:
                # Some other I/O problem, reraise error
                raise err
        except EOFError:
            # File was null?  Continue ...
            self.queue = []

        # Rewrite file, so it's created if it doesn't exist,
        # and raises an exception now if we aren't allowed
        self.writefile = file(self.filename, 'w')
        cPickle.dump(self.queue, self.writefile, 1)

    def __sync(self):
        # Writes the queue to the pickle file.
        self.writefile.seek(0)
        cPickle.dump(self.queue, self.writefile, 1)
        self.writefile.flush()

    def _put(self, item):
        # Implements Queue protocol _put for persistent queue.
        self.queue.append(item)
        self.__sync()

    def _get(self):
        # Implements Queue protocol _get for persistent queue.
        item = self.queue[0]
        del self.queue[0]
        self.__sync()
        return item
