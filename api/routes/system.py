from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from ..models import (
    SystemInfo, PerformanceMetrics, DisplayInfo, PowerInfo,
    LogEntry, LogFilter, NetworkMetrics,
    APIResponse, PaginatedResponse
)
from ..services.monitoring_service import MonitoringService
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/system", tags=["system"])

# Global monitoring service instance
monitoring_service: MonitoringService = None

def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    global monitoring_service
    if monitoring_service is None:
        monitoring_service = MonitoringService()
    return monitoring_service

@router.get("/info", response_model=APIResponse[SystemInfo])
async def get_system_info():
    """Get general system information."""
    try:
        service = get_monitoring_service()
        info = await service.get_system_info()
        return APIResponse(
            success=True,
            data=info,
            message="System information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance", response_model=APIResponse[PerformanceMetrics])
async def get_performance_metrics():
    """Get current system performance metrics."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        return APIResponse(
            success=True,
            data=metrics,
            message="Performance metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/displays", response_model=APIResponse[List[DisplayInfo]])
async def get_display_info():
    """Get information about connected displays."""
    try:
        service = get_monitoring_service()
        displays = await service.get_display_info()
        return APIResponse(
            success=True,
            data=displays,
            message=f"Found {len(displays)} displays"
        )
    except Exception as e:
        logger.error(f"Failed to get display info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/power", response_model=APIResponse[PowerInfo])
async def get_power_info():
    """Get power and battery information."""
    try:
        service = get_monitoring_service()
        power = await service.get_power_info()
        return APIResponse(
            success=True,
            data=power,
            message="Power information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get power info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=PaginatedResponse[LogEntry])
async def get_logs(
    level: Optional[str] = Query(None, description="Log level filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    source: Optional[str] = Query(None, description="Log source filter"),
    start_time: Optional[datetime] = Query(None, description="Start time filter (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time filter (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip")
):
    """Get system logs with optional filtering."""
    try:
        service = get_monitoring_service()
        
        # Create log filter
        log_filter = LogFilter(
            level=level,
            source=source,
            start_time=start_time,
            end_time=end_time
        )
        
        logs = await service.get_logs(log_filter, limit, offset)
        total_count = len(logs)  # In a real implementation, you'd get the total count separately
        
        return PaginatedResponse(
            success=True,
            data=logs,
            total=total_count,
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(logs)} log entries"
        )
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network", response_model=APIResponse[NetworkMetrics])
async def get_network_metrics():
    """Get current network metrics."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        # Extract network metrics from performance metrics
        network_metrics = NetworkMetrics(
            bytes_sent=metrics.network_io.bytes_sent,
            bytes_recv=metrics.network_io.bytes_recv,
            packets_sent=metrics.network_io.packets_sent,
            packets_recv=metrics.network_io.packets_recv,
            connections_active=len(metrics.network_connections) if metrics.network_connections else 0,
            timestamp=metrics.timestamp
        )
        
        return APIResponse(
            success=True,
            data=network_metrics,
            message="Network metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get network metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processes", response_model=APIResponse[List[dict]])
async def get_top_processes(
    limit: int = Query(10, ge=1, le=50, description="Number of top processes to return")
):
    """Get top processes by CPU or memory usage."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        # Sort processes by CPU usage and limit
        top_processes = sorted(
            metrics.top_processes,
            key=lambda p: p.cpu_percent,
            reverse=True
        )[:limit]
        
        # Convert to dict format for easier consumption
        processes_data = [
            {
                "pid": proc.pid,
                "name": proc.name,
                "cpu_percent": proc.cpu_percent,
                "memory_percent": proc.memory_percent,
                "memory_mb": round(proc.memory_mb, 1),
                "status": proc.status
            }
            for proc in top_processes
        ]
        
        return APIResponse(
            success=True,
            data=processes_data,
            message=f"Retrieved top {len(processes_data)} processes"
        )
    except Exception as e:
        logger.error(f"Failed to get top processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/temperature", response_model=APIResponse[dict])
async def get_temperature_info():
    """Get system temperature information."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        temperature_data = {
            "cpu_temperature": metrics.cpu_temperature,
            "thermal_state": metrics.thermal_state,
            "timestamp": metrics.timestamp.isoformat()
        }
        
        return APIResponse(
            success=True,
            data=temperature_data,
            message="Temperature information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get temperature info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disk", response_model=APIResponse[List[dict]])
async def get_disk_usage():
    """Get disk usage information for all mounted drives."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        disk_data = [
            {
                "device": disk.device,
                "mountpoint": disk.mountpoint,
                "fstype": disk.fstype,
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": disk.percent
            }
            for disk in metrics.disk_usage
        ]
        
        return APIResponse(
            success=True,
            data=disk_data,
            message=f"Retrieved disk usage for {len(disk_data)} drives"
        )
    except Exception as e:
        logger.error(f"Failed to get disk usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memory", response_model=APIResponse[dict])
async def get_memory_details():
    """Get detailed memory usage information."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        memory_data = {
            "total_gb": round(metrics.memory.total / (1024**3), 2),
            "available_gb": round(metrics.memory.available / (1024**3), 2),
            "used_gb": round(metrics.memory.used / (1024**3), 2),
            "percent_used": metrics.memory.percent,
            "swap_total_gb": round(metrics.memory.swap_total / (1024**3), 2) if metrics.memory.swap_total else 0,
            "swap_used_gb": round(metrics.memory.swap_used / (1024**3), 2) if metrics.memory.swap_used else 0,
            "swap_percent": metrics.memory.swap_percent if metrics.memory.swap_percent else 0,
            "timestamp": metrics.timestamp.isoformat()
        }
        
        return APIResponse(
            success=True,
            data=memory_data,
            message="Memory details retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get memory details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cpu", response_model=APIResponse[dict])
async def get_cpu_details():
    """Get detailed CPU usage information."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        
        cpu_data = {
            "usage_percent": metrics.cpu_percent,
            "core_count": metrics.cpu_count,
            "frequency_mhz": metrics.cpu_freq,
            "load_average": metrics.load_average,
            "per_core_usage": metrics.cpu_per_core,
            "timestamp": metrics.timestamp.isoformat()
        }
        
        return APIResponse(
            success=True,
            data=cpu_data,
            message="CPU details retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get CPU details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-logs", response_model=APIResponse[dict])
async def clear_logs(
    older_than_hours: int = Query(24, ge=1, description="Clear logs older than specified hours")
):
    """Clear old log entries."""
    try:
        service = get_monitoring_service()
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        # In a real implementation, you would clear logs from the log capture
        # For now, we'll just return a success message
        cleared_count = 0  # Placeholder
        
        return APIResponse(
            success=True,
            data={"cleared_count": cleared_count, "cutoff_time": cutoff_time.isoformat()},
            message=f"Cleared {cleared_count} log entries older than {older_than_hours} hours"
        )
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=APIResponse[dict])
async def get_system_health():
    """Get overall system health status."""
    try:
        service = get_monitoring_service()
        metrics = await service.get_performance_metrics()
        power = await service.get_power_info()
        
        # Calculate health score based on various metrics
        health_score = 100
        issues = []
        
        # Check CPU usage
        if metrics.cpu_percent > 90:
            health_score -= 20
            issues.append("High CPU usage")
        elif metrics.cpu_percent > 70:
            health_score -= 10
            issues.append("Moderate CPU usage")
        
        # Check memory usage
        if metrics.memory.percent > 90:
            health_score -= 20
            issues.append("High memory usage")
        elif metrics.memory.percent > 70:
            health_score -= 10
            issues.append("Moderate memory usage")
        
        # Check disk usage
        for disk in metrics.disk_usage:
            if disk.percent > 95:
                health_score -= 15
                issues.append(f"Disk {disk.device} almost full")
            elif disk.percent > 85:
                health_score -= 5
                issues.append(f"Disk {disk.device} getting full")
        
        # Check battery (if available)
        if power.battery_percent is not None and power.battery_percent < 20:
            health_score -= 10
            issues.append("Low battery")
        
        # Check thermal state
        if metrics.thermal_state and metrics.thermal_state.lower() in ['critical', 'emergency']:
            health_score -= 25
            issues.append("Critical thermal state")
        elif metrics.thermal_state and metrics.thermal_state.lower() in ['warning', 'hot']:
            health_score -= 10
            issues.append("High temperature")
        
        health_status = "excellent" if health_score >= 90 else \
                       "good" if health_score >= 70 else \
                       "fair" if health_score >= 50 else "poor"
        
        health_data = {
            "score": max(0, health_score),
            "status": health_status,
            "issues": issues,
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory.percent,
                "disk_usage_max": max([d.percent for d in metrics.disk_usage]) if metrics.disk_usage else 0,
                "battery_percent": power.battery_percent,
                "thermal_state": metrics.thermal_state
            }
        }
        
        return APIResponse(
            success=True,
            data=health_data,
            message=f"System health: {health_status} (score: {max(0, health_score)})"
        )
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))