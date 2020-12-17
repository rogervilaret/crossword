import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for object in self.domains:
            list_domain = self.domains.get(object).copy()
            wordchars = object.length
            for every_word in list_domain:
                if len(every_word) != wordchars:
                    self.domains[object].remove(every_word)

                  
        

        return
        raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains1[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        # get overlap positions
        
        overlap = self.crossword.overlaps.get((x,y))
        revision = False
        if overlap is None:
            return False
        else:
            pos_x, pos_y = overlap
            list_domainX = self.domains.get(x).copy()
            for wordx in list_domainX:
                letterX = wordx[pos_x]
                consistent = False
                for wordy in self.domains.get(y):
                    if letterX == wordy[pos_y]:
                        consistent = True
                        break
                if not consistent:
                    revision = True
                    self.domains[x].remove(wordx)
        
        return revision
       
        #maybe here we should check repetitions
        raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = list(self.crossword.overlaps.keys())

        while arcs:
            x , y = arcs.pop(-1)
            if self.revise(x, y):
                if len(self.domains.get(x)) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:    
                        arcs.append((x, neighbor))

            
        return True
        raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if not self.consistent(assignment):
            return False

        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
            
                    
        return True
        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        #check no repeat values
        flipped = {}
        for key, value in assignment.items():
            if value in flipped:
                return False
            else:
                flipped[value] = [key] 

        for object in assignment:
            value = assignment.get(object)
            #check if exist
           
            for neighbor in self.crossword.neighbors(object):
                 if neighbor in assignment.keys():
                     ob_pos, ng_pos = self.crossword.overlaps.get((object,neighbor))
                     if value[ob_pos] !=  assignment.get(neighbor)[ng_pos]:
                         return False

        return True
        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        #get domain
        domain_values = self.domains.get(var)
        new_list = list()
        for object in domain_values:
                calculate=0
                #check constraints
                for neighbor in self.crossword.neighbors(var).difference(assignment):
                        ob_pos, ng_pos = self.crossword.overlaps.get((var,neighbor))
                        for word in self.domains.get(neighbor):
                            if object[ob_pos] !=  word[ng_pos]:
                                calculate += 1
                new_list.append((object,calculate))
        def takeSecond(elem):
            return elem[1]
        new_list.sort(key=takeSecond)
        
        return new_list
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        nextvar = None
        for var in self.crossword.variables - assignment.keys():
            if nextvar is None:
                nextvar = var
            elif len(list(self.domains.get(nextvar))) > len(list(self.domains.get(var))):
                nextvar = var
            elif len(list(self.domains.get(nextvar))) == len(list(self.domains.get(var))):
                if len(list(self.crossword.neighbors(nextvar))) < len(list(self.crossword.neighbors(var))):
                    nextvar = var
            
        return nextvar
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            st = value[0]
            test = assignment.copy()
            test.update({var : value[0]})
            if self.consistent(test):
                assignment.update({var : value[0]})
                result = self.backtrack(assignment)
                if result != None:
                    return result
                else:
                    assignment.pop(var)
        return None

        raise NotImplementedError


def main():
   
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    
    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None
   
   
    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
