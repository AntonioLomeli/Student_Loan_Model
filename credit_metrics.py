import pandas as pd
import numpy as np
import numpy_financial as npf
from users import Student, Major

class Credit:
    def __init__(self, student:Student, major:Major, principal:float, n_semesters:int, interest_rate:float):
        self.student = student
        self.major = major

        if principal < 0:
            raise ValueError("Principal cannot be negative")
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if n_semesters < 0:
            raise ValueError("Number of semesters cannot be negative")

        self.principal = principal
        self.n_semesters = n_semesters
        self.interest_rate = interest_rate

        self.semester_payment = self.principal/self.n_semesters
        

    def simulate_payments(self, semester_internship:int, payment_internship):
        '''
        Simulate payments for whole payment plan, beginning in the first semester of the major.
        '''
        if semester_internship < 0:
            raise ValueError("Semester internship cannot be negative")
        elif semester_internship > self.n_semesters:
            raise ValueError("Semester internship cannot be greater than the number of semesters")
        if payment_internship < 0:
            raise ValueError("Payment internship cannot be negative")
        
        df_payments_studying = Credit.payment_during_study(semester_internship, self.semester_payment, payment_internship, self.n_semesters, 0.08)
        
        # FIRST AND SECODN PAYMENT PLAN FOLLOW THE SAME LOGIC
        last_month = df_payments_studying.index[-1]
        amount_owed = df_payments_studying['Total_Payment_FV'].sum()
        df_first_payment_plan = Credit.payment_plan(self.major, 0.3, last_month, 3, amount_owed, 0.1, income_bracket="Income_Bracket_1")
        last_month = df_first_payment_plan.index[-1]
        amount_owed = df_first_payment_plan['Principal_End_Period'].iloc[-1]
        time_for_second_payment_plan = 30 - (3  + self.student.Edad + self.n_semesters/2)
        df_second_payment_plan = Credit.payment_plan(self.major, 0.3, last_month, time_for_second_payment_plan, amount_owed, 0.08, income_bracket="Income_Bracket_2")
        
        # FOR THE THIRD PAYMENT PLAN, WE FOLLOW A DIFFERENT PROCESS
        time_during_payment = 3 + time_for_second_payment_plan
        max_time = 20 - time_during_payment
        amount_owed = df_second_payment_plan['Principal_End_Period'].iloc[-1]
        mthly_income = getattr(self.major, "Income_Bracket_3")[1:]
        mthly_income = mthly_income.replace(",", "")
        mthly_income = float(mthly_income)
        max_payment_capacity = 0.3 * mthly_income

        time, mtlhy_pmt = Credit.find_payment_plan(amount_owed, max_payment_capacity, max_time, 0.08)
        if time is None or mtlhy_pmt is None:
            raise ValueError("No payment plan found within the specified parameters.")
        last_month = df_second_payment_plan.index[-1]
        df_third_payment_plan = Credit.payment_plan(self.major, mtlhy_pmt, last_month, time, amount_owed, 0.08, calculate_payment_capacity=False)

        # Concatenate all the dataframes
        df_payment_complete = pd.concat([-df_payments_studying[['Total_Payment']], 
                                         -df_first_payment_plan[['Payment']].rename(columns={'Payment': 'Total_Payment'}), 
                                         -df_second_payment_plan[['Payment']].rename(columns={'Payment': 'Total_Payment'}), 
                                         -df_third_payment_plan[['Payment']].rename(columns={'Payment': 'Total_Payment'})],
                                        axis=0)

        dic_amortization_tables = {'Payments_Studying': -df_payments_studying,
                                   'First_Payment_Plan': -df_first_payment_plan,
                                   'Second_Payment_Plan': -df_second_payment_plan,
                                   'Third_Payment_Plan': -df_third_payment_plan}
        
        interest_rate = 0.08
        df_payment_complete['PV_factor'] = (1 + interest_rate/12) ** (df_payment_complete.index)
        df_payment_complete['Total_Payment_PV'] = df_payment_complete['Total_Payment']/df_payment_complete['PV_factor']

        mask_payments = df_payment_complete['Total_Payment'] < 0
        total_payed = -df_payment_complete.loc[mask_payments, 'Total_Payment'].sum()

        self.data_payments_complete = df_payment_complete
        self.list_amortization_tables = dic_amortization_tables
        self.total_payed = total_payed
        self.total_payment_periods = df_payment_complete.index[-1] - (self.n_semesters - semester_internship)




    @staticmethod
    def payment_during_study(semester_internship:int, semester_payment:float, payment_internship:float, n_semesters:int, interest_rate:float):
        # The months while the student is studying
        months_studying = np.arange(0, n_semesters * 6, 1)
        # The months while the student is in internship
        months_internship = np.arange(semester_internship * 6, n_semesters * 6, 1)
        df_payment_internship = pd.DataFrame(index=months_internship, columns=['Payment_Internship'])
        df_payment_internship['Payment_Internship'] = payment_internship

        # Create dataframes to store the negative payments ()
        df_studying = pd.DataFrame(index=months_studying, columns=['Payment'])
        mask = (df_studying.index % 6 == 0) | (df_studying.index == 0)
        df_studying.loc[mask, 'Payment'] = -semester_payment
        df_studying.loc[~mask, 'Payment'] = 0
        df_studying['Acumulated_debt'] = df_studying['Payment'].cumsum()

        # Merge with the internship payments
        df_studying = df_studying.join(df_payment_internship)
        df_studying['Payment_Internship'] = df_studying['Payment_Internship'].fillna(0)
        df_studying['Acumulated_debt'] = df_studying['Acumulated_debt'] + df_studying['Payment_Internship']

        # Adjust the 'cupon' payments
        df_studying['FV_factor'] = (1 + (interest_rate-0.02)/12) ** (df_studying.index) # The cupon is always 2%
        df_studying['Cupon_Principal'] = -df_studying['Acumulated_debt'] * df_studying['FV_factor']
        df_studying.loc[~mask, 'Cupon_Principal'] = 0
        df_studying['Cupon_Payment'] = df_studying['Cupon_Principal'] * 0.02/1

        # Total Payment
        df_studying['Total_Payment'] = df_studying['Payment'] + df_studying['Cupon_Payment'] + df_studying['Payment_Internship']
        df_studying['FV_factor'] = (1 + interest_rate/12) ** (df_studying.index)
        df_studying['Total_Payment_FV'] = df_studying['Total_Payment'] * df_studying['FV_factor']
        
        # Cols Keep
        df_studying = df_studying[['Payment', 'Payment_Internship', 'Cupon_Principal', 'Cupon_Payment', 'Total_Payment', "Total_Payment_FV"]]
        print(df_studying)

        return df_studying
    
    @staticmethod
    def payment_plan(major_data:Major, payment_capacity:float, month_beginning:int, T:float, amount_owed:float, interest_rate:float, calculate_payment_capacity = True, income_bracket:str = None):
        if calculate_payment_capacity:
            mthly_income = getattr(major_data, income_bracket)[1:]
            mthly_income = mthly_income.replace(",", "")
            mthly_income = float(mthly_income)
            mthly_payment = payment_capacity*mthly_income
        else:
            mthly_payment = payment_capacity

        total_payments = int(T*12)
        mthly_interest = interest_rate / 12

        months = np.arange(month_beginning+1, month_beginning + 1 + total_payments, 1)
        df_payment_plan = pd.DataFrame(index=months, columns=['Amount_Owed', 'Principal', 'Interest', 'IVA_Interest', 'Payment', 'Principal_End_Period'])

        # Inicializar el saldo inicial
        df_payment_plan.iloc[0, df_payment_plan.columns.get_loc('Principal')] = amount_owed

        for i in range(len(df_payment_plan)):
            if i == 0:
                principal = amount_owed
            else:
                principal = df_payment_plan.iloc[i-1, df_payment_plan.columns.get_loc('Principal_End_Period')]
            interest = principal * mthly_interest
            iva_interest = interest * 0.16
            payment = mthly_payment
            principal_end = principal + interest + iva_interest + payment

            df_payment_plan.iloc[i, df_payment_plan.columns.get_loc('Amount_Owed')] = principal
            df_payment_plan.iloc[i, df_payment_plan.columns.get_loc('Interest')] = interest
            df_payment_plan.iloc[i, df_payment_plan.columns.get_loc('IVA_Interest')] = iva_interest
            df_payment_plan.iloc[i, df_payment_plan.columns.get_loc('Payment')] = payment
            df_payment_plan.iloc[i, df_payment_plan.columns.get_loc('Principal_End_Period')] = principal_end

        df_payment_plan.drop(columns=['Principal'], inplace=True)
        return df_payment_plan

    @staticmethod
    def find_payment_plan(amount_owed:float, max_payment_capacity:float, max_time:float, interest_rate:float):
        times_to_evaluate = np.arange(3, max_time, 1).tolist()

        for time in times_to_evaluate:
            n_per = int(time * 12)
            iva_interest = 0.16*(interest_rate/12)
            mthly_interest = (interest_rate) / 12 + iva_interest # Sum an extra % to make sure the payment will cover the IVA on the interest

            mthly_pmt = npf.pmt(rate=mthly_interest, nper=n_per, pv=amount_owed)
            if mthly_pmt < max_payment_capacity:
                return time, mthly_pmt
        
        return None, None
