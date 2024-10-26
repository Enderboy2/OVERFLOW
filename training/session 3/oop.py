class account:
    def __init__(self,i):
        self.__balance = i
        self.account_type = "generic"
    def __str__(self):
        return "this is a bank acount"
    def deposit(self,i):
        self.__balance += i
    def withdraw(self,i):
        self.__balance -= i
    def get_balance(self):
        return self.__balance
    

jo = account(100)
jo.deposit(20)
jo.withdraw(5)
print(jo.get_balance())
print(jo)

del jo
