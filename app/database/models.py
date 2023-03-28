from datetime import datetime

from sqlalchemy import Integer, Column, String, Numeric, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.enums import UserRole, UnitOfMeasureType, TransactionType


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum(UserRole))

    company_id = Column(Integer, ForeignKey("company.id", ondelete='SET NULL'))
    company = relationship('Company', back_populates='users')

    workers = relationship('Worker', back_populates='company')

    balance = relationship('Balance', back_populates='user', uselist=False)


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    user = relationship('User', back_populates='company')

    workers = relationship('Worker', back_populates='company')

    finance = relationship('Finance', back_populates='company')

    balance = relationship('Balance', back_populates='company', uselist=False)

    budget = relationship('Budget', back_populates='company', uselist=False)


class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    user = relationship('User', back_populates='workers')

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='workers')


class Balance(Base):
    __tablename__ = 'balance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    balance = Column(Numeric(20, 3))

    history = relationship('BalanceHistory', back_populates='balance')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='balance')

    company_id = Column(Integer, ForeignKey('company.id', ondelete="CASCADE"), nullable=True)
    company = relationship('Company', back_populates='balance')


class BalanceHistory(Base):
    __tablename__ = 'balance_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    prev_balance = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)
    transaction_type = Column(Enum(TransactionType))
    amount = Column(Numeric(20, 3))

    balance_id = Column(Integer, ForeignKey('balance.id', ondelete='CASCADE'))
    balance = relationship('Balance', back_populates='history')

    invoice_id = Column(Integer, ForeignKey('invoices.id', ondelete='SET NULL'))


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    purchase_price = Column(Numeric(20, 3))
    sale_price = Column(Numeric(20, 3))
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(Enum(UnitOfMeasureType), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)

    invoice = relationship('Invoice', back_populates='products')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller = Column(Integer, nullable=False)
    buyer = Column(Integer, nullable=False)
    to_pay = Column(Numeric(20, 3))
    paid = Column(Numeric(20, 3))
    debt = Column(Numeric(20, 3))
    date = Column(DateTime, nullable=False, default=datetime.now)

    products_id = Column(Integer, ForeignKey('products.id', ondelete='SET NULL'))
    products = relationship('Products', back_populates='invoice')

    # balance_id = Column(Integer, ForeignKey('balance.id', ondelete='CASCADE'))
    # balance = relationship('Balance', back_populates='operations')


class Finance(Base):
    # Expense and Income table
    __tablename__ = 'finances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)
    transaction_type = Column(Enum(TransactionType))

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='finances')

    budget_id = Column(Integer, ForeignKey('budget.id', ondelete='SET NULL'))
    budget = relationship('Budget', back_populates='finances')


class Budget(Base):
    __tablename__ = 'budget'

    id = Column(Integer, primary_key=True, autoincrement=True)
    income = Column(Numeric(20, 3))
    expense = Column(Numeric(20, 3))
    debt = Column(Numeric(20, 3))
    profit = Column(Numeric(20, 3))

    history = relationship('BudgetHistory', back_populates='budget')

    finance = relationship('Finance', back_populates='budget')

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='budget')


class BudgetHistory(Base):
    __tablename__ = 'budget_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    income = Column(Numeric(20, 3))
    expense = Column(Numeric(20, 3))
    debt = Column(Numeric(20, 3))
    profit = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)
    transaction_type = Column(Enum(TransactionType))
    amount = Column(Numeric(20, 3))

    budget_id = Column(Integer, ForeignKey('budget.id', ondelete='CASCADE'))
    budget = relationship('Budget', back_populates='history')
