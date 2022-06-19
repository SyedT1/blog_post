from piccolo.table import Table
from piccolo.columns import Varchar, Float, Timestamp
from piccolo.columns.column_types import TimestampNow

class Expense(Table):
    amount = Float()
    description = Varchar()
    category = Varchar()
    date = Timestamp(TimestampNow())



class ExpenseIn(Table):
    amount = Float()
    description = Varchar()
    category = Varchar()

