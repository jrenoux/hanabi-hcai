import justpy as jp
from hanabi_learning_environment import pyhanabi


import gui


if __name__ == "__main__":
    # Check that the cdef and library were loaded from the standard paths.
    assert pyhanabi.cdef_loaded(), "cdef failed to load"
    assert pyhanabi.lib_loaded(), "lib failed to load"
    jp.justpy(gui.render_front_page)
