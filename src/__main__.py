import datetime
import sys
import os
import argparse






def main():
    parser = argparse.ArgumentParser(description='Mathemonastical is an app that provides statistical analysis of '
                                                 'daily activities for informed decision making')

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help',
                                       dest="command")

    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('priority', nargs=1)
    add_parser.add_argument('name', nargs=1)

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('name', nargs=1)

    pickup_parser = subparsers.add_parser('pickup')
    pickup_parser.add_argument('name', nargs=1)

    begin_parser = subparsers.add_parser('begin')
    begin_parser.add_argument('name', nargs='?')

    end_parser = subparsers.add_parser('end')

    list_parser = subparsers.add_parser('list')

    args = parser.parse_args()

    print(args)

#TODO: arg_parsed dispatch

if __name__ == '__main__':
    main()