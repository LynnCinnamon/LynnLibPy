"""
This module provides utility for working with attributes, types, console, and process management.
    COLORS: Provides ANSI escape sequences for text formatting and coloring in the terminal.
    CURSOR: Provides methods for manipulating the cursor position and visibility in the terminal.
"""

from __future__ import annotations

import dataclasses
from multiprocessing import Process, Queue
import os
import re
import sys
from typing import Iterable, Type
from typing_extensions import TypeVar

T = TypeVar("T")

def attributify(obj):
    """
    Extracts non-callable attributes of an object.
    This function returns a list of tuples, where each tuple contains the name 
    and value of a non-callable attribute of the given object. Attributes that 
    start with double underscores are excluded.
    Args:
        obj: The object from which to extract attributes.
    Returns:
        List[Tuple[str, Any]]: A list of tuples containing attribute names and their values.
    """
    return [
        (attr, getattr(obj, attr))
        for attr in dir(obj)
        if not callable(getattr(obj, attr)) and not attr.startswith("__")
        ]

def is_value_of_member(value, obj):
    """
    Check if a given value is one of the attribute values of an object.

    Args:
        value: The value to check for.
        obj: The object whose attributes will be checked.

    Returns:
        bool: True if the value is found among the object's attribute values, False otherwise.
    """
    attrs = attributify(obj)
    for attr in attrs:
        if value == attr[1]:
            return True
    return False

def is_float(num):
    """
    Check if the given input can be converted to a float.

    Args:
        num (any): The input to check.

    Returns:
        bool: True if the input can be converted to a float, False otherwise.
    """
    try:
        float(num)
        return True
    except ValueError:
        return False

def constrained(value: T, values:Iterable) -> T | None:
    """
    Returns the value if it is present in the provided iterable of values, otherwise returns None.

    Args:
        value (T): The value to be checked.
        values (Iterable): An iterable containing the allowed values.

    Returns:
        T | None: The value if it is in the iterable, otherwise None.
    """
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
        #We need to ignore the type error here,
        #because we are casting the input to a known bool type but
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
        #We need to ignore the type error here,
        #because we are casting the input to a type that is not known at compile time
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
    print(char, end="", flush=True)

class COLORS():
    """
    COLORS class provides ANSI escape sequences for text formatting and coloring in the terminal.
    """
    #See: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    @dataclasses.dataclass
    class Foreground():
        """
        Provides ANSI escape codes for setting the foreground color in terminal output.
        """
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

    @dataclasses.dataclass
    class Background():
        """
        A class to represent background colors using ANSI escape codes.
        """
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
    def rgb(r:int, g:int, b:int) -> str:
        """
        Generates an ANSI escape code for setting the text color in the terminal using RGB values.

        Args:
            r (int): Red component of the color (0-255).
            g (int): Green component of the color (0-255).
            b (int): Blue component of the color (0-255).

        Returns:
            str: ANSI escape code string for the specified RGB color.
        """
        return f'\033[38;2;{r};{g};{b}m'

    @staticmethod
    def rgb_background(r:int, g:int, b:int) -> str:
        """
        Generates an ANSI escape code for setting the background color in the terminal.

        Args:
            r (int): Red component of the RGB color (0-255).
            g (int): Green component of the RGB color (0-255).
            b (int): Blue component of the RGB color (0-255).

        Returns:
            str: ANSI escape code string for the specified RGB background color.
        """
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
    '''
    CURSOR class provides methods to manipulate the terminal cursor.
    '''
    ERASE_LINE = '\033[2K'
    ERASE_TILL_LINE_END = '\033[0J'

    @staticmethod
    def set_pos(line, column):
        """
        Set the cursor position in the terminal.

        Parameters:
        line (int): The line number to move the cursor to.
        column (int): The column number to move the cursor to.
        """
        print(f'\033[{line};{column}f', end='', flush=True)

    @staticmethod
    def hide_cursor(hidden: bool):
        """
        Hide or show the cursor in the terminal.

        Parameters:
        hidden (bool): If True, hide the cursor. If False, show the cursor.
        """
        if hidden:
            print('\033[?25l', end='', flush=True)
            return
        print('\033[?25h', end='', flush=True)


def styled(text:str, *styles:str) -> str:
    """Wraps the given text in the provided styles for display in the console"""
    if not styles:
        return text
    for style in styles:
        if not style and style != "":
            raise TypeError("Style must not be None.")
        if not isinstance(style, str):
            raise TypeError("Style must be a string.")

    #assert that all styles are from COLORS, COLORS.FOREGROUND, COLORS.BACKGROUND
    #or match r"^\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m$"
    #or match r"^\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m$"
    for style in styles:
        if style == "":
            continue
        assert style, "Style must not be None."
        if  not is_value_of_member(style, COLORS)\
        and not is_value_of_member(style, COLORS.Foreground)\
        and not is_value_of_member(style, COLORS.Background):
            if not re.match(r"^\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m$", style) \
                and not re.match(r"^\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m$", style):
                raise ValueError("Style "+str(style.replace('\033', '\\033'))+\
                    " is not a valid style."+os.linesep+"Use the "+str(__name__)+\
                        ".COLORS object for valid styles.")

    return f"{''.join([style for style in styles if style])}{text}{COLORS.RESET}"

def unstyled(text:str):
    '''
    strips all styles from the given text
    '''
    for piece in [COLORS, COLORS.Foreground, COLORS.Background]:
        for _, value in attributify(piece):
            text = text.replace(value, "")
    reg_rbg =            r"\033\[38;2;(\d{1,3});(\d{1,3});(\d{1,3})m"
    reg_rbg_background = r"\033\[48;2;(\d{1,3});(\d{1,3});(\d{1,3})m"
    text = re.sub(reg_rbg, "", text)
    text = re.sub(reg_rbg_background, "", text)
    return text

def __run_with_limited_time_helper(func, queue, *args, **kwargs):
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
    p = Process(target=__run_with_limited_time_helper, args=_args, kwargs=kwargs)
    p.start()
    p.join(time)
    if p.is_alive():
        p.terminate()
        return None

    return queue.get()

#if we call this file, call the ./main.py file in the same directory instead
if __name__ == "__main__": # pragma: no cover
    EXE = sys.executable
    print("Running of lib detected. Running main.py instead.")
    os.system(f'{EXE} "{os.path.dirname(__file__)}/main.py"')
