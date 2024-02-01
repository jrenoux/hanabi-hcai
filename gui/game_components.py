import justpy as jp
label_classes = 'block uppercase text-gray-500 text-xs font-bold'
card_colors = [ 'red', 'yellow', 'green', 'white', 'blue' ] 

class Card(jp.Div):
    """Card component.
    
       Params: rank: int, Rank of the card.
               color: string, Color of the card.
    """
    def __init__(self, **kwargs):
        self.rank = 0
        self.color = ''
        super().__init__(**kwargs)

        color = self.color if self.color == 'white' else self.color + '-500'
        card = jp.Div(classes = f'w-8 bg-{color} border-2 border-solid border-{self.color}-700 rounded text-center mr-1 py-2', name = 'card', a = self)
        jp.Label(classes = f'font-bold text-{self.color}-700', text = f'{self.rank}', name = 'label', a = card)

class DiscardedCards(jp.Div):
    """Discarded Cards component.
       Shows stacks of cards in a grid.

       Params: label_text: string, Lead text for the label.
               cards: list, List of played cards. 
               card_index: int, Index counter for card positions in the grid.
    """
    def __init__(self, **kwargs):
        self.label_text = ''
        self.cards = []
        self.card_index = 0
        super().__init__(**kwargs)

        container = jp.Div(classes = 'grid grid-rows-2 grid-cols-5 text-center', name = 'container', a = self)
        jp.Label(classes = f'{label_classes} col-span-5', text = self.label_text, name = 'label', a = container)

        color_sorted_cards = self.sort_cards(self.cards)
        for color_position in color_sorted_cards:
            card_container = jp.Div(classes = f'col-start-{color_position + 1}', a = container)
            transform_counter = 0
            for card in color_sorted_cards[color_position]:
                Card(classes = f'absolute transform translate-y-{transform_counter}', 
                     rank = card.rank()+1, 
                     color = card_colors[card.color()], 
                     a = card_container)           
                transform_counter += 8

    def sort_cards(self, cards):
        """Sorts the cards based on the card color as keys in the dictionary.

            Args: cards: list, List of cards to sort.

            Returns: color_sorted_cards: dict, keys being card color index and values are list of cards.
        """
        color_sorted_cards = {0: [], 1: [], 2: [], 3: [], 4: []}
        for card in cards:
            color_sorted_cards[card.color()].append(card)
        return color_sorted_cards
        
class PlayedCards(jp.Div):
    """Played Cards component.
       Shows stacks of cards in a grid.

       Params: label_text: string, Lead text for the label.
               cards: list, List of played cards. 
               card_index: int, Index counter for card positions in the grid.
    """
    def __init__(self, **kwargs):
        self.label_text = ''
        self.cards = []
        self.card_index = 0
        super().__init__(**kwargs)

        container = jp.Div(classes = 'grid grid-rows-2 grid-cols-5 text-center', name = 'container', a = self) 
        jp.Label(classes = f'{label_classes} col-span-5', text = self.label_text, name = 'label', a = container)
        for card in self.cards:
            card_container = jp.Div(classes = f'col-start-{self.card_index + 1} mr-4', a = container)
            for i in range(0, card):
                Card(classes = f'absolute transform translate-y-{i}', 
                     rank = card, 
                     color = f'{card_colors[self.card_index]}', 
                     a = card_container)
            self.card_index += 1

class GameUtilities(jp.Div):
    """Game utilities class.
       Contains the deck, info and life token components.
    
       Params: state: state of a game, passed from the benchmark.
               page: WebPage, The page which this component is instanced in, used for updating the page in the benchmark.
               session: dict, Current session of a client.
               session_id: string, ID of the current session. 
    """
    def __init__(self, **kwargs):
        self.deck_size = 0
        self.info_tokens = 0
        self.life_tokens = 0
        super().__init__(**kwargs)
        
        container = jp.Div(classes = 'flex items-start justify-center', name = 'container', a = self)
        Deck(deck_size = self.deck_size, name = 'deck', a = container)
        Token(token_type = 'Info', value = self.info_tokens, name = 'life_token', a = container)
        Token(token_type = 'Life', value = self.life_tokens, name = 'info_token', a = container)

class Deck(jp.Div):
    """Deck component.
        Shows a stack of cards.
        
        Params: deck_size: int, Size of the deck.
    """
    def __init__(self, **kwargs):
        self.deck_size = 0
        super().__init__(**kwargs)

        container = jp.Div(classes = 'flex flex-col items-center text-center', name = 'container', a = self)
        jp.Label(classes = f'{label_classes}', text = 'Deck', name = 'label', a = container)
        card_container = jp.Div(classes = 'flex flex-col items-center', name = 'card_container', a = container)
        for i in range(0,3):
            Card(classes = f'absolute transform translate-y-{i}', rank = self.deck_size, color = 'gray', a = card_container)

class Token(jp.Div):
    """Token component.
        Shows a round of token.
        
        Params: token_type: string, Type of token.
                value: int, Value of token.
    """
    def __init__(self, **kwargs):
        self.token_type = ''
        self.value = 0
        super().__init__(**kwargs)

        self.color = 'indigo' if self.token_type == 'Info' else 'red' 
        container = jp.Div(classes = 'flex flex-col justify-center text-center ml-1', name = 'container', a = self)
        jp.Label(classes = f'{label_classes}', text = f'{self.token_type}', name = 'label', a = container)

        token = jp.Div(classes = f'w-10 bg-{self.color}-500 border-2 border-solid border-{self.color}-900 rounded-full py-1', name = 'token', a = container)
        jp.Label(classes = f'text-sm font-bold text-{self.color}-900', text = f'{self.value}', name = 'token_label', a = token)
