# Code for non-interest bearing loans
import json
import customtkinter as tk
import tkinter as otk


class Loan(object):
    def __init__(self, id, memo, amount, term, remaining, save=False):
        self.id = id
        self.memo = memo
        self.amount = amount  # start amount
        self.term = term  # in months
        self.remaining = remaining  # remaining amount
        self.monthlyPayment = self.monthly_payment()

        if save:
            self.save_loan()

    def monthly_payment(self):
        return round((self.amount / self.term), 2)

    def save_loan(self):
        # check if loan already exists
        try:
            get_loan(self.id)
            print('Loan already exists...')
            print('Backing up loan...')
            f = open('loans.txt', 'r')
            fw = open('loans_backup.txt', 'w')
            fw.write(f.read())
            f.close()
            fw.close()
            print('Loan backed up')
            print('Removing old loan...')
            self.remove_loan()
            print('Old loan removed')
        except Exception as e:
            print(e)
            pass
        # save loan to file
        with open('loans.txt', 'a') as f:
            newLoan = self.to_dict()
            f.write(json.dumps(newLoan) + '\n')

    def to_dict(self):
        return {
            'id': self.id,
            'memo': self.memo,
            'amount': self.amount,
            'term': self.term,
            'monthlyPayment': self.monthlyPayment,
            'remaining': self.remaining
        }

    def remove_loan(self):
        # remove loan from file
        with open('loans.txt', 'r') as f:
            loans = f.readlines()
        with open('loans.txt', 'w') as f:
            for loan in loans:
                loan = json.loads(loan)
                if loan['id'] != self.id:
                    f.write(json.dumps(loan) + '\n')

    def make_payment(self, amount):
        print('Start Remaining: ' + str(self.remaining))
        print('Making payment of ' + str(amount))
        if amount > self.remaining:
            print('Amount exceeds remaining balance')
            return self.remaining
        self.remaining -= amount
        if self.remaining == 0:
            # ISSUE: Causes errors with UI
            print('Loan paid off')
            self.remove_loan()
        else:
            print('Remaining balance: ' + str(self.remaining))
            self.save_loan()
        return self.remaining


def get_loans():
    f = open('loans.txt', 'r')
    loans = f.readlines()
    f.close()
    return loans


def get_loan(id):
    loans = get_loans()
    for loan in loans:
        loan = json.loads(loan)
        if loan['id'] == id:
            return loan
    raise Exception('Loan not found')


def import_loan(id):
    loan = get_loan(id)
    memo = loan['memo']
    amount = loan['amount']
    term = loan['term']
    remaining = loan['remaining']
    return Loan(id, memo, amount, term, remaining, True)


def runTests():
    print('Welcome to the loan app')
    print('ID: 1')
    print('Memo: Car loan')
    print('Amount: 10000')
    print('Term: 12')
    print('Creating loan...')
    loan = Loan(1, 'Car loan', 10000, 12, True)
    print('Loan created')
    print('Making payment... [$5000]')
    loan.make_payment(5000)
    print('Saving loan...')
    loan.save_loan()
    print('Closing app...')
    print('Goodbye')
    exit()


def create_loan(id, memo, amount, term, save=False):
    # check if already exists
    try:
        get_loan(id)
        print('Loan already exists...')
        return
    except Exception as e:
        print(e)
        pass
    # check if memo already exists
    if checkMemoExists(memo):
        print('Loan already exists...')
        return
    # create loan
    id = generate_id()
    output = Loan(id, memo, amount, term, amount, save)
    output.save_loan()
    return output


def get_loan_obj(id):
    loanDict = get_loan(id)
    return Loan(
        loanDict['id'],
        loanDict['memo'],
        loanDict['amount'],
        loanDict['term'],
        loanDict['remaining'],
        True
    )


def generate_id():
    loans = get_loans()
    if not loans:
        return 1
    else:
        return int(json.loads(loans[-1])['id']) + 1


def checkMemoExists(memo):
    loans = get_loans()
    for loan in loans:
        loan = json.loads(loan)
        if loan['memo'] == memo:
            return True
    return False


class LoanAppGUI(tk.CTk):
    def __init__(self):
        super().__init__()
        tk.set_appearance_mode('system')
        tk.set_default_color_theme('green')

        root = tk.CTk()
        root.title('Loan App')
        root.geometry('800x800')

        frame = tk.CTkFrame(master=root)
        frame.pack(pady=20, padx=60, fill="both", expand=True)

        mainLabel = tk.CTkLabel(
            master=frame,
            text='Loan App',
            font=('Roboto', 24)
        )
        mainLabel.pack(pady=12, padx=10)

        self.loanListbox = otk.Listbox(
            master=frame,
            font=('Roboto', 12),
            bg='#3c3c3c',
            width=100,
            height=10,
            bd=0,
            highlightthickness=0,
            fg='white'
        )
        self.loanListbox.pack(pady=12, padx=10)

        self.loanInfoFrame = tk.CTkFrame(master=frame)
        self.loanInfoFrame.pack(pady=12, padx=10)

        self.loanInfoLabel = tk.CTkLabel(
            master=self.loanInfoFrame,
            text='Loan Info',
            font=('Roboto', 16)
        )
        self.loanInfoLabel.pack(pady=12, padx=10)

        self.loanInfoText = tk.CTkTextbox(
            master=self.loanInfoFrame,
            font=('Roboto', 16),
            width=250
        )
        self.loanInfoText.pack(pady=12, padx=10)

        self.makePaymentButton = tk.CTkButton(
            master=self.loanInfoFrame,
            text='Make Payment',
            font=('Roboto', 16),
            command=self.makePayment
        )
        self.makePaymentButton.pack(pady=12, padx=10)

        self.addLoanButton = tk.CTkButton(
            master=frame, text='Add Loan',
            font=('Roboto', 16),
            command=self.openAddLoanWindow
        )
        self.addLoanButton.pack(pady=12, padx=10)

        self.exitButton = tk.CTkButton(
            master=frame, text='Exit',
            font=('Roboto', 16),
            hover_color='red',
            command=root.quit
        )
        self.exitButton.pack(pady=12, padx=10)

        loans = get_loans()
        self.idLookup = {}
        for loan in loans:
            loan = json.loads(loan)
            self.loanListbox.insert('end', loan['memo'])
            self.idLookup[loan['memo']] = loan['id']

        self.loanListbox.bind('<<ListboxSelect>>', self.show_loan_info)

        root.mainloop()

    def show_loan_info(self, event):
        data = self.get_selected_data()
        loan = get_loan(self.idLookup[data])
        # update loan info text
        self.loanInfoText.delete('1.0', 'end')
        self.loanInfoText.insert('end', 'ID: ' + str(loan['id']) + '\n')
        self.loanInfoText.insert('end', 'Memo: ' + loan['memo'] + '\n')
        self.loanInfoText.insert('end', f"Amount: ${loan['amount']:,.2f}\n")
        self.loanInfoText.insert('end', 'Term: ' + str(loan['term']) + '\n')
        self.loanInfoText.insert(
            'end',
            f"Monthly Payment: ${loan['monthlyPayment']:,.2f}\n"
        )
        self.loanInfoText.insert(
            'end',
            f"Remaining: ${loan['remaining']:,.2f}"
        )

    def get_selected_data(self):
        selection = self.loanListbox.curselection()
        if selection:
            index = selection[0]
            data = self.loanListbox.get(index)
            return data

    def addLoan(self, id, memo):
        """This method is meant to load an already created loan to the UI
        since there is no way to handle state in the UI

        Args:
            id (int): id of the loan
            memo (str): memo of the loan
        """
        self.idLookup[memo] = id
        self.loanListbox.insert('end', memo)

    def openAddLoanWindow(self):
        LoanAppAddLoanGUI(self)

    def makePayment(self):
        dialog = tk.CTkInputDialog(
            text='Enter payment amount',
            title='Make Payment',
            font=('Roboto', 16)
        )
        amount = dialog.get_input()
        if not amount:
            return
        memo = self.get_selected_data()
        id = self.idLookup[memo]
        loan = get_loan_obj(id)
        if loan.make_payment(float(amount)) == 0:
            self.loanListbox.delete(self.loanListbox.curselection())
            # clear loan info
            self.loanInfoText.delete('1.0', 'end')
        else:
            self.show_loan_info(None)


class LoanAppAddLoanGUI(tk.CTkToplevel):
    def __init__(self, mainAppUI):
        super().__init__()

        tk.set_appearance_mode('system')
        tk.set_default_color_theme('green')

        self.title('Add Loan')
        self.geometry('500x800')

        self.mainAppUI = mainAppUI

        frame = tk.CTkFrame(master=self)
        frame.pack(pady=20, padx=60, fill="both", expand=True)

        mainLabel = tk.CTkLabel(
            master=frame,
            text='Add Loan',
            font=('Roboto', 24)
        )
        mainLabel.pack(pady=12, padx=10)

        memoLabel = tk.CTkLabel(
            master=frame,
            text='Memo:',
            font=('Roboto', 16)
        )
        memoLabel.pack(pady=12, padx=10)

        self.memoEntry = tk.CTkEntry(master=frame, font=('Roboto', 16))
        self.memoEntry.pack(pady=12, padx=10)

        amountLabel = tk.CTkLabel(
            master=frame,
            text='Amount:',
            font=('Roboto', 16)
        )
        amountLabel.pack(pady=12, padx=10)

        self.amountEntry = tk.CTkEntry(master=frame, font=('Roboto', 16))
        self.amountEntry.pack(pady=12, padx=10)

        termLabel = tk.CTkLabel(
            master=frame,
            text='Term:',
            font=('Roboto', 16)
        )
        termLabel.pack(pady=12, padx=10)

        self.termEntry = tk.CTkEntry(master=frame, font=('Roboto', 16))
        self.termEntry.pack(pady=12, padx=10)

        saveButton = tk.CTkButton(
            master=frame, text='Save', font=('Roboto', 16),
            command=self.save_loan
        )
        saveButton.pack(pady=12, padx=10)

        cancelButton = tk.CTkButton(
            master=frame, text='Cancel', font=('Roboto', 16),
            command=self.destroy
        )
        cancelButton.pack(pady=12, padx=10)

    def save_loan(self):
        id = 0  # id will be generated later
        memo = self.memoEntry.get()
        amount = float(self.amountEntry.get())
        term = int(self.termEntry.get())
        loan = create_loan(id, memo, amount, term, True)
        self.mainAppUI.addLoan(loan.id, memo)
        self.destroy()


def main():
    # runTests()
    LoanAppGUI()


if __name__ == '__main__':
    main()
