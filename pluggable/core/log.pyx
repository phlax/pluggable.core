# distutils: define_macros=CYTHON_TRACE_NOGIL=1
# cython: linetrace=True
# cython: binding=True

import time
from datetime import datetime
from uuid import uuid4


cdef class ServerLog(object):

    def __init__(self, app):
        self.app = app

    cpdef get_timestamp(self):
        now = datetime.now()
        return int(time.mktime(now.timetuple())*1e3 + now.microsecond/1e3)

    async def get_log_db(self):
        return await self.app.couchdb.db('global/log')

    async def log(self, of, msg, log_type="info"):
        db = await self.get_log_db()
        # await db.create()
        uuid = uuid4()
        key = '%s@%s' % (self.get_timestamp(), uuid)
        doc = await db.doc(key)
        await doc.update(dict(_id=key, type=log_type, of=of, msg=msg))

    async def of(self, of, limit=100) -> list:
        db = await self.get_log_db()
        _logs = await db.all_docs(include_docs='true', limit=limit)
        logs = []
        count = 0
        while True:
            log = await _logs.next()
            count += 1
            if log is None or count > limit:
                break
            logs.append(
                dict(of=log['doc']['of'],
                     msg=log['doc']['msg'],
                     type=log['doc']['type'],
                     timestamp=log['id'].split('@')[0]))
        return logs
