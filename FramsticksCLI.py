from subprocess import Popen, PIPE
import json
import os


class FramsticksCLI():

    def __init__(self, framsPath):
        self.framsPath = framsPath

        args = "\\frams -vs -Q -s -icliutils.ini"
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

    def __saveGenotypeToFile(self, genotype, name):
        outputName = name
        outputPath = self.framsPath + "\\data\\" + outputName
        file = open(outputPath, "w")
        file.write("org:")
        file.write("\n")
        file.write("genotype:~")
        file.write("\n")
        file.write(genotype + "~")
        file.close()
        return outputName

    def __saveToFile(self, genotype, name):
        outputName = name
        outputPath = self.framsPath + "\\data\\" + outputName
        file = open(outputPath, "w")
        file.write(genotype)
        file.close()
        return outputName

    def __removeFile(self, path):
        filePath = self.framsPath + "\\data\\" + path
        if(os.path.exists(filePath)):
            os.remove(filePath)

    def getSimpleGenotype(self):
        """

        Returns:
            String -- simple genotype
        """
        outputFileName = "simplest.gen"
        getSimpleCommand = "getsimplest 1 " + outputFileName + "\n"
        self.framsProcess.stdin.write(bytes(getSimpleCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

        with open(self.framsPath + "\\data\\scripts_output\\" + outputFileName) as f:
            genotype = "".join(f.readlines())

        self.__removeFile("scripts_output\\" + outputFileName)

        return genotype

    def evaluate(self, genotype):
        """

        Arguments:
            genotype {String}

        Returns:
            Dictionary -- genotype evaluated with eval-allcriteria.sim
        """
        filePath = self.__saveGenotypeToFile(genotype, "toEvaluate.gen")

        evalCommand = "eval eval-allcriteria.sim " + filePath + "\n"

        self.framsProcess.stdin.write(bytes(evalCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

        with open(self.framsPath + "\\data\\scripts_output\\" + "genos_eval.json") as f:
            data = json.load(f)
        dictionary = data[0]
        results_temp = dictionary["evaluations"]
        results = results_temp[""]

        self.__removeFile("scripts_output\\" + "genos_eval.json")
        self.__removeFile(filePath)

        return results

    def mutate(self, genotype):
        """

        Arguments:
            genotype {String} 

        Returns:
            String -- genotype
        """
        inputFilePath = self.__saveToFile(genotype, "toMutate.gen")
        outputFilePath = "mutant.gen"

        mutationCommand = "mut " + inputFilePath + " " + outputFilePath + "\n"
        self.framsProcess.stdin.write(bytes(mutationCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

        with open(self.framsPath + "\\data\\scripts_output\\" + outputFilePath) as f:
            newGenotype = "".join(f.readlines())

        self.__removeFile(inputFilePath)
        self.__removeFile("scripts_output\\" + outputFilePath)

        return newGenotype

    def crossover(self, genotype1, genotype2):
        """

        Arguments:
            genotype1 {String}
            genotype2 {String}

        Returns:
            String -- genotype
        """
        parent1FilePath = self.__saveToFile(genotype1, "parent1.gen")
        parent2FilePath = self.__saveToFile(genotype2, "parent2.gen")

        childFilePath = "child.gen"

        crossoverCommand = "crossover " + parent1FilePath + \
            " " + parent2FilePath + " " + childFilePath + "\n"

        self.framsProcess.stdin.write(bytes(crossoverCommand, "UTF-8"))
        self.framsProcess.stdin.flush()

        while("FileObject.write" not in self.framsProcess.stdout.readline().decode()):
            pass

        with open(self.framsPath + "\\data\\scripts_output\\" + childFilePath) as f:
            childGenotype = "".join(f.readlines())

        self.__removeFile(parent1FilePath)
        self.__removeFile(parent2FilePath)
        self.__removeFile("scripts_output\\" + childFilePath)

        return childGenotype


if __name__ == "__main__":

    framsPath = "E:\\Polibuda\\mag sem1\\Framsy\\Framsticks"

    framsCLI = FramsticksCLI(framsPath)

    genotype = framsCLI.getSimpleGenotype()
    print(genotype)

    parent1 = framsCLI.mutate(genotype)
    parent2 = framsCLI.mutate(parent1)
    print("Parent1: ", parent1)
    print("Parent2: ", parent2)
    child = framsCLI.crossover(parent1, parent2)

    print("child: ", child)
    print(framsCLI.evaluate(child))
