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


def getSimpleGenotype(outputFileName):
    simple = "getsimplest 1 " + outputFileName + "\n"
    p.stdin.write(bytes(simple, "UTF-8"))
    p.stdin.flush()

    maxLines = 1
    for _ in range(0, maxLines):
        #print("reading :", p.stderr.readline())
        print("reading :", p.stdout.readline())


"expdef standard-eval" "eval eval-allcriteria.sim plik_z_genotypem.gen" - q


def mutate(inputFileName, outputFileName):
    mutation = "mut scripts_output/" + inputFileName + " " + outputFileName + "\n"
    p.stdin.write(bytes(mutation, "UTF-8"))
    p.stdin.flush()

    maxLines = 1
    for _ in range(0, maxLines):
        #print("reading :", p.stderr.readline())
        print("reading :", p.stdout.readline())


def framsCrossover(inputFileName1, inputFileName2, outputFileName):

    crossover = "crossover scripts_output/" + inputFileName1 + \
        " scripts_output/" + inputFileName2 + " " + outputFileName + "\n"

    p.stdin.write(bytes(crossover, "UTF-8"))
    p.stdin.flush()

    maxLines = 1
    for _ in range(0, maxLines):
        print("reading :", p.stdout.readline())


framsPath = r"E:\\Polibuda\\mag sem1\\Framsy\\Framsticks\\"

args = "frams -vs -Q -s -icliutils.ini"


command = framsPath + args

p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)


prepareConsole()

getSimpleGenotype("abc")

mutate("abc", "def")

framsCrossover("abc", "def", "krzyzowka")

p.stdin.close()
p.terminate()
