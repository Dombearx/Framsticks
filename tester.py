import os, os.path, sys, platform, re, copy
import traceback # for custom printing of exception trace/stack
import errno  # for delete_file_if_present()
import argparse
from subprocess import Popen, PIPE
from time import sleep
import telnetlib

import comparison  # our source
import globals  # our source


def test(args, test_name, input, output_net, output_msg, exe_prog, exeargs):
	print(test_name, end=" ")
	command = prepare_exe_with_name(exe_prog)
	command += exeargs
	if len(output_net) > 0:
		command += globals.EXENETMODE
	if args.valgrind:
		command = globals.EXEVALGRINDMODE + command

	p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)

	if len(output_net) > 0:
		sleep(10 if args.valgrind else 1)  # time for the server to warm up
		tn = telnetlib.Telnet("localhost", 9009)
		tn.write(bytes(input, "UTF-8"))
		sleep(2)  # time for the server to respond...
		# if we had a command in the frams server protocol to close the connection gracefully, then we could use read_all() instead of the trick with sleep()+read_very_eager()+close()
		stdnet = tn.read_very_eager().decode().split("\n")  # the server uses "\n" as the end-of-line character on each platform
		tn.close()  # after this, the server is supposed to close by itself (the -N option)
		input = ""
	# under Windows, p.stderr.read() and p.stdout.read() block while the process works, under linux it may be different
	# http://stackoverflow.com/questions/3076542/how-can-i-read-all-availably-data-from-subprocess-popen-stdout-non-blocking?rq=1
	# http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
	# p.terminate() #this was required when the server did not have the -N option
	# stderrdata=p.stderr.read() #fortunately it is possible to reclaim (a part of?) stream contents after the process is killed... under Windows this is the ending of the stream

	(stdoutdata, stderrdata) = p.communicate(bytes(input, "UTF-8"))  # the server process ends...
	stdoutdata = stdoutdata.decode()  # bytes to str
	stderrdata = stderrdata.decode()  # bytes to str
	# p.stdin.write(we) #this is not recommended because buffers can overflow and the process will hang up (and indeed it does under Windows) - so communicate() is recommended
	# stdout = p.stdout.read()
	# p.terminate()

	# print repr(input)
	# print repr(stdoutdata)

	stdout = stdoutdata.split(os.linesep)
	# print stdout
	stderr = stderrdata.split(os.linesep)
	ok = check(stdnet if len(output_net) > 0 else stdout, output_list if len(output_list) > 0 else output_net, output_msg)

	if p.returncode != 0 and p.returncode is not None:
		print("  ", p.returncode, "<- returned code")

	if len(stderrdata) > 0:
		print("   (stderr has %d lines)" % len(stderr))
		# valgrind examples:
		# ==2176== ERROR SUMMARY: 597 errors from 50 contexts (suppressed: 35 from 8)
		# ==3488== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 35 from 8)
		if (not args.valgrind) or ("ERROR SUMMARY:" in stderrdata and " 0 errors" not in stderrdata) or (args.always_show_stderr):
			print(stderrdata)

	if not ok and args.stop:
		sys.exit("First test failure, stopping early.")
	return ok


def compare(jest, goal, was_compared_to):
	p = comparison.Comparison(jest, goal)
	if p.ok:
		print("\r", globals.ANSI_SETGREEN + " ok" + globals.ANSI_RESET)
	else:
		print("\r", globals.ANSI_SETRED + " FAIL\7" + globals.ANSI_RESET)
		print(p.result)
		f = open(os.path.join(globals.THISDIR, '_last_failed' + was_compared_to + '.output'), 'w')  # files are easier to compare than stdout
		print('\n'.join(jest), end="", file=f)
		f = open(os.path.join(globals.THISDIR, '_last_failed' + was_compared_to + '.goal'), 'w')  # files are easier to compare than stdout
		print('\n'.join(goal), end="", file=f)
	return p.ok


def remove_prefix(text, prefix):
	return text[len(prefix):] if text.startswith(prefix) else text


def check(stdout, output_net, output_msg):
	actual_out_msg = []
	if len(output_net) > 0:  # in case of the server, there is no filtering
		for line in stdout:
			actual_out_msg.append(line)
		return compare(actual_out_msg, output_net, '')
	else:
		FROMSCRIPT = "Script.Message: "
		beginnings = tuple(["[" + v + "] " for v in ("INFO", "WARN", "ERROR", "CRITICAL")])  # there is also "DEBUG"
		header_begin = 'VMNeuronManager.autoload: Neuro classes added: '  # header section printed when the simulator is created
		header_end = "UserScripts.autoload: "  # ending of the header section
		now_in_header = False
		for line in stdout:
			if now_in_header:
				if header_end in line:  # "in" because multithreaded simulators prefix their messages with their numerical id, e.g. #12/...
					now_in_header = False
				continue
			else:
				if header_begin in line:  # as above
					now_in_header = True
					continue
				line = remove_prefix(line, beginnings[0])  # cut out [INFO], other prefixes we want to leave as they are
				line = remove_prefix(line, FROMSCRIPT)  # cut out FROMSCRIPT
				actual_out_msg.append(line)
		if actual_out_msg[-1] == '':  # empty line at the end which is not present in our "goal" contents
			actual_out_msg.pop()
		return compare(actual_out_msg, output_msg, '')


def delete_file_if_present(filename):
	print('"%s" (%s)' % (filename, "the file was present" if os.path.exists(filename) else "this file did not exist"))
	try:
		os.remove(filename)
	except OSError as e:
		if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
			raise  # re-raise exception if a different error occurred


def reset_values():
	global input_text, output_net, output_msg, test_name, ini, output_list, exeargs, exe_prog
	input_text = ""
	output_list = []
	ini = ""
	output_net, output_msg = [], []
	exeargs = []
	test_name = "no-name test"


def is_test_active():
	global test_name
	if name_template == "":
		return True
	if re.match(name_template, test_name):
		return True
	return False


def prepare_exe_with_name(name):
	if name in globals.EXENAMES:
		exename = copy.copy(globals.EXENAMES[name])  # without copy, the following modifications would change values in the EXENAMES table
	else:
		exename = [name]
	for rule in globals.EXERULES:
		exename[0] = re.sub(rule[0], rule[1], exename[0])
	return exename


def print_exception():
	print("\n"+("-"*60),'begin exception')
	traceback.print_exc()
	print("-"*60,'end exception')


def main():
	global input_text, name_template, test_name, exe_prog, exeargs
	name_template = ""
	exeargs = []

	parser = argparse.ArgumentParser()
	parser.add_argument("-val", "--valgrind", help="Use valgrind", action="store_true")
	parser.add_argument("-c", "--nocolor", help="Don't use color output", action="store_true")
	parser.add_argument("-f", "--file", help="File name with tests", required=True)
	parser.add_argument("-tp", "--tests-path", help="tests directory, files containing test definitions, inputs and outputs are relative to this directory, default is '" + globals.THISDIR + "'")
	parser.add_argument("-fp", "--files-path", help="files directory, files tested by OUTFILECOMPARE are referenced relative to this directory, default is '" + globals.FILESDIR + "'")
	parser.add_argument("-wp", "--working-path", help="working directory, test executables are launched after chdir to this directory, default is '" + globals.EXEDIR + "'")
	parser.add_argument("-n", "--name", help="Test name (regexp)")  # e.g. '^((?!python).)*$' = these tests which don't have the word "python" in their name
	parser.add_argument("-s", "--stop", help="Stops on first difference", action="store_true")
	parser.add_argument("-ds", "--diffslashes", help="Discriminate between slashes (consider / and \\ different)", action="store_true")
	parser.add_argument("-err", "--always-show-stderr", help="Always print stderr (by default it is hidden if 0 errors in valgrind)", action="store_true")
	parser.add_argument("-e", "--exe", help="Regexp 'search=replace' rule(s) transforming executable name(s) into paths (eg. '(.*)=path/to/\\1.exe')", action='append')  # in the example, double backslash is just for printing
	parser.add_argument("-p", "--platform", help="Override platform identifier (referencing platform specific files " + globals.SPEC_INSERTPLATFORMDEPENDENTFILE + "), default:sys.platform (win32,linux2)")
	args = parser.parse_args()
	if args.valgrind:
		print("Using valgrind...")
	if args.diffslashes:
		globals.DIFFSLASHES = args.diffslashes
	if args.file:
		main_test_filename = args.file
	if args.tests_path:
		globals.THISDIR = args.tests_path
	if args.files_path:
		globals.FILESDIR = args.files_path
	if args.working_path:
		globals.EXEDIR = args.working_path
	if args.name:
		name_template = args.name
	if args.exe:
		for e in args.exe:
			search, replace = e.split('=', 1)
			globals.EXERULES.append((search, replace))
	if args.platform:
		globals.PLATFORM = args.platform

	os.chdir(globals.EXEDIR)

	globals.init_colors(args)

	fin = open(os.path.join(globals.THISDIR, args.file))
	reset_values()
	exe_prog = "default"  # no longer in reset_values (exe: persists across tests)
	outfile = []
	tests_failed = 0
	tests_total = 0
	for line in fin:
		line = globals.stripEOL(line)
		if len(line) == 0 or line.startswith("#"):
			continue
		line = line.split(":", 1)
		# print line
		command = line[0]
		if command == "TESTNAME":
			reset_values()
			test_name = line[1]
		elif command == "arg":
			exeargs.append(line[1])
		elif command == "exe":
			exe_prog = line[1]
		elif command == "in":
			input_text += line[1] + "\n"
		elif command == "out-net":
			output_net.append(line[1])
		elif command == "out-file":
			outfile.append(line[1])
		elif command == "out-mesg":
			output_msg.append(line[1])
		elif command == "out":
			output_list.append(line[1])
		elif command == "DELETEFILENOW":
			if is_test_active():
				print("\t ", command, end=" ")
				delete_file_if_present(os.path.join(globals.FILESDIR, line[1]))
		elif command == "OUTFILECLEAR":
			outfile = []
		elif command == "OUTFILECOMPARE":
			if is_test_active():
				print("\t", command, '"%s"' % line[1], end=" ")
				try:
					contents = []
					with open(os.path.join(globals.FILESDIR, line[1]), 'r') as main_test_filename:
						for line in main_test_filename:
							contents.append(globals.stripEOL(line))
					ok = compare(contents, outfile, '_file')
				except Exception as e: # could also 'raise' for some types of exceptions if we wanted
					print_exception()
					ok = 0
				tests_failed += int(not ok)
				tests_total += 1
		elif command == "RUNTEST":
			if is_test_active():
				print("\t", command, end=" ")
				try:
					ok = test(args, test_name, input_text, output_net, output_msg, exe_prog, exeargs)
				except Exception as e: # could also 'raise' for some types of exceptions if we wanted
					print_exception()
					ok = 0
				tests_failed += int(not ok)
				tests_total += 1
		else:
			raise Exception("Don't know what to do with this line in test file: ", line)

	return (tests_failed, tests_total)


if __name__ == "__main__":
	tests_failed, tests_total = main()
	print("%d / %d failed tests" % (tests_failed, tests_total))
	sys.exit(tests_failed)  # return the number of failed tests as exit code ("error level") to shell
