import pytest

def test_equal_or_not_equal():
    assert 3 != 2

def test_is_instance():
    assert isinstance('this is a String',str)
    assert not isinstance('10',int)

def test_booleans():
    validated =True
    assert validated is True
    assert ('hello'=='world') is False

def test_type():
    assert type('hello' is str)
    assert type('world' is not int)

def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10

def test_list():
    num_list=[1,2,3,4,5]
    any_list =[False,False]
    assert 1 in num_list
    assert True not in any_list

class Student:
    def __init__(self,first_name:str,last_name:str,major:str,years:int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():
    return Student("Divyansh","Sharma","Computer Science",4)


def test_initialization(default_employee):

    assert default_employee.first_name == "Divyansh"
    assert default_employee.last_name == "Sharma"
    assert default_employee.major == "Computer Science"
    assert default_employee.years == 4