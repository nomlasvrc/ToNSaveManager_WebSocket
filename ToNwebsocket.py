import asyncio
import socket
import time
import websockets
import json

def IsBool(value): # 不要かも
    if value == "true" or value == "True" or value == True:
        return True
    else:
        return False
    
def clamp_color(value):
    if (value > 255):
        value = 255
    if (value < 0):
        value = 0
    return value
    
def color(display_color, hexType: bool):
    color_r = clamp_color(int(display_color / 65536))
    color_g = clamp_color(int(display_color % 65536 / 256))
    color_b = clamp_color(int(display_color % 256))
    if hexType:
        return f"#{color_r:0=2x}{color_g:0=2x}{color_b:0=2x}"
    else:
        return f"\033[38;2;{color_r};{color_g};{color_b}m"

def XSOverlayNotification(NotificationMessage):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    msg = {
    "messageType": 1,
    "index": 0,
    "title": NotificationMessage,
    "content": "",
    "height": 120.0,
    "sourceApp": "ToN WebSocket",
    "timeout": 6.0,
    "volume": 0.1,
    "audioPath": "default",
    "useBase64Icon": False,
    "icon": "default",
    "opacity": 1.0
    }
    msgdata = json.dumps(msg)
    byte = msgdata.encode()
    sock.sendto(byte, ("127.0.0.1", 42069))   
    sock.close()

def show_message(message, item_stats: bool, overseer: bool, colorful: bool, xsoverlay: bool):
    RESET = '\033[0m'
    try:
        data = json.loads(message)
        type = data.get("Type")
        match type:
            case "CONNECTED":
                display_name = data.get("DisplayName")
                user_id = data.get("UserID")
                args = data.get("Args", [])
                print(f"Hello, {display_name}さん！")

            case "STATS":
                stat_name = data.get("Name")
                value = data.get("Value")
                #print(f"Stat changed: {stat_name} = {value}")

            case "TERRORS":
                command = data.get("Command")
                names = data.get("Names", [])
                display_name = data.get("DisplayName")
                display_color = data.get("DisplayColor")
                if names != None:
                    m = "テラー:"
                    n = "テラー:"
                    for i in range(len(names)):
                        if i == 0:
                            if colorful:
                                m += f" {color(display_color, False)}{names[i]}{RESET}"
                                n += f" <color={color(display_color, True)}>{names[i]}</color>"
                            else:
                                m += f" {names[i]}"
                                n += f" {names[i]}"
                        else:
                            m += f", {names[i]}"
                            n += f", {names[i]}"
                    print(m)
                    if xsoverlay:
                        XSOverlayNotification(n)

            case "ROUND_TYPE":
                command = data.get("Command")
                value = data.get("Value")
                name = data.get("Name")
                display_name = data.get("DisplayName")
                display_color = data.get("DisplayColor")
                if command == 0:
                    print(f"ラウンド終了")
                elif command == 1:
                    if colorful:
                        print(f"ラウンド: {color(display_color, False)}{display_name}{RESET}")
                    else:
                        print(f"ラウンド: {display_name}")
                else:
                    print(f"(未定義エラー)ラウンドコマンド: {command}")

            case "LOCATION":
                command = data.get("Command")
                name = data.get("Name")
                creator = data.get("Creator")
                origin = data.get("Origin")
                m = f"LOCATION: {name}"
                if creator != "":
                    m += f" by {creator}"
                if origin != "":
                    m += f" from {origin}"
                if overseer or name != "Overseer's Court":
                    print(m)

            case "ITEM":
                command = data.get("Command")
                name = data.get("Name")
                item_id = data.get("ID")
                if item_stats:
                    if command == 0:
                        print(f"アイテムを置いた")
                    elif command == 1:
                        print(f"アイテム: {name}")
                    else:
                        print(f"(未定義エラー)アイテムコマンド: {command}")

            case "INSTANCE":
                instance_value = data.get("Value")
                #print(f"Instance: {instance_value}")

            case "ROUND_ACTIVE":
                is_active = IsBool(data.get("Value"))
                #print(f"Round Active: {is_active}")

            case "ALIVE":
                is_alive = IsBool(data.get("Value"))

            case "REBORN":
                is_reborn = IsBool(data.get("Value"))
                if is_reborn:
                    print("マクスウェルにお礼を言おうね！")

            case "OPTED_IN":
                opted_in = IsBool(data.get("Value"))
                #print(f"Opted In: {opted_in}")

            case "IS_SABOTEUR":
                is_saboteur = IsBool(data.get("Value"))
                #if is_saboteur:
                #    print("「良い仕事ぶり」期待しているよ。")

            case "PAGE_COUNT":
                page_count = data.get("Value")
                if page_count != 0:
                    print(f"{page_count}/8ページ")

            case "DAMAGED":
                damage_value = data.get("Value")
                #print(f"{damage_value}ダメージ")

            case "DEATH":
                name = data.get("Name")
                message = data.get("Message")
                is_local = IsBool(data.get("IsLocal"))
                print(message)

            case "PLAYER_JOIN":
                player_name = data.get("Value")
                print(f"[Join] { player_name}")

            case "PLAYER_LEAVE":
                player_name = data.get("Value")
                print(f"[Leave] {player_name}")

            case "SAVED":
                save_code = data.get("Value")
                #print(f"{save_code}")

            case "MASTER_CHANGE":
                print("マスター変更")

            case "TRACKER":
                event = data.get("event")
                args = data.get("args")
                #print(f"[{event}] {args}")

            case _:
                print(data)
    except json.JSONDecodeError:
        print("JSON解析エラー")
        print(message)

async def main():
    uri = "ws://localhost:11398"
    async with websockets.connect(uri) as websocket:
        while True:
            show_message(await websocket.recv(), False, False, True, False)


try:
    print("ToNSaveManagerに接続中...")
    asyncio.run(main())
except ConnectionRefusedError as e:
    print()
    print(e)
    print()
    print("接続拒否エラーが発生しました。ToNSaveManagerが起動していることを確認してください。")
    print("5秒後に終了します...")
    time.sleep(5)
except websockets.exceptions.ConnectionClosedError as e:
    print()
    print(e)
    print()
    print("切断されました。")
    print("5秒後に終了します...")
    time.sleep(5)
except KeyboardInterrupt as e:
    print(e)
    print("終了中...")
    exit()