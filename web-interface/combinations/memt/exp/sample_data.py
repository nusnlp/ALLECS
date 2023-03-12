import argparse
import random
import os.path as op

def main(args):
    files = []
    file_length = None
    for f_path in args.data:
        print('Reading {}...'.format(f_path))
        with open (f_path) as f:
            content = f.readlines()
            if file_length is None:
                file_length = len(content)
            else:
                assert file_length == len(content), "file lengths are different ({} and {})"\
                    .format(file_length, len(content))
            files.append(content)
    

    dor = list(zip(*files))
    print('total length: ', len(dor))
    selected = random.choices(dor, k=args.length)
    selected = zip(*selected)
    
    for content, f_path in zip(selected, args.data):
        out_path = op.join(args.out_dir, op.basename(f_path))
        with open(out_path, 'w') as f:
            for line in content:
                f.write(line.strip())
                f.write('\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', nargs='+', help='list of file paths to downsample')
    parser.add_argument('--length', type=int, help='desired new file length')
    parser.add_argument('--out_dir', type=str,help='output directory path')
    args = parser.parse_args()
    main(args)