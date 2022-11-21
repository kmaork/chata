import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from chata import visualize


def show(args):
    visualize(args.input).show()


def save(args):
    visualize(args.input).save(args.dest)


def add_input_args(parser: ArgumentParser):
    parser.add_argument('input', help='Path to an exported WhatsApp chat in text format')


def get_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')
    show = subparsers.add_parser('show')
    add_input_args(show)
    save = subparsers.add_parser('save')
    add_input_args(save)
    save.add_argument('dest', help='Path to directory in which results will be stored', default='.')
    return parser


def parse_args(cli_args: list[str]):
    parser = get_parser()
    return parser.parse_args(cli_args)


def cli(cli_args: list[str]):
    args = parse_args(cli_args)
    func = dict(save=save, show=show)[args.command]
    func(args)


def main():
    cli(sys.argv[1:])


if __name__ == '__main__':
    main()
