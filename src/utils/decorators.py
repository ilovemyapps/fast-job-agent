#!/usr/bin/env python3
"""
Decorator utilities for Fast Job Agent
"""

import asyncio
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def with_error_handling(
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False
) -> Callable:
    """
    Decorator for consistent error handling
    
    Args:
        default_return: Value to return on error
        log_errors: Whether to log errors
        reraise: Whether to reraise exceptions
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                if log_errors:
                    logger.error(f"Timeout in {func.__name__}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {e}")
                if reraise:
                    raise
                return default_return
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
