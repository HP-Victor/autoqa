import subprocess
import os
import time
import shlex
from agents import Computer


def docker_exec(cmd: str, container_name: str, decode=True) -> str:
    safe_cmd = cmd.replace('"', '"')
    docker_cmd = f'docker compose exec {container_name} sh -c "{safe_cmd}"'
    output = subprocess.check_output(docker_cmd, shell=True)
    if decode:
        return output.decode("utf-8", errors="ignore")
    return output


class DockerComputer(Computer):
    def __init__(
        self,
        display=":99",
        container_name="computer",
        port_mapping="5900:5900",
    ):
        self.name = "computer"
        self.display = display
        self.container_name = container_name
        self.port_mapping = port_mapping

    def __enter__(self):
        print("Entering DockerComputer context")
        result = subprocess.run(
            ["docker", "compose", "ps", "-q", "-f", f"name={self.container_name}"],
            capture_output=True,
            text=True,
        )

        if not result.stdout.strip():
            raise RuntimeError(
                f"Container {self.container_name} is not running. Start it with Docker Compose."
            )

        try:
            geometry = docker_exec(
                f"DISPLAY={self.display} xdotool getdisplaygeometry",
                self.container_name,
            ).strip()
            if geometry:
                w, h = geometry.split()
                self._dimensions = (int(w), int(h))
        except:
            pass

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting DockerComputer context")
        pass

    @property
    def environment(self) -> str:
        return "linux"

    @property
    def dimensions(self) -> tuple[int, int]:
        if hasattr(self, "_dimensions"):
            return self._dimensions

        output = docker_exec(
            f"xdpyinfo -display {self.display} | grep dimensions", self.container_name
        )
        dimensions = (
            output.split("dimensions:")[1].split("pixels")[0].strip().split("x")
        )
        self._dimensions = (int(dimensions[0]), int(dimensions[1]))
        return self._dimensions

    def screenshot(self) -> str:
        print("📸 Taking screenshot")
        docker_exec(
            f"DISPLAY={self.display} import -window root /tmp/screenshot.png",
            self.container_name,
        )

        timestamp = int(time.time())
        local_path = f"screenshot_{timestamp}.png"
        subprocess.run(
            f"docker compose cp {self.container_name}:/tmp/screenshot.png {local_path}",
            shell=True,
            check=True,
        )
        print(f"Screenshot saved to {os.path.abspath(local_path)}")

        base64_output = docker_exec(
            "base64 -w 0 /tmp/screenshot.png", self.container_name
        )
        return base64_output

    def click(self, x: int, y: int, button: str = "left") -> None:
        print(f"🖱️ Clicking: x={x}, y={y}, button={button}")
        button_map = {"left": 1, "middle": 2, "right": 3, "back": 8, "forward": 9}
        button_num = button_map.get(button, 1)
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click {button_num}",
            self.container_name,
        )

    def double_click(self, x: int, y: int) -> None:
        print(f"🖱️ Double-clicking: x={x}, y={y}")
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click --repeat 2 1",
            self.container_name,
        )

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        print(f"🖱️ Scrolling: position=({x}, {y}), scroll=({scroll_x}, {scroll_y})")
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
        )

        if scroll_y != 0:
            button = 4 if scroll_y > 0 else 5
            repeat = abs(scroll_y) // 10
            if repeat < 1:
                repeat = 1
            docker_exec(
                f"DISPLAY={self.display} xdotool click --repeat {repeat} {button}",
                self.container_name,
            )

        if scroll_x != 0:
            button = 6 if scroll_x > 0 else 7
            repeat = abs(scroll_x) // 10
            if repeat < 1:
                repeat = 1
            docker_exec(
                f"DISPLAY={self.display} xdotool click --repeat {repeat} {button}",
                self.container_name,
            )

    def type(self, text: str) -> None:
        print(f"⌨️ Typing: '{text}'")
        safe_text = text.replace("'", "'\\''")
        cmd = f"DISPLAY={self.display} xdotool type -- '{safe_text}'"
        docker_exec(cmd, self.container_name)

    def wait(self, ms: int = 1000) -> None:
        print(f"⏱️ Waiting: {ms}ms")
        docker_exec(f"sleep {ms/1000}", self.container_name)

    def move(self, x: int, y: int) -> None:
        print(f"🖱️ Moving to: x={x}, y={y}")
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
        )

    def keypress(self, keys: list[str]) -> None:
        mapping = {
            "ENTER": "Return",
            "LEFT": "Left",
            "RIGHT": "Right",
            "UP": "Up",
            "DOWN": "Down",
            "ESC": "Escape",
            "SPACE": "space",
            "BACKSPACE": "BackSpace",
            "TAB": "Tab",
        }
        mapped_keys = [mapping.get(key, key) for key in keys]
        combo = "+".join(mapped_keys)
        docker_exec(f"DISPLAY={self.display} xdotool key {combo}", self.container_name)

    def drag(self, path: list[tuple[int, int]]) -> None:
        if not path or len(path) < 2:
            return

        print(
            f"🖱️ Dragging: from ({path[0][0]}, {path[0][1]}) to ({path[-1][0]}, {path[-1][1]})"
        )
        start_x, start_y = path[0]
        docker_exec(
            f"DISPLAY={self.display} xdotool mousemove {start_x} {start_y}",
            self.container_name,
        )

        docker_exec(f"DISPLAY={self.display} xdotool mousedown 1", self.container_name)

        for x, y in path[1:]:
            docker_exec(
                f"DISPLAY={self.display} xdotool mousemove {x} {y}", self.container_name
            )
            docker_exec("sleep 0.01", self.container_name)

        docker_exec(f"DISPLAY={self.display} xdotool mouseup 1", self.container_name)

    def get_current_url(self):
        return None


computer = DockerComputer(display=":99", container_name="computer")
