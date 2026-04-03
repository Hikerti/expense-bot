from aiogram.fsm.state import State, StatesGroup


class AddExpense(StatesGroup):
    parsing = State()
    ask_category = State()
    ask_account = State()
    ask_tranche = State()
    ask_recurring = State()
    confirm = State()