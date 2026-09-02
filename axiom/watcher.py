"""
File system watcher for Axiom Aegis live watch mode
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

IGNORE_DIRS = {
    ".git", ".venv", "venv", "myenv", "central_venv", "env", "__pycache__",
    ".pytest_cache", ".hypothesis", "build", "dist", ".idea", ".vscode"
}


class PollingWatcher:
    """Fallback directory watcher using timestamp polling when watchdog is not installed"""

    def __init__(self, target_dir: str = ".", callback: Optional[Callable[[], None]] = None, interval: float = 1.0):
        self.target_dir = Path(target_dir)
        self.callback = callback
        self.interval = interval
        self._running = False
        self.is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._mtimes: Dict[str, float] = {}

    def _scan_mtimes(self) -> Dict[str, float]:
        mtimes: Dict[str, float] = {}
        try:
            for path in self.target_dir.rglob("*.py"):
                parts = set(path.parts)
                if not parts.intersection(IGNORE_DIRS):
                    try:
                        mtimes[str(path)] = path.stat().st_mtime
                    except OSError:
                        pass
        except Exception:
            pass
        return mtimes

    def _loop(self):
        self._mtimes = self._scan_mtimes()
        while self._running:
            time.sleep(self.interval)
            if self.is_paused or not self._running:
                continue
            current_mtimes = self._scan_mtimes()
            if current_mtimes != self._mtimes:
                self._mtimes = current_mtimes
                if self.callback:
                    try:
                        self.callback()
                    except Exception:
                        pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None


class PythonFileChangeHandler(FileSystemEventHandler if HAS_WATCHDOG else object):
    def __init__(self, watcher_instance, debounce_seconds: float = 0.8):
        self.watcher = watcher_instance
        self.debounce_seconds = debounce_seconds
        self.last_triggered = 0.0

    def on_any_event(self, event):
        if self.watcher.is_paused or getattr(event, 'is_directory', False):
            return
        path = Path(event.src_path)
        if path.suffix == ".py":
            parts = set(path.parts)
            if not parts.intersection(IGNORE_DIRS):
                now = time.time()
                if now - self.last_triggered > self.debounce_seconds:
                    self.last_triggered = now
                    if self.watcher.callback:
                        self.watcher.callback()


class CodeWatcher:
    """Universal code watcher supporting both Watchdog and Polling fallback"""

    def __init__(self, target_dir: str = ".", callback: Optional[Callable[[], None]] = None):
        self.target_dir = target_dir
        self.callback = callback
        self.observer: Optional[Any] = None
        self._polling: Optional[PollingWatcher] = None
        self._running = False
        self.is_paused = False

    def pause(self):
        self.is_paused = True
        if self._polling:
            self._polling.is_paused = True

    def resume(self):
        time.sleep(0.3)
        self.is_paused = False
        if self._polling:
            self._polling.is_paused = False

    def start(self):
        if self._running:
            return
        if HAS_WATCHDOG:
            self.handler = PythonFileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(self.handler, self.target_dir, recursive=True)
            self.observer.daemon = True
            self.observer.start()
        else:
            self._polling = PollingWatcher(self.target_dir, self.callback)
            self._polling.start()
        self._running = True

    def stop(self):
        if not self._running:
            return
        if HAS_WATCHDOG and self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=1.0)
            except Exception:
                pass
        if self._polling:
            self._polling.stop()
        self._running = False


__all__ = ['CodeWatcher', 'PollingWatcher']
