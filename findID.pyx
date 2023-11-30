# my_module.pyx

cimport cython

# @cython.boundscheck(False)
# @cython.wraparound(False)
# def find_id_cython(int pos, dict points):
#     cdef int i_d = <int>points['id'][pos]
#     return i_d

# Define the function with Cython types
@cython.boundscheck(False)  # Disable bounds checking for better performance
@cython.wraparound(False)    # Disable negative index wrapping for better performance
cpdef find_id(int pos, dict points):
        cdef int i_d = <int>points[b'id'][pos]
        return i_d
