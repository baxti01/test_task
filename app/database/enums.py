import enum


class UserRole(enum.Enum):
    DIRECTOR = 'DIRECTOR'
    ADMIN = 'ADMIN'
    WORKER = 'WORKER'
    CUSTOMER = 'CUSTOMER'


class UnitOfMeasureType(enum.Enum):
    KILOGRAM = 'KILOGRAM'
    PIECES = 'PIECES'


class TransactionType(enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'


class BalanceType(enum.Enum):
    user = "user"
    company = "company"
