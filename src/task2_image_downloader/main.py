import asyncio
import concurrent.futures
import threading
from pathlib import Path
from typing import List
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class DownloadResult:
    __slots__ = ("url", "status", "message", "filename")

    def __init__(self, url: str, status: str, message: str = "", filename: str | None = None) -> None:
        self.url = url
        self.status = status
        self.message = message
        self.filename = filename or ""


async def save_image(url: str, destination: Path) -> Path:
    parsed = urlparse(url)
    name = Path(parsed.path).name or "image"
    suffix = Path(name).suffix
    stem = Path(name).stem or "image"
    filename = destination / f"{stem}{suffix}"
    counter = 1
    while filename.exists():
        filename = destination / f"{stem}_{counter}{suffix}"
        counter += 1

    def download() -> bytes:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image"):
                raise ValueError("Ссылка не ведет на изображение")
            return response.read()

    data = await asyncio.to_thread(download)
    filename.write_bytes(data)
    return filename


async def download_worker(url: str, destination: Path, results: List[DownloadResult]) -> None:
    try:
        filename = await save_image(url, destination)
    except Exception as error:  # noqa: BLE001
        results.append(DownloadResult(url, "Ошибка", str(error)))
    else:
        results.append(DownloadResult(url, "Успех", filename=str(filename)))


def ensure_directory() -> Path:
    while True:
        user_input = input().strip()
        path = Path(user_input).expanduser()
        if not user_input:
            print("Путь не может быть пустым.")
            continue
        if path.exists():
            if not path.is_dir():
                print("Указанный путь не является директорией.")
                continue
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as error:
                print(f"Не удалось создать директорию: {error}")
                continue
        test_file = path / ".permission_test"
        try:
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink(missing_ok=True)
        except OSError as error:
            print(f"Нет доступа для записи в эту директорию: {error}")
            continue
        return path


def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main() -> None:
    destination = ensure_directory()
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=start_background_loop, args=(loop,), daemon=True)
    thread.start()

    tasks: List[concurrent.futures.Future] = []
    results: List[DownloadResult] = []

    try:
        while True:
            url = input().strip()
            if not url:
                break
            future = asyncio.run_coroutine_threadsafe(
                download_worker(url, destination, results),
                loop,
            )
            tasks.append(future)
        if any(not future.done() for future in tasks):
            print("Ожидание завершения загрузок...")
        for future in tasks:
            try:
                future.result()
            except Exception:  # noqa: BLE001
                pass
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join()

    print_summary(results)


def print_summary(results: List[DownloadResult]) -> None:
    headers = ("Ссылка", "Статус")
    rows: List[List[str]] = []
    for result in results:
        status = result.status
        if result.status == "Успех" and result.filename:
            status = f"{status} ({result.filename})"
        elif result.status == "Ошибка" and result.message:
            status = f"{status}: {result.message}"
        rows.append([result.url, status])

    column_widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            column_widths[index] = max(column_widths[index], len(cell))

    horizontal = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"
    header_line = "|" + "|".join(
        f" {headers[index].ljust(column_widths[index])} " for index in range(len(headers))
    ) + "|"
    row_lines = [
        "|" + "|".join(
            f" {row[index].ljust(column_widths[index])} " for index in range(len(row))
        ) + "|"
        for row in rows
    ]

    print("Сводка об успешных и неуспешных загрузках")
    print(horizontal)
    print(header_line)
    print(horizontal)
    for line in row_lines:
        print(line)
    print(horizontal)


if __name__ == "__main__":
    main()
