"""FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_name = State()


class NewOrderStates(StatesGroup):
    # Tartib: telefon → ism → nima qilish kerak → tasdiqlash
    waiting_customer_phone = State()
    waiting_customer_name = State()
    waiting_description = State()
    confirming_order = State()


class CompleteOrderStates(StatesGroup):
    waiting_order_number = State()
    waiting_work_description = State()
    waiting_price = State()
    confirming = State()


class SearchStates(StatesGroup):
    waiting_order_number = State()


class InventoryStates(StatesGroup):
    waiting_name = State()
    waiting_qty = State()
    waiting_price = State()
    confirming = State()


class ReminderStates(StatesGroup):
    waiting_time = State()


class BroadcastStates(StatesGroup):
    waiting_content = State()
    confirming = State()
