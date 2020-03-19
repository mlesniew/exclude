#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import subprocess


include_pattern = re.compile(r'^\s*#\s*include\s+((?:<[^>]+>)|(?:"[^"]+"))', re.I)


def remove_lines(source, target, lines_to_skip):
    with open(source) as source_file, open(target, 'w') as target_file:
        for lineno, line in enumerate(source_file, 1):
            if lineno in lines_to_skip:
                continue
            else:
                target_file.write(line)


def iter_includes(filename):
    with open(filename) as f:
        for lineno, line in enumerate(f, 1):
            match = include_pattern.match(line)
            if match:
                yield lineno, match.group(1)


def check(checkcmd):
    try:
        subprocess.check_call(checkcmd, shell=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def exclude(filename, checkcmd):
    includes = list(iter_includes(filename))

    print(f'{filename}: Found {len(includes)} include directive(s)')

    if not includes:
        return

    # backup
    original = filename + '.bak'
    shutil.copyfile(filename, original)

    removal_possible = set()

    for lineno, header in includes:
        print(f'{filename}:{lineno}: Attempt to remove #include {header}')
        removal_possible.add(lineno)
        remove_lines(original, filename, removal_possible)
        if check(checkcmd):
            print(f'{filename}:{lineno}: #include {header} can be removed')
        else:
            print(f'{filename}:{lineno}: #include {header} is required')
            removal_possible.remove(lineno)

    if removal_possible:
        print(f'{filename}: Removed {len(removal_possible)} #include directive(s)')
        remove_lines(original, filename, removal_possible)
    else:
        print(f'{filename}: No #include directives removed')
        shutil.move(original, filename)



def main():
    parser = argparse.ArgumentParser('Minimize set of required #includes')
    parser.add_argument('filename', nargs='+')
    parser.add_argument('--command', default='make')
    args = parser.parse_args()

    for filename in args.filename:
        exclude(filename, args.command)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit('Abort')
