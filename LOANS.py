from datetime import date, timedelta
import json

# Clase principal
# Valida que el el monto del préstamo, la tasa de interés y 
# el plazo no sean negativos y arroja un error si lo son
class Loan:
    def __init__(self, principal, interest_rate, tenure, start_date):
        if principal < 0:
            raise ValueError("Principal cannot be negative")
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if tenure < 0:
            raise ValueError("Tenure cannot be negative")
        self._principal = principal
        self._interest_rate = interest_rate
        self._tenure = tenure
        self._start_date = start_date
        self._repayments = []

    # Definir un método getter que permite acceder a un atributo 
    # privado de una clase como si fuera un atributo público. 
    @property
    def principal(self):
        return self._principal

    @principal.setter
    def principal(self, value):
        if value < 0:
            raise ValueError("Principal cannot be negative")
        self._principal = value

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, value):
        if value < 0:
            raise ValueError("Interest rate cannot be negative")
        self._interest_rate = value

    # Para asegurarse de que TODAS las subclases calculen los intereses, 
    # el calendario de pafos y los detalles del préstamo
    def calculate_interest(self):
        raise NotImplementedError("Subclasses must implement this method")

    def repayment_schedule(self):
        raise NotImplementedError("Subclasses must implement this method")

    def add_repayment(self, amount, repayment_date):
        if amount < 0:
            raise ValueError("Repayment amount cannot be negative")
        if repayment_date < self._start_date:
            raise ValueError("Repayment date cannot be before the start date")
        self._repayments.append((amount, repayment_date))

    def remaining_balance(self):
        total_paid = sum(amount for amount, _ in self._repayments)
        return self._principal - total_paid

    def calculate_penalties(self, overdue_days):
        if overdue_days < 0:
            raise ValueError("Overdue days cannot be negative")
        return overdue_days * 0.01 * self._principal  # 1% of principal per day

    def generate_report(self):
        return {
            "Principal": self._principal,
            "Interest": self.calculate_interest(),
            "Remaining Balance": self.remaining_balance(),
            "Repayment Schedule": self.repayment_schedule(),
        }

# Subclases 
class PersonalLoan(Loan):
    def calculate_interest(self):
        return self._principal * self._interest_rate * self._tenure / 12
    
    # Pagos mensuales
    def repayment_schedule(self):
        schedule = []
        for month in range(self._tenure):
            schedule.append(self._start_date + timedelta(days=30 * month))
        return schedule

class MortgageLoan(Loan):
    def calculate_interest(self):
        return self._principal * (1 + self._interest_rate / 12) ** self._tenure - self._principal

    # Pagos quincenales
    def repayment_schedule(self):
        schedule = []
        for week in range(self._tenure * 2):
            schedule.append(self._start_date + timedelta(days=14 * week))
        return schedule

class CarLoan(Loan):
    def calculate_interest(self):
        return self._principal * self._interest_rate * self._tenure / 12
    
    # Pagos mensuales
    def repayment_schedule(self):
        schedule = []
        for month in range(self._tenure):
            schedule.append(self._start_date + timedelta(days=30 * month))
        return schedule

# Clientes
class Customer:
    def __init__(self, name, customer_id, contact_info):
        self.name = name
        self.customer_id = customer_id
        self.contact_info = contact_info
        self.loans = []

    def view_loan_details(self):
        # Solo muestra los detalles del préstamo y el calendario de pagos
        return [
            {
                "Principal": loan.principal,
                "Interest": loan.calculate_interest(),
                "Remaining Balance": loan.remaining_balance(),
                "Repayment Schedule": loan.repayment_schedule(),
            }
            for loan in self.loans
        ]
class Administrator:
    def __init__(self, name, admin_id):
        self.name = name
        self.admin_id = admin_id
        self.customers = []

    def add_customer(self, customer):
        self.customers.append(customer)

    def add_loan_to_customer(self, customer_id, loan):
        # Busca al cliente por su ID y le agrega un préstamo
        for customer in self.customers:
            if customer.customer_id == customer_id:
                customer.loans.append(loan)
                return f"Préstamo agregado al cliente {customer.name}."
        return "Cliente no encontrado."

    def update_loan_details(self, customer_id, loan_index, new_principal=None, new_interest_rate=None):
        # Actualiza los detalles de un préstamo específico de un cliente
        for customer in self.customers:
            if customer.customer_id == customer_id:
                if 0 <= loan_index < len(customer.loans):
                    loan = customer.loans[loan_index]
                    if new_principal is not None:
                        loan.principal = new_principal
                    if new_interest_rate is not None:
                        loan.interest_rate = new_interest_rate
                    return f"Detalles del préstamo actualizados para el cliente {customer.name}."
                return "Índice de préstamo no válido."
        return "Cliente no encontrado."

    def generate_reports(self):
        # Genera un reporte de todos los préstamos de todos los clientes
        reports = []
        for customer in self.customers:
            for loan in customer.loans:
                reports.append({
                    "Customer": customer.name,
                    "Loan Details": loan.generate_report(),
                })
        return reports

# Guardar y cargar datos en un archivo JSON
class DataStore:
    @staticmethod
    def save_data(filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file, default=str)  # Convierte fechas a strings

    @staticmethod
    def load_data(filename):
        with open(filename, 'r') as file:
            return json.load(file)

