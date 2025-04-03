import asyncio
import logging
import shlex
from typing import List, Dict, Optional, Any, NamedTuple

logger = logging.getLogger(__name__)


class CommandResult(NamedTuple):
    """Result of running a shell command"""
    returncode: int
    stdout: str
    stderr: str


async def run_command(cmd: str, timeout: int = 30) -> CommandResult:
    """
    Run a shell command asynchronously
    
    Args:
        cmd: Command to run
        timeout: Maximum execution time in seconds
    
    Returns:
        CommandResult with return code, stdout, and stderr
    
    Raises:
        asyncio.TimeoutError: If command execution exceeds timeout
        OSError: If command execution fails
    """
    logger.debug(f"Running command: {cmd}")
    
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for command to complete with timeout
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        # Kill process if it times out
        process.kill()
        logger.error(f"Command timed out after {timeout}s: {cmd}")
        raise
    
    # Decode output
    stdout = stdout_bytes.decode("utf-8").strip() if stdout_bytes else ""
    stderr = stderr_bytes.decode("utf-8").strip() if stderr_bytes else ""
    
    # Log command results
    if process.returncode != 0:
        logger.warning(
            f"Command exited with code {process.returncode}: {cmd}\n"
            f"STDERR: {stderr}"
        )
    else:
        logger.debug(f"Command completed successfully: {cmd}")
    
    return CommandResult(
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr
    )


def validate_path_safety(path: str) -> bool:
    """
    Validate that a path is safe to use in shell commands
    
    Args:
        path: Path to validate
    
    Returns:
        True if path is safe, False otherwise
    """
    # Check for shell metacharacters and other dangerous patterns
    dangerous_chars = ['&', ';', '|', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']', '!', '*', '?', '~', '\n', '\r']
    return not any(char in path for char in dangerous_chars)


def safe_path(path: str) -> str:
    """
    Make a path safe for use in shell commands by escaping it
    
    Args:
        path: Path to make safe
    
    Returns:
        Escaped path safe for shell commands
    """
    return shlex.quote(path)