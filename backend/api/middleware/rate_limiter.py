"""
Per-IP Rate Limiter for ETo Calculations.

Limita o número de cálculos por IP por dia usando Redis.
Protege contra abuso e uso excessivo das APIs externas.

Limits:
- Dashboard modes (current/forecast): 30/day per IP
- Historical mode (email): 10/day per IP
- Global: 50/day per IP across all modes
"""

from datetime import datetime
from typing import Optional

from loguru import logger
from redis import Redis

from config.settings.app_config import get_settings

settings = get_settings()

# Per-IP daily limits
CALC_LIMITS = {
    "dashboard_current": 30,   # Dashboard: 30 cálculos/dia por IP
    "dashboard_forecast": 30,  # Dashboard: 30 cálculos/dia por IP
    "historical_email": 10,    # Histórico (email): 10/dia por IP
    "global": 50,              # Total geral: 50/dia por IP
}


def _get_redis() -> Redis:
    """Get Redis connection."""
    return Redis.from_url(settings.redis.redis_url, decode_responses=True)


def _get_key(ip: str, mode: str) -> str:
    """Build Redis key for rate limiting."""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"calc_limit:{ip}:{mode}:{today}"


def check_calculation_limit(
    client_ip: str,
    mode: str = "dashboard_current",
) -> tuple[bool, Optional[str]]:
    """
    Check if IP has remaining calculation quota.

    Args:
        client_ip: IP address of the client
        mode: Operation mode (dashboard_current, dashboard_forecast, historical_email)

    Returns:
        (allowed, error_message) - True if allowed, False with message if blocked
    """
    try:
        redis = _get_redis()

        # 1. Check mode-specific limit
        mode_key = _get_key(client_ip, mode)
        mode_usage_raw = redis.get(mode_key)
        mode_usage = int(mode_usage_raw) if mode_usage_raw else 0
        mode_limit = CALC_LIMITS.get(mode, 30)

        if mode_usage >= mode_limit:
            logger.warning(
                f"🚫 Rate limit exceeded: IP={client_ip} mode={mode} "
                f"usage={mode_usage}/{mode_limit}"
            )
            return False, (
                f"Daily limit reached for this mode ({mode_limit} calculations/day). "
                f"Try again tomorrow."
            )

        # 2. Check global limit
        global_key = _get_key(client_ip, "global")
        global_usage_raw = redis.get(global_key)
        global_usage = int(global_usage_raw) if global_usage_raw else 0
        global_limit = CALC_LIMITS["global"]

        if global_usage >= global_limit:
            logger.warning(
                f"🚫 Global rate limit exceeded: IP={client_ip} "
                f"usage={global_usage}/{global_limit}"
            )
            return False, (
                f"Daily calculation limit reached ({global_limit}/day). "
                f"Try again tomorrow."
            )

        return True, None

    except Exception as e:
        # If Redis fails, allow the request (fail open)
        logger.error(f"Rate limiter error: {e}")
        return True, None


def track_calculation(client_ip: str, mode: str = "dashboard_current") -> int:
    """
    Increment calculation counter for IP.

    Call this AFTER successfully dispatching the Celery task.

    Args:
        client_ip: IP address of the client
        mode: Operation mode

    Returns:
        Current global usage count for this IP today
    """
    try:
        redis = _get_redis()
        ttl = 86400 * 2  # 48h TTL

        # Increment mode-specific counter
        mode_key = _get_key(client_ip, mode)
        redis.incr(mode_key)
        redis.expire(mode_key, ttl)

        # Increment global counter
        global_key = _get_key(client_ip, "global")
        global_usage = int(redis.incr(global_key))
        redis.expire(global_key, ttl)

        logger.info(
            f"📊 Calc tracked: IP={client_ip} mode={mode} "
            f"global_usage={global_usage}/{CALC_LIMITS['global']}"
        )

        return global_usage

    except Exception as e:
        logger.error(f"Track calculation error: {e}")
        return 0


def get_remaining_calculations(
    client_ip: str,
    mode: str = "dashboard_current",
) -> dict:
    """
    Get remaining calculation quota for an IP.

    Returns:
        Dict with remaining quotas
    """
    try:
        redis = _get_redis()

        mode_key = _get_key(client_ip, mode)
        mode_usage_raw = redis.get(mode_key)
        mode_usage = int(mode_usage_raw) if mode_usage_raw else 0
        mode_limit = CALC_LIMITS.get(mode, 30)

        global_key = _get_key(client_ip, "global")
        global_usage_raw = redis.get(global_key)
        global_usage = int(global_usage_raw) if global_usage_raw else 0

        return {
            "mode": mode,
            "mode_used": mode_usage,
            "mode_limit": mode_limit,
            "mode_remaining": max(0, mode_limit - mode_usage),
            "global_used": global_usage,
            "global_limit": CALC_LIMITS["global"],
            "global_remaining": max(0, CALC_LIMITS["global"] - global_usage),
        }

    except Exception as e:
        logger.error(f"Get remaining error: {e}")
        return {
            "mode": mode,
            "mode_remaining": -1,
            "global_remaining": -1,
        }
