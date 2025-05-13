import pandas as pd
import numpy as np
import numpy_financial as npf
from .users import Student, Major
from .data_credit_scores import get_scores_assesment


class Credit:
    def __init__(self, student:Student, principal:float, n_semesters:int, interest_rate:float):
        self.student = student
        self.major = self.student.major

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
        
        self.dictionary_scores_credit = []
        self.list_amortization_tables = {}
        

        acceptance = self.calculate_metrics_for_risk_assesment("", "Evaluation at Admissions")
        print(acceptance)
        
        if acceptance:
            self.payed = True
            df_payments_studying = Credit.payment_during_study(semester_internship, self.semester_payment, payment_internship, self.n_semesters, 0.08)
            self.list_amortization_tables['Payments_Studying']= Credit.negate_df_except_month(df_payments_studying)

            # FIRST AND SECODN PAYMENT PLAN FOLLOW THE SAME LOGIC
            last_month = df_payments_studying.index[-1]
            age_adder = np.floor(last_month/12)
            amount_owed = df_payments_studying['Total_Payment_FV'].sum()

            mthly_income = getattr(self.major, "income_bracket_1")[1:]
            mthly_income = mthly_income.replace(",", "")
            mthly_income = float(mthly_income)
            max_payment_capacity = 0.3 * mthly_income

            max_ir_payment = Credit.max_ir(max_payment_capacity, amount_owed, 3*12)/100
            print("MAXIMUM IR IN FIRST PMT",max_ir_payment)
            ir_first_payment_plan = self.calculate_metrics_for_risk_assesment("income_bracket_1", "3 yrs after graduatign payment plan", first_assesment=False, age_adder=age_adder)
            
            ir_first_payment_plan = ir_first_payment_plan if ir_first_payment_plan<=max_ir_payment else max_ir_payment
            print(ir_first_payment_plan)

            self.dictionary_scores_credit[1]["result"] = ir_first_payment_plan

            df_first_payment_plan = Credit.payment_plan(self.major, 0.3, last_month, 3, amount_owed, ir_first_payment_plan, income_bracket="income_bracket_1")
            self.list_amortization_tables['First_Payment_Plan'] =  Credit.negate_df_except_month(df_first_payment_plan)

            last_month = df_first_payment_plan.index[-1]
            amount_owed = df_first_payment_plan['Principal_End_Period'].iloc[-1]
            age_adder = np.floor(last_month/12)
            time_for_second_payment_plan = 30 - (3  + self.student.edad + self.n_semesters/2)

            if amount_owed<0:
                ir_second_payment_plan = self.calculate_metrics_for_risk_assesment("income_bracket_3", "Until 30 years payment Plan", first_assesment=False, age_adder=age_adder)
                df_second_payment_plan = Credit.payment_plan(self.major, 0.3, last_month, time_for_second_payment_plan, amount_owed, ir_second_payment_plan, income_bracket="income_bracket_2")
                self.list_amortization_tables['Second_Payment_Plan'] =  Credit.negate_df_except_month(df_second_payment_plan)

                # FOR THE THIRD PAYMENT PLAN, WE FOLLOW A DIFFERENT PROCESS
                time_during_payment = 3 + time_for_second_payment_plan
                max_time = 20 - time_during_payment
                amount_owed = df_second_payment_plan['Principal_End_Period'].iloc[-1]
                mthly_income = getattr(self.major, "income_bracket_4")[1:]
                mthly_income = mthly_income.replace(",", "")
                mthly_income = float(mthly_income)
                max_payment_capacity = 0.3 * mthly_income
                age_adder = np.floor(df_second_payment_plan.index[-1]/12)

                if amount_owed<0:
                    ir_third_payment_plan = self.calculate_metrics_for_risk_assesment("income_bracket_4", "+30 years of age payment", first_assesment=False, age_adder=age_adder)
                    time, mtlhy_pmt = Credit.find_payment_plan(amount_owed, max_payment_capacity, max_time, ir_third_payment_plan)
                    if time is not None or mtlhy_pmt is not None:
                        last_month = df_second_payment_plan.index[-1]
                        df_third_payment_plan = Credit.payment_plan(self.major, mtlhy_pmt, last_month, time, amount_owed, ir_third_payment_plan, calculate_payment_capacity=False)
                        self.list_amortization_tables['Third_Payment_Plan'] = Credit.negate_df_except_month(df_third_payment_plan)
                        self.payed = True
                    else:
                        self.payed = False
          
        else:
            self.payed = False

        # Concatenate all the dataframes and calculate PV, considering a cost of money of 8%
        df_payments_complete = self.create_concat_payments(0.08) if acceptance else pd.DataFrame()

        if acceptance:
            mask_payments = df_payments_complete['Total_Payment'] < 0
            total_payed = -df_payments_complete.loc[mask_payments, 'Total_Payment'].sum()
            payment_periods = df_payments_complete["Month"].iloc[-1] - (self.n_semesters - semester_internship)
        else:
            total_payed = 0
            payment_periods = 0

        self.data_payments_complete = df_payments_complete
        self.total_payed = total_payed
        self.total_payment_periods = payment_periods


    def create_concat_payments(self, ir):
        list_payments_concat = []

        for df in self.list_amortization_tables.values():
            if not "Total_Payment" in df.columns:
                df = df.rename(columns={'Payment': 'Total_Payment'})
            df = df[['Month','Total_Payment']]
            list_payments_concat.append(df)
        
        df_payment_complete = pd.concat(list_payments_concat, axis=0)

        df_payment_complete['PV_factor'] = (1 + ir/12) ** (df_payment_complete['Month'])
        df_payment_complete['Total_Payment_PV'] = df_payment_complete['Total_Payment']/df_payment_complete['PV_factor']

        return df_payment_complete


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
        df_studying['Cupon_Payment'] = df_studying['Cupon_Principal'] * 0.02/2

        # Total Payment
        df_studying['Total_Payment'] = df_studying['Payment'] + df_studying['Cupon_Payment'] + df_studying['Payment_Internship']
        df_studying['FV_factor'] = (1 + interest_rate/12) ** (df_studying.index)
        df_studying['Total_Payment_FV'] = df_studying['Total_Payment'] * df_studying['FV_factor']
        
        # Cols Keep
        df_studying = df_studying[['Payment', 'Payment_Internship', 'Cupon_Principal', 'Cupon_Payment', 'Total_Payment', "Total_Payment_FV"]]

        return df_studying
    
    def calculate_metrics_for_risk_assesment(self, income_bracket:str, stage_name:str, first_assesment=True, age_adder=0):
        if not hasattr(self, "assesment_scores"):
            self.assesment_scores = get_scores_assesment()


        dic_metrics_credit_stage = {'stage':stage_name}
        df_scores = self.assesment_scores[0] if first_assesment else self.assesment_scores[1]

        warranty_principal_ratio = self.student.aval.garantía/self.principal
        score_aval = self.student.aval.score_crediticio
        edad_aval = self.student.aval.edad + age_adder

        self.aval_metrics = {"warranty_principal_ratio":warranty_principal_ratio,
                             "credit_score" : score_aval,
                             "age": edad_aval}

        if first_assesment:
            avg = self.student.promedio
            self.student_metrics = {"gpa":avg}
        else:
            mthly_income = getattr(self.major, income_bracket)
            mthly_income = mthly_income[1:].replace(",","")
            mthly_income = float(mthly_income)
            credit_score = np.random.choice(np.linspace(450,750,7))
            n_dependants = np.random.choice([0,1,2], p=[0.8, 0.1, 0.1]) if not hasattr(self, "student_metrics") else self.student_metrics["n_dependants"]
            rent = np.random.choice(["Sí","No"])
            job_type = np.random.choice(["Formal","Informal","Independiente"], p=[0.74, 0.13, 0.13])
            age = self.student.edad + age_adder

            self.student_metrics = {
                "mthly_income": mthly_income,
                "credit_score": credit_score,
                "n_dependants": n_dependants,
                "rent": rent,
                "job_type": job_type,
                "age": age
            }

            print(self.student_metrics)
        
        total_score, list_scores = Credit.calculate_score(self.student_metrics, self.aval_metrics, df_scores)

        dic_metrics_credit_stage["student_metrics"] = list_scores[0]
        dic_metrics_credit_stage["aval_metrics"] = list_scores[1]
        dic_metrics_credit_stage["total_score"]= total_score

        if first_assesment:
            if total_score <= 2.5:
                self.acceptance = False
            else:
                self.acceptance = True

            dic_metrics_credit_stage["result"] = total_score
            self.dictionary_scores_credit.append(dic_metrics_credit_stage)
            del self.student_metrics
            return self.acceptance
   
        
        else:
            if total_score>= 7:
                rate = 0.08
            elif total_score >=4 and total_score<7:
                rate = 0.085
            elif total_score <4 and total_score>=0:
                rate = 0.095
            elif total_score<0 and total_score>-4:
                rate = 0.105
            else:
                rate = 0.12

            dic_metrics_credit_stage["result"] = rate
            self.dictionary_scores_credit.append(dic_metrics_credit_stage)
            return rate
        

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

            # Candado: si principal_end cambia de signo (de positivo a negativo o viceversa), rompemos el ciclo
            if i > 0:
                prev_principal_end = df_payment_plan.iloc[i-1, df_payment_plan.columns.get_loc('Principal_End_Period')]
                if (principal_end < 0 and prev_principal_end > 0) or (principal_end > 0 and prev_principal_end < 0):
                    break

        df_payment_plan.drop(columns=['Principal'], inplace=True)
        return df_payment_plan

    @staticmethod
    def find_payment_plan(amount_owed:float, max_payment_capacity:float, max_time:float, interest_rate:float):
        times_to_evaluate = np.arange(1, max_time, 1).tolist()

        for time in times_to_evaluate:
            n_per = int(time * 12)
            iva_interest = 0.16*(interest_rate/12)
            mthly_interest = (interest_rate) / 12 + iva_interest # Sum an extra % to make sure the payment will cover the IVA on the interest

            mthly_pmt = npf.pmt(rate=mthly_interest, nper=n_per, pv=amount_owed)
            if mthly_pmt < max_payment_capacity:
                return time, mthly_pmt
        
        return None, None

    @staticmethod
    def negate_df_except_month(df):
        df = df.reset_index(drop=False).rename(columns={"index": "Month"})
        df = -df
        df['Month'] = df['Month'].abs()
        return df


    @staticmethod
    def calculate_score(data_student, data_aval, data_scores):
        data_scores_aval = data_scores[data_scores["Variable"]=="Aval"].copy()
        data_scores_student = data_scores[data_scores["Variable"]=="Estudiante"].copy()
        list_score_results = []

        for tuple_ in [(data_student, data_scores_student), (data_aval, data_scores_aval)]:
            diccionario = tuple_[0]
            df = tuple_[1]
            resultados = {}
            for variable, valor in diccionario.items(): 
                df_filtered = df.copy()
                df_filtered  = df_filtered[df_filtered["Rango"] == variable]
                if isinstance(valor, str):
                    fila = df_filtered[df_filtered["Valor categórico"] == valor]
                else:
                    fila = df_filtered[(df_filtered['Valor mínimo'] <= valor) & (valor <= df_filtered['Valor máximo'])]
                
                if not fila.empty:
                    resultados[variable] = fila["Puntaje"].iloc[0] * fila["Factor"].iloc[0] 
                else:
                    resultados[variable] = None  # o alguna marca de que no se encontró
            
            list_score_results.append(resultados)
        
        dic_return = [{'person':"student", 'scores':list_score_results[0], 'total_score':sum(v for v in list_score_results[0].values() if v is not None)},
                      {'person':"aval", 'scores':list_score_results[1], 'total_score':sum(v for v in list_score_results[1].values() if v is not None)},]
        
        total_score = dic_return[0]["total_score"] + dic_return[1]["total_score"]

        return total_score, dic_return


    @staticmethod
    def max_ir(pmt, pv, nper, precision=1e-6, max_iter=1000):
        low = 0.0
        high = 1.0
        for _ in range(max_iter):
            mid = (low + high) / 2
            cuota = npf.pmt(mid, nper, -pv)  # -pv porque es un egreso
            if cuota > pmt:
                high = mid
            else:
                low = mid
            if abs(cuota - pmt) < precision:
                break
        return (mid*12) - (mid*12*(0.16))

class PaymentPlan:
    def __init__(self, pirincipal, begin, end):
        pass