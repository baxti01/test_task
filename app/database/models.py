from datetime import datetime

from sqlalchemy import Integer, Column, String, Numeric, ForeignKey, DateTime, Float, Enum, Boolean
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

    worker_id = Column(Integer, ForeignKey("workers.id", ondelete='SET NULL'))
    worker = relationship('Worker', back_populates='users')
    invoices = relationship('Invoice', back_populates='users')

    balance = relationship('Balance', back_populates='user',
                           uselist=False, cascade="all, delete")


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship('User', back_populates='company')

    workers = relationship('Worker', back_populates='company',
                           cascade="all, delete")

    finances = relationship('Finance', back_populates='company',
                            cascade="all, delete")

    invoices = relationship('Invoice', back_populates='company')

    balance = relationship('Balance', back_populates='company',
                           uselist=False, cascade="all, delete")

    budget = relationship('Budget', back_populates='company',
                          uselist=False, cascade="all, delete")


class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    users = relationship('User', back_populates='worker')
    invoices = relationship('Invoice', back_populates='worker')

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='workers')


class Finance(Base):
    # Expense and Income table
    __tablename__ = 'finances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)
    transaction_type = Column(Enum(TransactionType))

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='finances')

    budget = relationship('Budget', back_populates='finance', uselist=False)
    budget_history = relationship('BudgetHistory', back_populates='finance',
                                  uselist=False)

    balance = relationship('Balance', back_populates='finance', uselist=False)
    balance_history = relationship('BalanceHistory', back_populates='finance',
                                   uselist=False)


class Budget(Base):
    __tablename__ = 'budget'

    id = Column(Integer, primary_key=True, autoincrement=True)
    income = Column(Numeric(20, 3))
    expense = Column(Numeric(20, 3))
    profit = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)

    history = relationship('BudgetHistory', back_populates='budget',
                           cascade="all, delete")

    finance_id = Column(Integer, ForeignKey('finances.id', ondelete='SET NULL'))
    finance = relationship('Finance', back_populates='budget')

    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))
    company = relationship('Company', back_populates='budget')


class BudgetHistory(Base):
    __tablename__ = 'budget_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    income = Column(Numeric(20, 3))
    expense = Column(Numeric(20, 3))
    profit = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)
    transaction_type = Column(Enum(TransactionType))
    amount = Column(Numeric(20, 3))

    finance_id = Column(Integer, ForeignKey('finances.id', ondelete='SET NULL'))
    finance = relationship('Finance', back_populates='budget_history')

    budget_id = Column(Integer, ForeignKey('budget.id', ondelete='CASCADE'))
    budget = relationship('Budget', back_populates='history')


class Balance(Base):
    __tablename__ = 'balance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    balance = Column(Numeric(20, 3))
    date = Column(DateTime, default=datetime.now)

    history = relationship('BalanceHistory', back_populates='balance', cascade="all, delete")

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='balance')

    company_id = Column(Integer, ForeignKey('company.id', ondelete="CASCADE"), nullable=True)
    company = relationship('Company', back_populates='balance')

    invoice_id = Column(Integer, ForeignKey('invoices.id', ondelete='SET NULL'))
    invoice = relationship('Invoice', back_populates='balance')

    finance_id = Column(Integer, ForeignKey('finances.id', ondelete='SET NULL'))
    finance = relationship('Finance', back_populates='balance')


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
    invoice = relationship('Invoice', back_populates='balance_history')

    finance_id = Column(Integer, ForeignKey('finances.id', ondelete='SET NULL'))
    finance = relationship('Finance', back_populates='balance_history')


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_pay = Column(Numeric(20, 3))
    date = Column(DateTime, nullable=False, default=datetime.now)

    products = relationship('Product', secondary='invoices_products',
                            back_populates='invoices')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    users = relationship('User', back_populates='invoices')

    worker_id = Column(Integer, ForeignKey('workers.id', ondelete='SET NULL'))
    worker = relationship('Worker', back_populates='invoices')

    company_id = Column(Integer, ForeignKey('company.id', ondelete='SET NULL'))
    company = relationship('Company', back_populates='invoices')

    balance = relationship('Balance', back_populates='invoice', uselist=False)
    balance_history = relationship('BalanceHistory', back_populates='invoice',
                                   uselist=False)


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    purchase_price = Column(Numeric(20, 3))
    sale_price = Column(Numeric(20, 3))
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(Enum(UnitOfMeasureType), nullable=False)
    sale_quantity = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)

    invoices = relationship('Invoice', secondary='invoices_products',
                            back_populates='products')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'))


class InvoiceProduct(Base):
    __tablename__ = 'invoices_products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    # quantity = Column(Float, nullable=False)
