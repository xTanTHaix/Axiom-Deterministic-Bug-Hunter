import time
import random
import statistics
from dataclasses import dataclass
from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import requests


@dataclass
class LoadTestResult:
    total_requests: int
    failures: int
    avg_response_time: float
    p95_response_time: float
    rps: float
    success: bool


def task(weight_or_func=1):
    """Decorator to define task function"""
    if callable(weight_or_func):
        weight_or_func._is_task = True
        weight_or_func._task_weight = 1
        return weight_or_func

    def decorator(func):
        func._is_task = True
        func._task_weight = weight_or_func
        return func

    return decorator


def between(min_v: float, max_v: float) -> Callable[[], float]:
    """Generate random delay between requests"""
    return lambda: random.uniform(min_v, max_v)


class HttpClientSession:
    """Client session for sending HTTP requests with detailed Metrics"""

    def __init__(self, host: str, metrics: List[dict]):
        self.host = host.rstrip("/")
        self.metrics = metrics
        self.session = requests.Session()

    def get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.host}/{path.lstrip('/')}"
        start = time.perf_counter()
        success = True
        error_msg = ""
        try:
            resp = self.session.request(
                method, url, timeout=kwargs.pop("timeout", 5), **kwargs
            )
            success = resp.status_code < 400
            return resp
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.metrics.append(
                {
                    "duration_ms": elapsed_ms,
                    "success": success,
                    "error": error_msg,
                }
            )


class HttpUser:
    """Base User class for creating Load Scenarios"""

    wait_time = staticmethod(between(0.01, 0.05))

    def __init__(self, host: str, metrics: List[dict]):
        self.client = HttpClientSession(host, metrics)


def run_micro_load(
    user_class: type,
    host: str = "http://127.0.0.1",
    user_count: int = 5,
    spawn_rate: int = 5,
    run_time_seconds: int = 1,
) -> LoadTestResult:
    """Run Micro Load Simulation with high Concurrency without affecting GUI Loop"""
    metrics: List[dict] = []
    stop_flag = False

    tasks = []
    for attr_name in dir(user_class):
        attr = getattr(user_class, attr_name)
        if callable(attr) and getattr(attr, "_is_task", False):
            weight = getattr(attr, "_task_weight", 1)
            tasks.extend([attr] * weight)

    if not tasks:
        raise ValueError(f"No @task defined in class {user_class.__name__}")

    def worker_loop():
        user = user_class(host=host, metrics=metrics)
        while not stop_flag:
            selected_task = random.choice(tasks)
            try:
                selected_task(user)
            except Exception:
                pass

            delay = user.wait_time() if callable(user.wait_time) else 0.01
            time.sleep(delay)

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=user_count) as executor:
        for _ in range(user_count):
            executor.submit(worker_loop)
        time.sleep(run_time_seconds)
        stop_flag = True

    total_time = max(time.time() - start_time, 0.001)
    durations = [m["duration_ms"] for m in metrics]
    failures = sum(1 for m in metrics if not m["success"])
    total_reqs = len(metrics)

    avg_latency = statistics.mean(durations) if durations else 0.0
    if durations:
        sorted_durations = sorted(durations)
        p95_idx = int(len(sorted_durations) * 0.95)
        p95_latency = sorted_durations[min(p95_idx, len(sorted_durations) - 1)]
    else:
        p95_latency = 0.0

    rps = total_reqs / total_time

    return LoadTestResult(
        total_requests=total_reqs,
        failures=failures,
        avg_response_time=round(avg_latency, 2),
        p95_response_time=round(p95_latency, 2),
        rps=round(rps, 2),
        success=(failures == 0 and total_reqs > 0),
    )