from subprocess import Popen, PIPE


def prepareConsole():
    # At start
    maxLines = 2
    for _ in range(0, maxLines):
        print("reading :", p.stdout.readline())

    # rnd
    rnd = "rnd" + "\n"
    p.stdin.write(bytes(rnd, "UTF-8"))
    p.stdin.flush()

    # expdef
    expdef = "expdef standard-eval" + "\n"
    p.stdin.write(bytes(expdef, "UTF-8"))
    p.stdin.flush()


def getSimpleGenotype(outputFileName):
    simple = "getsimplest 1 " + outputFileName + "\n"
    p.stdin.write(bytes(simple, "UTF-8"))
    p.stdin.flush()

    while("FileObject.write" not in p.stdout.readline().decode()):
        pass


def framsEvaluate(inputFileName):
    eval = "eval " + inputFileName + " eval-allcriteria.sim" + "\n"

    p.stdin.write(bytes(eval, "UTF-8"))
    p.stdin.flush()

    while("FileObject.write" not in p.stdout.readline().decode()):
        pass


def mutate(inputFileName, outputFileName):
    mutation = "mut scripts_output/" + inputFileName + " " + outputFileName + "\n"
    p.stdin.write(bytes(mutation, "UTF-8"))
    p.stdin.flush()

    while("FileObject.write" not in p.stdout.readline().decode()):
        pass


def framsCrossover(inputFileName1, inputFileName2, outputFileName):

    crossover = "crossover scripts_output/" + inputFileName1 + \
        " scripts_output/" + inputFileName2 + " " + outputFileName + "\n"

    p.stdin.write(bytes(crossover, "UTF-8"))
    p.stdin.flush()

    while("FileObject.write" not in p.stdout.readline().decode()):
        pass


framsPath = r"E:\\Polibuda\\mag sem1\\Framsy\\Framsticks\\"

args = "frams -vs -Q -s -icliutils.ini"


command = framsPath + args

p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)


prepareConsole()

getSimpleGenotype("abc")

mutate("abc", "def")

framsCrossover("abc", "def", "krzyzowka")

framsEvaluate("toEvaluate.gen")

p.stdin.close()
p.terminate()
