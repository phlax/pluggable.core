

cdef class Signals(object):

    def __init__(self, app):
        self.app = app
        self._signals = {}

    def log(self, *msgs):
        print('app.signals: ' + ' '.join(str(m) for m in msgs))

    cpdef listen(self, signal, cb):
        if signal not in self._signals:
            self._signals[signal] = []
        self.log('added', signal, cb)
        self._signals[signal].append(cb)

    def emit(self, signal, *args, **kwargs):
        if signal not in self._signals:
            return
        self.log(
            'emit',
            signal,
            self._signals[signal],
            dict(args=args, kwargs=kwargs))
        for cb in self._signals[signal]:
            self.app.loop.create_task(cb(*(signal, ) + args, **kwargs))

    cpdef unlisten(self, signal, cb):
        if signal not in self._signals:
            return
        if cb not in self._signals[signal]:
            return
        self.log('removed', signal, self._signals[signal])
        self._signals[signal].remove(cb)
        if len(self._signals[signal]) == 0:
            del self._signals[signal]
