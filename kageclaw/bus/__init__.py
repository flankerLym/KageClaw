"""Message bus module for decoupled channel-agent communication."""

from kageclaw.bus.events import InboundMessage, OutboundMessage
from kageclaw.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
