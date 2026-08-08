"""The interface every source of truth implements.

Three operations, exactly, for stage 1a. Sequences, shots and assets belong to
stage 1b, and schema_version exists so that growth is declared and not silent.

get_project is here even though the filesystem backend derives it from a scan.
Against a production tracker it is an indexed query and against folders it is a
sweep, and the point of an interface is to let the backend choose. Adding it
later would mean changing the interface exactly when a new backend arrives,
which is what this layer exists to avoid.
"""

import abc


class SourceOfTruth(abc.ABC):
    """What answers "what projects exist" and "make me a new one"."""

    @abc.abstractmethod
    def list_projects(self):
        """Returns a ScanResult with every project this backend can see.

        Tolerates a partial view: unreadable roots and damaged project files
        come back as warnings rather than as an exception, because a labelled
        incomplete answer is still worth having.
        """

    @abc.abstractmethod
    def get_project(self, code):
        """Returns the ProjectRecord for a code, or None if no project has it."""

    @abc.abstractmethod
    def create_project(self, code, name, root_name, houdini_version):
        """Creates a project and returns its record.

        Demands certainty: raises rather than write when the view is partial,
        when the code is taken anywhere, or when the target folder exists
        without a project file.
        """
