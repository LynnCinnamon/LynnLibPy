import pytest
import LynnLib

def test_style_text():
    text = "test"
    color = LynnLib.COLORS.FOREGROUND.RED
    colorized_text = LynnLib.styled(text, color)
    assert colorized_text == f"\033[31m{text}\033[0m", "Text should be colored red"

def test_strip_style():
    text = "test"
    color = LynnLib.COLORS.FOREGROUND.RED
    style2 = LynnLib.COLORS.RGB(10, 20, 30)
    style3 = LynnLib.COLORS.RGB_BACKGROUND(10, 20, 30)
    styled_text = LynnLib.styled(text, color, style2, style3)
    stripped_text = LynnLib.unstyled(styled_text)
    assert stripped_text == text, "Text should be stripped of all styles"
    
def test_no_style():
    text = "test"
    styled_text = LynnLib.styled(text)
    assert styled_text == text, "Text should not be styled"
    with pytest.raises(TypeError):
        LynnLib.styled(text, None) #type: ignore [arg-type] #Wrong type is wanted for this test
    with pytest.raises(TypeError):
        LynnLib.styled(text, 1) #type: ignore [arg-type] #Wrong type is wanted for this test
    with pytest.raises(ValueError):
        LynnLib.styled(text, "not a color")
    LynnLib.styled(text, "")
        
def test_constrained():
    #test with numbers
    assert LynnLib.constrained(5, [1, 2, 3, 4, 5]) == 5, "Should return 5"
    assert LynnLib.constrained(1, [1, 2, 3, 4, 5]) == 1, "Should return 1"
    assert LynnLib.constrained(7, [1, 2, 3, 4, 5]) == None, "Should return None"
    
    #test with strings
    assert LynnLib.constrained("a", ["a", "b", "c"]) == "a", "Should return 'a'"
    assert LynnLib.constrained("d", ["a", "b", "c"]) == None, "Should return None"
    
    #test with bools
    assert LynnLib.constrained(True, [True, False]) == True, "Should return True"
    assert LynnLib.constrained(False, [True, False]) == False, "Should return False"
    assert LynnLib.constrained(None, [True, False]) == None, "Should return None"
    
    #test with mixed types
    assert LynnLib.constrained("a", [1, "a", True]) == "a", "Should return 'a'"
    assert LynnLib.constrained(1, [1, "a", True]) == 1, "Should return 1"
    assert LynnLib.constrained("nope", [1, "a", True]) == None, "Should return None"
    
def test_is_float():
    assert LynnLib.is_float(1.0) == True, "Is a float"
    assert LynnLib.is_float(1) == True, "1 is also a valid float"
    assert LynnLib.is_float("1.0") == True, "String representation of a float"
    assert LynnLib.is_float("1") == True, "String representation of an int is also a valid float"
    assert LynnLib.is_float("1.0.0") == False, "Invalid float"
    assert LynnLib.is_float("a") == False, "Not a float"
    assert LynnLib.is_float("1a") == False, "Not a float"

def test_typed_input(monkeypatch):
    #test with int
    monkeypatch.setattr('builtins.input', lambda _: "1")
    assert LynnLib.typed_input("Enter a number: ", int) == 1, f"Should return 1"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert LynnLib.typed_input("Enter a number: ", int) == None, "Should return None"
    
    #test with float
    monkeypatch.setattr('builtins.input', lambda _: "1.0")
    assert LynnLib.typed_input("Enter a number: ", float) == 1.0, "Should return 1.0"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert LynnLib.typed_input("Enter a number: ", float) == None, "Should return None"
    
    #test with str
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert LynnLib.typed_input("Enter a string: ", str) == "a", "Should return 'a'"
    
    #test with bool
    monkeypatch.setattr('builtins.input', lambda _: "True")
    assert LynnLib.typed_input("Enter a boolean: ", bool) == True, "Should return True"
    monkeypatch.setattr('builtins.input', lambda _: "False")
    assert LynnLib.typed_input("Enter a boolean: ", bool) == False, "Should return False"
    monkeypatch.setattr('builtins.input', lambda _: "a")
    assert LynnLib.typed_input("Enter a boolean: ", bool) == False, "Should return False"