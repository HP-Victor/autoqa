import subprocess
import os
import time
from agents import Computer


def docker_exec(cmd: str, container_name: str, decode=True) -> str:
    safe_cmd = cmd.replace('"', '"')
    docker_cmd = f'docker compose exec {container_name} sh -c "{safe_cmd}"'
    output = subprocess.check_output(docker_cmd, shell=True)
    if decode:
        return output.decode("utf-8", errors="ignore")
    return output


class VM(Computer):
    def __init__(self, display, container_name):
        self.name = "computer"
        self.display = display
        self.container_name = container_name

    @property
    def environment(self) -> str:
        return "linux"

    @property
    def dimensions(self) -> tuple[int, int]:
        output = docker_exec(
            f"xdpyinfo -display {self.display} | grep dimensions", self.container_name
        )
        dimensions = (
            output.split("dimensions:")[1].split("pixels")[0].strip().split("x")
        )
        return (int(dimensions[0]), int(dimensions[1]))

    def screenshot(self) -> str:
        # Take screenshot using imagemagick and convert to base64
        docker_exec(
            f"DISPLAY={self.display} import -window root /tmp/screenshot.png",
            self.container_name,
        )

        # Save screenshot to local directory with timestamp
        timestamp = int(time.time())
        local_path = f"screenshot_{timestamp}.png"
        subprocess.run(
            f"docker compose cp {self.container_name}:/tmp/screenshot.png {local_path}",
            shell=True,
            check=True,
        )
        print(f"Screenshot saved to {os.path.abspath(local_path)}")

        # Convert to base64 and return
        base64_output = docker_exec(
            "base64 -w 0 /tmp/screenshot.png", self.container_name
        )
        return base64_output

    def click(self, x: int, y: int, button: str = "left") -> None:
        button_map = {"left": 1, "right": 3, "wheel": 2, "back": 8, "forward": 9}
        button_num = button_map.get(button, 1)
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click {button_num}",
            self.container_name,
        )

    def double_click(self, x: int, y: int) -> None:
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click --repeat 2 1",
            self.container_name,
        )

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        # Move to position first
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
        )

        # Handle vertical scrolling
        if scroll_y != 0:
            button = 4 if scroll_y > 0 else 5  # 4 is scroll up, 5 is scroll down
            repeat = abs(scroll_y) // 10  # Convert pixels to scroll events
            if repeat < 1:
                repeat = 1
            docker_exec(
                f"DISPLAY={self.display} xdotool click --repeat {repeat} {button}",
                self.container_name,
            )

        # Handle horizontal scrolling
        if scroll_x != 0:
            button = 6 if scroll_x > 0 else 7  # 6 is scroll right, 7 is scroll left
            repeat = abs(scroll_x) // 10  # Convert pixels to scroll events
            if repeat < 1:
                repeat = 1
            docker_exec(
                f"DISPLAY={self.display} xdotool click --repeat {repeat} {button}",
                self.container_name,
            )

    def type(self, text: str) -> None:
        # Escape special characters for shell
        escaped_text = text.replace('"', '\\"')
        docker_exec(
            f'DISPLAY={self.display} xdotool type "{escaped_text}"', self.container_name
        )

    def wait(self, ms: int = 1000) -> None:
        docker_exec(f"sleep {ms/1000}", self.container_name)

    def move(self, x: int, y: int) -> None:
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
        )

    def keypress(self, keys: list[str]) -> None:
        key_sequence = " ".join(keys)
        docker_exec(
            f"DISPLAY={self.display} xdotool key {key_sequence}", self.container_name
        )

    def drag(self, path: list[tuple[int, int]]) -> None:
        if not path or len(path) < 2:
            return

        # Move to the starting position
        start_x, start_y = path[0]
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {start_x} {start_y}",
            self.container_name,
        )

        # Start the drag operation
        docker_exec(f"DISPLAY={self.display} xdotool mousedown 1", self.container_name)

        # Move through each point in the path
        for x, y in path[1:]:
            docker_exec(
                f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
            )
            # Small delay to make the drag smoother
            docker_exec("sleep 0.01", self.container_name)

        # Release the mouse button at the final position
        docker_exec(f"DISPLAY={self.display} xdotool mouseup 1", self.container_name)


vm = VM(display=":99", container_name="computer")
