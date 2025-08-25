import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from ..models import BotStatus, BotConfig, BotState, BotStats
from ..utils.logger import get_logger, log_performance
from .device_service import DeviceService
from .monitoring_service import MonitoringService

logger = get_logger(__name__)

class BotService:
    """Service for managing the Rush Royale bot."""
    
    def __init__(self):
        self.config = BotConfig()
        self.state = BotState.STOPPED
        self.start_time: Optional[datetime] = None
        self.battles_played = 0
        self.battles_won = 0
        self.current_wave: Optional[int] = None
        self.current_coop: Optional[int] = None
        self.last_action: Optional[str] = None
        self.last_action_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.connected_device: Optional[str] = None
        
        # Services
        self.device_service: Optional[DeviceService] = None
        self.monitoring_service: Optional[MonitoringService] = None
        
        # Bot control
        self._bot_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        
        # Statistics
        self.stats = BotStats(
            total_runtime=0.0,
            total_battles=0,
            win_rate=0.0,
            average_wave=0.0,
            cards_upgraded=0,
            merges_performed=0,
            screenshots_taken=0,
            errors_encountered=0,
            last_reset=datetime.now()
        )
    
    async def initialize(self):
        """Initialize the bot service."""
        logger.info("Initializing bot service...")
        
        # Initialize dependent services
        from .device_service import DeviceService
        from .monitoring_service import MonitoringService
        
        self.device_service = DeviceService()
        self.monitoring_service = MonitoringService()
        
        await self.device_service.initialize()
        await self.monitoring_service.initialize()
        
        logger.info("Bot service initialized")
    
    async def cleanup(self):
        """Cleanup bot service."""
        logger.info("Cleaning up bot service...")
        
        if self.state in [BotState.RUNNING, BotState.PAUSED]:
            await self.stop_bot()
        
        if self.device_service:
            await self.device_service.cleanup()
        
        if self.monitoring_service:
            await self.monitoring_service.cleanup()
        
        logger.info("Bot service cleanup complete")
    
    @log_performance
    async def start_bot(self, config_updates: Optional[Dict[str, Any]] = None) -> BotStatus:
        """Start the bot with optional configuration updates."""
        if self.state in [BotState.RUNNING, BotState.STARTING]:
            raise ValueError("Bot is already running or starting")
        
        logger.info("Starting bot...")
        self.state = BotState.STARTING
        self.error_message = None
        
        try:
            # Update configuration if provided
            if config_updates:
                await self.update_config(config_updates)
            
            # Ensure device is connected
            if not await self._ensure_device_connected():
                raise RuntimeError("No device available for bot operation")
            
            # Reset statistics for new session
            self.start_time = datetime.now()
            self.battles_played = 0
            self.battles_won = 0
            self.current_wave = None
            self.current_coop = None
            
            # Start bot task
            self._stop_event.clear()
            self._pause_event.set()  # Start unpaused
            self._bot_task = asyncio.create_task(self._bot_main_loop())
            
            self.state = BotState.RUNNING
            self.last_action = "Bot started"
            self.last_action_time = datetime.now()
            
            logger.info("Bot started successfully")
            return await self.get_status()
            
        except Exception as e:
            self.state = BotState.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def stop_bot(self) -> BotStatus:
        """Stop the bot."""
        if self.state == BotState.STOPPED:
            return await self.get_status()
        
        logger.info("Stopping bot...")
        self.state = BotState.STOPPING
        
        try:
            # Signal stop
            self._stop_event.set()
            
            # Wait for bot task to complete
            if self._bot_task and not self._bot_task.done():
                try:
                    await asyncio.wait_for(self._bot_task, timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning("Bot task did not stop gracefully, cancelling...")
                    self._bot_task.cancel()
                    try:
                        await self._bot_task
                    except asyncio.CancelledError:
                        pass
            
            # Update statistics
            if self.start_time:
                session_time = (datetime.now() - self.start_time).total_seconds()
                self.stats.total_runtime += session_time
            
            self.state = BotState.STOPPED
            self.start_time = None
            self.last_action = "Bot stopped"
            self.last_action_time = datetime.now()
            
            logger.info("Bot stopped successfully")
            return await self.get_status()
            
        except Exception as e:
            self.state = BotState.ERROR
            self.error_message = str(e)
            logger.error(f"Failed to stop bot: {e}")
            raise
    
    async def pause_bot(self) -> BotStatus:
        """Pause the bot."""
        if self.state != BotState.RUNNING:
            raise ValueError("Bot is not running")
        
        logger.info("Pausing bot...")
        self.state = BotState.PAUSED
        self._pause_event.clear()
        
        self.last_action = "Bot paused"
        self.last_action_time = datetime.now()
        
        return await self.get_status()
    
    async def resume_bot(self) -> BotStatus:
        """Resume the bot."""
        if self.state != BotState.PAUSED:
            raise ValueError("Bot is not paused")
        
        logger.info("Resuming bot...")
        self.state = BotState.RUNNING
        self._pause_event.set()
        
        self.last_action = "Bot resumed"
        self.last_action_time = datetime.now()
        
        return await self.get_status()
    
    async def get_status(self) -> BotStatus:
        """Get current bot status."""
        uptime = None
        if self.start_time and self.state in [BotState.RUNNING, BotState.PAUSED]:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return BotStatus(
            state=self.state,
            uptime=uptime,
            battles_played=self.battles_played,
            battles_won=self.battles_won,
            current_wave=self.current_wave,
            current_coop=self.current_coop,
            last_action=self.last_action,
            last_action_time=self.last_action_time,
            error_message=self.error_message,
            connected_device=self.connected_device,
            config=self.config
        )
    
    async def update_config(self, updates: Dict[str, Any]) -> BotConfig:
        """Update bot configuration."""
        logger.info(f"Updating bot configuration: {updates}")
        
        # Validate and update configuration
        config_dict = self.config.dict()
        config_dict.update(updates)
        
        try:
            self.config = BotConfig(**config_dict)
            self.last_action = "Configuration updated"
            self.last_action_time = datetime.now()
            
            logger.info("Bot configuration updated successfully")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise ValueError(f"Invalid configuration: {e}")
    
    async def get_stats(self) -> BotStats:
        """Get bot statistics."""
        # Update current session stats
        if self.start_time and self.state in [BotState.RUNNING, BotState.PAUSED]:
            session_time = (datetime.now() - self.start_time).total_seconds()
            current_runtime = self.stats.total_runtime + session_time
        else:
            current_runtime = self.stats.total_runtime
        
        # Calculate win rate
        win_rate = (self.battles_won / max(self.battles_played, 1)) * 100
        
        return BotStats(
            total_runtime=current_runtime,
            total_battles=self.stats.total_battles + self.battles_played,
            win_rate=win_rate,
            average_wave=self.stats.average_wave,  # TODO: Calculate properly
            cards_upgraded=self.stats.cards_upgraded,
            merges_performed=self.stats.merges_performed,
            screenshots_taken=self.stats.screenshots_taken,
            errors_encountered=self.stats.errors_encountered,
            last_reset=self.stats.last_reset
        )
    
    async def reset_stats(self) -> BotStats:
        """Reset bot statistics."""
        logger.info("Resetting bot statistics")
        
        self.stats = BotStats(
            total_runtime=0.0,
            total_battles=0,
            win_rate=0.0,
            average_wave=0.0,
            cards_upgraded=0,
            merges_performed=0,
            screenshots_taken=0,
            errors_encountered=0,
            last_reset=datetime.now()
        )
        
        return self.stats
    
    async def _ensure_device_connected(self) -> bool:
        """Ensure a device is connected and ready."""
        if not self.device_service:
            return False
        
        devices = await self.device_service.get_devices()
        
        # Use preferred device if specified
        if self.config.preferred_device:
            for device in devices:
                if device.id == self.config.preferred_device and device.status.value == "connected":
                    self.connected_device = device.id
                    return True
        
        # Use any connected device
        for device in devices:
            if device.status.value == "connected":
                self.connected_device = device.id
                return True
        
        # Try to connect to available devices
        for device in devices:
            if device.status.value == "disconnected":
                try:
                    await self.device_service.connect_device(device.id)
                    self.connected_device = device.id
                    return True
                except Exception as e:
                    logger.warning(f"Failed to connect to device {device.id}: {e}")
        
        return False
    
    async def _bot_main_loop(self):
        """Main bot execution loop."""
        logger.info("Bot main loop started")
        
        try:
            while not self._stop_event.is_set():
                # Wait if paused
                await self._pause_event.wait()
                
                # Check if we should stop
                if self._stop_event.is_set():
                    break
                
                # Perform bot actions
                await self._bot_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(self.config.screenshot_interval)
                
        except Exception as e:
            logger.error(f"Bot main loop error: {e}")
            self.state = BotState.ERROR
            self.error_message = str(e)
            self.stats.errors_encountered += 1
        
        logger.info("Bot main loop ended")
    
    async def _bot_cycle(self):
        """Perform one bot cycle."""
        try:
            # Take screenshot
            if self.device_service and self.connected_device:
                screenshot_result = await self.device_service.take_screenshot(self.connected_device)
                if screenshot_result.success:
                    self.stats.screenshots_taken += 1
                    
                    # Analyze screenshot and perform actions
                    await self._analyze_and_act(screenshot_result.file_path)
            
            self.last_action = "Bot cycle completed"
            self.last_action_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Bot cycle error: {e}")
            self.stats.errors_encountered += 1
            raise
    
    async def _analyze_and_act(self, screenshot_path: Optional[str]):
        """Analyze screenshot and perform appropriate actions."""
        if not screenshot_path:
            return
        
        # TODO: Implement actual game analysis and actions
        # This is a placeholder for the core bot logic
        
        # For now, just log that we're analyzing
        logger.debug(f"Analyzing screenshot: {screenshot_path}")
        
        # Simulate some bot actions
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Example: Check if we're in battle, in menu, etc.
        # This would be replaced with actual image recognition
        
        self.last_action = "Screenshot analyzed"