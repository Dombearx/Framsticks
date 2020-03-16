from subprocess import Popen, PIPE
import json


class FramsticksCLI():

    def __init__(self, framsPath):
        self.framsPath = framsPath

        args = "frams -vs -Q -s -icliutils.ini"
        command = framsPath + args

        self.framsProcess = Popen(
            command, stdout=PIPE, stderr=PIPE, stdin=PIPE)

        self.__prepareConsole()

    def __prepareConsole(self):
        # At start
        while("UserScripts.autoload" not in self.framsProcess.stdout.readline().decode()):
            pass

        # rnd
        rndCommand = "rnd" + "\n"
        self.framsProcess.stdin.write(bytes(rndCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        # expdef
        expdefCommand = "expdef standard-eval" + "\n"
        self.framsProcess.stdin.write(bytes(expdefCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

    def getSimpleGenotype(self):
        outputFileName = "simplest.gen"
        getSimpleCommand = "getsimplest 1 " + outputFileName + "\n"
        self.framsProcess.stdin.write(bytes(getSimpleCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

        with open(self.framsPath + "\\data\\scripts_output\\" + outputFileName) as f:
            return "".join(f.readlines())

        '''
        with open(self.framsPath + "\\data\\scripts_output\\" + outputFileName) as f:
            data = json.load(f)
        dictionary = data[0]
        results_temp = dictionary["evaluations"]
        results = results_temp[""]
        return results
        '''

    def evaluate(self, inputFilePath):
        evalCommand = "eval " + inputFilePath + " eval-allcriteria.sim" + "\n"

        self.framsProcess.stdin.write(bytes(evalCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

    def mutate(self, inputFilePath, outputFilePath):
        mutationCommand = "mut scripts_output/" + \
            inputFilePath + " " + outputFilePath + "\n"
        self.framsProcess.stdin.write(bytes(mutationCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

    def crossover(self, parent1FilePath, parent2FilePath, childFilePath):

        crossoverCommand = "crossover scripts_output/" + parent1FilePath + \
            " scripts_output/" + parent2FilePath + " " + childFilePath + "\n"

        self.framsProcess.stdin.write(bytes(crossoverCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass


if __name__ == "__main__":

    framsPath = r"E:\\Polibuda\\mag sem1\\Framsy\\Framsticks\\"

    framsCLI = FramsticksCLI(framsPath)

    genotype = framsCLI.getSimpleGenotype()
    print(genotype)
    print(len(genotype))
