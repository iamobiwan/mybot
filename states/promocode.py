from aiogram.dispatcher.filters.state import State, StatesGroup


class PromocodeStates(StatesGroup):
    promocode = State()