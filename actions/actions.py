# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import json
import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

AGENDAMENTO_PATH = "agendamentos.json"

# Utilitário para carregar e salvar agendamentos
def carregar_agendamentos():
    if not os.path.exists(AGENDAMENTO_PATH):
        return []
    with open(AGENDAMENTO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_agendamentos(agendamentos):
    with open(AGENDAMENTO_PATH, "w", encoding="utf-8") as f:
        json.dump(agendamentos, f, ensure_ascii=False, indent=4)

class ActionMarcarConsulta(Action):
    def name(self) -> Text:
        return "action_marcar_consulta"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nome = tracker.get_slot("nome")
        procedimento = tracker.get_slot("procedimento")
        data = tracker.get_slot("data")
        hora = tracker.get_slot("hora")

        if not (nome and procedimento and data and hora):
            dispatcher.utter_message(text="Preciso de todas as informações para marcar sua consulta.")
            return []

        agendamentos = carregar_agendamentos()

        # Verifica conflito
        for ag in agendamentos:
            if ag["data"] == data and ag["hora"] == hora:
                dispatcher.utter_message(response="utter_horario_ocupado")
                return []

        # Salva novo agendamento
        novo_agendamento = {
            "nome": nome,
            "procedimento": procedimento,
            "data": data,
            "hora": hora
        }

        agendamentos.append(novo_agendamento)
        salvar_agendamentos(agendamentos)

        dispatcher.utter_message(response="utter_confirmar_agendamento", 
                                 nome=nome, procedimento=procedimento, data=data, hora=hora)
        return []

class ActionVerificarValor(Action):
    def name(self) -> Text:
        return "action_verificar_valor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        procedimento = tracker.get_slot("procedimento")

        tabela_valores = {
            "limpeza": 120.00,
            "clareamento": 500.00,
            "extração": 300.00,
            "canal": 650.00,
            "obturação": 200.00
        }

        if procedimento and procedimento.lower() in tabela_valores:
            valor = tabela_valores[procedimento.lower()]
            dispatcher.utter_message(response="utter_valor_procedimento", procedimento=procedimento, valor=valor)
        else:
            dispatcher.utter_message(text="Desculpe, não tenho o valor desse procedimento. Poderia confirmar o nome?")
        return []

