import io
import os
import json
import sys
from PIL import Image, ImageSequence
import numpy as np

gif_black_pixel = [4, 2, 4]
black_pixel = [0, 0, 0]
white_pixel = [255, 255, 255]
letters = "bcefghjkmpqrtvwxy2346789"

golden = {}
for filename in os.listdir("golden"):
    if not filename.endswith(".png"):
        continue
    im = Image.open(os.path.join("golden", filename))
    golden[filename] = np.asarray(im)

def captcha(img_data):
    stream = io.BytesIO(img_data)
    im = Image.open(stream)
    black_count = 0
    choose_frame = None
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        frame = frame.convert("RGB")
        arr = np.asarray(frame)
        height, width = arr.shape[0], arr.shape[1]
        cnt = np.sum(arr == gif_black_pixel)
        if cnt > black_count:
            black_count = cnt
            choose_frame = frame

    choose_frame.save("1p3a-captcha.png")
    arr = np.asarray(choose_frame)
    height, width = arr.shape[0], arr.shape[1]
    clean_arr = np.full(arr.shape, 255, dtype="uint8")
    letter_idx = 0
    result = ""
    for j in range(width):
        for i in range(height):
            if np.all(arr[i][j] == gif_black_pixel):
                if i == 0 or j == 0 or np.any(clean_arr[i - 1][j - 1] != white_pixel):
                    continue
                q, p, color = [(i - 1, j - 1)], 0, arr[i - 1][j - 1]
                up, down, left, right = i - 1, i - 1, j - 1, j - 1
                while p < len(q):
                    x, y = q[p]
                    clean_arr[x][y] = black_pixel
                    if y < left:
                        left = y
                    if y > right:
                        right = y
                    if x < up:
                        up = x
                    if x > down:
                        down = x
                    if x - 1 >= 0 and np.all(arr[x - 1][y] == color) and not (x - 1, y) in q:
                        q.append((x - 1, y))
                    if y + 1 < width and np.all(arr[x][y + 1] == color) and not (x, y + 1) in q:
                        q.append((x, y + 1))
                    if y - 1 >= 0 and np.all(arr[x][y - 1] == color) and not (x, y - 1) in q:
                        q.append((x, y - 1))
                    if x + 1 < height and np.all(arr[x + 1][y] == color) and not (x + 1, y) in q:
                        q.append((x + 1, y))
                    p += 1
                if len(q) < 5:
                    continue
                letter_idx += 1
                letter_arr = clean_arr[up: down + 1, left: right + 1]
                letter_im = Image.fromarray(letter_arr, mode="RGB")
                letter_im = letter_im.resize((24, 24), Image.BOX)
                #letter_im.save("letter-%d.png" % letter_idx)
                q_arr = np.asarray(letter_im)
                score = []
                for name, g in golden.items():
                    cnt = 0
                    for i in range(24):
                        for j in range(24):
                            if np.all(q_arr[i][j] != g[i][j]):
                                cnt += 1
                    score.append((cnt, name))
                score.sort()
                result += score[0][1][0]
    return result

if __name__ == "__main__":
    img_data = open(sys.argv[1], "rb").read()
    print(captcha(img_data))
