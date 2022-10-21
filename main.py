import argparse
from pathlib import Path
from shutil import copyfile, rmtree
from threading import Thread
import logging
from normalize import normalize


parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument("--source", "-s", help="Path to trash folder for scan", required=True)
parser.add_argument("--output", "-o", help="Path to sorted folder by file extension", default="sort_dist")

args = vars(parser.parse_args())

source = args.get("source")
output = args.get("output")

FOLDERS = []


def scan_folder(path: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            FOLDERS.append(el)
            scan_folder(el)


def copy_file(path: Path) -> None:
    for el in path.iterdir():
        if el.is_file():
            ext = el.suffix.casefold()
            if ext in ['.jpg', '.png', '.jpeg', '.bmp', '.gif', 'svg']:
                new_path = output_folder / 'images' / ext[1:].upper()
            elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a']:
                new_path = output_folder / 'audio' / ext[1:].upper()
            elif ext in ['.avi', '.mpg', '.mpeg', '.mkv', '.mov', '.flv', '.wmv', '.mp4', '.webm', '.mp4']:
                new_path = output_folder / 'video' / ext[1:].upper()
            elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.rtf', '.csv']:
                new_path = output_folder / 'documents' / ext[1:].upper()
            elif ext in ['.zip', '.tag', '.gz']:
                new_path = output_folder / 'archives' / ext[1:].upper()
            else:
                new_path = output_folder / 'other'
            try:
                new_path.mkdir(parents=True, exist_ok=True)
                copyfile(el, new_path / normalize(el.name))
            except OSError as err:
                logging.error(f"Can't copy file {el.name}. Error: {err}")


def workers(path: Path):
    FOLDERS.append(path)
    scan_folder(path)

    threads = []

    for folder in FOLDERS:
        th = Thread(target=copy_file, args=(folder,))
        th.start()
        # logging.debug(f"Thread {th.name} started")
        threads.append(th)

    [th.join() for th in threads]
    # [logging.debug(f'Thread {th.name} finished!') for th in threads]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    base_folder = Path(source)
    output_folder = Path(output)
    workers(base_folder)
    print('Done!')
    print(f'Remove the source folder {source}?')
    if input('y/n: ').lower() == 'y':
        try:
            rmtree(base_folder)
            print('Source folder removed!')
        except OSError as e:
            print(f"Can't remove source folder. Error: {e}")
    else:
        print('Goodbye!')
