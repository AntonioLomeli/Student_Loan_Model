import flet as ft
import os
import sys
from utils.read_drive_files import read_excel_drive
import utils.app_views as views

class ControlsView:
    def __init__(self, page, dic_information=None):
        self.page = page
        self.dic_information = dic_information
        self.views = {}  # Guardar instancias de las vistas
        self.update_auxiliar_views = False

    def create_controls_view(self):
        try:
            self.page.clean()
        except:
            pass

        list_functions_to_execute = [{'name_view':'CreditSimulator', 
                                      'create_object': views.CreditSimulatorView,
                                      'args_object':(self.page, self.dic_information)},]
        
        for dic_ in list_functions_to_execute:
            if dic_['name_view'] == "CreditSimulator":
                view_instance = dic_['create_object'](*dic_['args_object'])
                view_instance.create_controls()
                setattr(self, dic_['name_view'], view_instance)
                self.views[dic_['name_view']] = view_instance

    def get_view_body(self, name):
        # Devuelve el control raíz de la vista, no lo copies ni lo reconstruyas
        # Se asume que cada vista tiene un atributo 'root_control' que es el control principal (ej. Column)
        return self.views[name].body

    def update_payment_plan(self):
        try:
            pre_requisites = getattr(getattr(self, 'CreditSimulator'), 'payment_plan')
        except:
            print("Impossible to show this view right now")
            views.show_alert_message(self.page, "First simulate a credit to show something on this view")
        else:
            pre_requisites = getattr(self, 'CreditSimulator')
            if not hasattr(self, 'PaymentPlan'):
                view_instance = views.PaymentPlanView(self.page, pre_requisites)
                setattr(self, 'PaymentPlan', view_instance)
                self.views['PaymentPlan'] = view_instance.create_controls() # Update
                return view_instance.create_controls()
            else:
                return self.views['PaymentPlan']

    
    def update_scores(self):
        try:
            pre_requisites = getattr(getattr(self, 'CreditSimulator'), 'payment_plan')
        except:
            views.show_alert_message(self.page, "First simulate a credit to show something on this view")
        else:
            pre_requisites = getattr(self, 'CreditSimulator')
            print(getattr(pre_requisites, "update_auxiliar_views"))
            if not hasattr(self, 'ScoresView'):
                student_data = getattr(pre_requisites, 'student')
                credit_data = getattr(pre_requisites, 'credit')

                view_instance = views.ScoresView(self.page, student_data, credit_data)
                setattr(self, 'ScoresView', view_instance)
                self.views['ScoresView'] = view_instance.create_controls()
                return view_instance.create_controls()
            else:
                return self.views['ScoresView']


class App():
    def __init__(self, dic_information=None):
        self.dic_information = dic_information

    def main(self, page: ft.Page):
        self.page = page

        self.page.title = "Student Credit Calculator"
        self.edit_body_view = ControlsView(self.page, self.dic_information)
        self.edit_body_view.create_controls_view()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_400)
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # Create a navigation bar on the right side of the page
        nav_bar = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            extended=False,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.CREDIT_SCORE_SHARP, label="Credit Simulator"),
                ft.NavigationRailDestination(icon=ft.Icons.ATTACH_MONEY_ROUNDED, label="Payment Plans"),
                ft.NavigationRailDestination(icon=ft.Icons.EXPOSURE_PLUS_1_OUTLINED, label="Scoring Details"),
            ],
            on_change=lambda e:self.navigation_rail_change(e.control.selected_index),
        )

        # Add the navigation bar to the page
        self.body = ft.Row(
                    [
                        nav_bar,
                        ft.VerticalDivider(width=1),
                        ft.Column()
                    ],
                    expand=True,
                )

        self.page.add(
                self.body
            )

        self.navigation_rail_change(0)
    
    def navigation_rail_change(self, index):
        print(f"Selected index: {index}")
        if index == 0:
            new_body_controls = self.edit_body_view.get_view_body('CreditSimulator')
            print(new_body_controls)
        elif index == 1:
            print("Trying to create PaymentPlan")
            new_body_controls = self.edit_body_view.update_payment_plan()
        elif index==2:
            print("Trying to create score details")
            new_body_controls = self.edit_body_view.update_scores()

        if isinstance(new_body_controls, ft.Control):
            self.update_body(new_body_controls)

    def update_body(self, new_body):
        # self.body.controls[2].controls.clear()
        self.body.controls[2] = new_body
        
        self.page.update()

dic_drive_links = {'data_majors':'1O4t--0tDPCi8zrBQjsc_pu7jdIpHzkYV',
                   'data_students':'1u510KnPUoRNqVBHSESLQzostDHFR6Zp5',
                   'data_avales':'1AtuxkonjQ72bpQtjA0BsrY-yCoa4mZsR'}

dic_dataframes = {}
for key, value in dic_drive_links.items():
    data = read_excel_drive(value, file_type='csv')
    dic_dataframes[key] = data

object = App(dic_dataframes)
ft.app(target=object.main, 
       view=ft.WEB_BROWSER,
       port=int(os.environ.get("PORT", 8000))
        )
