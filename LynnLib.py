from __future__ import annotations
from enum import Enum
from inspect import walktree
import inspect
import msvcrt
from multiprocessing import Process, Queue
from collections.abc import Callable
import os
import re
import stat
import sys
from typing import Any, ClassVar, Iterable, Literal, Type
from typing_extensions import TypeVar

T = TypeVar("T")

def attributify(obj):
    return [(attr, getattr(obj, attr)) for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
    
def isValueOfMember(value, obj):
    attrs = attributify(obj)
    for attr in attrs:
        if value == attr[1]:
            return True

def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def constrained(value: T, values:Iterable) -> T | None:
    return value if value in values else None
    
def typed_input(prompt:str, my_type:Type[T]) -> T | None:
    """ Prompts the user for an input and returns it casted to the specified type OR None
    Parameters
    ------------
        prompt : str
            the prompt for the user
        my_type : Type[T]
            the type we want the input in

    Return
    -----------
        typed_input : T|None
            our type specific, casted value OR None
    Example Usage
    ------------
    .. code-block:: python
        while (my_float := typed_input("Insert a float: ", float)) == None:
            pass
            
        while (my_int := typed_input("Insert an int: ", int)) == None:
            pass
    """


    #get the user input as a string
    user_input = input(prompt)
    #special case: bool
    if my_type == bool:
        #check for common true-ish strings
        #We need to ignore the type error here, because we are casting the input to a known bool type but
        #the type checker doesn't know that for some reason.
        return user_input.lower() in [
            "true",
            "yes",
            "y",
        ] or (
            #all numbers except 0 are true-ish
            is_float(user_input) and float(user_input) != 0
        ) #type: ignore [return-value]

    try:
        #if possible, cast the user input into the wanted type.
        #We need to ignore the type error here, because we are casting the input to a type that is not known at compile time
        casted = my_type(user_input) # type: ignore [call-arg]
        #and return it
        print(user_input, "is a valid", my_type.__name__)
        return casted
    except ValueError:
        #if we couldn't cast it, it is not the wanted type
        #in that case we want to return None as a sign that the user input was invalid
        print(user_input, "is not a valid", my_type.__name__)
        return None

def put_char(char:str, x:int, y:int):
    """Puts a character at the specified position in the console"""
    CURSOR.set_pos(y, x)
    print(char, end="", flush=True)# pragma: no cover
  
class COLORS():
    #See: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    class FOREGROUND():
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGNETA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        DEFAULT = '\033[39m'

        BRIGHT_BLACK = '\033[90m'
        BRIGHT_RED = '\033[91m'
        BRIGHT_GREEN = '\033[92m'
        BRIGHT_YELLOW = '\033[93m'
        BRIGHT_BLUE = '\033[94m'
        BRIGHT_MAGNETA = '\033[95m'
        BRIGHT_CYAN = '\033[96m'
        BRIGHT_WHITE = '\033[97m'

    class BACKGROUND():
        BLACK = '\033[40m'
        RED = '\033[41m'
        GREEN = '\033[42m'
        YELLOW = '\033[43m'
        BLUE = '\033[44m'
        MAGNETA = '\033[45m'
        CYAN = '\033[46m'
        WHITE = '\033[47m'
        DEFAULT = '\033[49m'

        BRIGHT_BLACK = '\033[100m'
        BRIGHT_RED = '\033[101m'
        BRIGHT_GREEN = '\033[102m'
        BRIGHT_YELLOW = '\033[103m'
        BRIGHT_BLUE = '\033[104m'
        BRIGHT_MAGNETA = '\033[105m'
        BRIGHT_CYAN = '\033[106m'
        BRIGHT_WHITE = '\033[107m'

    @staticmethod
    def RGB(r:int, g:int, b:int) -> str:
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def RGB_BACKGROUND(r:int, g:int, b:int) -> str:
        return f'\033[48;2;{r};{g};{b}m'

    #NON-COLOR
    BOLD = '\033[1m'
    FAINT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINKING = '\033[5m'
    INVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

    #NON-COLOR UNSET
    BOLD_UNSET = '\033[21m'
    FAINT_UNSET = '\033[22m'
    ITALIC_UNSET = '\033[23m'
    UNDERLINE_UNSET = '\033[24m'
    BLINKING_UNSET = '\033[25m'
    INVERSE_UNSET = '\033[27m'
    HIDDEN_UNSET = '\033[28m'
    STRIKETHROUGH_UNSET = '\033[29m'

    #END FORMATTING
    RESET = '\033[0m'

class CURSOR:
    ERASE_LINE = '\033[2K'
    ERASE_TILL_LINE_END = '\033[0J'

    @staticmethod
    def set_pos(line, column):
        print(f'\033[{line};{column}f', end='', flush=True)# pragma: no cover
        
    @staticmethod
    def hide_cursor(hidden:bool):
        if hidden:
            print('\033[?25l', end='', flush=True)
            return
        print('\033[?25h', end='', flush=True)

FOREGROUND_COLOR = COLORS.FOREGROUND
BACKGROUND_COLOR = COLORS.BACKGROUND

def styled(text:str, *styles:str) -> str:
    """Wraps the given text in the provided styles for display in the console"""
    if not styles:
        return text
    if len(styles) == 0:
        return text
    for style in styles:
        if not style and style != "":
            raise TypeError("Style must not be None.")
        if not isinstance(style, str):
            raise TypeError("Style must be a string.")
    
    #assert that all styles are from COLORS, COLORS.FOREGROUND, COLORS.BACKGROUND
    #or match r"^\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m$" or r"^\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m$"
    for style in styles:
        if style == "":
            continue
        assert style, "Style must not be None."
        if  not isValueOfMember(style, COLORS)\
        and not isValueOfMember(style, COLORS.FOREGROUND)\
        and not isValueOfMember(style, COLORS.BACKGROUND):
            if not re.match(r"^\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m$", style) \
                and not re.match(r"^\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m$", style):
                raise ValueError("Style "+str(style.replace('\033', '\\033'))+" is not a valid style."+os.linesep+"Use the "+str(__name__)+".COLORS object for valid styles.")

    return f"{''.join([style for style in styles if style])}{text}{COLORS.RESET}"

def unstyled(text:str):
    for piece in [COLORS, COLORS.FOREGROUND, COLORS.BACKGROUND]:
        for _, value in attributify(piece):
            text = text.replace(value, "")
    reg_rbg =            r"\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m"
    reg_rbg_background = r"\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m"
    text = re.sub(reg_rbg, "", text)
    text = re.sub(reg_rbg_background, "", text)
    return text

def run_with_limited_time_helper(func, queue, *args, **kwargs):
    # run the function and get the result
    result = func(*args, **kwargs)
    # put the result on the queue
    queue.put(result)

def run_with_limited_time(func, args, kwargs, time):
    """Runs a function with time limit

    :param func: The function to run
    :param args: The functions args, given as tuple
    :param kwargs: The functions keywords, given as dict
    :param time: The time limit in seconds
    :return: the return value if the function ended successfully. None if it was terminated.
    """
    #We are using a Queue to retrieve the result
    queue:Queue = Queue()
    #Build the arg list
    _args = []
    _args.extend([func, queue])
    _args.extend(args)
    p = Process(target=run_with_limited_time_helper, args=_args, kwargs=kwargs)
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        return None

    return queue.get()

#if we call this file, call the ./main.py file in the same directory instead
if __name__ == "__main__": # pragma: no cover
    exe = sys.executable
    print("Running of lib detected. Running main.py instead.")
    os.system(f'{exe} "{os.path.dirname(__file__)}/main.py"')

    