import flet as ft
import pandas as pd
from .users import Student, Major
from .credit_metrics import Credit

def show_alert_message(page, message):
   # Función para cerrar el diálogo
    def close_dialog(e):
        page.dialog.open = False
        page.update()
    
    # Crear el diálogo
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Alerta"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("OK", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Dialog dismissed!"),
    )
    
    # Mostrar el diálogo
    page.dialog = dlg
    page.dialog.open = True
    page.update()



class CreditSimulatorView:
    def __init__(self, page, dic_information=None):
        self.page = page
        self.update_auxiliar_views = False

        for key, value in dic_information.items():
            setattr(self, key, value)

    def create_controls(self):
        list_students = self.data_students['Nombre'].tolist()
        dropdow_students = [ft.DropdownOption(student) for student in list_students]

        self.txt_student_name = ft.Dropdown(value = list_students[0], 
                                                options=dropdow_students,	
                                                label="Student Name",
                                                width=500,
                                                on_change=self.update_student_data)
        self.txt_student_age = self.create_input("Age", "number", width_textfield=150)
        self.txt_avg_grade = self.create_input("Average Grade", "number", width_textfield=150)

        self.btn_calculate = ft.ElevatedButton(text="Calculate",
                                        icon=ft.Icons.CHECK,
                                        width=150,
                                        on_click=self.calculate_credit_metrics)


        first_section = ft.Column([
                                ft.Row([self.txt_student_name]),
                                ft.Row([self.txt_student_age, self.txt_avg_grade]),
                                ft.Row([self.btn_calculate]),
                                ], expand=1)
        
        list_majors = self.data_majors['Carrera'].tolist()
        self.lstbox_major = ft.Dropdown(value="Electrónica", 
                                               options=[ft.DropdownOption(major) for major in list_majors],	
                                               label="Select the Major",
                                               width=400,
                                               on_change=self.update_major_data)
        self.txt_n_semester = self.create_input("Number of Semesters", "number", width_textfield=150)
        self.txt_n_semester.value = 9

        self.total_credits = ft.TextField(label="Total Credits", border=ft.InputBorder.UNDERLINE, value="0", width=150, on_change=self.update_total_cost)

        self.credit_cost = 2800 # Get credit cost from database
        self.lbl_cost_per_credit = ft.TextField(label = "Cost per Credit",
                                                value=f"{self.credit_cost:,.1f}", 
                                                width=150, read_only=True, border=ft.InputBorder.UNDERLINE)

        self.total_major_cost = 0
        self.lbl_total_cost = ft.TextField(label = "Major Total Cost",
                                           value=f"{self.total_major_cost:,.2f}", 
                                           width=200, read_only=True, border=ft.InputBorder.UNDERLINE)

        self.scholarship_pct = 0.50 # Get scholarship percentage from database
        self.lbl_scholarship = ft.TextField(label= 'Scholarship %',value=f"{self.scholarship_pct*100:.1f}%", width=150, read_only=True, border=ft.InputBorder.UNDERLINE)

        
        self.txt_loan_pct = ft.TextField(label="Proposed Loan %",  
                                         value=f'{0.3*100:,.1f}', 
                                         width=150, suffix_text="%", filled=True,
                                         on_change=self.update_amount_owed)

        self.payment_tutor = 1 - self.scholarship_pct - float(self.txt_loan_pct.value)/100 if self.txt_loan_pct.value else 0.0
        self.txt_payment_by_tutor = ft.TextField(label="Payment by Tutor %",
                                                 value=f"{self.payment_tutor*100:.1f}%", 
                                                 width=150, read_only=True, border=ft.InputBorder.UNDERLINE)

        self.amount_owed = 0
        self.txt_amount_owed = ft.TextField(label="Amount Owed", 
                                            value=self.amount_owed, 
                                            width=250, read_only=True, border=ft.InputBorder.UNDERLINE)

        second_section = ft.Column([
                                ft.Row([self.lstbox_major, self.txt_n_semester]),
                                ft.Row([self.total_credits, self.lbl_cost_per_credit, self.lbl_total_cost]),
                                ft.Row([self.lbl_scholarship, self.txt_loan_pct, self.txt_payment_by_tutor]),
                                ft.Row([self.txt_amount_owed]),

                                ], expand=1)
        

        self.txt_credit_accepted = ft.TextField(value='Credit Accepted', visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)
        self.txt_total_payment = ft.TextField(label='Total Payment', value=0, visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)

        self.txt_ir_studying = ft.TextField(label='IR while studying', value='0.00%', visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)
        self.txt_ir_first = ft.TextField(label='IR for first payment plan', value='0.00%', visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)
        self.txt_ir_second = ft.TextField(label='IR for second payment plan', value='0.00%', visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)
        self.txt_ir_third = ft.TextField(label='IR for third payment plan', value='0.00%', visible=False, read_only=True, width=200, border = ft.InputBorder.UNDERLINE, filled=True, fill_color=ft.Colors.GREEN_200)
        
        third_section = ft.Row([
                                 ft.Column([self.txt_credit_accepted, self.txt_total_payment]),
                                 ft.Column([self.txt_ir_studying, self.txt_ir_first, self.txt_ir_second,self.txt_ir_third])   
                                ], expand=True)

        self.update_student_data(e=None)
        self.update_major_data(e=None)

        body = ft.Column([  
                            ft.Text("Student Credit Simulator", size=30, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                    first_section,
                                    second_section
                                    ], 
                                    expand=True, scroll=ft.ScrollMode.AUTO),
                            third_section,
                        ], 
                        expand=True, 
                        alignment=ft.MainAxisAlignment.START,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=5
                        )

        self.body = body
        return body
    
    def create_input(self, label: str, var_type: str = "text", width_textfield: int = None):
        if var_type == "text":
            input_var = ft.TextField(label=label, width=width_textfield, filled=True)
        elif var_type == "number":
            input_var = ft.TextField(label=label, keyboard_type=ft.KeyboardType.NUMBER, width=width_textfield, filled=True)
        elif var_type == "date":
            input_var = ft.DatePicker(label=label)
        return input_var

    def update_total_cost(self, e):
        cost_per_credit = self.credit_cost
        total_credits = int(self.total_credits.value)
        self.total_major_cost = cost_per_credit * total_credits
        self.update_attribute_control(self.total_major_cost, self.lbl_total_cost, self.total_major_cost)
        self.amount_owed = self.total_major_cost * float(self.txt_loan_pct.value.strip())/100
        self.update_attribute_control(self.amount_owed, self.txt_amount_owed, self.amount_owed)
        self.page.update()

    def update_amount_owed(self, e):
        pct_scholarship = self.scholarship_pct
        pct_loan = float(self.txt_loan_pct.value.strip())/100

        payment_tutor = 1 - pct_scholarship - pct_loan
        
        self.update_attribute_control(self.payment_tutor, self.txt_payment_by_tutor, payment_tutor, suffix="%", multiplier=100)
        amount_owed = (self.total_major_cost * pct_loan)
        self.update_attribute_control(self.amount_owed, self.txt_amount_owed, amount_owed)
        self.page.update()

    def update_student_data(self, e):
        self.update_auxiliar_views = True
        student_name = self.txt_student_name.value
        student_data = self.data_students[self.data_students['Nombre'] == student_name].iloc[0]

        # Update the text fields with the student's data
        self.txt_student_age.value = str(student_data['Edad'])
        self.txt_avg_grade.value = str(student_data['Promedio'])
        self.scholarship_pct = float(student_data['Beca'][:-1])/100
        self.lbl_scholarship.value = f"{self.scholarship_pct*100:.1f}%"

        interest_major = student_data['Interes']
        self.lstbox_major.value = interest_major

        self.update_major_data(e=None)
        self.update_credit_info_txt(unhide=False)
    
    def update_major_data(self, e):
        major_name = self.lstbox_major.value
        print(major_name)
        major_data = self.data_majors[self.data_majors['Carrera'] == major_name].iloc[0].copy()
        
        self.total_major_cost = self.credit_cost * major_data['Total Creditos']

        # Update the text fields with the major's data
        self.total_credits.value = str(major_data['Total Creditos'])
        self.lbl_total_cost.value = f"{self.total_major_cost:,.2f}"

        self.update_amount_owed(e=None)
        
        # Update the controls
        self.page.update()

    def update_attribute_control(self, attribute, control, value, suffix = "", multiplier = 1):
        attribute = value
        control.value = f"{attribute*multiplier:,.1f}{suffix}"

    def calculate_credit_metrics(self, e):

        student_name = self.txt_student_name.value
        student_data = self.data_students[self.data_students['Nombre'] == student_name].iloc[0].copy()
        major_name = self.lstbox_major.value
        major_data = self.data_majors[self.data_majors['Carrera'] == major_name].iloc[0].copy()
        
        # Create a Major object
        major = Major(major_data)
        # Create a Student object
        student = Student(student_data, major)

        if float(self.txt_loan_pct.value.strip()) >= 30:
            self.amount_owed = self.total_major_cost * float(self.txt_loan_pct.value.strip())/100
            # Create a Credit object
            try:
                if not hasattr(student, 'aval'):
                    student.get_aval(data_avales=self.data_avales)

                credit = Credit(student, self.amount_owed, int(self.txt_n_semester.value), 0.08)
                
                # Simulate payments
                credit.simulate_payments(semester_internship=5, payment_internship=3000)
                self.payment_plan = credit.data_payments_complete
                self.list_amortization_tables = credit.list_amortization_tables
                self.data_scores_credit = credit.dictionary_scores_credit
                self.credit = credit
                self.student = student
                self.major = major
                if self.credit.payed:
                    print(-credit.data_payments_complete['Total_Payment_PV'].sum())
                    print(credit.data_payments_complete)

                self.update_credit_info_txt(credit_payed=True if self.credit.payed else False)
                self.update_auxiliar_views = True
            except:
                raise

    def update_credit_info_txt(self, unhide=True, credit_payed = True):
        list_txt = [self.txt_ir_studying, self.txt_ir_first, self.txt_ir_second, self.txt_ir_third]
        for txt in list_txt:
            txt.visible = unhide

        self.txt_total_payment.visible = unhide
        self.txt_credit_accepted.visible = unhide

        if unhide and credit_payed:
            self.txt_credit_accepted.fill_color = ft.Colors.GREEN_200
            self.txt_credit_accepted.value = "Credit Accepted"
            self.txt_total_payment.value = f'{self.credit.total_payed:,.2f}'
            self.txt_ir_studying.value = '8.00%'
            for i in range(1,4):
                try:
                    ir = self.data_scores_credit[i]['result']
                    list_txt[i].value =  f'{ir*100:,.2f}%'
                except IndexError:
                    list_txt[i].value =  "NA"


        
        elif not credit_payed:
            for txt in list_txt:
                txt.visible = False
            self.txt_total_payment.visible = False
            self.txt_credit_accepted.visible = True
            self.txt_credit_accepted.value = "Reject, payment capacity is not enough"
            self.txt_credit_accepted.fill_color = ft.Colors.RED_100
        
        self.page.update()



class PaymentPlanView:
    def __init__(self, page, pre_requisites:CreditSimulatorView):
        self.page = page
        self.student = pre_requisites.student
        self.major = pre_requisites.major
        self.payment_plan = pre_requisites.payment_plan
        self.credit = pre_requisites.credit
        list_amortization_tables = pre_requisites.list_amortization_tables

        self.list_amortization_tables = {}
        self.list_amortization_tables['Payment Plan'] = self.payment_plan

        for key, value in list_amortization_tables.items():
            self.list_amortization_tables[key] = value

    def create_controls(self):
        destinations = []
        for key, value in self.list_amortization_tables.items():
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.TABLE_VIEW, label=key))

        nav_bar = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            extended=False,
            destinations= destinations,
            on_change= self.navigation_rail_change,
        )

        self.txt_student_name = ft.TextField(label="Student Name", value=self.student.nombre, width=500, read_only=True)
        self.txt_student_age = ft.TextField(label="Age", value=str(self.student.edad), width=100, read_only=True)
        self.txt_avg_grade = ft.TextField(label="Average Grade", value=str(self.student.promedio), width=100, read_only=True)

        self.txt_major_name = ft.TextField(label="Major Name", value=self.major.carrera, width=400, read_only=True)
        self.txt_principal = ft.TextField(label="Amount Owed", value=f'{self.credit.principal:,.1f}', width=300, read_only=True)

        self.txt_total_payed = ft.TextField(label="Total Payed", value=f'{self.credit.total_payed:,.1f}', width=400, read_only=True)
        self.txt_total_payment_periods = ft.TextField(label="Total Payment Periods", value=f'{round(self.credit.total_payment_periods/12,1)} Years', width=200, read_only=True)

        self.first_row = ft.Column([
                                    ft.Column([self.txt_student_name, ft.Row([self.txt_student_age, self.txt_avg_grade])], expand=True),
                                    ft.Row([self.txt_major_name, self.txt_principal], expand=True),
                                    ft.Row([self.txt_total_payed, self.txt_total_payment_periods], expand=True)
                                    ],
                                    expand=True,
                                    height=200)
        
        self.dataframe_shown = self.payment_plan.reset_index(drop=False).rename(columns={'index':'Month'})
        self.table_shown = PaymentPlanView.dataframe_to_datatable(self.payment_plan)
        self.btn_to_excel = ft.ElevatedButton(text="Export to Excel",
                                        icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                        width=150,
                                        on_click=self.export_to_excel)


        self.column_table = ft.Row([
                                    ft.Column([
                                                ft.Row([self.table_shown], expand=True)
                                            ],
                                            expand=True,
                                            scroll=ft.ScrollMode.AUTO,
                                            ),
                                    self.btn_to_excel
                                    ], 
                                    expand=True)
        
        self.body = ft.Row([
                            ft.Column([self.first_row, self.column_table], expand=True),
                            ft.VerticalDivider(width=1),
                            nav_bar,
                            
                            ],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        )

        return self.body

    def navigation_rail_change(self, e):
        print(f"Selected index: {e.control.selected_index}")

        selected_key = list(self.list_amortization_tables.keys())[e.control.selected_index]
        
        new_table = self.list_amortization_tables[selected_key]
        if "Month" not in new_table.columns:
            new_table = new_table.reset_index(drop=False).rename(columns={"index": "Month"})
        
        self.dataframe_shown = new_table
        new_table_object = PaymentPlanView.dataframe_to_datatable(new_table)
        self.body.controls[0].controls[1].controls[0].controls[0] = new_table_object
        self.page.update()

    def export_to_excel(self, e):
        # Export the current DataFrame to an Excel file
        self.payment_plan.to_excel("payment_plan.xlsx", index=False)
        show_alert_message(self.page, "Payment plan exported to payment_plan.xlsx")


    @staticmethod
    def dataframe_to_datatable(df: pd.DataFrame):
        columns = [ft.DataColumn(ft.Text(str(col))) for col in df.columns]
        rows = [
            ft.DataRow([
                ft.DataCell(ft.Text(f"{value:,.2f}" if isinstance(value, (int, float)) else str(value))) for value in row
            ]) for row in df.values
        ]
        return ft.DataTable(columns=columns, rows=rows, heading_row_color=ft.Colors.BLUE_200)



class ScoresView:
    def __init__(self, page, student, credit):
        self.page = page
        self.student = student
        self.major = self.student.major
        self.credit = credit
        self.data_credit_scores = self.credit.dictionary_scores_credit
        

    def create_controls(self):
        self.txt_student_name = ft.TextField(label="Student Name", value=self.student.nombre, width=500, read_only=True)

        self.txt_major_name = ft.TextField(label="Major Name", value=self.major.carrera, width=400, read_only=True)
        self.txt_principal = ft.TextField(label="Amount Owed", value=f'{self.credit.principal:,.1f}', width=300, read_only=True)

        self.txt_total_payed = ft.TextField(label="Total Payed", value=f'{self.credit.total_payed:,.1f}', width=400, read_only=True)
        self.txt_total_payment_periods = ft.TextField(label="Total Payment Periods", value=f'{round(self.credit.total_payment_periods/12,1)} Years', width=200, read_only=True)

        first_row = ft.Column([
                                    ft.Row([self.txt_student_name,], expand=True),
                                    ft.Row([self.txt_major_name, self.txt_principal], expand=True),
                                    ft.Row([self.txt_total_payed, self.txt_total_payment_periods], expand=True)
                                    ],
                                    height=200)

        dataframe_details = self.create_dataframe_details().fillna(0).sort_values(by="Person", ascending=False)

        total_row = {}
        for col in dataframe_details.columns:
            if col not in ["Aspect Evaluated", "Person"]:
                # Suma ignorando NaN
                total_row[col] = dataframe_details[col].sum(numeric_only=True)
            else:
                total_row[col] = "Gran Total" if col == "Aspect Evaluated" else ""
        
        dataframe_details = pd.concat([dataframe_details, pd.DataFrame([total_row])], ignore_index=True)

        datatable_details = PaymentPlanView.dataframe_to_datatable(dataframe_details)

        body = ft.Column([
                            first_row,
                            ft.Column([datatable_details], expand=True, scroll=ft.ScrollMode.AUTO)
                        ])
        
        self.body = body
        return self.body
        
    def create_dataframe_details(self):
        dfs  = []
        for dictionary in self.data_credit_scores:
            student_data = dictionary["student_metrics"]["scores"]
            df_student = pd.DataFrame([student_data]).T
            df_student.columns = [dictionary["stage"]]
            df_student["Person"] = "Student"
            df_student = df_student.set_index("Person", append=True)
            
            aval_data = dictionary["aval_metrics"]["scores"]
            df_aval = pd.DataFrame([aval_data]).T
            df_aval.columns = [dictionary["stage"]]
            df_aval["Person"] = "Aval"
            df_aval = df_aval.set_index("Person", append=True)

            df_concat = pd.concat([df_student, df_aval], axis=0)
            print(df_concat)
            dfs.append(df_concat)

        df_final_concat = pd.concat(dfs, axis=1)
        print(df_final_concat)
        return df_final_concat.reset_index(drop=False).rename(columns={"level_0":"Aspect Evaluated"})



