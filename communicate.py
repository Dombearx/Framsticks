from subprocess import Popen, PIPE


framsPath = r"E:\\Polibuda\\mag sem1\\Framsticks\\"

args = "frams -vs -Q -s -icliutils.ini"

rnd = "rnd"

simple = "getsimplest 1 abc"

command = framsPath + args

print(command)

p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)

# the server process ends...
(stdoutdata, stderrdata) = p.communicate(bytes(rnd, "UTF-8"))
stdoutdata = stdoutdata.decode()  # bytes to str
stderrdata = stderrdata.decode()  # bytes to str

print(stdoutdata)

(stdoutdata, stderrdata) = p.communicate(bytes(simple, "UTF-8"))
