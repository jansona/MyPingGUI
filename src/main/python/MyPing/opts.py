#!/usr/bin/python
import argparse
import time
import struct
import socket
import select
import sys


class PingOptions(object):

    def __init__(self):
        """Reset the class; indicates the class hasn't been initailized"""
        self.initialized = False

    def initialize(self, parser):
        parser.add_argument('--host', required=True, help='')
        parser.add_argument('--packet-size', type=int, default=32, help='')
        parser.add_argument('--ping-times', type=int, default=5, help='')
        return parser
    
    def gather_options(self):

        if not self.initialized:
            parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        # opt, _ = parser.parse_known_args()
        return parser.parse_args()

    def print_options(self, opt):

        message = ''
        message += '----------------- Options ---------------\n'
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        message += '----------------- End -------------------'
        print(message)

    def parse(self):

        opt = self.gather_options()
        self.opt = opt
        return self.opt
