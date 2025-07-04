# mobile.py - Versão FINAL com a correção do botão de apagar

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
import json
from datetime import datetime

class MainApp(MDApp):
    dialog = None 

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.data = {}
        self.load_data()

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(self.create_register_screen())
        self.screen_manager.add_widget(self.create_history_screen())
        self.screen_manager.add_widget(self.create_manage_screen())

        self.update_labels()
        self.update_history_list()
        return self.screen_manager
        
    def create_nav_bar(self):
        nav_bar = MDBoxLayout(adaptive_height=True, padding="10dp", spacing="10dp")
        
        nav_bar.add_widget(MDButton(
            MDButtonIcon(icon="plus"), MDButtonText(text="Registrar"),
            on_release=lambda x: self.switch_screen('registrar'), style="elevated", size_hint_x=1
        ))
        nav_bar.add_widget(MDButton(
            MDButtonIcon(icon="history"), MDButtonText(text="Histórico"),
            on_release=lambda x: self.switch_screen('historico'), style="elevated", size_hint_x=1
        ))
        nav_bar.add_widget(MDButton(
            MDButtonIcon(icon="cog"), MDButtonText(text="Gerenciar"),
            on_release=lambda x: self.switch_screen('gerenciar'), style="elevated", size_hint_x=1
        ))
        return nav_bar

    def create_register_screen(self):
        screen = Screen(name='registrar')
        layout = MDBoxLayout(orientation='vertical')
        top_bar = MDTopAppBar()
        top_bar.title = "Controle de Imersão"
        
        content = MDBoxLayout(orientation='vertical', padding="30dp", spacing="20dp")
        input_layout = MDBoxLayout(adaptive_height=True, spacing="20dp")
        self.hour_entry = MDTextField(hint_text="Horas", input_type="number", mode="outlined")
        self.minute_entry = MDTextField(hint_text="Minutos", input_type="number", mode="outlined")
        input_layout.add_widget(self.hour_entry)
        input_layout.add_widget(self.minute_entry)
        content.add_widget(input_layout)
        content.add_widget(MDButton(
            MDButtonIcon(icon="check-bold"), MDButtonText(text="Adicionar Tempo"),
            on_release=self.add_time, style="filled", pos_hint={'center_x': 0.5}
        ))
        content.add_widget(MDBoxLayout(size_hint_y=None, height="20dp"))
        self.today_total_label = MDLabel(halign='center', adaptive_height=True)
        self.grand_total_label = MDLabel(halign='center', theme_text_color="Primary", font_size="32sp", adaptive_height=True)
        content.add_widget(self.today_total_label)
        content.add_widget(self.grand_total_label)
        
        layout.add_widget(top_bar)
        layout.add_widget(self.create_nav_bar())
        layout.add_widget(content)
        screen.add_widget(layout)
        return screen

    def create_history_screen(self):
        screen = Screen(name='historico')
        layout = MDBoxLayout(orientation='vertical')
        top_bar = MDTopAppBar()
        top_bar.title = "Histórico de Registros"
        
        scroll = ScrollView()
        self.history_list = MDList()
        scroll.add_widget(self.history_list)
        
        layout.add_widget(top_bar)
        layout.add_widget(self.create_nav_bar())
        layout.add_widget(scroll)
        screen.add_widget(layout)
        return screen

    def create_manage_screen(self):
        screen = Screen(name='gerenciar')
        layout = MDBoxLayout(orientation='vertical')
        top_bar = MDTopAppBar()
        top_bar.title = "Gerenciamento"

        content = MDBoxLayout(orientation='vertical', padding="20dp", spacing="20dp")

        import_card = MDCard(orientation='vertical', padding="15dp", size_hint_y=None, height="180dp", style="elevated")
        import_card.add_widget(MDLabel(text="Importação de Horas Antigas", adaptive_height=True))
        import_card.add_widget(MDLabel(text="Importe horas de outros registros aqui (ação única).", adaptive_height=True))
        
        import_input_layout = MDBoxLayout(adaptive_height=True, spacing="10dp", padding=("10dp", "10dp", "10dp", 0))
        self.legacy_hours_entry = MDTextField(hint_text="Total de horas", input_type="number", mode="outlined")
        self.import_button = MDButton(MDButtonText(text="Importar"), on_release=self.importar_horas_antigas, style="tonal")
        import_input_layout.add_widget(self.legacy_hours_entry)
        import_input_layout.add_widget(self.import_button)
        import_card.add_widget(import_input_layout)
        
        if self.data.get("config", {}).get("legacy_imported", False):
            self.legacy_hours_entry.disabled = True
            self.import_button.disabled = True
        
        content.add_widget(import_card)

        danger_card = MDCard(orientation='vertical', padding="15dp", size_hint_y=None, height="150dp", style="elevated")
        danger_card.line_color = (1, 0, 0, 0.7)
        danger_card.add_widget(MDLabel(text="Zona de Perigo", theme_text_color="Error", adaptive_height=True))
        danger_card.add_widget(MDLabel(text="A ação abaixo não pode ser desfeita.", adaptive_height=True))
        
        # --- CORREÇÃO FINALÍSSIMA APLICADA AQUI ---
        delete_button = MDButton(
            MDButtonIcon(icon="trash-can"), MDButtonText(text="Apagar Todo o Histórico"),
            style="filled", on_release=self.confirm_delete_all_data
            # Removido: theme_bg_color="Error" 
        )
        danger_card.add_widget(delete_button)
        content.add_widget(danger_card)
        
        content.add_widget(MDBoxLayout())

        layout.add_widget(top_bar)
        layout.add_widget(self.create_nav_bar())
        layout.add_widget(content)
        screen.add_widget(layout)
        return screen

    def switch_screen(self, screen_name):
        if screen_name == 'historico':
            self.update_history_list()
        self.screen_manager.current = screen_name

    def update_history_list(self):
        self.history_list.clear_widgets()
        all_entries = []
        for date_str, entries in self.data.get('registros_diarios', {}).items():
            if not isinstance(entries, list): continue
            for entry in entries:
                if isinstance(entry, dict):
                    all_entries.append(entry)
        try:
            sorted_entries = sorted(all_entries, key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            print(f"Erro ao ordenar registros: {e}")
            sorted_entries = all_entries
        
        for entry in sorted_entries:
            time_formatted = self.format_minutes_to_h_m(entry['minutes'])
            list_item = MDListItem()
            
            if entry.get('is_legacy', False):
                headline_text = f"REGISTRO ANTIGO IMPORTADO: {time_formatted}"
            else:
                date_obj = datetime.fromisoformat(entry['timestamp']).strftime('%d/%m/%Y')
                headline_text = f"{date_obj} - Adicionado: {time_formatted}"

            list_item.add_widget(MDListItemHeadlineText(text=headline_text))
            self.history_list.add_widget(list_item)


    def add_time(self, button_instance):
        try:
            hours = int(self.hour_entry.text or "0")
            minutes = int(self.minute_entry.text or "0")
            minutes_to_add = (hours * 60) + minutes
            if minutes_to_add <= 0:
                self.show_alert("Nenhum tempo inserido.")
                return
        except ValueError:
            self.show_alert("Valor inválido. Use apenas números.")
            return

        date_str_key = datetime.now().date().isoformat()
        new_entry = {"timestamp": datetime.now().isoformat(), "minutes": minutes_to_add}
        if date_str_key not in self.data['registros_diarios']:
            self.data['registros_diarios'][date_str_key] = []
        self.data['registros_diarios'][date_str_key].append(new_entry)
        self.data['total_geral_minutos'] = self.data.get('total_geral_minutos', 0) + minutes_to_add
        self.save_data()
        self.update_labels()
        self.hour_entry.text = ""
        self.minute_entry.text = ""
        print(f"SUCESSO: {minutes_to_add} minutos adicionados para hoje.")

    def update_labels(self):
        today_str = datetime.now().date().isoformat()
        today_minutes = sum(entry.get('minutes', 0) for entry in self.data['registros_diarios'].get(today_str, []))
        self.today_total_label.text = f"Tempo de hoje: {self.format_minutes_to_h_m(today_minutes)}"
        grand_total_minutes = self.data.get('total_geral_minutos', 0)
        self.grand_total_label.text = f"Total Geral: {self.format_minutes_to_h_m(grand_total_minutes)}"

    def load_data(self):
        try:
            with open('dados_imersao_mobile.json', 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"total_geral_minutos": 0, "registros_diarios": {}, "config": {}}

    def save_data(self):
        with open('dados_imersao_mobile.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def format_minutes_to_h_m(self, minutes):
        if minutes == 0: return "0m"
        hours = minutes // 60
        mins = minutes % 60
        parts = []
        if hours > 0: parts.append(f"{hours}h")
        if mins > 0: parts.append(f"{mins}m")
        return " ".join(parts)

    def show_alert(self, text, title="Aviso"):
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                MDDialogHeadlineText(text=title),
                MDDialogSupportingText(text=text),
                MDDialogButtonContainer(
                    MDButton(MDButtonText(text="Ok"), on_release=lambda x: self.dialog.dismiss())
                )
            )
        self.dialog.headline_text = title
        self.dialog.supporting_text = text
        self.dialog.open()
        
    def confirm_delete_all_data(self, *args):
        confirm_dialog = MDDialog(
            MDDialogHeadlineText(text="Apagar Tudo?"),
            MDDialogSupportingText(text="Esta ação é permanente. Você tem certeza?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancelar"), on_release=lambda x: confirm_dialog.dismiss()),
                MDButton(MDButtonText(text="Sim, Apagar"), on_release=lambda x: [self.delete_all_data(), confirm_dialog.dismiss()]),
            )
        )
        confirm_dialog.open()
        
    def delete_all_data(self):
        config = self.data.get('config', {})
        if 'legacy_imported' in config:
            config['legacy_imported'] = False
        
        self.data = {"total_geral_minutos": 0, "registros_diarios": {}, "config": config}
        self.save_data()
        
        self.update_labels()
        self.update_history_list()
        
        self.legacy_hours_entry.disabled = False
        self.import_button.disabled = False
        
        print("Histórico apagado e importação liberada.")
        
    def importar_horas_antigas(self, *args):
        try:
            horas = int(self.legacy_hours_entry.text or "0")
            if horas <= 0: return
        except ValueError:
            self.show_alert("Por favor, insira um número válido de horas.")
            return

        confirm_dialog = MDDialog(
            MDDialogHeadlineText(text="Confirmar Importação"),
            MDDialogSupportingText(text=f"Você tem certeza que deseja adicionar {horas} horas como um registro antigo?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancelar"), on_release=lambda x: confirm_dialog.dismiss()),
                MDButton(MDButtonText(text="Sim, Importar"), on_release=lambda x: [self.do_legacy_import(horas), confirm_dialog.dismiss()]),
            )
        )
        confirm_dialog.open()

    def do_legacy_import(self, horas):
        minutos_importados = horas * 60
        data_simbolica = "1970-01-01" 
        new_entry = {"timestamp": datetime.now().isoformat(), "minutes": minutos_importados, "is_legacy": True}
        if data_simbolica not in self.data['registros_diarios']:
            self.data['registros_diarios'][data_simbolica] = []
        
        self.data['registros_diarios'][data_simbolica].append(new_entry)
        self.data['total_geral_minutos'] = self.data.get('total_geral_minutos', 0) + minutos_importados
        
        if 'config' not in self.data:
            self.data['config'] = {}
        self.data['config']['legacy_imported'] = True
        
        self.save_data()
        
        self.update_labels()
        self.update_history_list()
        self.legacy_hours_entry.disabled = True
        self.import_button.disabled = True
        print(f"{horas} horas antigas importadas com sucesso.")

if __name__ == '__main__':
    MainApp().run()