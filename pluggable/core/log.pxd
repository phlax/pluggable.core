

cdef class ServerLog:
   cdef public app

   cpdef get_timestamp(self)
   