from openai import OpenAI
import os
from typing import List
import json
from database.agent import Agent, EnumDatabaseNames, EnumCollectionNames
from settings import Settings
import re


class MobilePhoneAdvisor:
    def __init__(self, celulares_estruturados: List[dict], model: str = "gpt-4o", temperature: float = 0.3):
        self.client = OpenAI(api_key=Settings.OPEN_AI_API_KEY)
        self.model = model
        self.temperature = temperature
        self.contexto = celulares_estruturados

    def perguntar(self, pergunta: str) -> str:
        contexto_str = json.dumps(self.contexto[:20], indent=2)

        prompt = f"""
            Você é um assistente de compras de celulares usados.
            
            Baseado na lista abaixo de celulares disponíveis no mercado secundário (extraída de anúncios), responda à pergunta do usuário. Considere o estado do aparelho, peças trocadas, bateria, modelo, preço e defeitos informados.
            
            Dados disponíveis:
            {contexto_str}
            
            Pergunta: {pergunta}
            
            Responda de forma objetiva, como um especialista.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

if __name__ == "__main__":
    agent = Agent(EnumDatabaseNames.DIGITAL_MARKETPLACE.value)
    database = agent.database
    collection = database[EnumCollectionNames.FACEBOOK_CLEANED_DATA.value]


    city_to_search = input("Qual a cidade em que deseja realizar a busca?: ")
    phone_model = input("Qual o modelo do celular buscado?: ")
    lista_de_celulares = list(collection.find({
        'city': city_to_search,
        'description': {
            "$regex": f".*{re.escape(phone_model)}.*",
            "$options": "i"
        }
    }))
    for doc in lista_de_celulares:
        doc.pop("_id", None)
        doc.pop("collection_date", None)

    advisor = MobilePhoneAdvisor(celulares_estruturados=lista_de_celulares)
    resposta = advisor.perguntar("Me dê uma tabela com o top-3 melhore negócios a serem feitos."
                                 "O cabeçalho da lista deve ser construído por: modelo, preço, link"
                                 "O top-3 deve ser observado de acordo com a hierarquia: "
                                 "  1.Melhor preço "
                                 "  2. sem defeitos "
                                 "  3. sem substituição de peças")
    print(resposta)