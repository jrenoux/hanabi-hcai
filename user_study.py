import justpy as jp
from hanabi_learning_environment import pyhanabi


from gui.gui import *
from gui.game_components import *


nb_players = 2
agents_list = ['rainbow',
               'quux-valuebot']
protocol_step = 0


def start_protocol(request):
  try:
    main_page = MyPage(body_classes = 'bg-gray-900')

    session = set_session(request, nb_players, [agents_list[protocol_step]])
    session['view'] = 'human_player'
    event_logger(session, 'button play the game')

    main_page.session = session
    MainPage(name = 'main_page', session = session, a = main_page)
    return main_page
  except Exception as err:
      print('The main page failed to load.')
      print('Exception: {}'.format(err))

if __name__ == "__main__":
    # Check that the cdef and library were loaded from the standard paths.
    assert pyhanabi.cdef_loaded(), "cdef failed to load"
    assert pyhanabi.lib_loaded(), "lib failed to load"

    jp.justpy(start_protocol)
