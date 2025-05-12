from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import json
from settings import Settings
from database.agent import Agent, EnumDatabaseNames, EnumCollectionNames
from scrap.facebook import EnumStatus
from tqdm import tqdm


class CelularInfo(BaseModel):
    modelo: str  # "N.A" se não for celular
    armazenamento: int  # -1 se não aplicável
    capacidade_bateria: Optional[int]  # -1 se não informado
    pecas_trocadas: List[str]
    face_id: Optional[bool]
    necessita_manutencao: bool
    pecas_com_problema: List[str]


class MobilePhoneParser:
    def __init__(self, model: str = "gpt-4", temperature: float = 0.2):
        self.client = OpenAI(api_key=Settings.OPEN_AI_API_KEY)
        self.model = model
        self.temperature = temperature


    def _build_prompt(self, description: str, seller_description: str) -> str:
        return f"""
            Você é um assistente treinado para extrair informações técnicas de aparelhos CELULARES usados a partir de textos de anúncios. Seu objetivo é retornar os dados de forma estruturada, desde que o produto anunciado seja um celular.
            
            ⚠️ Se o item analisado NÃO for um celular (por exemplo: acessórios, peças avulsas, eletrodomésticos, etc), retorne o seguinte JSON:
            
            {{
              "modelo": "N.A",
              "armazenamento": -1,
              "capacidade_bateria": -1,
              "pecas_trocadas": [],
              "face_id": null,
              "necessita_manutencao": false,
              "pecas_com_problema": []
            }}
            
            Campos a extrair, caso o item seja um celular:
            
            - modelo: nome completo do celular
            - armazenamento: capacidade em GB
            - capacidade_bateria: percentual da saúde da bateria
            - pecas_trocadas: lista de peças trocadas
            - face_id: True ou False
            - necessita_manutencao: True ou False
            - pecas_com_problema: lista de partes com defeito
            
            Texto analisado:
            Descrição geral: "{description}"
            Descrição do vendedor: "{seller_description}"
            
            Retorne apenas o JSON com os campos preenchidos.
                    """.strip()

    def parse(self, description: str, seller_description: str):
        prompt = self._build_prompt(description, seller_description)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw) if raw.startswith("{") else eval(raw)
            return CelularInfo(**data)
        except Exception as e:
            print(f"Erro ao processar JSON: {e}")
            return CelularInfo(
                modelo="N.A", armazenamento=-1, capacidade_bateria=-1,
                pecas_trocadas=[], face_id=None, necessita_manutencao=False,
                pecas_com_problema=[]
            )

    @staticmethod
    def main():
        agent = Agent(EnumDatabaseNames.DIGITAL_MARKETPLACE.value)
        database = agent.database
        collection = database[EnumCollectionNames.FACEBOOK_CLEANED_DATA.value]
        all_items = collection.find({'status': EnumStatus.CLEAN_DATA.value})

        # 1. Instantiate the model.
        parser = MobilePhoneParser()

        for item in tqdm(all_items):

            ia_info = parser.parse(
                description=item.get('description'),
                seller_description=item.get('seller_description')
            )

            if ia_info.get("modelo") != "N.A":
                collection.update_one({'_id': item.get('_id')},
                                      {'$set':
                                          {
                                              'model': ia_info.modelo,
                                              'storage': ia_info.armazenamento,
                                              'batery_capacity': ia_info.capacidade_bateria,
                                              'replaced_parts': ia_info.pecas_trocadas,
                                              'face_id': ia_info.face_id,
                                              'needs_repair': ia_info.necessita_manutencao,
                                              'broken_parts': ia_info.pecas_com_problema,
                                              'status': EnumStatus.AGENT_ACTION.value,
                                          }})

if __name__ == "__main__":
    MobilePhoneParser.main()