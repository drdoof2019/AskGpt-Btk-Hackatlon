import google.generativeai as genai # pip install google-generativeai
import time
import os
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI #pip install -U langchain-google-genai
from mcp_use import MCPAgent, MCPClient # pip install mcp-use
from google.api_core.exceptions import ResourceExhausted
import json

# --- .env Dosyası ve API Anahtarı Kontrolü ---
if not os.path.exists('.env'):
    raise FileNotFoundError(".env dosyası bulunamadı! Lütfen API anahtarınızı içeren bir .env dosyası oluşturun.")
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY ortam değişkeni .env dosyasında bulunamadı veya ayarlanmamış.")

def load_mcp_servers():
    """mcp_servers.json dosyasını okur ve sunucu adlarının bir listesini döndürür."""
    try:
        with open('mcp_servers.json', 'r') as f:
            data = json.load(f)
            # "mcpServers" anahtarı altındaki sözlüğün anahtarlarını (sunucu adlarını) al
            return list(data.get("mcpServers", {}).keys())
    except FileNotFoundError:
        print("Uyarı: mcp_servers.json dosyası bulunamadı.")
        return []
    except json.JSONDecodeError:
        print("Hata: mcp_servers.json dosyası geçerli bir formatta değil.")
        return []


async def run_mcp_agent(server_name: str, prompt: str, max_steps: int = 30):
    """
    Belirtilen MCP sunucusuna bağlanır, İşgören(agent) oluşturur ve verilen sorguyu çalıştırır.
    Args:
        server_name (str): MCP sunucusunun adı.
        prompt (str): İşgörenin çalıştıracağı sorgu.
        max_steps (int, optional): Ajanın maksimum adım sayısı.
    Returns:
        str: İşgörenin döndürdüğü sonuç, hatalıysa None
    """
    print(f"İşgören {server_name} ile başlatılıyor...")
    
    # Create MCPClient from config file
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "mcp_servers.json")
    )

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=GOOGLE_API_KEY,
    )

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=max_steps)

    try:
        # Run the query
        result = await agent.run(
            f"{prompt}. USING {server_name}",
            max_steps=30,
        )
        # print(f"\nResult: {result}")
        return result

    except ResourceExhausted:
        time.sleep(5)
        return await run_mcp_agent(server_name, prompt, max_steps)
    except Exception as e:
        print(f"An error occurredv1: {e}")
        return None