#!/usr/bin/env python
import configman
parser = configman.ArgumentParser()
parser.add_argument("square", help="display a square of a given number")
args = parser.parse_args()
print args.square**2

