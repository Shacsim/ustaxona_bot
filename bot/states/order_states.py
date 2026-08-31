"""FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_name = State()


class NewOrderStates(StatesGroup):
    waiting_order_number = State()
    confirming_order = State()


class CompleteOrderStates(StatesGroup):
    waiting_order_number = State()
    waiting_work_description = State()
    waiting_price = State()
    confirming = State()


class SearchStates(StatesGroup):
    waiting_order_number = State()
