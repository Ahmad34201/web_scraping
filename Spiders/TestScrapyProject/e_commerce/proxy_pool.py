# importing ABC module to use Abstract classes
from abc import ABC, abstractmethod
import random
from urllib.parse import urlparse
# Observable Abstract class


class Observable(ABC):

    @abstractmethod
    def __init__(self):
        self.observers = []

    def register(self, observer):
        self.observers.append(observer)

    def unregister(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_all_observers(self):
        for observer in self.observers:
            observer.received_notification(self)


# Observer Abstract class
class Observer(ABC):
    @abstractmethod
    def received_notification(self, observeable):
        pass


class Proxy(Observable):
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address

    def reduce_weight(self):
        self.notify_all_observers()


class Pool(Observer):

    def __init__(self, ip_addresses: list):
        MAX_HEALTH = 100
        self.proxies = [Proxy(ip_address) for ip_address in ip_addresses]
        self.proxy_healths = {ip_address: MAX_HEALTH
                              for ip_address in ip_addresses}
        for ip in self.proxies:
            ip.register(self)

    def received_notification(self, observable):
        self.reduce_weight(proxy=observable)

    def reduce_weight(self, proxy):
        HEALTH_REDUCE_FACTOR = 10
        self.proxy_healths[proxy.ip_address] -= HEALTH_REDUCE_FACTOR

        parsed_url = urlparse(proxy.ip_address)
        ip_port = f"https://{parsed_url.hostname}:{parsed_url.port}"
        print(
            f'Health of Proxy {ip_port} reduces to {self.proxy_healths[proxy.ip_address]}')
        if self.proxy_healths[proxy.ip_address] == 0:
            self.proxies.remove(proxy)
            self.proxy_healths.pop(proxy.ip_address, None)
            print("Proxy removed successfully:", ip_port)

    def __getitem__(self, index):
        return self.proxies[index]

    def __len__(self):
        return len(self.proxies)

    def random_proxy_selection(self):
        total_proxies_health = 0
        proxies_health = []

        # Pre calculating the weights of all proxies related to their health's
        for proxy in self.proxies:
            total_proxies_health += self.proxy_healths[proxy.ip_address]
            proxies_health.append((total_proxies_health, proxy.ip_address))

        if total_proxies_health:
            bisection_random_num = random.randint(0, total_proxies_health - 1)
            # Custom left bisect algorithm implementation
            random_ip_selected = None
            for i, (proxy_health, ip_address) in enumerate(proxies_health):
                if proxy_health > bisection_random_num:
                    random_ip_selected = proxies_health[i]
                    break

            # Check if random_ip_selected is found
            if random_ip_selected:
                for proxy in self.proxies:
                    if proxy.ip_address == random_ip_selected[1]:
                        return proxy
            else:
                print(
                    "No proxy selected. Random number may be greater than total proxy health.")

        else:
            return None
