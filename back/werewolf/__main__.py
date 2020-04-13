from autobahn.asyncio.component import Component, run
from autobahn.asyncio.wamp import ApplicationRunner

from .controller import Controller


component = Component(
    transports="ws://localhost:8081/ws",
    realm="realm1")


controller = Controller(component)
run([component])
