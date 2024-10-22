'''
This is the test file for the LynnLib module
'''

import time
import pytest
import lynn_lib

def test_style_text():
    '''Test that the text is styled correctly'''
    text = "test"
    color = lynn_lib.COLORS.Foreground.RED
    colorized_text = lynn_lib.styled(text, color)
    assert colorized_text == f"\033[31m{text}\033[0m", "Text should be colored red"

def test_strip_style():
    '''Test that the text is stripped of all styles'''
    text = "test"
    color = lynn_lib.COLORS.Foreground.RED
    style2 = lynn_lib.COLORS.rgb(10, 20, 30)
    style3 = lynn_lib.COLORS.rgb_background(10, 20, 30)
    styled_text = lynn_lib.styled(text, color, style2, style3)
    stripped_text = lynn_lib.unstyled(styled_text)
    assert stripped_text == text, "Text should be stripped of all styles"

def test_no_style():
    '''
    Test that the text is not styled when no style is provided
    Also test that the function raises the correct exceptions
    '''
    text = "test"
    styled_text = lynn_lib.styled(text)
    assert styled_text == text, "Text should not be styled"
    with pytest.raises(TypeError):
        lynn_lib.styled(text, None) #type: ignore [arg-type] #Wrong type is wanted for this test
    with pytest.raises(TypeError):
        lynn_lib.styled(text, 1) #type: ignore [arg-type] #Wrong type is wanted for this test
    with pytest.raises(ValueError):
        lynn_lib.styled(text, "not a color")
    lynn_lib.styled(text, "")

def test_constrained():
    '''Test that the value is correctly constrained to the list'''
    #test with numbers
    assert lynn_lib.constrained(5, [1, 2, 3, 4, 5]) == 5, "Should return 5"
    assert lynn_lib.constrained(1, [1, 2, 3, 4, 5]) == 1, "Should return 1"
    assert lynn_lib.constrained(7, [1, 2, 3, 4, 5]) is None, "Should return None"

    #test with strings
    assert lynn_lib.constrained("a", ["a", "b", "c"]) == "a", "Should return 'a'"
    assert lynn_lib.constrained("d", ["a", "b", "c"]) is None, "Should return None"

    #test with bools
    assert lynn_lib.constrained(True, [True, False]) is True, "Should return True"
    assert lynn_lib.constrained(False, [True, False]) is False, "Should return False"
    assert lynn_lib.constrained(None, [True, False]) is None, "Should return None"

    #test with mixed types
    assert lynn_lib.constrained("a", [1, "a", True]) == "a", "Should return 'a'"
    assert lynn_lib.constrained(1, [1, "a", True]) == 1, "Should return 1"
    assert lynn_lib.constrained("nope", [1, "a", True]) is None, "Should return None"

def test_is_float():
    '''Test that the function correctly identifies floats'''
    assert lynn_lib.is_float(1.0) is True, "Is a float"
    assert lynn_lib.is_float(1) is True, "1 is also a valid float"
    assert lynn_lib.is_float("1.0") is True, "String representation of a float"
    assert lynn_lib.is_float("1") is True, "String representation of an int is also a valid float"
    assert lynn_lib.is_float("1.0.0") is False, "Invalid float"
    assert lynn_lib.is_float("a") is False, "Not a float"
    assert lynn_lib.is_float("1a") is False, "Not a float"

def test_typed_input(monkeypatch):
    '''Test that the function correctly returns the typed input'''

    #test with int
    monkeypatch.setattr('builtins.input', lambda _: "1")
    assert lynn_lib.typed_input("Enter a number: ", int) == 1, "Should return 1"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert lynn_lib.typed_input("Enter a number: ", int) is None, "Should return None"

    #test with float
    monkeypatch.setattr('builtins.input', lambda _: "1.0")
    assert lynn_lib.typed_input("Enter a number: ", float) == 1.0, "Should return 1.0"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert lynn_lib.typed_input("Enter a number: ", float) is None, "Should return None"

    #test with str
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert lynn_lib.typed_input("Enter a string: ", str) == "a", "Should return 'a'"

    #test with bool
    monkeypatch.setattr('builtins.input', lambda _: "True")
    assert lynn_lib.typed_input("Enter a boolean: ", bool) is True, "Should return True"
    monkeypatch.setattr('builtins.input', lambda _: "False")
    assert lynn_lib.typed_input("Enter a boolean: ", bool) is False, "Should return False"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert lynn_lib.typed_input("Enter a boolean: ", bool) is False, "Should return False"

def test_put_char(monkeypatch, capsys):
    '''Test that the character is placed at the correct position in the console'''

    # Mock the CURSOR.set_pos method to avoid actual cursor movement
    def mock_set_pos(line, column):
        print(f"Cursor set to line {line}, column {column}")

    monkeypatch.setattr(lynn_lib.CURSOR, 'set_pos', mock_set_pos)

    # Test putting a character at a specific position
    lynn_lib.put_char('A', 10, 5)
    captured = capsys.readouterr()
    # pylint: disable-next=line-too-long
    assert captured.out == "Cursor set to line 5, column 10\nA", "Character should be placed at the correct position"

    # Test putting another character at a different position
    lynn_lib.put_char('B', 20, 15)
    captured = capsys.readouterr()
    # pylint: disable-next=line-too-long
    assert captured.out == "Cursor set to line 15, column 20\nB", "Character should be placed at the correct position"

def test_set_pos(capsys):
    '''Test that the cursor is set to the correct position in the console'''

    # Test setting the cursor position
    lynn_lib.CURSOR.set_pos(5, 10)
    captured = capsys.readouterr()
    assert captured.out == '\033[5;10f', "Cursor should be set to line 5, column 10"

    # Test setting the cursor position to another location
    lynn_lib.CURSOR.set_pos(15, 20)
    captured = capsys.readouterr()
    assert captured.out == '\033[15;20f', "Cursor should be set to line 15, column 20"

# The following functions are used for testing the run_with_limited_time function
# They are defined here to allow for pickeling by the multiprocessing module
def __sample_function(x, y):#pragma: no cover (We are not testing this function)
    return x + y

def __long_running_function():#pragma: no cover (We are not testing this function)
    time.sleep(10)
    assert False, "This code should always timeout"

def __sample_function_2(x, y, z=0):#pragma: no cover (We are not testing this function)
    return x + y + z

def __sample_function_3():#pragma: no cover (We are not testing this function)
    return "no args"

def test_run_with_limited_time_success():
    '''Test that the function completes within the time limit'''
    result = lynn_lib.run_with_limited_time(__sample_function, (1, 2), {}, 5)
    assert result == 3, "Function should return 3"

def test_run_with_limited_time_timeout():
    '''Test that the function times out correctly'''

    result = lynn_lib.run_with_limited_time(__long_running_function, (), {}, 1)
    assert result is None, "Function should be terminated and return None"

def test_run_with_limited_time_with_args_and_kwargs():
    '''Test that the function handles args and kwargs correctly'''



    result = lynn_lib.run_with_limited_time(__sample_function_2, (1, 2), {'z': 3}, 5)
    assert result == 6, "Function should return 6"

def test_run_with_limited_time_no_args():
    '''Test that the function works with no args and kwargs'''

    result = lynn_lib.run_with_limited_time(__sample_function_3, (), {}, 5)
    assert result == "no args", "Function should return 'no args'"

def test_hide_cursor(capsys):
    '''Test that the cursor is hidden or shown correctly in the console'''

    # Test hiding the cursor
    lynn_lib.CURSOR.hide_cursor(True)
    captured = capsys.readouterr()
    assert captured.out == '\033[?25l', "Cursor should be hidden"

    # Test showing the cursor
    lynn_lib.CURSOR.hide_cursor(False)
    captured = capsys.readouterr()
    assert captured.out == '\033[?25h', "Cursor should be shown"
