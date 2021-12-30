import pathlib
import shutil
import re
import argparse

from mutagen.mp3 import EasyMP3 as MP3
from mutagen.flac import FLAC


def update_track_metadata(path, artist=None, album=None):
    if path.is_dir():
        label = path.stem
        try:
            artist, album, *_ = label.split(" - ", 1)
        except ValueError:
            print(f"directory {label} does not follow album format convention")

        for child in path.iterdir():
            update_track_metadata(child, artist, album)
        return

    elif path.is_file():
        if artist is not None and album is not None:
            #            print(f"working on song {path}")
            if (song := parse_track(path)) is not None:
                # if file name starts with a track number identifier
                # e.g. 03 TheThirdTrack then remove the number identifer
                if match := re.match("^\d+\s+(.*)", path.stem):
                    title = match.group(1)
                else:
                    title = path.stem

                song['title'] = title
                song['album'] = album
                song['artist'] = artist
                song.save()
                print(f"updated song {song}")
                return song
            else:
                print(f"could not parse {path}")
    else:
        print(f"found file {path} but parent directory did not provide album/artist")


def parse_track(path):
    suffix = path.suffix.lower()
    if suffix == '.mp3':
        return MP3(path)
    elif suffix == '.flac':
        return FLAC(path)
    else:
        print(f"path {path} has an invalid suffix")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-m", "--music_path", help="full path of music directory")

    # Read arguments from command line
    args = parser.parse_args()

    if args.music_path:
        mpath = pathlib.Path(args.music_path)
        backup_path = mpath.with_name(mpath.stem + "_bak").with_suffix(mpath.suffix)
        try:
            shutil.copytree(mpath, backup_path)
        except FileExistsError:
            print(f"backup path {backup_path} already exists. Can I overwrite it?")
            overwrite = input("y/N ")
            if overwrite.lower() == 'y':
                shutil.copytree(mpath, backup_path, dirs_exist_ok=True)
            else:
                print(f"Please remove or rename your existing backup directory before proceeding")
                exit(1)

        update_track_metadata(mpath)
    else:
        print("Please provide a path to the directory you want to fix up, e.g. /Users/gjlondon/Music/my_music_files")
