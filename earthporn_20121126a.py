#!/usr/bin/env python3
import json
import os
import random
import shutil
import string
from typing import Dict, List

import requests
from PIL import Image, UnidentifiedImageError

LETTERS = string.digits + string.ascii_letters


def is_image(url: str) -> bool:
    try:
        i = Image.open(requests.get(url, stream=True).raw)
        return True
    except UnidentifiedImageError:
        return False


def get_image_format(url: str) -> str:
    i = Image.open(requests.get(url, stream=True).raw)
    return str(i.format)


def image_urls(json_text: str) -> List[str]:
    res = []
    d = json.loads(json_text)
    map_data = map_load()
    for item in d["data"]["children"]:
        volt = False
        url = item["data"]["url"]
        for val in map_data:
            if val["url"] == url:
                volt = True
                break
        if not volt and is_image(url):
            res.append(url)
    return res


def url_get(url: str) -> str:
    r = requests.get(url)
    res = r.text
    if res == '{"message": "Too Many Requests", "error": 429}':
        return url_get_wget(url)
    return res


def url_get_wget(url: str) -> str:
    cmd = f"wget {url} -O reddit.json 2> /dev/null"
    # print(cmd)
    os.system(cmd)
    f = open("reddit.json", "r")
    res = f.read()
    f.close()
    return res


def get_name() -> str:
    try:
        li = os.listdir("wallpepers")
        if "map.json" in li:
            li.remove("map.json")
        max_num = 0
        for item in li:
            bont = item.split(".")
            bont = bont[0].split("wallpeper")
            szam = int(bont[1])
            if szam > max_num:
                max_num = szam
        return "wallpeper" + str((max_num + 1))
    except FileNotFoundError:
        os.system("mkdir wallpepers")
        return "wallpeper1"
    except Exception as e:
        print("Hiba név fejtés közben:", e)
        return "".join(random.choice(LETTERS) for i in range(50))


def map_save(d: List[Dict[str, str]]) -> None:
    ment = map_load() + d
    fname = "./wallpepers/map.json"
    f = open(fname, "w")
    json.dump(ment, f)
    f.close()


def map_load() -> List[Dict[str, str]]:
    fname = "./wallpepers/map.json"
    try:
        f = open(fname)
        json_text = f.read()
        f.close()
        return json.loads(json_text)
    except FileNotFoundError:
        return []


def image_download(urls: List[str]) -> None:
    siker_urls = []
    for url in urls:
        try:
            name = get_name()
            formatum = get_image_format(url)
            res = requests.get(url, stream=True)
            file_name = name + "." + formatum
            if res.status_code == 200:
                with open("./wallpepers/" + file_name, "wb") as f:
                    shutil.copyfileobj(res.raw, f)
                print("Kép mentése befejezödőt:", file_name)
                d = {"url": url, "name": file_name}
                siker_urls.append(d)
            else:
                print("A kép nem tölthető le: ", url)
        except Exception as e:
            print("Hiba történt mentés közben:", e)
    map_save(siker_urls)
    print("-" * 20)
    print(
        "Az összes kép letöltése befejeződőtt. Letöltöt képek száma:",
        str(len(urls)) + "/" + str(len(siker_urls)),
    )


def image_download_wget(urls: List[str]) -> None:
    siker_urls = []
    for url in urls:
        try:
            name = get_name()
            formatum = get_image_format(url)
            cmd = f"wget {url} -O ./wallpepers/{name}.{formatum} 2> /dev/null"
            # print(cmd)
            os.system(cmd)
            print("Kép mentése befejezödőt:", name)
            d = {"url": url, "name": name + "." + formatum}
            siker_urls.append(d)
        except Exception as e:
            print("Hiba történt mentés közben:", e)
    map_save(siker_urls)
    print("-" * 20)
    print(
        "Az összes kép letöltése befejeződőtt. Letöltöt képek száma:",
        str(len(urls)) + "/" + str(len(siker_urls)),
    )


def main() -> None:
    reddit_url = "https://www.reddit.com/r/earthporn/.json"
    image_download(image_urls(url_get(reddit_url)))


if __name__ == "__main__":
    main()
