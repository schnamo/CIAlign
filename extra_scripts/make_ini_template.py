#!/usr/bin/env python3
"""
Converts the output of CIAlign --help into a config file with the
default options
"""
import sys

def main():

    infile = sys.argv[1] # python3 CIAlign --help > temp.txt
    outfile = sys.argv[2] # ini file

    lines = [line.strip() for line in open(infile).readlines()]
    bigstring = " ".join(lines)
    bigstring = bigstring.split("Required Arguments: ")[1]
    arguments = bigstring.split("--")[1:-1]
    out = open(outfile, "w")
    out.write("# CIAlign Parameters\n")

    for argument in arguments:
        nam = argument.split(" ")[0]
        parts = argument.split(" ")[1:]
        if parts[0].upper() == parts[0]:
            parts = parts[1:]
        desc = " ".join(parts)
        desc = desc.replace("  ", " ").strip()
        desc = desc.replace("Optional Arguments:", "").replace(" -h,", "")
        if "Required" not in desc:
            desc, d2 = desc.split("Default: ")
        else:
            desc = desc.replace(" Required", "")
            d2 = "XXXXX"
        if "config" not in desc:
            out.write("# %s\n%s = %s\n" % (desc, nam, d2))
    out.close()

if __name__ == "__main__":
    main()
