from fastapi import WebSocket
import json
import logging
from typing import Dict, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        # Active connections
        self.active_connections: List[WebSocket] = []
        
        # Subscriptions: stream_name -> set of websockets
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "subscriptions": set()
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for stream_name, subscribers in self.subscriptions.items():
            subscribers.discard(websocket)
        
        # Clean up metadata
        self.connection_metadata.pop(websocket, None)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, websocket: WebSocket, stream_name: str):
        """Subscribe a WebSocket to a data stream."""
        if stream_name not in self.subscriptions:
            self.subscriptions[stream_name] = set()
        
        self.subscriptions[stream_name].add(websocket)
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscriptions"].add(stream_name)
        
        logger.debug(f"WebSocket subscribed to {stream_name}. Subscribers: {len(self.subscriptions[stream_name])}")
        
        # Send confirmation
        await self.send_personal_message(websocket, {
            "type": "subscription_confirmed",
            "stream": stream_name,
            "timestamp": datetime.now().isoformat()
        })
    
    async def unsubscribe(self, websocket: WebSocket, stream_name: str):
        """Unsubscribe a WebSocket from a data stream."""
        if stream_name in self.subscriptions:
            self.subscriptions[stream_name].discard(websocket)
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscriptions"].discard(stream_name)
        
        logger.debug(f"WebSocket unsubscribed from {stream_name}")
        
        # Send confirmation
        await self.send_personal_message(websocket, {
            "type": "unsubscription_confirmed",
            "stream": stream_name,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Remove disconnected websocket
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSockets."""
        if not self.active_connections:
            return
        
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_subscribers(self, stream_name: str, message: dict):
        """Broadcast a message to subscribers of a specific stream."""
        if stream_name not in self.subscriptions:
            return
        
        subscribers = self.subscriptions[stream_name].copy()
        if not subscribers:
            return
        
        disconnected = []
        for websocket in subscribers:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to subscriber: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def get_subscription_count(self, stream_name: str) -> int:
        """Get the number of subscribers for a stream."""
        return len(self.subscriptions.get(stream_name, set()))
    
    def get_all_subscriptions(self) -> Dict[str, int]:
        """Get subscription counts for all streams."""
        return {stream: len(subscribers) for stream, subscribers in self.subscriptions.items()}
    
    def get_connection_info(self) -> List[dict]:
        """Get information about all connections."""
        info = []
        for websocket in self.active_connections:
            metadata = self.connection_metadata.get(websocket, {})
            info.append({
                "client": str(websocket.client) if websocket.client else "unknown",
                "connected_at": metadata.get("connected_at", datetime.now()).isoformat(),
                "subscriptions": list(metadata.get("subscriptions", set()))
            })
        return info
    
    async def send_ping_to_all(self):
        """Send ping to all connections to check if they're alive."""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(ping_message)
    
    async def cleanup_dead_connections(self):
        """Clean up connections that are no longer responsive."""
        # This would typically involve sending pings and removing
        # connections that don't respond within a timeout
        pass