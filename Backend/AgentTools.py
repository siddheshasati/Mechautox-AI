import os
import asyncio
import subprocess
import webbrowser
import logging
from typing import Optional, List
from datetime import datetime

from langchain_core.tools import tool, Tool
from pydantic import BaseModel, Field
from rich import print as rprint

try:
    from pywhatkit import sendwhatmsg_instantly, search, playonyt
except ImportError:
    sendwhatmsg_instantly = None
    search = None
    playonyt = None

try:
    from AppOpener import open as app_open, close as app_close
except ImportError:
    app_open = None
    app_close = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppMessage(BaseModel):
    """WhatsApp message parameters"""
    phone_number: str = Field(..., description="Phone number with country code (e.g., +91XXXXXXXXXX)")
    message: str = Field(..., description="Message to send")


class WebSearchParams(BaseModel):
    """Web search parameters"""
    query: str = Field(..., description="Search query")
    max_results: int = Field(default=5, description="Maximum results to retrieve")


class ApplicationParams(BaseModel):
    """Application open/close parameters"""
    app_name: str = Field(..., description="Application name (e.g., 'notepad', 'chrome', 'vs code')")


class YouTubeParams(BaseModel):
    """YouTube play/search parameters"""
    query: str = Field(..., description="Song name or video search query")
    action: str = Field(default="play", description="'play' to play directly, 'search' to open YouTube search")


class VolumeParams(BaseModel):
    """Volume control parameters"""
    action: str = Field(..., description="'up', 'down', 'mute', 'unmute'")


class BrightnessParams(BaseModel):
    """Brightness control parameters"""
    level: int = Field(..., description="Brightness level (0-100)")


class ReminderParams(BaseModel):
    """Reminder parameters"""
    time: str = Field(..., description="Reminder time (HH:MM format)")
    message: str = Field(..., description="Reminder message")
    date: Optional[str] = Field(default=None, description="Date (YYYY-MM-DD format, defaults to today)")


@tool(args_schema=WhatsAppMessage)
def send_whatsapp_message(phone_number: str, message: str) -> str:
    """
    Send a WhatsApp message to a specified phone number.
    Requires pywhatkit and active WhatsApp Web.

    Args:
        phone_number: Recipient's phone number with country code
        message: Message content to send

    Returns:
        Status message
    """
    if not sendwhatmsg_instantly:
        return "WhatsApp tool unavailable. Install pywhatkit: pip install pywhatkit"

    try:
        logger.info(f"📱 Sending WhatsApp message to {phone_number}")
        sendwhatmsg_instantly(phone_number, message)
        return f"WhatsApp message sent to {phone_number}"
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return f"Failed to send message: {str(e)}"


@tool(args_schema=WebSearchParams)
def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform a web search and return top results.

    Args:
        query: Search query
        max_results: Number of results to retrieve
    Returns:
        Formatted search results
    """
    if not search:
        return "Web search unavailable. Install pywhatkit: pip install pywhatkit"

    try:
        logger.info(f"🔍 Searching web for: {query}")
        search(query)  # Opens in browser
        return f"Web search results opened for: {query}"
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"


@tool
def google_search(query: str) -> str:
    """
    Search Google and open results in browser.
    Args:
        query: Search query
    Returns:
        Status message
    """
    try:
        logger.info(f"🔍 Google search: {query}")
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Google search opened for: {query}"
    except Exception as e:
        logger.error(f"Google search error: {e}")
        return f"Search failed: {str(e)}"


@tool(args_schema=ApplicationParams)
def open_application(app_name: str) -> str:
    """
    Open an application by name.

    Args:
        app_name: Name of the application to open
    Returns:
        Status message
    """
    if not app_open:
        return "AppOpener unavailable. Install: pip install AppOpener"

    try:
        logger.info(f"📂 Opening application: {app_name}")
        app_open(app_name, match_closest=True, throw_error=True)
        return f"Opened {app_name}"
    except Exception as e:
        # Fallback to web search
        logger.warning(f"App not found locally, searching web for {app_name}")
        try:
            webbrowser.open(f"https://www.google.com/search?q={app_name.replace(' ', '+')}")
            return f"Opened {app_name} search in browser"
        except:
            return f"Failed to open {app_name}: {str(e)}"


@tool(args_schema=ApplicationParams)
def close_application(app_name: str) -> str:
    """
    Close an application by name.

    Args:
        app_name: Name of the application to close

    Returns:
        Status message
    """
    if not app_close:
        return "AppOpener unavailable. Install: pip install AppOpener"

    critical_apps = ["chrome", "firefox", "explorer", "system"]
    if any(critical in app_name.lower() for critical in critical_apps):
        return f"Cannot close {app_name} - system protection enabled"

    try:
        logger.info(f"Closing application: {app_name}")
        app_close(app_name, match_closest=True, throw_error=True)
        return f"Closed {app_name}"
    except Exception as e:
        logger.error(f"Close error: {e}")
        return f"Failed to close {app_name}: {str(e)}"


@tool(args_schema=YouTubeParams)
def youtube_action(query: str, action: str = "play") -> str:
    """
    Play or search a song/video on YouTube.
    Args:
        query: Song name or video search query
        action: 'play' to play directly, 'search' to open YouTube search
    Returns:
        Status message
    """
    try:
        if action.lower() == "play":
            if not playonyt:
                return "YouTube feature unavailable. Install pywhatkit: pip install pywhatkit"
            logger.info(f"🎵 Playing on YouTube: {query}")
            playonyt(query)
            return f"Playing {query} on YouTube"
        else:
            logger.info(f"🔍 Searching YouTube for: {query}")
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"YouTube search opened for: {query}"
    except Exception as e:
        logger.error(f"YouTube error: {e}")
        return f"YouTube action failed: {str(e)}"


@tool(args_schema=VolumeParams)
def control_volume(action: str) -> str:
    """
    Control system volume (requires keyboard library).

    Args:
        action: 'up', 'down', 'mute', or 'unmute'

    Returns:
        Status message
    """
    try:
        import keyboard

        actions_map = {
            "up": "volume up",
            "down": "volume down",
            "mute": "volume mute",
            "unmute": "volume mute"
        }
        if action.lower() not in actions_map:
            return f"Invalid volume action. Use: up, down, mute, unmute"

        keyboard.press_and_release(actions_map[action.lower()])
        logger.info(f"Volume {action}")
        return f"Volume {action}ed"
    except Exception as e:
        logger.error(f"Volume control error: {e}")
        return f" Volume control failed: {str(e)}"


@tool(args_schema=BrightnessParams)
def control_brightness(level: int) -> str:
    """
    Set system brightness level.
    Args:
        level: Brightness level (0-100)

    Returns:
        Status message
    """
    try:
        import screen_brightness_control as sbc

        if not 0 <= level <= 100:
            return f"Invalid brightness level. Use 0-100"

        sbc.set_brightness(level)
        logger.info(f"Brightness set to {level}%")
        return f"Brightness set to {level}%"
    except ImportError:
        return "Brightness control unavailable. Install: pip install screen-brightness-control"
    except Exception as e:
        logger.error(f"Brightness control error: {e}")
        return f"Brightness control failed: {str(e)}"


@tool
def read_pdf_file(file_path: str) -> str:
    """
    Read and extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content
    """
    try:
        from pypdf import PdfReader

        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        logger.info(f"Read PDF: {file_path} ({len(text)} chars)")
        return f"PDF content extracted ({len(reader.pages)} pages):\n{text[:500]}..."
    except Exception as e:
        logger.error(f"PDF read error: {e}")
        return f"Failed to read PDF: {str(e)}"


@tool
def list_files_in_directory(directory: str) -> str:
    """
    List files in a specified directory.

    Args:
        directory: Directory path

    Returns:
        List of files
    """
    try:
        if not os.path.exists(directory):
            return f"Directory not found: {directory}"

        files = os.listdir(directory)
        logger.info(f"Listed {len(files)} files in {directory}")
        return f"Files in {directory}:\n" + "\n".join(files[:20])
    except Exception as e:
        logger.error(f"Directory list error: {e}")
        return f"Failed to list files: {str(e)}"


def get_agent_tools() -> List[Tool]:
    """
    Get all agent tools for LangChain agent.

    Returns:
        List of Tool objects
    """
    return [
        send_whatsapp_message,
        web_search,
        google_search,
        open_application,
        close_application,
        youtube_action,
        control_volume,
        control_brightness,
        read_pdf_file,
        list_files_in_directory,
    ]


if __name__ == "__main__":
    tools = get_agent_tools()
    rprint(f"[bold green] Loaded {len(tools)} agent tools[/bold green]")
    for tool in tools:
        rprint(f"  • {tool.name}: {tool.description}")


