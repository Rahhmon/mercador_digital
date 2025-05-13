# Avaliador Inteligente de Ofertas de Celulares Usados

## 🧹 Visão Geral
Este projeto tem como objetivo construir um sistema inteligente que coleta, analisa e avalia listagens de celulares usados em marketplaces como o Facebook Marketplace. O sistema extrai especificações técnicas relevantes diretamente das descrições dos anúncios e gera uma estrutura padronizada de dados para posterior análise ou visualização.

### 🌟 Objetivos principais
- Extrair automaticamente atributos técnicos (modelo, armazenamento, bateria, Face ID, etc.) de celulares.
- Validar se o item listado é realmente um celular.
- Preparar os dados para análise de mercado, precificação e visualização.

## 🚀 Instalação e Configuração

1. Clone o repositório e acesse a pasta do projeto:
   git clone <url-do-repositorio>
   cd <nome-da-pasta>

2. Crie e ative um ambiente virtual:
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows

3. Instale as dependências:
   pip install -r requirements.txt

4. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

   FACEBOOK_EMAIL=seu_email_facebook  
   FACEBOOK_PASSWORD=sua_senha_facebook  
   MONGO_URI=mongodb://localhost:27017/  
   OPENAI_API_KEY=sua_chave_openai  

Essas variáveis são usadas para:
- Autenticar no Facebook Marketplace via scraping
- Conectar ao banco de dados MongoDB
- Acessar a API da OpenAI para análise de texto

## 📦 Componentes do Sistema

1. Coleta de Dados (Scraping)
Coleta periódica de anúncios de marketplaces com campos como título, descrição, preço, data e localização usando ferramentas como Playwright ou Selenium.

2. Processamento de Texto com LLM
Utiliza LLMs como GPT-4 para interpretar e extrair dados técnicos das descrições, considerando linguagem informal, emojis e variações de escrita.

Campos extraídos:
- modelo: Ex. "iPhone 11 Pro Max"
- armazenamento: Ex. 64 GB
- capacidade_bateria: Ex. 75%
- pecas_trocadas: Ex. ["tela", "bateria"]
- face_id: True / False
- necessita_manutencao: True / False
- pecas_com_problema: Ex. ["alto-falante", "carregador"]

Caso o item não seja um celular, retorna estrutura com campos nulos:

{
  "modelo": "N.A",
  "armazenamento": -1,
  "capacidade_bateria": -1,
  "pecas_trocadas": [],
  "face_id": null,
  "necessita_manutencao": false,
  "pecas_com_problema": []
}
