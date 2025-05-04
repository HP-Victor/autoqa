import asyncio
import base64
import io
import time
import os
from PIL import Image
import asyncvnc
from agents import AsyncComputer


class VNCComputer(AsyncComputer):
    def __init__(
        self,
        host="localhost",
        port=5901,
        username=None,
        password=None,
    ):
        self.name = "vnc_computer"
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._dimensions = None
        self._connection_lock = asyncio.Lock()
        self._connection_manager = None

    @property
    def environment(self) -> str:
        return "linux"

    @property
    def dimensions(self) -> tuple[int, int]:
        if (
            self._connection_manager
            and self._connection_manager.client
            and self._connection_manager.client.video
        ):
            return (
                self._connection_manager.client.video.width,
                self._connection_manager.client.video.height,
            )
        return (1024, 768)  # Default fallback dimensions

    async def _get_connection_manager(self):
        """Get or create the connection manager"""
        async with self._connection_lock:
            if self._connection_manager is None:
                self._connection_manager = _VNCConnectionManager(
                    self.host, self.port, self.username, self.password
                )

            # Start the connection if not started
            if not self._connection_manager.is_started:
                await self._connection_manager.start()

            return self._connection_manager

    async def screenshot(self) -> str:
        print("📸 Taking screenshot")
        connection = await self._get_connection_manager()

        # Get screenshot as numpy array
        pixels = await connection.screenshot()

        # Convert to PIL Image
        image = Image.fromarray(pixels)

        # Save the image to a file
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        image.save(filename)
        print(f"Screenshot saved to {os.path.abspath(filename)}")

        # Convert to base64 (return only raw base64 string without prefix)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Return raw base64 string (matching Docker implementation)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def click(self, x: int, y: int, button: str = "left") -> None:
        print(f"🖱️ Clicking: x={x}, y={y}, button={button}")
        connection = await self._get_connection_manager()
        await connection.click(x, y, button)

    async def double_click(self, x: int, y: int) -> None:
        print(f"🖱️ Double-clicking: x={x}, y={y}")
        connection = await self._get_connection_manager()
        await connection.double_click(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        print(f"🖱️ Scrolling: position=({x}, {y}), scroll=({scroll_x}, {scroll_y})")
        connection = await self._get_connection_manager()
        await connection.scroll(x, y, scroll_x, scroll_y)

    async def type(self, text: str) -> None:
        print(f"⌨️ Typing: '{text}'")
        connection = await self._get_connection_manager()
        await connection.type(text)

    async def wait(self, ms: int = 1000) -> None:
        print(f"⏱️ Waiting: {ms}ms")
        await asyncio.sleep(ms / 1000)

    async def move(self, x: int, y: int) -> None:
        print(f"🖱️ Moving to: x={x}, y={y}")
        connection = await self._get_connection_manager()
        await connection.move(x, y)

    async def keypress(self, keys: list[str]) -> None:
        print(f"⌨️ Pressing keys: {keys}")
        connection = await self._get_connection_manager()

        key_mapping = {
            "CTRL": "Ctrl",
            "ALT": "Alt",
            "SHIFT": "Shift",
            "ENTER": "Return",
            "ESC": "Escape",
            "BACKSPACE": "BackSpace",
            "TAB": "Tab",
            "SPACE": "space",
            "LEFT": "Left",
            "RIGHT": "Right",
            "UP": "Up",
            "DOWN": "Down",
        }

        # Translate keys to VNC format
        mapped_keys = []
        for k in keys:
            mapped_key = key_mapping.get(k, k)
            if (
                len(keys) > 1
                and len(mapped_key) == 1
                and mapped_key.isalpha()
                and mapped_key.isupper()
            ):
                mapped_key = mapped_key.lower()
            mapped_keys.append(mapped_key)
        print(f"  Mapped to VNC keys: {mapped_keys}")

        await connection.keypress(mapped_keys)

    def _get_available_vnc_keys(self):
        """Get a sample of available VNC keys (for debugging)"""
        try:
            import asyncvnc

            # Try to access the key_codes dictionary if it exists
            if hasattr(asyncvnc, "key_codes"):
                # Return just a sample of keys to avoid overwhelming logs
                return list(asyncvnc.key_codes.keys())[:20]
            return ["Key information not available"]
        except:
            return ["Unable to determine available keys"]

    async def drag(self, path: list[tuple[int, int]]) -> None:
        if not path or len(path) < 2:
            return

        print(
            f"🖱️ Dragging: from ({path[0][0]}, {path[0][1]}) to ({path[-1][0]}, {path[-1][1]})"
        )
        connection = await self._get_connection_manager()
        await connection.drag(path)

    async def get_current_url(self):
        return None


class _VNCConnectionManager:
    """Internal class to manage VNC connections"""

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.task = None
        self.is_started = False
        self._closed = False
        self._event_loop = None

    async def start(self):
        """Start the connection manager"""
        if self.is_started:
            return

        print(f"Starting VNC connection to {self.host}:{self.port}")
        self._event_loop = asyncio.get_running_loop()
        self.task = self._event_loop.create_task(self._connection_task())
        self.is_started = True

        # Wait for connection to be established
        timeout = 10
        start_time = time.time()
        while not self.client and time.time() - start_time < timeout:
            await asyncio.sleep(0.1)

        if not self.client:
            raise RuntimeError(
                f"Failed to connect to VNC server within {timeout} seconds"
            )

    async def _connection_task(self):
        """Task that maintains the VNC connection"""
        while not self._closed:
            try:
                print(f"Connecting to VNC server at {self.host}:{self.port}")
                # Try to connect with only standard encodings enabled
                async with asyncvnc.connect(
                    self.host, self.port, username=self.username, password=self.password
                ) as client:
                    self.client = client
                    print("Connected to VNC server")

                    # Keep connection alive until closed
                    while not self._closed:
                        await asyncio.sleep(1)

            except ValueError as e:
                # Handle encoding errors
                print(f"VNC encoding error: {e}")
                print(
                    "The VNC server is using an encoding that asyncvnc doesn't support."
                )
                print(
                    "You might need to configure your VNC server to use more standard encodings."
                )
                self.client = None

                if not self._closed:
                    # Longer wait for encoding errors before retry
                    await asyncio.sleep(5)

            except Exception as e:
                print(f"VNC connection error: {e}")
                self.client = None

                if not self._closed:
                    # Wait before reconnecting
                    await asyncio.sleep(2)

        print("VNC connection task finished")

    async def close(self):
        """Close the connection manager"""
        self._closed = True
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        self.client = None
        self.is_started = False

    async def screenshot(self):
        """Take a screenshot"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        try:
            return await self.client.screenshot()
        except ValueError as e:
            if str(e).isdigit():
                print(f"Unsupported VNC encoding: {e}")
                print("Try configuring your VNC server to use basic encodings only.")
                # Return a placeholder image to prevent crashes
                return self._create_placeholder_image()
            raise

    def _create_placeholder_image(self):
        """Create a placeholder image when screenshot fails"""
        # Create a small image with text that explains the error
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np

        # Create a 640x480 image with a message
        img = Image.new("RGB", (640, 480), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "VNC Error: Unsupported encoding", fill=(255, 255, 255))
        d.text((10, 30), "Please check VNC server configuration", fill=(255, 255, 255))

        # Convert to numpy array
        return np.array(img)

    async def click(self, x, y, button="left"):
        """Click at position"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.mouse.move(x, y)
        if button == "right":
            self.client.mouse.right_click()
        elif button == "middle":
            self.client.mouse.middle_click()
        else:
            self.client.mouse.click()

        await self.client.drain()

    async def double_click(self, x, y):
        """Double click at position"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.mouse.move(x, y)
        self.client.mouse.click()
        await asyncio.sleep(0.1)
        self.client.mouse.click()
        await self.client.drain()

    async def scroll(self, x, y, scroll_x, scroll_y):
        """Scroll at position"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.mouse.move(x, y)

        if scroll_y != 0:
            scroll_amount = abs(scroll_y) // 10
            if scroll_amount < 1:
                scroll_amount = 1

            for _ in range(scroll_amount):
                if scroll_y > 0:
                    self.client.mouse.scroll_up()
                else:
                    self.client.mouse.scroll_down()

        await self.client.drain()

    async def type(self, text):
        """Type text"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.keyboard.write(text)
        await self.client.drain()

    async def move(self, x, y):
        """Move mouse to position"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.mouse.move(x, y)
        await self.client.drain()

    async def drag(self, path):
        """Drag along path"""
        if not self.client or not path or len(path) < 2:
            return

        start_x, start_y = path[0]
        self.client.mouse.move(start_x, start_y)

        with self.client.mouse.hold():
            for x, y in path[1:]:
                self.client.mouse.move(x, y)
                await asyncio.sleep(0.01)

        await self.client.drain()

    async def keypress(self, keys):
        """Press keys"""
        if not self.client:
            raise RuntimeError("VNC client not connected")

        self.client.keyboard.press(*keys)
        await self.client.drain()
