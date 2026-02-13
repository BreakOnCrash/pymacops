class MacOpsError(RuntimeError):
    """Base error for pymacops."""


class DependencyMissingError(MacOpsError):
    """Raised when an optional dependency is missing."""


class PermissionDeniedError(MacOpsError):
    """Raised when macOS permissions block an action."""
