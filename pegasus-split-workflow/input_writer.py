#!/usr/bin/env python
# encoding: UTF-8
import sys, json, commands, os

print "Reading input parameters from 'input.json' file"
with open(sys.argv[1]) as data_file:
  data = json.load(data_file)
  file_name_to_parse = data["file_to_parse"]

print "File name to parse - ", file_name_to_parse

# path to a folder with simulation model
dir = os.path.dirname(os.path.realpath(__file__))

print "Copying a folder with the split workflow in Pegasus format"
cmd = "cp -R %s/split-workflow ." % (dir)
commands.getoutput(cmd)

print "Setting the '%s' file as the split workflow input" % (file_name_to_parse)
commands.getoutput("mkdir ./split-workflow/input")
commands.getoutput("mkdir ./split-workflow/output")
cmd = "cp -R %s/inputs/%s ./split-workflow/input/pegasus.html" % (dir, file_name_to_parse)
commands.getoutput(cmd)

rc = open('./split-workflow/rc.txt')
rc_content = rc.read()
rc.close()
input_file_location = "file://%s" % (dir)
rc_content.replace('file:///home/tutorial/', input_file_location)

rc = open('./split-workflow/rc.txt', 'w')
rc.write(rc_content)
rc.close()
