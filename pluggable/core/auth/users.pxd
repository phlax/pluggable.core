
from cpython cimport bool


cdef class UserManager:
    cdef public app
    cdef public http
    cdef public email_queue

    cpdef str hash_password(self, str password)
    cpdef public bool verify_password(self, str stored_password, str provided_password)
