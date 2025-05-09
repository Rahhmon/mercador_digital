# 💻 README do Projeto — Avaliador Inteligente de Ofertas de Computadores

## 🧩 Visão Geral
Este projeto tem como objetivo construir um sistema inteligente que coleta, analisa e avalia listagens de produtos (como computadores) em marketplaces como o Facebook Marketplace. Ele extrai especificações técnicas relevantes (CPU, GPU, RAM, armazenamento, bateria, etc.), compara com uma base de preços de referência e determina se a oferta é um bom negócio.

O sistema usa uma arquitetura híbrida combinando:
- ✅ Web scraping  
- ✅ NLP + LLM para extração estruturada de dados  
- ✅ Busca vetorial para correspondência de componentes  
- ✅ Lógica de negócio para avaliação de preço  
- ✅ LLM opcional para geração de explicações  

---

## 📦 Componentes do Sistema

### 1. **Coleta de Dados (Scraping)**
Coleta de listagens diariamente usando Playwright ou Selenium. Cada item deve incluir título, descrição, preço, data e localização.

### 2. **Processamento de Texto & Normalização**
Uso de regex ou prompts GPT-3.5/4 para extrair campos estruturados como:
- CPU: ex. `i7 12700K`  
- GPU: ex. `RTX 3060 Ti`  
- RAM: ex. `32GB DDR4`  
- Armazenamento: ex. `512GB SSD`  
- Saúde da bateria (se for notebook)  
- Condição: novo, usado, recondicionado

### 3. **Base de Preço de Referência**
Manter um banco de preços médios dos componentes:
- CPU, GPU, RAM, SSD, etc.  
- Armazenar preços médios ou de mercado  
- Atualização periódica (via API, scraping ou manual)

### 4. **Matching Semântico (Embeddings)**
Usar o modelo `text-embedding-ada-002` da OpenAI + Chroma ou FAISS para mapear descrições vagas a componentes padronizados.

### 5. **Motor de Avaliação**
Comparar o preço anunciado com o valor estimado:
- Definir lógica de avaliação (ex: bom negócio = 15% abaixo do mercado)  
- Usar regras ou regressão linear para estimativa de preço

### 6. **Saída e Explicação**
Armazenar os documentos finais no MongoDB:
- Objeto estruturado com campos aninhados  
- LLM opcional para gerar explicação:
  > "Este PC inclui i7 12700K + RTX 3060 Ti avaliados em ~$950. Preço do anúncio $780 = bom negócio."

---

## 🧠 Tecnologias Utilizadas
- **Python** (scraping, lógica, integração com LLM)  
- **FastAPI** (camada de API opcional)  
- **Chroma / FAISS** (banco vetorial para matching)  
- **MongoDB** (armazenamento de documentos)  
- **OpenAI API** (LLM + embeddings)  
- **Pandas / NumPy** (avaliação e ETL)

---

## 📊 Exemplo de Documento no MongoDB

```json
{
  "title": "PC Gamer",
  "components": {
    "cpu": "i7 12700K",
    "gpu": "RTX 3060 Ti",
    "ram": {"size": 32, "um": "GB"},
    "storage": {"type": "SSD", "size": 512, "um": "GB"}
  },
  "battery_life": null,
  "changed_pieces": ["fonte"],
  "price": 780,
  "valuation": {
    "estimated_value": 950,
    "deal_score": 170
  },
  "is_deal": true,
  "listing_info": {
    "source": "Facebook Marketplace",
    "date_scraped": "2025-05-08T14:30:00Z",
    "location": "São Paulo, BR"
  },
  "tags": ["usado", "gamer"]
}
