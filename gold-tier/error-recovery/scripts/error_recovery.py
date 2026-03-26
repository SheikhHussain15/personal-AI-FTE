#!/usr/bin/env python3
"""
Error Recovery Module

Provides retry logic, circuit breaker, and graceful degradation.
"""

import logging
import random
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Transient error that may succeed on retry."""
    pass


class CircuitBreakerError(Exception):
    """Circuit breaker is open."""
    pass


class RetryHandler:
    """Handle retries with exponential backoff."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (TransientError,),
    ):
        """
        Initialize retry handler.
        
        Args:
            max_attempts: Maximum retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            jitter: Add random jitter to delay
            exceptions: Exception types to retry
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exceptions = exceptions
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for attempt."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        
        if self.jitter:
            # Add up to 25% jitter
            delay = delay * (0.75 + random.random() * 0.25)
        
        return delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retries.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all attempts fail
        """
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f'Attempt {attempt + 1}/{self.max_attempts} failed: {e}. '
                        f'Retrying in {delay:.1f}s...'
                    )
                    time.sleep(delay)
                else:
                    logger.error(f'All {self.max_attempts} attempts failed')
            except Exception as e:
                # Non-retryable exception
                logger.error(f'Non-retryable error: {e}')
                raise
        
        if last_exception:
            raise last_exception


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (TransientError,),
) -> Callable:
    """
    Decorator for retry logic.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter
        exceptions: Exception types to retry
        
    Returns:
        Decorated function
    """
    handler = RetryHandler(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        jitter=jitter,
        exceptions=exceptions,
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute(func, *args, **kwargs)
        return wrapper
    
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failing, stop trying
    - HALF_OPEN: Testing if recovered
    """
    
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 300,
        half_open_attempts: int = 1,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening
            recovery_timeout: Seconds before trying again
            half_open_attempts: Successful attempts to close
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_attempts = half_open_attempts
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == self.CLOSED:
            return True
        
        if self.state == self.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = datetime.now() - self.last_failure_time
                if elapsed.total_seconds() >= self.recovery_timeout:
                    logger.info('Circuit breaker moving to HALF_OPEN')
                    self.state = self.HALF_OPEN
                    self.success_count = 0
                    return True
            return False
        
        if self.state == self.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record successful execution."""
        if self.state == self.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.half_open_attempts:
                logger.info('Circuit breaker moving to CLOSED')
                self.state = self.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = datetime.now()
        else:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == self.HALF_OPEN:
            logger.warning('Circuit breaker moving to OPEN (failure in half-open)')
            self.state = self.OPEN
            self.last_state_change = datetime.now()
        elif self.failure_count >= self.failure_threshold:
            logger.warning(f'Circuit breaker moving to OPEN ({self.failure_count} failures)')
            self.state = self.OPEN
            self.last_state_change = datetime.now()
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_state_change': self.last_state_change.isoformat(),
        }


class DegradationMode:
    """Track and manage graceful degradation."""
    
    def __init__(self):
        """Initialize degradation tracker."""
        self.degraded_services: Dict[str, datetime] = {}
        self.auto_recovery = True
        self.recovery_check_interval = 60  # seconds
    
    def set_degraded(self, service: str):
        """Mark service as degraded."""
        self.degraded_services[service] = datetime.now()
        logger.warning(f'Service {service} marked as degraded')
    
    def is_degraded(self, service: str) -> bool:
        """Check if service is degraded."""
        return service in self.degraded_services
    
    def recover(self, service: str):
        """Mark service as recovered."""
        if service in self.degraded_services:
            del self.degraded_services[service]
            logger.info(f'Service {service} recovered')
    
    def get_degraded_services(self) -> list:
        """Get list of degraded services."""
        return list(self.degraded_services.keys())
    
    def execute_with_fallback(
        self,
        primary: Callable,
        fallback: Callable,
        service: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute primary with fallback.
        
        Args:
            primary: Primary function
            fallback: Fallback function
            service: Service name
            *args: Arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from primary or fallback
        """
        if self.is_degraded(service):
            logger.info(f'Service {service} degraded, using fallback')
            return fallback(*args, **kwargs)
        
        try:
            result = primary(*args, **kwargs)
            # Recover if previously degraded
            self.recover(service)
            return result
        except Exception as e:
            logger.error(f'Primary failed for {service}: {e}')
            self.set_degraded(service)
            return fallback(*args, **kwargs)


# Global instances for common use cases

_api_retry = RetryHandler(
    max_attempts=3,
    base_delay=1,
    max_delay=30,
    exceptions=(TransientError, ConnectionError, TimeoutError),
)

_api_circuit_breaker: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service: str) -> CircuitBreaker:
    """Get or create circuit breaker for service."""
    if service not in _api_circuit_breaker:
        _api_circuit_breaker[service] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300,
        )
    return _api_circuit_breaker[service]


def execute_with_recovery(
    service: str,
    func: Callable,
    *args,
    **kwargs,
) -> Any:
    """
    Execute function with retry and circuit breaker.
    
    Args:
        service: Service name
        func: Function to execute
        *args: Arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result
        
    Raises:
        CircuitBreakerError if circuit is open
        Last exception if all retries fail
    """
    breaker = get_circuit_breaker(service)
    
    if not breaker.can_execute():
        raise CircuitBreakerError(f'Circuit breaker open for {service}')
    
    try:
        result = _api_retry.execute(func, *args, **kwargs)
        breaker.record_success()
        return result
    except Exception as e:
        breaker.record_failure()
        raise


# Test/demo

if __name__ == '__main__':
    print('Error Recovery Module Test')
    print('=' * 50)
    
    # Test retry
    attempt = 0
    
    @with_retry(max_attempts=3, base_delay=0.1)
    def flaky_function():
        global attempt
        attempt += 1
        if attempt < 3:
            raise TransientError(f'Transient error (attempt {attempt})')
        return 'Success!'
    
    print('\nTesting retry with flaky function...')
    try:
        result = flaky_function()
        print(f'Result: {result}')
    except Exception as e:
        print(f'Failed: {e}')
    
    # Test circuit breaker
    print('\nTesting circuit breaker...')
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    for i in range(5):
        if breaker.can_execute():
            print(f'  Execution {i+1}: allowed')
            breaker.record_failure()
        else:
            print(f'  Execution {i+1}: blocked (circuit open)')
            time.sleep(0.1)
    
    print(f'\nCircuit state: {breaker.get_state()}')
    
    print('\n✅ Error Recovery module test complete')
