import argparse
import re
import sys


class Color:
    # Class that defines the color that highlight the matching text
    """
           Parameters
           ----------
        color - string - ANSI format color of the colored output
        reset_color - string - ANSI format color of the terminal default color
    """

    def __init__(self, color, reset_color):
        self.color = color
        self.reset_color = reset_color


# This script uses green color to highlight the matching text, instance of Color class
green_color = Color('\033[0;32m', '\033[00m')
default_color = Color('\033[00m', '\033[00m')


class AbstractPrinter:
    # Using a Factory Method Design pattern - AbstractPrinter
    # Class that hold the states required to print line and abstract method to print line

    def __init__(self, line, line_number, text_file, match, color):
        """
               Parameters
               ----------
            line - the line that hold the matching text
            line number -  to be printed
            text_file - which is the file we read from
            match - the match object we get returned finditer method of re module
            color - boolean parameter which indicate if highlighting the matching text is needed
            underscore -boolean parameter which indicate if '^' under the matching text is needed
            machine - boolean parameter which indicate if the format should be the machine format
        """
        self.line = line
        self.line_number = line_number
        self.text_file = text_file
        self.match = match
        self.color = color

    def print_line(self):
        """
            Method
            -------
            Abstract method to print line according to given format
        """
        pass


class DefaultFormat(AbstractPrinter):
    # Default Format printer inherit from AbstractPrinter
    # Override the print_line method from AbstractPrinter

    def print_line(self):
        """
                Method
                -------
                Method to print line according to default format
        """
        # Remove last character if is '\n' - work around to not print additional empty line between results
        if self.line[-1] is "\n":
            self.line = self.line.rstrip("\n")

        color_string = self.color.color + self.line[self.match.start():self.match.end()] + self.color.reset_color

        if self.match.start() is 0:
            line_with_color = color_string + self.line[self.match.end() + 1:]
        else:
            line_with_color = self.line[:self.match.start() - 1] + color_string + self.line[self.match.end() + 1:]
        # Example: "File: /tmp/file.txt, Line: 12 - this is the line to be printed"
        print("File: {0}, Line: {1} - {2}".format(self.text_file.name, self.line_number, line_with_color))


class MachineFormat(AbstractPrinter):
    # Machine Format printer class inherit from AbstractPrinter
    # Override the print_line method from AbstractPrinter

    def print_line(self):
        """
                Method
                -------
                Method to print line according to machine format
        """
        # Example: "/tmp/file.txt:12:0:this"
        print(
            "{0}:{1}:{2}:{3}{4}{5}".format(self.text_file.name, self.line_number, self.match.start(), self.color.color,
                                           self.match.group(), self.color.reset_color))


class UnderscoreLine:
    # Class that used to print line with '^' under the matching text

    def __init__(self, num_of_spaces):
        """
               Parameters
               ----------
            num_of_spaces - number of spaces before '^' character
            underscore_line - string composed by (num_of_spaces*' ') + '^'
        """
        self.num_of_spaces = num_of_spaces
        self.underscore_line = " " * num_of_spaces + '^'

    def print_underscore_line(self):
        """
            Method
            -------
            Method to print the underscored line
        """
        print(self.underscore_line)


def print_match(line, line_number, text_file, match, color, underscore, machine):
    # This method will print the given math according to the desired format
    """
               Parameters
               ----------
            line - the line that hold the matching text
            line_number -  to be printed
            text_file - which is the file we read from
            match - the match object we get returned finditer method of re module
            color - boolean parameter which indicate if highlighting the matching text is needed
            underscore -boolean parameter which indicate if '^' under the matching text is needed
            machine - boolean parameter which indicate if the format should be the machine format

    """

    # Setting color to be used
    color_of_match = green_color if color else default_color

    # Construct printers
    default_printer = DefaultFormat(line, line_number, text_file, match, color_of_match)
    machine_printer = MachineFormat(line, line_number, text_file, match, color_of_match)

    # Machine format
    if machine:
        machine_printer.print_line()

    # Default format
    else:
        default_printer.print_line()

    if underscore:

        if machine:
            number_of_spaces_for_underscore = len("{0}:{1}:{2}:".format(text_file.name, line_number, match.start()))
        else:
            number_of_spaces_for_underscore = match.start() + len(
                "File: {0}, Line: {1} - ".format(text_file.name, line_number))

        # Create underscore format line instance to be printed
        underscore_line_printer = UnderscoreLine(number_of_spaces_for_underscore)

        # Print the underscored line
        underscore_line_printer.print_underscore_line()


def main():
    # Parsing arguments
    parser = argparse.ArgumentParser()
    parser.epilog = "Example: python patternFinder.py -f /tmp/file.txt -r ^ab.* -u -c -m"

    # Mandatory argument
    parser.add_argument("--regex", "-r", action="store", type=str, required=True,
                        help="The pattern to look for into the file given - regular expression")

    # Optional arguments:
    parser.add_argument("--files", "-f", nargs='+', action="store", type=argparse.FileType('r'), default=None, help="The file to search the pattern into")
    parser.add_argument("--color", "-c", action="store_true", help="highlight matching text")
    parser.add_argument("--underscore", "-u", action="store_true", help=" prints '^' under the matching text ")
    parser.add_argument("---machine", "-m", action="store_true", help="generate machine readable output")
    args = parser.parse_args()

    pattern = re.compile(args.regex)

    # Use STDIN if file not exist
    if args.files is None:
        if args.files is None:
            try:
                tmp = sys.stdin.readlines()
                args.files = []
                f = open("stdin.txt", "w+")
                for line in tmp:
                    f.write(line)
                f.close()
                f = open("stdin.txt", "r")
                args.files.append(f)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
            except:  # handle other exceptions such as attribute errors
                print("Unexpected error:", sys.exc_info()[0])
            print("done")

    # For each file - go over the lines one by one and search for the regular expression
    # If found, go to print_match method to print according the given format
    for text_file in args.files:
        line_number = 0
        for line in text_file:
            line_number += 1
            matches = pattern.finditer(line)
            for match in matches:
                print_match(line, line_number, text_file, match, args.color, args.underscore, args.machine)


if __name__ == "__main__":
    main()
