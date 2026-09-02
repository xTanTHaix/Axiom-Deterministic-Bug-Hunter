import functools
from typing import Any, Dict, Optional, Callable
import responses


class MockHttp:
    """Wrapper for managing Mock HTTP Requests via Responses"""

    GET = responses.GET
    POST = responses.POST
    PUT = responses.PUT
    DELETE = responses.DELETE
    PATCH = responses.PATCH

    @staticmethod
    def activate(func: Optional[Callable] = None, *, assert_all_called: bool = True):
        """Decorator supports both @mock_http.activate and @mock_http.activate(...)"""
        def decorator(f):
            return responses.activate(assert_all_requests_are_fired=assert_all_called)(f)

        if func is not None and callable(func):
            return responses.activate(func)
        return decorator

    @staticmethod
    def mock_json(
        method: str,
        url: str,
        response_data: Dict[str, Any],
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Record Mock endpoint with JSON response"""
        responses.add(
            method=method,
            url=url,
            json=response_data,
            status=status,
            content_type="application/json",
            headers=headers or {},
        )

    @staticmethod
    def get_calls():
        """Retrieve all captured API call history"""
        return responses.calls


mock_http = MockHttp