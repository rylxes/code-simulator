import re
from .logging_config import logger


class LanguageFormatter:
    """Base class for language-specific formatters."""

    def __init__(self, indent_size=4):
        self.indent_size = indent_size
        self.indent_level = 0
        self.indent_style = " " * indent_size

    def format_line(self, line: str) -> str:
        """Format a single line of code.

        This is a base method that should be overridden by subclasses.
        """
        line = line.strip()

        # Handle indentation
        if line.endswith("{") or line.endswith("("):
            indented_line = self.indent_style * self.indent_level + line
            self.indent_level += 1
        elif line.startswith("}") or line.startswith(")"):
            self.indent_level = max(0, self.indent_level - 1)
            indented_line = self.indent_style * self.indent_level + line
        else:
            indented_line = self.indent_style * self.indent_level + line

        return indented_line


class JavaFormatter(LanguageFormatter):
    """Formatter for Java code."""

    def format_line(self, line: str) -> str:
        """Format a single line of Java code."""
        line = super().format_line(line)  # Apply base formatting first

        # Add Java-specific formatting rules here:
        # Example: Add a space after commas in argument lists
        line = re.sub(r"(?<=\w),(?=\w)", ", ", line)

        # Example: Ensure class, method, and if/else/for blocks are indented correctly
        if line.endswith("{"):
            indented_line = self.indent_style * self.indent_level + line
            self.indent_level += 1
        elif line.startswith("}"):
            self.indent_level = max(0, self.indent_level - 1)
            indented_line = self.indent_style * self.indent_level + line
        elif (
                line.startswith("if")
                or line.startswith("else")
                or line.startswith("for")
                or line.startswith("while")
        ):
            indented_line = self.indent_style * self.indent_level + line
            self.indent_level += 1
        else:
            indented_line = self.indent_style * self.indent_level + line

        return indented_line


class PythonFormatter(LanguageFormatter):
    """Formatter for Python code."""

    def format_line(self, line: str) -> str:
        """Format a single line of Python code."""
        line = super().format_line(line)  # Apply base formatting first

        # Add Python-specific formatting rules here:
        # Example: Ensure colons are at the end of if/else/for/def lines
        if re.match(
                r"^(if|elif|else|for|while|try|except|finally|def|class)\b.*[^:]$", line
        ):
            line = line + ":"

        return line


class PHPFormatter(LanguageFormatter):
    """Formatter for PHP code."""

    def format_line(self, line: str) -> str:
        """Format a single line of PHP code."""
        line = super().format_line(line)

        # Add PHP-specific formatting rules here:
        # Example: Add spaces around operators
        line = re.sub(r"(\s*)(=|!=|==|<=|>=|<|>|\+|-|\*|\/|%|&&|\|\|)(\s*)", r" \1 ", line)

        # Example: Add spaces after commas
        line = re.sub(r"(,)(?=\S)", r"$1 ", line)

        # Example: Remove spaces before closing parenthesis
        line = re.sub(r"\s+\)", ")", line)

        # Ensure class, method, and if/else/for blocks are indented correctly
        if line.endswith("{"):
            indented_line = self.indent_style * self.indent_level + line
            self.indent_level += 1
        elif line.startswith("}"):
            self.indent_level = max(0, self.indent_level - 1)
            indented_line = self.indent_style * self.indent_level + line
        elif (
                line.startswith("if")
                or line.startswith("else")
                or line.startswith("elseif")
                or line.startswith("for")
                or line.startswith("foreach")
                or line.startswith("while")
                or line.startswith("function")
        ):
            indented_line = self.indent_style * self.indent_level + line
            self.indent_level += 1
        else:
            indented_line = self.indent_style * self.indent_level + line

        return indented_line


# Add more formatters for other languages (e.g., CppFormatter, JavaScriptFormatter, etc.)


class FormatterFactory:
    """Factory class to create formatters based on language."""

    @staticmethod
    def create_formatter(language: str, indent_size: int = 4) -> LanguageFormatter:
        """Create a formatter for the given language."""
        if language == "java":
            return JavaFormatter(indent_size)
        elif language == "python":
            return PythonFormatter(indent_size)
        elif language == "php":
            return PHPFormatter(indent_size)
        # Add cases for other languages here
        else:
            logger.warning(
                f"No specific formatter found for {language}. Using default formatter."
            )
            return LanguageFormatter(indent_size)