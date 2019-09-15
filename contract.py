"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


def ceiling(x: float) -> int:
    """return the smallest integer that is greater than or equal to x"""
    if x > int(x):
        return int(x) + 1
    else:
        return int(x)


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(call.duration)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """
    TermContract, a subclass of Contract

    === Public Attributes ===
    start:
         starting date for the contract
    end:
        ending date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    end: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date, end: datetime.datetime) -> None:
        Contract.__init__(self, start)
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(TERM_MONTHLY_FEE + TERM_DEPOSIT)
        else:
            bill.add_fixed_cost(TERM_MONTHLY_FEE)
        self.start = datetime.date(year, month, self.start.day)
        bill.set_rates("TERM", TERM_MINS_COST)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        if self.bill.free_min < TERM_MINS:
            if self.bill.free_min + ceiling(call.duration/60) <= TERM_MINS:
                self.bill.add_free_minutes(ceiling(call.duration/60))
            else:
                self.bill.add_billed_minutes(self.bill.free_min +
                                             ceiling(call.duration/60)
                                             - TERM_MINS)
                self.bill.free_min = TERM_MINS
        else:
            self.bill.add_billed_minutes(ceiling(call.duration/60))

    def cancel_contract(self) -> float:
        if self.start >= self.end:
            self.start = None
            return self.bill.get_cost() - TERM_DEPOSIT
        else:
            self.start = None
            return self.bill.get_cost()


class MTMContract(Contract):
    """
    Month-TO-Month Contract, a subclass of Contract

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.start = datetime.date(year, month, self.start.day)
        bill.set_rates("MTM", MTM_MINS_COST)
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        self.bill.add_billed_minutes(ceiling(call.duration / 60))


class PrepaidContract(Contract):
    """
    Prepaid Contract, a subclass of Contract

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    balance:
        positive balance is how much the customer owes
        negative balance is how much the customer has prepaid
    """
    start: datetime.datetime
    bill: Optional[Bill]
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        Contract.__init__(self, start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.start = datetime.date(year, month, self.start.day)
        if self.balance > -10:
            bill.add_fixed_cost(-25)
        bill.add_fixed_cost(self.balance)
        self.balance = PREPAID_MINS_COST * bill.billed_min + bill.fixed_cost
        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        self.bill.add_billed_minutes(ceiling(call.duration / 60))
        self.balance += PREPAID_MINS_COST * self.bill.billed_min

    def cancel_contract(self) -> float:
        self.start = None
        if self.balance > 0:
            return self.bill.get_cost()
        else:
            return 0




if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
