import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

# Configurando logging para simular um ambiente real
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')

@dataclass(order=True)
class Message:
    """
    Representa uma mensagem na fila. 
    O `order=True` faz com que o heapq ordene automaticamente pelo timestamp e, 
    em caso de empate, pelo sender_id.
    """
    timestamp: int
    sender_id: str
    content: str = field(compare=False) # Ignorado na ordenação
    msg_type: str = field(compare=False, default='MSG')


class Network:
    """
    Simula a rede de comunicação.
    """
    def __init__(self):
        self.users: Dict[str, 'User'] = {}
        self.latencies: Dict[tuple, float] = {}
        self._pending_tasks: Set[asyncio.Task] = set() # Protege as tasks do Garbage Collector

    def register_user(self, user: 'User'):
        self.users[user.user_id] = user

    def set_latency(self, sender: str, receiver: str, delay_seconds: float):
        self.latencies[(sender, receiver)] = delay_seconds

    def broadcast(self, sender_id: str, msg_type: str, timestamp: int, content: str = ""):
        for receiver_id, user in self.users.items():
            if receiver_id != sender_id:
                delay = self.latencies.get((sender_id, receiver_id), 0.1)
                
                # Cria a task e guarda a referência para evitar cancelamento prematuro
                task = asyncio.create_task(
                    self._deliver(delay, user, sender_id, msg_type, timestamp, content)
                )
                self._pending_tasks.add(task)
                task.add_done_callback(self._pending_tasks.discard)

    async def _deliver(self, delay: float, user: 'User', sender_id: str, msg_type: str, timestamp: int, content: str):
        await asyncio.sleep(delay)
        user.receive(sender_id, msg_type, timestamp, content)


class User:
    def __init__(self, user_id: str, network: Network):
        self.user_id = user_id
        self.network = network
        self.clock = 0
        self.queue: List[Message] = [] 
        self.latest_ts_from: Dict[str, int] = {} 
        self.delivered_chat: List[str] = [] 

    def init_peers(self, peer_ids: List[str]):
        for pid in peer_ids:
            if pid != self.user_id:
                self.latest_ts_from[pid] = 0

    def send_chat(self, text: str):
        self.clock += 1
        msg_ts = self.clock
        logging.info(f"[REDE] {self.user_id} enviou: '{text}' (Ts Lógico: {msg_ts})")
        
        msg = Message(timestamp=msg_ts, sender_id=self.user_id, content=text, msg_type='MSG')
        heapq.heappush(self.queue, msg)
        
        self.network.broadcast(self.user_id, 'MSG', msg_ts, text)
        self.try_deliver()

    def receive(self, sender_id: str, msg_type: str, timestamp: int, content: str):
        self.clock = max(self.clock, timestamp) + 1
        self.latest_ts_from[sender_id] = max(self.latest_ts_from[sender_id], timestamp)

        if msg_type == 'MSG':
            msg = Message(timestamp=timestamp, sender_id=sender_id, content=content, msg_type=msg_type)
            heapq.heappush(self.queue, msg)
            
            self.clock += 1
            self.network.broadcast(self.user_id, 'ACK', self.clock)

        self.try_deliver()

    def try_deliver(self):
        while self.queue:
            top_msg = self.queue[0]
            can_deliver = True
            
            for peer_id, last_ts in self.latest_ts_from.items():
                # Validação de Ordenação Total de Lamport
                if last_ts < top_msg.timestamp or (last_ts == top_msg.timestamp and peer_id < top_msg.sender_id):
                    can_deliver = False
                    break
            
            if can_deliver:
                heapq.heappop(self.queue)
                self.delivered_chat.append(f"{top_msg.sender_id}: {top_msg.content}")
            else:
                break


async def main():
    net = Network()
    
    # Nomes atualizados aqui
    users = [User("Matheus", net), User("Luiz", net), User("Fernando", net)]
    
    for u in users:
        net.register_user(u)
        u.init_peers(["Matheus", "Luiz", "Fernando"])

    # Ajuste das latências para os novos nomes
    net.set_latency("Matheus", "Luiz", 0.1)
    net.set_latency("Matheus", "Fernando", 1.8)
    
    net.set_latency("Luiz", "Matheus", 0.2)
    net.set_latency("Luiz", "Fernando", 1.5)
    
    net.set_latency("Fernando", "Matheus", 1.2)
    net.set_latency("Fernando", "Luiz", 1.2)

    logging.info("--- Iniciando envio concorrente ---")
    users[0].send_chat("Oi equipe!")
    users[1].send_chat("Bom dia!")
    users[2].send_chat("Desculpem o atraso, a net ta ruim.")

    logging.info("Aguardando propagação e ordenação (simulação de atrasos de rede)...")
    await asyncio.sleep(4)

    print("\n" + "="*30)
    print("--- Telas Finais do Chat ---")
    for u in users:
        print(f"Tela de {u.user_id}:")
        for msg in u.delivered_chat:
            print(f"  > {msg}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
