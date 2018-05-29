import os
import sys


def create_file(path):
    dirs = os.listdir(path)
    name = 1
    for i in range(len(dirs)):
        if i % 1000 == 0:
            f = open('files/lote_{}.txt'.format(name), 'w')
            name += 1
        f.write('%s\n' % dirs[i])
    f.close()


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 0:
        print('Entre com path rapideye 4a cobertura')
    else:
        create_file(args[1])
