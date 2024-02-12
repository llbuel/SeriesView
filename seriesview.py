import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from sympy import sympify, latex
import os
import readline
import re

class MathNode:
    def __init__(self, value=None):
        if value is None:
            self.value = None
        else:
            self.value = value
        
        self.left = None
        self.right = None
        self.parent = None

def plotSeries(indices,sums,title):
    x_smooth = np.linspace(indices[0],indices[-1],100*len(indices))
    spline = make_interp_spline(indices,sums,k=3)
    y_smooth = spline(x_smooth)

    plt.plot(x_smooth,y_smooth,linestyle='-')
    plt.scatter(indices,sums,marker='o',color='red')

    plt.xlabel('Index')
    plt.xticks(indices)
    plt.ylabel('Accumulation')
    plt.title(title)
    plt.grid(True)
    plt.show()

def generateGraphExpressionStr(iterator,startIdx,endIdx,expression):
    expressionStr = 'Series Visualization of $\sum_{' + iterator + '=' + str(startIdx) + '}^{' + str(endIdx) + '} ' + latex(sympify(expression)) + '$'
    
    return expressionStr

def buildExprTree(tokens,variable):
    node = MathNode()

    precedence = {'+':1, '-':1, '*':2, '/':2, '^':3}
    functions = ['sqrt','sin','cos','tan','ln','log']
    operators = ['^','*','/','+','-']
    output = []

    parenCount = 0

    for inputChar in tokens:
        if inputChar == ' ':
            continue
        if (inputChar == '(' or inputChar == '[') and len(tokens) > 3:
            node.left = MathNode()
            node.left.parent = node
            node = node.left
            parenCount = parenCount + 1
        elif (inputChar.isdigit() or inputChar == variable):
            node.value = inputChar
            if len(tokens) > 1:
                if node.parent is not None:
                    node = node.parent
                else:
                    node.parent = MathNode()
                    node.parent.left = node
                    node = node.parent
        elif inputChar in operators:
            if node.value in operators:
                if (precedence[inputChar] <= precedence[node.value]) or (node.value == '-' and node.left.value is None and node.right.value.isdigit()):
                    newNode = MathNode()
                    newNode.left = node
                    newNode.parent = node.parent
                    if node.parent is not None:
                        node.parent.right = newNode
                    node = newNode
                elif precedence[inputChar] > precedence[node.value]:
                    node = node.right
                    newNode = MathNode()
                    newNode.left = node
                    newNode.parent = node.parent
                    if node.parent is not None:
                        node.parent.right = newNode
                    node = newNode
                elif node.right.left is None:
                    node.right.left = MathNode()
                    node.right.left.value = node.right.value
                    node.right.value = None
                    node.right.left.parent = node.right
                    node = node.right
            elif node.value is not None and (node.value.isdigit() or node.value == variable):
                if node.left is None:
                    node.left = MathNode()
                    node.left.parent = node
                    node.left.value = node.value
                    node.value = None
                    node.left.parent = node
            elif node.parent is not None:
                if node.parent.value is None:
                    node = node.parent
            node.value = inputChar
            node.right = MathNode()
            node.right.parent = node
            node = node.right
        elif (inputChar == ')' or inputChar == ']') and len(tokens) > 3:
            if node.value is not None and node.parent is not None:
                node = node.parent
            parenCount = parenCount - 1

    if parenCount != 0:
        raise ValueError("Mismatched parentheses!\n")

    while node.parent is not None:
        node = node.parent

    tree = node

    return tree

def computeTree(root,variable,index):
    node = root

    if node is None:
        return 0

    if node.left is None and node.right is None:
        if node.value == variable:
            return index
        else:
            return node.value
    elif node.value == '-' and node.left.value is None:
        right = computeTree(node.right,variable,index)
        right = eval(right)
        return (-1)*right

    left = computeTree(node.left,variable,index)
    right = computeTree(node.right,variable,index)

    if isinstance(left,str):
        left = eval(left)
    if isinstance(right,str):
        right = eval(right)

    if node.value == '+':
        return left + right
    if node.value == '-':
        return left - right
    if node.value == '*':
        return left * right
    if node.value == '/':
        if right == 0:
            raise Exception("Cannot divide by zero! Double check your indices.\n")
        else:
            return left / right
    if node.value == '^':
        return left ** right

def seriesInterpret(tokens,variable,index):
    result = 0

    expressionTree = buildExprTree(tokens,variable)
    result = computeTree(expressionTree,variable,index)

    return result


def seriesEvaluate(iterator,startIdx,endIdx,tokens):
    accumVector = []
    partialSum = 0

    if type(endIdx) == int:
        sumRange = list(range(startIdx,endIdx+1))

        for i in sumRange:
            partialSum = partialSum + seriesInterpret(tokens,iterator,i)
            accumVector.append(partialSum)
    else:
        maxdiff = 0.000001
        previous = 0

        loopItr = startIdx

        sumdiff = 1

        while sumdiff > maxdiff:
            partialSum = previous + seriesInterpret(tokens,iterator,loopItr)

            sumdiff = abs(partialSum - previous)

            previous = partialSum

            loopItr = loopItr + 1

            accumVector.append(partialSum)

    return accumVector

def generateTokens(variable,expression):
    regex = rf"(\b\d*[\.]?\d+\b|[\+\-\*\/\^\(\)]|sqrt|sin|cos|tan|ln|log|{variable}\b)"

    tokens = re.findall(regex, expression)

    return tokens

def checkInput(iterator,startIdx,endIdx,expression):
    itr_type = type(iterator)
    start_type = type(startIdx)
    end_type = type(endIdx)
    expr_type = type(expression)

    allowed_iterators = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    allowed_expr_chars = "0123456789" + allowed_iterators + "+-*/^()[]"

    allowed_iterators_set = set(allowed_iterators)
    if itr_type != str or not all(char in allowed_iterators_set for char in iterator):
        raise ValueError("Invalid iterator variable.\nVariable must be a string:\n\nseriesview([iterator_variable_str],[startIndex_int],[endIndex_int],[series_expression_str])\n\nExample: seriesview('n',0,10,'n^2')\n")
    
    if start_type != int:
        raise ValueError("Invalid start index.\nIndices must be integers:\n\nseriesview([iterator_variable_str],[startIndex_int],[endIndex_int],[series_expression_str])\n\nExample: seriesview('n',0,10,'n^2')\n")
    
    if end_type != int and (end_type == str and (endIdx != 'Inf' and endIdx != 'inf')):
        raise ValueError("Invalid end index.\nIndices must be integers or infinite:\n\nseriesview([iterator_variable_str],[startIndex_int],[endIndex_int],[series_expression_str])\n\nExample: seriesview('n',0,10,'n^2')\n")

    allowed_expr_chars_set = set(allowed_expr_chars)
    if expr_type != str or not all(char in allowed_expr_chars_set for char in expression):
        raise ValueError("Invalid expression.\nExpression must be a string:\n\nseriesview([iterator_variable_str],[startIndex_int],[endIndex_int],[series_expression_str])\n\nExample: seriesview('n',0,10,'n^2')\n")
    
    multSubPattern = re.compile(r'(\d)({0})|({0})(\d)'.format(re.escape(iterator)))
    expression = re.sub(multSubPattern,r'\1*\2\3',expression)


    parenSubPattern = re.compile(r'\)(\()', re.MULTILINE)
    expression = re.sub(parenSubPattern, r')*\1', expression)
    
    invalidRegex = rf"^\d\.\+\-\*\/\^\(\)(?!sqrt)(?!sin)(?!cos)(?!tan)(?!ln)(?!log)(?!{iterator})"

    invalidChars = re.findall(invalidRegex, expression)

    if invalidChars:
        raise ValueError("Unrecognized characters in series formula.\n")
    
    return expression


def seriesview(iterator, startIdx, endIdx, expression):
    expression = checkInput(iterator,startIdx,endIdx,expression)
    tokens = generateTokens(iterator,expression)
    
    sumVector = seriesEvaluate(iterator,startIdx,endIdx,tokens)
    
    title = generateGraphExpressionStr(iterator,startIdx,endIdx,expression)
    
    if type(endIdx) == int:
        indices = list(range(startIdx,endIdx+1))
    else:
        indices = list(range(startIdx,len(sumVector)+startIdx))
    
    plotSeries(indices,sumVector,title)

def main():
    commandHistory = []

    #app = tk.Tk()
    #app.title("SeriesVIEW")

    #app.attributes('-zoomed',True)

    #app.mainloop()

    while True:
        userInput = input("SV> ")
        commandHistory.append(userInput)

        if userInput.lower() == 'exit':
            os.system('clear')
            break
        if userInput == "" and commandHistory:
            previousCommand = commandHistory[-1]
            readline.set_startup_hook(lambda: readline.insert_text(previousCommand))

            try:
                userInput = input("SV> ")
            finally:
                readline.set_startup_hook()
            
            userInput = input("SV>")
        
        try:
            exec(userInput)
            print("")
        except NameError as ne:
            print("Invalid input type. Input must be formatted as: seriesview(<string>,<int>,<int>,<string>)\n\nExample: seriesview('n',0,10,'n^2')\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
