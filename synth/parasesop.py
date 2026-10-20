"""
parasesop.py - Seperates SOP expression into product form

"""
from synth.function import BooleanFunction

def parsesop(expression):
    # Splits the terms in the boolean expression at the +
    terms = expression.split("+")
    cleanedterms = []

    # Cleans up white space in each term
    for term in terms:
        newterm = term.strip()
        cleanedterms.append(newterm)

    return cleanedterms

# print(parsesop("A'B + AC"))

# terms = ["A'", "C"]
# Now we have to assign values to the terms
def productterms(term):
    # Creates a dictionary
    literals = {}

    for i, char in enumerate(term):
        if char == "'":
            continue

        # If the variable exists and the next term is ', then its compliment, otherwise just 1
        if i + 1 < len(term) and term[i + 1] == "'":
            literals[char] = 0
        else:
            literals[char] = 1

    return literals

# print(productterms(terms))

# Now we have to combine both functions
def parseexpression(expression):
    terms = parsesop(expression)
    print (terms)
    parsedterms = []

    for i in terms:
        literals = productterms(i)
        parsedterms.append(literals)    

    return parsedterms

# print(parseexpression("A'B + AC"))

# Next we need to find out how many variables we have to make truth tables
def getvariables(parsedterms):
    variables = set()

    for term in parsedterms:
        for variable in term:
            variable = variable.upper()
            variables.add(variable)

    return sorted(variables)

# Sanity Test
#parsed = parseexpression("A'B + AC")
#print (parsed) 
#variables = getvariables(parsed)
#print(getvariables(parsed))


# Next we need to generate the combinations depending on how many variables there are
def generatecombinations(variables):
    combinations = []

    # Creates each binary for each number, 0 is 000, 1 is 001, 2 is 010...
    for num in range(2 ** len(variables)):
        binary = format(num, f"0{len(variables)}b")

        # Creates value dictionaries for each binary
        values = {}

        # Saves the value in A, B and C
        for i, variable in enumerate(variables):
            # Makes sure binary is a number and not a string
            values[variable] = int(binary[i])

        # Adds new dictionary to list
        combinations.append(values)

    return combinations

# We then need to check the terms from the Boolean equation to the combinations to see which ones have output of 1
def matchterm(combination, term):
    # For each variable and its corresponding value, compare it to the variable and value of the combination 
    for variable, value in term.items():
        if combination[variable] != value:
            return False

    return True

# Now we can get the minterms
def minterms(parsedterms, variables):
    # Since we dont want to count double minterms
    minterm = set()

    for number, combination in enumerate(generatecombinations(variables)):
        # Check if any product term matches
        for term in parsedterms:
            # If it returns True, then it adds it to the minterm set
            if matchterm(combination, term):
                minterm.add(number)
                break

    return minterm
