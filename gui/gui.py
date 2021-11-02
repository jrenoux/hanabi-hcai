# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example code demonstrating the Python Hanabi interface."""

from __future__ import print_function

from hanabi_learning_environment import pyhanabi
from game_components import *
import numpy as np
import time
import threading
import asyncio
import copy
import justpy as jp

"""Tailwind CSS classes"""
label_classes = 'block uppercase text-gray-500 text-xs font-bold'
selectlist_classes = 'w-32 text-xl text-blue-500 text-center font-bold bg-gray-900 border border-blue-500 rounded'
button_classes = 'text-blue-500 font-bold uppercase border border-blue-500 rounded w-48 p-3 ml-2'

card_colors = [ 'red', 'yellow', 'green', 'white', 'blue' ] 
table_positions= {  1: [(1,3)], 
                    2: [(2,5), (2,1)], 
                    3: [(1,3), (2,5), (2,1)], 
                    4: [(2,5), (6,5), (6,1), (2,1)], 
                    5: [(1,3), (2,5), (6,5), (6,1), (2,1)]}
threads = []
sessions = {}

class Menu(jp.Div):
    """The menu component.

    Params: session: dict, Current session of a client.
    """
    def __init__(self, **kwargs):
        self.session = None
        super().__init__(**kwargs)

        async def run_benchmark(self, event):
            """Run the benchmark.
               Starts a separate thread for the benchmark if one is not already running.

               Args: self.session: dict, Access to session global variables.
            """
            if not self.session['is_running']:
                event_logger(self.session, 'button run')
                with self.session['wait_event']:
                    self.session['wait_event'].notify_all()

                self.session['is_running'] = True
                self.session['is_paused'] = False
                self.text = 'Stop'
                try:
                    self.session['states'].clear()
                    benchmark_thread = threading.Thread(target = run_game, 
                                                        args = ({"players": self.session['num_players'], "random_start_player": True}, 
                                                                self.session, 
                                                                event.page), 
                                                        name = self.session['id'], 
                                                        daemon = True)
                    threads.append(benchmark_thread)
                    benchmark_thread.start()
                except Exception as err:
                    print('The benchmark could not be started.')
                    print('Exception: {}'.format(err))
            else:
                event_logger(self.session, 'button stop')
                self.session['is_running'] = False
                self.session['is_paused'] = False
                self.text = 'Run'
                
                with self.session['wait_event']:
                    self.session['wait_event'].notify_all()

        def session_variable_change(self, event):
            """OnChange event handler. Wakes up sleeping threads for instant change.
               
               Args: self.session: dict, Access to the session global variables.
                     self.session_variable: A variable in the session dict.
                     self.cast_type: datatype, used for casting.
            """
            try:
                event_logger(self.session, "{} for variable {}".format(str(event.input_type), self.session_variable))
                self.session[self.session_variable] = self.cast_type(self.value)
                with self.session['wait_event']:
                    self.session['wait_event'].notify_all()
            except Exception as err:
                print('Variable change failed.')
                print('Exception: {}'.format(err))

        def pause_benchmark(self, event):
            """Pause the benchmark by setting is_paused variable, used in a conditional semaphore.
               Sets the text of the button accordingly.
               
               Args: session: dict, Access to the session global variables.
            """
            try:
                event_logger(self.session, 'button pause')
                self.session['is_paused'] = not self.session['is_paused']
                self.text = 'Pause' if not self.session['is_paused'] else 'Resume'
                with self.session['wait_event']:
                    if not self.session['is_paused']:
                        event_logger(self.session, 'button resume')
                        self.session['wait_event'].notify_all()
            except Exception as err:
                print('The pause function has crashed or timed/locked out. Try again.')
                print('Exception: {}'.format(err))

        class RadioItem(jp.Div):
            """A radio button component. 
               Used for different views.

               Params: label_text: string, Lead text for the label.
                       item_value: string, Value of radiobutton.
                       value_type: datatype, used for casting to the right datatype.
                       session: dict, Access to the session global variables.
                       session_variable: A variable in the session dict.
            """
            def __init__(self, **kwargs):
                self.label_text = None
                self.item_value = None
                self.cast_type = None
                self.session = None
                self.session_variable = None
                super().__init__(**kwargs)
            def react(self, data):
                self.delete_components()

                container = jp.Div(classes = 'flex px-1 mb-1', name = 'container', a = self)
                jp.Input(type = 'radio',
                         name = self.session_variable,
                         value = self.item_value,
                         cast_type = self.cast_type,
                         session = self.session,
                         session_variable = self.session_variable,
                         checked = True if self.session[self.session_variable] == self.item_value else False,
                         change = session_variable_change, 
                         a = container)
                jp.Label(classes = f'{label_classes} ml-1', text = self.label_text, name = 'label', a = container)

        class SelectListItem(jp.Div):
            """A select list component.
               Used for selecting number of players and step frequency.

               Params: label_text: string, Lead text for the label.
                       value_type: datatype, used for casting to the right datatype.
                       options: list, Options to add to the select list.
                       disabled: bool, Disables the use of the select list if True.
                       session: dict, Access to the session global variables.
                       session_variable: A variable in the session dict. 
            """
            def __init__(self, **kwargs):
                self.label_text = ''
                self.cast_type = None
                self.options = []
                self.disabled = False
                self.session = None
                self.session_variable = ''
                super().__init__(**kwargs)
            def react(self, data):
                self.delete_components()

                container = jp.Div(classes = 'flex flex-col px-2', name = 'container', a = self)
                jp.Label(classes = label_classes, text = self.label_text, name = 'label', a = container)
                select_list = jp.Select(classes = selectlist_classes, 
                                        value = self.session[self.session_variable],
                                        cast_type = self.cast_type,
                                        session = self.session,
                                        session_variable = self.session_variable,
                                        disabled = self.disabled, 
                                        change = session_variable_change, 
                                        name = self.session_variable,
                                        a = container)
                for option in self.options:
                    select_list.add(jp.Option(value = option, text = option))

        menu_container = jp.Div(classes = 'flex justify-between', name = 'menu_container', a = self)
        SelectListItem(label_text = 'Number of players', 
                       options = range(2,6),
                       cast_type = int,
                       session = self.session,
                       session_variable = 'num_players', 
                       name = 'num_players',
                       disabled = self.session['is_running'], 
                       a = menu_container)
        SelectListItem(label_text = 'Step frequency', 
                       options = range(0,11),
                       cast_type = int,
                       session = self.session,
                       session_variable = 'step_frequency', 
                       name = 'step_frequency',
                       a = menu_container)

        radio_container = jp.Div(classes = 'flex flex-col p-2', name = 'radio_container', a = menu_container)
        RadioItem(label_text = 'Observer view', 
                  item_value = 'observer',
                  cast_type = str,
                  session = self.session,
                  session_variable = 'view',
                  name = 'observer_view', 
                  a = radio_container)
        RadioItem(label_text = 'Agent view', 
                  cast_type = str,
                  item_value = 'agent',
                  session = self.session,
                  session_variable = 'view',
                  name = 'agent_view', 
                  a = radio_container)        

        button_container = jp.Div(classes = 'flex', name = 'button_container', a = menu_container)
        button_visibility = 'visible' if self.session['is_running'] else 'invisible'
        jp.Button(classes = f'{button_classes} {button_visibility}', 
                  text = f'Pause' if not self.session['is_paused'] else 'Resume', 
                  session = self.session,
                  click = pause_benchmark,
                  name = 'pause_button', 
                  a = button_container)
        jp.Button(classes = button_classes, 
                  text = f'Run' if not self.session['is_running'] else 'Stop', 
                  session = self.session,
                  click = run_benchmark, 
                  name = 'start_button',
                  a = button_container)
        
class Log(jp.Div):
    """Log component. Serves as either a log for either all the previous moves or previous moves for a certain player.

       Params: self.label_text: string, Label text for the component.
               self.log_type: string, Is either states_log or latest_moves_log
               self.log_items: list, List of history items of previous states.
               self.session: dict, Access to the global session variables.
               self.log_index:
    """
    def __init__(self, **kwargs):
        self.label_text = ''
        self.log_type = ''
        self.log_items = []
        self.session = None
        self.log_index = 0
        super().__init__(**kwargs)

        container = jp.Div(classes = f'{label_classes} flex flex-col', text = self.label_text, name = 'container', a = self)
        if self.log_type == 'states_log':
            self.log_items.reverse()
        for item in self.log_items:
            state = self.session['states'][self.log_index]
            self.LogItem(item = item, view_state = state, log_type = self.log_type, session = self.session, a = container)
            self.log_index += 1

    class LogItem(jp.Div):
        def __init__(self, **kwargs):
            self.log_type = ''
            self.item = None
            self.session = None
            self.view_state = None
            super().__init__(**kwargs)
            
            self.num_players = self.session['num_players']
            self.current_player = self.session['current_player']

            container = jp.Div(name = 'container', a = self)
            """Sets the current player's moves, the target player and the player a card is dealt to"""
            if self.log_type == 'states_log':
                self.player = self.item.player()
                self.dealt_player = self.item.deal_to_player()
                self.revealed_player = (self.player + self.item.move().target_offset()) % self.num_players
            elif self.log_type == 'latest_moves_log':
                self.player = (self.current_player + self.item.player()) % self.num_players
                self.dealt_player = (self.current_player + self.item.deal_to_player()) % self.num_players
                self.revealed_player = (self.player + self.item.move().target_offset()) % self.num_players

            if self.item.move().type() == 1:
                self.lead_text = f'Player {self.player + 1} played'
                self.card_color = card_colors[self.item.color()]
                self.card_text = f'{self.card_color} {self.item.rank() + 1}'
                self.end_text = ''
            elif self.item.move().type() == 2:
                self.lead_text = f'Player {self.player + 1} discarded'
                self.card_color = card_colors[self.item.color()]
                self.card_text = f'{self.card_color} {self.item.rank() + 1}'
                self.end_text = ''
            elif self.item.move().type() == 3:
                self.lead_text = f'Player {self.player + 1} revealed color'
                self.card_color = card_colors[self.item.move().color()]
                self.card_text = f'{self.card_color}'
                self.end_text = f'to player {self.revealed_player + 1}' 
            elif self.item.move().type() == 4:
                self.lead_text = f'Player {self.player + 1} revealed'
                self.card_color = 'white'
                self.card_text = f'rank {self.item.move().rank() + 1}'
                self.end_text = f'to player {self.revealed_player + 1}' 
            elif self.item.move().type() == 5:
                self.lead_text = f'Dealt'
                self.card_color = card_colors[self.item.move().color()] if (self.session['view'] == 'observer' or self.log_type == 'states_log') else 'gray'
                self.card_text = f'{self.card_color} {self.item.move().rank() + 1}' if (self.session['view'] == 'observer' or self.log_type == 'states_log') else 'unknown card'
                self.end_text = f'to player {self.dealt_player + 1}'
            else:
                self.log_title = 'No such log item.'

            color = self.card_color if self.card_color == 'white' else self.card_color + '-500'
            
            item_div = jp.Button(classes = f'{label_classes} flex flex-row items-center', click = self.update_page, name = 'item_div', a = container)
            item_button = jp.Img(classes = 'mb-1 mr-1', src = '/static/gui/img/visibility.png', a = item_div)
            jp.Span(classes = 'mr-1 mb-1', text = f'{self.lead_text}', name = 'lead_text_span', a = item_div)
            jp.Span(classes = f'mr-1 mb-1 text-{color}', text = f'{self.card_text}', name = 'card_text_span', a = item_div)
            jp.Span(classes = 'mr-1 mb-1', text = f'{self.end_text}', name = 'end_text_span', a = item_div)

        async def update_page(self, event):
            """Pause benchmark and update the GUI based on which state to be viewed.

            Args: state: state of the game.
                    session_id: string, ID of the current session.
                    page: WebPage, the webpage to be updated.
            """
            try:
                event_logger(self.session, 'a previous state')
                self.session['is_paused'] = True
                event.page.delete_components()
                current_state = self.session['states'][0]
                self.session['current_player'] = self.view_state.cur_player()
                MainPage(session = self.session, state = current_state, view_state = self.view_state, a = event.page)
                await event.page.update()
            except Exception as err:
                print('The main page failed to update from the log.')
                print("Exception: {}".format(err))
                
class LegalMoves(jp.Div):
    def __init__(self, **kwargs):
        self.label_text = ''
        self.session = None
        self.moves = []
        super().__init__(**kwargs)
    
        container = jp.Div(classes = f'{label_classes} text-xs grid grid-cols-2', text = self.label_text, name = 'container', a = self)

        sorted_moves = self.sort_moves(self.moves)
        for move_type in sorted_moves:
            if move_type != 0:
                move_container = jp.Div(classes = f'col-start-{move_type % 2} mr-10', a = container)
                for move in sorted_moves[move_type]:
                    self.Move(move = move, session = self.session, a = move_container)

    def sort_moves(self, moves):
        """Sorts the moves based on the move types as keys in the dictionary.

            Args: moves: list, List of moves to sort.

            Returns: sorted_moves: dict, keys being move type and values are list of moves.
        """
        try:
            sorted_moves = {0: [], 1: [], 2: [], 3: [], 4: []}
            for move in moves:
                sorted_moves[move.type()].append(move)
            return sorted_moves
        except Exception as err:
            print('Could not sort the moves list.')
            print('Exception: {}'.format(err))

    class Move(jp.Div):
        def __init__(self, **kwargs):
            self.move = None
            self.session = None
            super().__init__(**kwargs)

            self.current_player = self.session['current_player']
            self.num_players = self.session['num_players']

            container = jp.Div(name = 'container', a = self)
            self.revealed_player = (self.current_player + self.move.target_offset()) % self.num_players

            if self.move.type() == 1:
                self.lead_text = f'Play'
                self.card_color = 'white'
                self.card_text = f'Card {self.move.card_index() + 1}'
                self.end_text = ''
            elif self.move.type() == 2:
                self.lead_text = f'Discard'
                self.card_color = 'white'
                self.card_text = f'Card {self.move.card_index() + 1}'
                self.end_text = ''
            elif self.move.type() == 3:
                self.lead_text = f'Reveal color'
                self.card_color = card_colors[self.move.color()]
                self.card_text = f'{card_colors[self.move.color()]}'
                self.end_text = f'to player {self.revealed_player  + 1}' 
            elif self.move.type() == 4:
                self.lead_text = f'Reveal'
                self.card_color = 'white'
                self.card_text = f'rank {self.move.rank() + 1}'
                self.end_text = f'to player {self.revealed_player  + 1}' 
            else:
                self.log_title = 'Error'

            color = self.card_color if self.card_color == 'white' else self.card_color + '-500'

            jp.Span(classes = 'mr-1 mb-1', text = f'{self.lead_text}', name = 'lead_text_span', a = container)
            jp.Span(classes = f'mr-1 mb-1 text-{color}', text = f'{self.card_text}', name = 'card_text_span', a = container)
            jp.Span(classes = 'mr-1 mb-1', text = f'{self.end_text}', name = 'end_text_span', a = container)

class Player(jp.Div):
    """Player component.

       Params: id: int, ID for the player, also player number.
               hand: list, The cards in the player's hand.
               card_knowledge: list, Current knowledge about a player's own cards.
               card_index: int, Index of the cards in the player's hand.
               current_player: int, ID of the current player.
               view: string, current view.
    """
    def __init__(self, **kwargs):
        self.id = 0
        self.hand = []
        self.card_knowledge = []
        self.card_index = 0
        self.current_player = -1
        self.view = ''
        self.state = None
        self.session = None
        super().__init__(**kwargs)
    
        container = jp.Div(classes = 'flex flex-col items-center text-center h-24', name = 'container', a = self)

        player_label = jp.Button(classes = f'{label_classes} mb-2', click = self.update_page, text = f'Player {self.id + 1}', name = 'player_label', a = container)
        player_label.set_classes('text-yellow-400') if self.current_player == self.id else None

        card_container = jp.Div(classes = 'flex flex-row items-center', name = 'card_container', a = container)

        """Draws cards based on view. 
           If viewed from the player's perspective, draw card knowledge instead, if there is any knowledge.
           Otherwise draw and show all cards.
        """
        for card in self.hand:
            if self.current_player == self.id:
                if self.view == 'agent':
                    card_knowledge_rank, card_knowledge_color = None, None
                    if len(self.card_knowledge) > 0:
                        card_knowledge_rank = self.card_knowledge[self.card_index].rank() 
                        card_knowledge_color = self.card_knowledge[self.card_index].color()

                    Card(rank = '?' if card_knowledge_rank == None else card_knowledge_rank + 1, 
                         color = 'gray' if card_knowledge_color == None else card_colors[card_knowledge_color], 
                         a = card_container)
                else:
                    Card(rank = card.rank()+1, color = card_colors[card.color()], a = card_container)
            else:
                Card(rank = card.rank()+1, color = card_colors[card.color()], a = card_container)
            self.card_index += 1

    async def update_page(self, event):
            """Update the GUI based on the current player.

            Args: state: state of the game.
                    session_id: string, ID of the current session.
                    page: WebPage, the webpage to be updated.
            """
            try:
                event_logger(self.session, 'a different player view')
                self.session['is_paused'] = True
                event.page.delete_components()
                latest_state = self.session['states'][0]
                view_state = self.state
                self.session['current_player'] = self.id
                MainPage(name = 'main_page', session = self.session, state = latest_state, view_state = view_state, a = event.page)
                await event.page.update()
            except Exception as err:
                print('The main page failed to update from Log.')
                print(err)

class ObserverViewBoard(jp.Div):
    """Game board class containing the game components.
    
       Params: state: state of a game, passed from the benchmark.
               session: dict, Current session of a client.
               current_player: int, Current player, first player is 0.
               num_players: int, Number of players.
               player_hands: list, Player hands where index number of the hand is a player.
               played_cards: list, Cards that have been played.
               discarded_cards: list, Cards that have been discarded.
               deck_size: int, Current size of the deck
               info_tokens: int, Current amount of information tokens.
               life_tokens: int, Current amount of life tokens.
               index: int, Counting integer keeping track of a player's position from the list table_position.
    """
    def __init__(self, **kwargs):
        self.state = None
        self.session = None
        self.current_player = -1
        self.num_players = 0
        self.player_hands = []
        self.played_cards = []
        self.discarded_cards = []
        self.deck_size = 0
        self.info_tokens = 0
        self.life_tokens = 0
        self.index = 0
        super().__init__(**kwargs)

        if self.state:
            self.player_hands = self.state.player_hands()
            self.played_cards = self.state.fireworks()
            self.discarded_cards = self.state.discard_pile()
            self.deck_size = self.state.deck_size()
            self.info_tokens = self.state.information_tokens()
            self.life_tokens = self.state.life_tokens()

            game_grid = jp.Div(classes = 'grid grid-cols-5 grid-rows-5', name = 'game_grid', a = self)

            for player_index, player_hand in enumerate(self.player_hands):
                player_position = table_positions[self.num_players]
                player_id = player_index
                row = player_position[self.index][0]
                col = player_position[self.index][1]

                Player(classes = f'row-start-{row} col-start-{col}', state = self.state, session = self.session, hand = player_hand, current_player = self.current_player, view = self.session['view'], id = player_id, a = game_grid)
                self.index += 1

            GameUtilities(classes = 'row-start-3 col-start-3', 
                        deck_size = self.deck_size, 
                        info_tokens = self.info_tokens, 
                        life_tokens = self.life_tokens,
                        name = 'game_utilities', 
                        a = game_grid)

            PlayedCards(classes = 'row-start-4 col-start-2', label_text = 'Played Cards', cards = self.played_cards, name = 'played_cards', a = game_grid)
            DiscardedCards(classes = 'row-start-4 col-start-4', label_text = 'Discarded Cards', cards = self.discarded_cards, name = 'discarded_cards', a = game_grid)

class AgentViewBoard(jp.Div):
    def __init__(self, **kwargs):
        self.state = None
        self.observation = None
        self.session = None
        self.current_player = -1
        self.num_players = 0
        self.card_knowledge = []
        self.observed_hands = []
        self.played_cards = []
        self.discarded_cards = []
        self.deck_size = 0
        self.info_tokens = 0
        self.life_tokens = 0
        self.latest_moves = []
        self.legal_moves = []
        super().__init__(**kwargs)

        if self.state:
            if self.current_player >= 0:
                self.observation = self.state.observation(self.current_player)
                self.card_knowledge = self.sort_cards(self.observation.card_knowledge(), self.observation.num_players())
                self.observed_hands = self.sort_cards(self.observation.observed_hands(), self.observation.num_players())
                self.played_cards = self.observation.fireworks()
                self.discarded_cards = self.observation.discard_pile()
                self.deck_size = self.observation.deck_size()
                self.info_tokens = self.observation.information_tokens()
                self.life_tokens = self.observation.life_tokens()
                self.latest_moves = self.observation.last_moves()
                self.legal_moves = self.observation.legal_moves()
                self.index = 0

            container = jp.Div(classes = f'{label_classes} flex flex-col', text = f'Player {self.current_player + 1} observations', name = 'container', a = self)
            game_grid = jp.Div(classes = 'grid grid-cols-5 grid-rows-5', name = 'game_grid', a = container)

            for player_index, player_hand in enumerate(self.observed_hands):
                player_id = player_index
                player_position = table_positions[self.num_players]
                row = player_position[self.index][0]
                col = player_position[self.index][1]
                knowledge = self.card_knowledge[player_id]
                Player(classes = f'row-start-{row} col-start-{col}', session = self.session, state = self.state, view = self.session['view'], hand = player_hand, card_knowledge = knowledge, id = player_id, current_player = self.current_player, a = game_grid)
                self.index += 1

            GameUtilities(classes = 'row-start-3 col-start-3', 
                          deck_size = self.deck_size, 
                          info_tokens = self.info_tokens, 
                          life_tokens = self.life_tokens,
                          name = 'game_utilities', 
                          a = game_grid)
            PlayedCards(classes = 'row-start-4 col-start-2', title = 'Played Cards', cards = self.played_cards, name = 'played_cards', a = game_grid)
            DiscardedCards(classes = 'row-start-4 col-start-4', title = 'Discarded Cards', cards = self.discarded_cards, name = 'discarded_card', a = game_grid)

            bottom_container = jp.Div(classes = 'flex justify-between border-t border-blue-500 m-10 p-5', name = 'bottom_container', a = container)
            LegalMoves(label_text = 'Legal Moves', moves = self.legal_moves, session = self.session, name = 'legal_moves', a = bottom_container)
            
            Log(classes = 'h-60 overflow-scroll', 
                label_text = 'Latest moves since this player\'s action',
                log_type = 'latest_moves_log',
                log_items = self.latest_moves,
                session = self.session,
                num_players = self.session['num_players'],
                current_player = self.current_player,
                name = 'latest_moves_log',
                a = bottom_container)

    def sort_cards(self, cards, num_players):
        """Sorts the cards in actual player order instead of the offset from the current observer
            
            Args: cards: list, List of cards to be sorted.
                    num_players: int, Number of players in the game.

            Returns: sorted_cards: list, List of sorted cards.
        """
        try:
            sorted_cards = []
            for i in range(0, num_players):
                player_index = (self.current_player + i) % num_players
                sorted_cards.insert(player_index, cards[i])
            return sorted_cards
        except Exception as err:
            print('Cards could not be sorted.')
            print('Exception: {}'.format(err))

class FrontPage(jp.Div):
    """Front page class."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def react(self, data):        
        self.delete_components()
        container = jp.Div(classes = 'flex flex-col flex-wrap content-center justify-center h-screen w-screen text-center', name = 'container', a = self)
        jp.Div(classes = 'text-5xl text-blue-500 font-bold uppercase border-b border-line border-blue-500 mb-10', 
               text = 'Hanabi Learning Environment',
               name = 'title',  
               a = container)
        button_container = jp.Div(name = 'button_container', a = container)
        jp.Link(classes = f'{button_classes}', text = 'Run benchmark', href = '/gui', name = 'link', a = button_container)

class MainPage(jp.Div):
    """Main page class containing the GUI components.

       Params: state: state of a game, passed from the benchmark.
               page: WebPage, The page which this component is instanced in, used for updating the page in the benchmark.
               session: dict, Current session of a client.
    """
    def __init__(self, **kwargs):
        self.state = None
        self.view_state = None
        self.session = None
        super().__init__(**kwargs)

        container = jp.Div(classes = 'flex flex-col h-screen', name='container', a = self)
        Menu(classes = 'border-b border-blue-500 mx-6 py-4', name = 'menu', session = self.session, a = container)
        # Render the game components only if the benchmark has started
        if self.state:
            middle_container = jp.Div(classes = 'grid grid-cols-3 h-screen mt-10', name = 'middle_container', a = container)
            board_container = jp.Div(classes = 'col-span-2', name = 'board_container', a = middle_container)
            if self.session['view'] == 'observer' or self.session['current_player'] == -1:
                ObserverViewBoard(name = 'board', 
                                  session = self.session, 
                                  num_players = self.session['num_players'], 
                                  current_player = self.session['current_player'], 
                                  state = self.state if self.view_state == None else self.view_state,
                                  a = board_container)
            elif self.session['view'] == 'agent':
                AgentViewBoard(name = 'board',
                               session = self.session, 
                               num_players = self.session['num_players'], 
                               current_player = self.session['current_player'], 
                               state = self.state if self.view_state == None else self.view_state, 
                               a = board_container)
            Log(classes = 'overflow-auto border-l border-blue-500 px-4 mb-10',
                name = 'states_log', 
                label_text = 'Previous moves', 
                log_type = 'states_log',
                log_items = self.state.move_history() if self.state != None else [], 
                session = self.session,
                num_players = self.session['num_players'],
                current_player = self.session['current_player'],
                a = middle_container)

class MyPage(jp.WebPage):
    def __init__(self, **kwargs):
        self.session = None
        super().__init__(**kwargs)
    
    async def on_disconnect(self, websocket=None):
        await super().on_disconnect()
        if self.session:
            self.session['is_running'] = False
            print("{} disconnected".format(self.session['id']))

def event_logger(session, event_string):
    print("{} clicked on {}.".format(session['id'], event_string))

def set_session(request):
  """Sets default session global variables.
     Appends to a sessionlist.
     
     Args: request: A request object.

     Returns: session: dict, client's session.
  """
  try:
    session_id = request.session_id
    if session_id not in sessions:
        wait_event = threading.Condition()
        stop_event = threading.Condition()
        sessions[session_id] = {'id': session_id,
                                'current_state': None,
                                'states': [],
                                'view': 'observer', 
                                'step_frequency': 1, 
                                'num_players': 5, 
                                'current_player': 0, 
                                'is_running': False, 
                                'is_paused': False, 
                                'wait_event': wait_event, 
                                }
    return sessions[session_id]
  except Exception as err:
      print('Failed to set this clients session variables.')
      print('Exception: {}'.format(err))
        
@jp.SetRoute('/gui')
def render_main_page(request):
  """Renderer for the main page displaying the benchmark.
     
     Args: request: A request object.

     Returns: main_page: WebPage for the GUI
  """
  try:
    main_page = MyPage(body_classes = 'bg-gray-900')

    session = set_session(request)
    event_logger(session, 'button run benchmark')

    main_page.session = session
    MainPage(name = 'main_page', session = session, a = main_page)
    return main_page
  except Exception as err:
      print('The main page failed to load.')
      print('Exception: {}'.format(err))
    
def render_front_page(request):
  """Renderer for the front page.
     
     Args: request: A request object.

     Returns: front_page: WebPage for the front page.
  """
  try:
    front_page = MyPage(body_classes = 'bg-gray-900')

    session = set_session(request)
    print("{} has connected".format(session['id']))

    FrontPage(name = 'front_page', a = front_page)
    return front_page
  except Exception as err:
      print('The front page failed to load.')
      print('Exception: {}'.format(err))

def run_game(game_parameters, session, page):
  """Play a game, selecting random actions."""

  async def update_page(state, session, page):
    """Update the GUI.

       Args: state: HanabiState, State of the game.
             session: dict, Client's session.
             page: WebPage, The webpage to be updated.
    """
    try:
        page.delete_components()
        if state.cur_player() != -1:
            session['current_player'] = state.cur_player()
        MainPage(name = 'main_page', session = session, state = state, a = page)
        await page.update()
    except Exception as err:
        print('The main page failed to update.')
        print('Exception: {}'.format(err))

  def set_current_state(state):
      copied_state = state.copy()
      session['states'].insert(0, copied_state)
      session['current_state'] = copied_state
  
  game = pyhanabi.HanabiGame(game_parameters)

  print('\nBenchmark started for session: {}\n'.format(session['id']))
  print(game.parameter_string(), end="")

  obs_encoder = pyhanabi.ObservationEncoder(
      game, enc_type=pyhanabi.ObservationEncoderType.CANONICAL)
  state = game.new_initial_state()
  
  while not state.is_terminal() and session['is_running']:
    with session['wait_event']:
        if session['is_paused']:
            session['wait_event'].wait()

        if state.cur_player() == pyhanabi.CHANCE_PLAYER_ID:
            state.deal_random_card()
            set_current_state(state)
            asyncio.run(update_page(state, session, page))
            if session['step_frequency'] > 0:
                session['wait_event'].wait(timeout=float(session['step_frequency']))
            continue
        
        legal_moves = state.legal_moves()
        move = np.random.choice(legal_moves)
        state.apply_move(move)

        set_current_state(state)        
        asyncio.run(update_page(state, session, page))
        if session['step_frequency'] > 0:
            session['wait_event'].wait(timeout=float(session['step_frequency']))

  session['is_running'] = False
  asyncio.run(update_page(state, session, page))

  print("Stopping benchmark...")
  with session['wait_event']:
    session['wait_event'].wait(timeout=600)
  print('Benchmark finished.')

if __name__ == "__main__":
  # Check that the cdef and library were loaded from the standard paths.
  assert pyhanabi.cdef_loaded(), "cdef failed to load"
  assert pyhanabi.lib_loaded(), "lib failed to load"

  jp.justpy(render_front_page)
  
