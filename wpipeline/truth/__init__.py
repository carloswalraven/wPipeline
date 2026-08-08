"""The source of truth layer.

What a project *contains* is answered by its project file, never by the
filesystem. Where the project files *are* is the bootstrap question, and it is
answered by scanning the declared roots: if that answer came from the source of
truth itself, it would be chicken and egg.

The layer exists so that the day a production tracker answers instead of a
folder scan, no consumer changes. That is why the scan is an operation of this
layer and not loose code somewhere.
"""

from .base import SourceOfTruth
from .record import ProjectRecord, ScanResult

__all__ = ["SourceOfTruth", "ProjectRecord", "ScanResult"]
