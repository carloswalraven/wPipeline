"""Pipeline actions, one module each.

These know nothing about terminals. They take values, validate them, ask the
source of truth and return a result or raise. Whether the values came from a
command line or from a text field in a Houdini panel is not their business,
which is what keeps the rules in one place instead of scattered across UI
callbacks.
"""
