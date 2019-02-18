

cdef class L10nManager(object):

    def __cinit__(self, app):
        self.app = app

    async def get_l10n(self, language, filetype):
        l10ndb = self.app.data['global/l10n']
        result = await l10ndb.all_docs(
            include_docs='true',
            startkey=language + '@' + filetype,
            endkey=language + '@' + filetype + '@\uffff')
        l10ndata = {}
        while True:
            l10n = await result.next()
            if l10n is None:
                break
            language, filetype, plugin, key = l10n['doc']['_id'].split('@')
            l10ndata[key] = l10n['doc']['value']
        return l10ndata
