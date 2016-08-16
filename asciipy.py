import asyncio
import collections
import functools
import os
import re
import webbrowser

from PIL import Image

PALETTE = list("@$&mWJV/!:")  # From darkest to brightest
LEVEL_STEP = 255 // len(PALETTE)


def start(input_path, output_path=None, thumbnail_resolution=(320, 320), callback=webbrowser.open):
    # Load Image
    img = Image.open(input_path).convert('LA')
    img.thumbnail(thumbnail_resolution)

    # Create Dimension (x,y)
    width, height = img.size
    dim = img.load()

    # Convert Image
    avglevel, multiply = leveling_brightness(dim, width, height)
    # if avglevel > 100:
    #     ascii_converted = convert(dim, width, height, multiply)
    # else:
    #     ascii_converted = convert_most10only(dim, width, height)
    ascii_converted = convert(dim, width, height, multiply)
    ascii_converted += '\nPowered by asciipy'

    # Save Image if need
    if output_path:
        with open(output_path, 'w') as f:
            f.write(ascii_converted)

    # Call callback if available
    if callback:
        callback(output_path)

    return ascii_converted


def leveling_brightness(dim, width, height):
    avglevel = 0
    for h in range(height):
        for w in range(width):
            avglevel += dim[w, h][0]
    avglevel = avglevel / (width * height)
    multiply = 192 / avglevel if avglevel <= 128 else 1
    return avglevel, multiply


def convert(dim, width, height, brightness_multiply=1):
    ascii_converted = list()

    for h in range(height):
        ascii_converted.append(list())
        for w in range(width):
            bright = dim[w, h][0] * brightness_multiply
            level = int(bright // LEVEL_STEP)
            if level >= len(PALETTE):
                level = len(PALETTE) - 1
            elif level <= 0:
                level = 0
            c = PALETTE[level]
            ascii_converted[h].append(c)

    # merge characters into single string
    for h in range(height):
        ascii_converted[h] = ''.join(ascii_converted[h])
    ascii_converted = '\n'.join(ascii_converted)

    return ascii_converted


def convert_most10only(dim, width, height):
    ascii_converted = list()

    # Find most 10
    pixels = list()
    for h in range(height):
        for w in range(width):
            pixels.append(dim[w, h][0])
    counter = collections.Counter(pixels)
    pixels.clear()

    # Convert most 10
    most10 = dict(counter.most_common(10))
    most10_levels = sorted(most10.keys(), reverse=True)
    most10_levels = dict([(e[1], e[0]) for e in enumerate(most10_levels)])
    for h in range(height):
        ascii_converted.append(list())
        for w in range(width):
            b = dim[w, h][0]
            if b in most10:
                c = PALETTE[most10_levels[b]]
            else:
                c = ' '
            ascii_converted[h].append(c)

    # merge characters into single string
    for h in range(height):
        ascii_converted[h] = ''.join(ascii_converted[h])
    ascii_converted = '\n'.join(ascii_converted)

    return ascii_converted


def autodiscover():
    pathes = list()
    for root, dirs, names in os.walk(os.path.dirname(os.path.abspath(__file__))):
        for name in names:
            if not re.match('.*[.](jpg|jpeg|png|gif)$', name, re.I):
                continue
            input_path = os.path.join(root, name)
            output_path = input_path + '.txt'
            pathes.append((input_path, output_path))
    return pathes


def main():
    io = asyncio.get_event_loop()
    futures = list()
    for input_path, output_path in autodiscover():
        # Convert image in parallel
        futures.append(io.run_in_executor(None, functools.partial(start, input_path, output_path)))
    io.run_until_complete(asyncio.wait(futures))
    io.close()


if __name__ == '__main__':
    main()
