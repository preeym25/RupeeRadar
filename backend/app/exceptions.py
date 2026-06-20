"""Custom exceptions for the analysis pipeline."""

from __future__ import annotations


class PipelineError(Exception):
    """Base pipeline error with HTTP status code."""

    status_code: int = 500

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class InvalidFileTypeError(PipelineError):
    status_code = 400


class ParseError(PipelineError):
    status_code = 422


class JobNotFoundError(PipelineError):
    status_code = 404
