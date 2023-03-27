import enum


class UserRole(enum.Enum):
    ADMIN = 'ADMIN'
    WORKER = 'WORKER'
    CUSTOMER = 'CUSTOMER'
    ANONIM = 'ANONIM'


class UnitOfMeasureType(enum.Enum):
    KILOGRAM = 'KILOGRAM'
    PIECES = 'PIECES'


class TransactionType(enum.Enum):
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
