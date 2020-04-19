from autobahn.asyncio.component import Component, run

from .controller import Controller

COMPONENT = Component(transports="ws://localhost:8081/ws", realm="realm1")
CONTROLLER = Controller(COMPONENT)

run([COMPONENT])
