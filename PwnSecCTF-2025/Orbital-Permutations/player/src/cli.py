#!/usr/bin/python3
from __future__ import annotations
import argparse
from handout import create_handout

def main():
    
    ap = argparse.ArgumentParser(description="Rubik-ish KEM/DEM (5x5 layer)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("handout", help="Generate hard-mode public handout + author key")
    h.add_argument("--msg", required=True, help="String to encrypt/seal.")
    h.add_argument("--out", default="handout.json")
    h.add_argument("--priv", default="author_key.json")
    h.set_defaults(func=lambda args: create_handout(args.msg, args.out, args.priv,seed=None))

    return ap

if __name__ == "__main__":
    parser = main()
    args = parser.parse_args()
    args.func(args)