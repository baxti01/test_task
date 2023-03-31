import enum


class UserRole(enum.Enum):
    DIRECTOR = 'DIRECTOR'
    ADMIN = 'ADMIN'
    WORKER_DIRECTOR = 'WORKER_DIRECTOR'
    WORKER_ADMIN = 'WORKER_ADMIN'
    WORKER_USER = 'WORKER_USER'
    CUSTOMER = 'CUSTOMER'


class UnitOfMeasureType(enum.Enum):
    KILOGRAM = 'KILOGRAM'
    PIECES = 'PIECES'


class TransactionType(enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'


class BalanceType(enum.Enum):
    USER = "user"
    COMPANY = "company"
