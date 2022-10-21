

try:
    from numba import njit as _njit  # type: ignore
    njit = lambda f: _njit(cache=True)(f) # type: ignore
except ImportError:
    def njit(f, *args, **kwargs):
        return f

