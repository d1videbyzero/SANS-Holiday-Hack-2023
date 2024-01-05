from websockets import connect
import json, time, asyncio

url = 'wss://2023.holidayhackchallenge.com/ws'
sail_url = 'wss://2023.holidayhackchallenge.com/sail'
# username = ''
# password = ''
current_state = {}

async def login():
    async with connect(url) as websocket:
        username = input("Username: ")
        password = input("Password: ")
        # await ws.send('{"type":"WS_CONNECTED","session":null,"protocol":"43ae08fd-9cf2-4f54-a6a6-8454aef59581"}')
        await websocket.send('{"type":"WS_LOGIN","usernameOrEmail":"%s","password":"%s"}' % (username, password))
        await handle_receive_ohhimark(websocket)
        await set_sail(websocket)
        await handle_receive_set_sail(websocket)
        return current_state['dockSlip']
    

async def run():
    dock_slip = await login()
    special_url = "{}?dockSlip={}".format(sail_url, dock_slip)
    async with connect(special_url) as websocket:
        await websocket.send('cast')
        print('Line cast...')
        while True:
            response = await websocket.recv()
            response_type = response[:2]
            if response_type in ['v:','x:']:
                continue
            if response_type == 'i:':
                data = json.loads(response[2:])
                fish_caught = data['fishCaught']
                print("Fish caught: {}/171".format(len(fish_caught)))
            if 'fishing":false' in response:
                await websocket.send("cast")
            if 'onTheLine' in response:
                data = json.loads(response[2:])
                fish = data['53428']['onTheLine']
                if fish:
                    await websocket.send('reel')
                    fish_caught = data['53428']['fishCaught']
                    print("Caught a", fish)
                    await websocket.send('cast')
                    print("Line cast...")

async def handle_receive(ws):
    data = await ws.recv()

    try:
        if data == "":
            print("No message to receive")

        message = json.loads(data)
        m_type = message['type']
        print("Received message with type: ", m_type)

        if m_type == "WS_OHHIMARK":
            print(data)
            if 'sid' in data:
                current_state['sid'] = message['sid']
                print("set sid")
            if 'userId' in data:
                current_state['userId'] = message['userId']
                print("set userId")
            return m_type
        elif m_type == "SET_SAIL":
            current_state['dockSlip'] = message['dockSlip']
            print("Dock:{}".format(current_state['dockSlip']))
            return m_type
        elif m_type == "AAANNNDD_SCENE":
            return m_type
        elif m_type == "SET_ENTITYAREAS":
            return m_type
        elif m_type == "OOOH_SPARKLY":
            return m_type
        elif m_type == "SET_CONVERSATIONS":
            return m_type
        elif m_type == "WS_USERS":
            return m_type
        elif m_type == "SET_TOKENS":
            return m_type
        elif m_type == "SET_ENV":
            return m_type
        elif m_type == "SET_HIDDEN_CHATTERS":
            return m_type
        elif m_type == "SET_LOCATIONS":
            return m_type
        elif m_type == "SET_ENTITYAREAS":
            return m_type
        elif m_type == "SET_CONVERSATIONS":
            return m_type
        elif m_type == "SET_ENTITIES":
            return m_type
        elif m_type == "CHORT":
            return m_type
        elif m_type == "AUF_WIEDERSEHEN":
            return m_type
        elif m_type == "SIDDOWN":
            return m_type
        elif m_type == "HIDE_SPINNER":
            return m_type
        elif m_type == "SET_SAIL":
            if 'dockSlip' in message:
                print("Got dockslip: ", message['dockSlip'])
            return
        else:
            print("Type:{} Message:{}".format(m_type, message))
        return m_type
    except:
        print("Error in handle_receive: ", data)

async def handle_receive_sailing(ws):
    data = await ws.recv()
    message_type = data[:2]
    payload = data[2:]

    if message_type == 'e:':
        if 'canFish' in payload:
            await cast_line(ws)
        elif 'user2022' in payload:
            print(payload)
    elif message_type == 'v:':
        parts = payload.split(":")
        for i in range(0, len(parts), 5):
            uid = parts[i]
            x = parts[i+1]
            y = parts[i+2]
            o = parts[i+3]
            fishing = parts[i+4]

            if uid not in current_state:
                current_state[uid] = {}
            current_state[uid]['x'] = x
            current_state[uid]['y'] = y
            current_state[uid]['o'] = o
            current_state[uid]['fishing'] = fishing == '1'
    elif message_type == 'i:':
        parsed = json.loads(payload)
        current_state['player_data'] = parsed
    else:
        return

async def handle_receive_set_sail(ws):
    while True:
        m_type = await handle_receive(ws)
        if m_type == "SET_SAIL":
            print("we set sail")
            return

async def handle_receive_ohhimark(ws):
    while 'sid' not in current_state:
        await handle_receive(ws)

async def handle_receive_cont(ws):
    while True:
        await handle_receive(ws)

async def handle_receive_sailing_cont(ws):
    while True:
        await handle_receive_sailing(ws)

async def set_sail(ws):
    await ws.send('{"type":"setSail"}')
    print("Set Sail!")
    # handle_receive_cont(ws)

async def cast_line(ws):
    print("line cast")
    await ws.send("cast")

async def reel_line(ws):
    await ws.send("reel")

async def fish(ws):
    await cast_line(ws)
    # Wait for event
    await handle_receive_sailing_cont(ws)

if __name__ == "__main__":
    asyncio.run(run())
