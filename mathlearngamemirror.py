import streamlit as st
import typing
import random
import plotly.express as px
import json
import dataclasses
import os
import pandas as pd

# PAGE TITLE
st.title("Math Learning App")

class Problem:
    @property
    def tags(self) -> typing.List[str]:
        raise NotImplementedError()

    def render(self) -> None:
        raise NotImplementedError()
    
    @property
    def correct_answer(self) -> str:
        raise NotImplementedError()
    
    def get_answer(self) -> None:
        raise NotImplementedError()
    
    def check_answer(self) -> bool:
        raise NotImplementedError()


# FULLY COMPLETED    
class SimpleAdditionProblem(Problem):
    def __init__(self):
        self.a = random.randint(1, 10)
        self.b = random.randint(1, 10)
        self.answer = self.a + self.b
    
    def render(self) -> None:
        st.write(f"""
        Bob has {self.a} apples, Carl has {self.b} apples. How many
        apples do they have together?
        """)
        
    def get_answer(self, problemkey, multichoice) -> None:
        if multichoice:
            choices = []
            for _ in range(3):
                choice = random.randint(1, self.answer + 5)
                while choice in choices:
                    choice = random.randint(1, self.answer + 5)
                choices.append(choice)
            st.session_state['choicemasterlist'].append(choices)
            print(st.session_state['choicemasterlist'])
            choices.insert(random.randint(0,2), self.answer) # Inserts answer at random location
            self.user_answer = st.selectbox("Answer", st.session_state['choicemasterlist'][problemkey])
        else:
            self.user_answer = st.number_input('Answer', step=1, key = problemkey)

    def check_answer(self):
        return self.user_answer == self.answer
    

class LineSlopeProblem(Problem):
    def __init__(self):
        self.m = random.randint(-5, 5)
        self.answer = self.m

    def render(self) -> None:
        st.write('What is the slope of the line below?')
        st.write(px.line(x=[-10, -5], y=[5, self.m * 5 + 5]))

    def get_answer(self, problemkey, multichoice) -> None:
        print(self.answer)
        if multichoice:
            choices = []
            for _ in range(3):
                choice = random.randint(self.answer - 5, self.answer + 5)
                while choice in choices:
                    choice = random.randint(self.answer - 5, self.answer + 5)
                choices.append(choice)
            st.session_state['choicemasterlist'].append(choices)
            print(st.session_state['choicemasterlist'])
            choices.insert(random.randint(0,2), self.answer) # Inserts answer at random location
            self.user_answer = st.selectbox("Answer", st.session_state['choicemasterlist'][problemkey])
        else:
            self.user_answer = st.number_input('Answer', step=1, key = problemkey)

    def check_answer(self):
        return self.user_answer == self.m
    
class QuadraticProblem(Problem):
    def __init__(self):
        self.root0 = random.randint(-10, 10)
        self.root1 = random.randint(-10, 10)
        while self.root0 == self.root1:
            self.root1 = random.randint(-10, 10)
        self.constant = random.randint(-10, 10)

        self.answer = {self.root0*-1, self.root1*-1}
    def render(self) -> None:
        a = self.constant
        b = self.constant * (self.root0 + self.root1)
        c = self.constant * self.root0 * self.root1
        print(self.root0, self.root1)
        st.write(f"""
        What are the roots of the equation {a}x^2 + {b}x + {c} = 0
        """)

    def get_answer(self, problemkey, multichoice = False) -> None:
        print(self.answer)
        if multichoice:
            choices = []
            for _ in range(3):
                choice = {random.randint(-10, 10), random.randint(-10,10)}
                while choice in choices:
                    choice = {random.randint(-10, 10), random.randint(-10,10)}
                choices.append(choice)
            st.session_state['choicemasterlist'].append(choices)
            print(st.session_state['choicemasterlist'])
            choices.insert(random.randint(0,2), self.answer) # Inserts answer at random location
            self.user_answer = st.selectbox("Answer", st.session_state['choicemasterlist'][problemkey])
        else:
            self.user_answer = {
                st.number_input('Answer', step=1, key = problemkey), 
                st.number_input('Answer', step=1, key = problemkey*1000 + 5),
            }

    def check_answer(self):
        return set(self.user_answer) == self.answer

def generate_problems(problemClass):
    print("Generating Problems...")
    st.session_state['problems'].append(problemClass)
    print(st.session_state)


def render_problems(multichoice = False):
    print('Rendering Problems...')
    for problem in st.session_state['problems']:
        st.session_state['problemkey'] += 1
        print('problemkey:',st.session_state['problemkey'])
        problem.render()
        problem.get_answer(st.session_state['problemkey'], multichoice)
        print(problem.get_answer)

def set_state(i):
    st.session_state.stage = i

@dataclasses.dataclass
class ProblemRecord:
    problem_type: str
    problem_tags: typing.List[str]
    user_answer_correct: bool

@dataclasses.dataclass
class UserData:
    total_problems: int
    correct_problems: int
    total_problems_by_tag: typing.Dict[str, int]
    problem_history: typing.List[ProblemRecord]

# UPDATES USER_DATA TOTAL_PROBLEMS BASED ON NUMBER OF PROBLEMS USER ANSWERED
if os.path.exists('data.json'):
    with open('data.json', "r") as read_file:
        user_data_dict = json.load(read_file)
        user_data = UserData(**user_data_dict)
else:
    user_data = UserData(0, 0, {}, {}, )

if 'stage' not in st.session_state:
    st.session_state.stage = 0

# STATISTICS 
def update_stats():
    global user_data
    st.write("Your stats:")
    st.write("Total problems:", user_data.total_problems)
    st.write("Correct problems:", user_data.correct_problems)

    if user_data.total_problems > 0: # Prevent DivisionByZero Error
        st.write("Percentage correct:", int(user_data.correct_problems/user_data.total_problems*100//1), "%")
    else:
        st.write("Percentage correct:", 0, "%")

    if st.button("Reset Stats", type = 'primary'): # Reset Stats Button
        if os.path.exists('data.json'):
            os.remove('data.json')
        user_data = UserData(0, 0, {}, {}, )
        st.rerun()

def home():
    st.session_state['generated'] = False
    st.session_state['choicemasterlist'] = []
    '---'
    st.session_state['multiselect_problems'] = st.multiselect("Choose question type(s)", ["Addition", "Line Slope", "Quadratic"])
    
    st.session_state['multiselect_total'] = st.number_input("Choose the total amount of problems.", step = 1)
    st.session_state['multichoice'] = st.checkbox("Multiple Choice Questions", key = 'quick')
    if st.button('Quick Practice'):
        excess = int(st.session_state['multiselect_total']) % len(st.session_state['multiselect_problems'])
        factor = int(st.session_state['multiselect_total']) // len(st.session_state['multiselect_problems'])

        problemdict = {
            "Addition": 'additionproblems',
            "Line Slope": 'lineslopeproblems',
            "Quadratic": 'quadradicproblems',
        }

        excessnotadded = True
        for problem in st.session_state['multiselect_problems']:
            if excessnotadded:
                st.session_state[problemdict[problem]] = int(factor) + int(excess)
                excessnotadded = False
            else:
                st.session_state[problemdict[problem]] = int(factor)
            print(st.session_state[problemdict[problem]])
            print(st.session_state['additionproblems'])
        print(st.session_state['additionproblems'])
        set_state(1)
        st.rerun()
        return
            
    '---'
    
    st.session_state['additionproblems'] = st.number_input("Addition Problems", step=1)
    st.session_state['lineslopeproblems'] = st.number_input("Line Slope Problems", step=1)
    st.session_state['quadradicproblems'] = st.number_input("Quadratic Problems", step=1)
    st.session_state['multichoice'] = st.checkbox("Multiple Choice Questions")
    st.button('Practice', on_click=set_state, args = [1])

    

if st.session_state.stage == 2:
    submitted_problems = st.session_state['problems']
    print(submitted_problems)
    for problem in st.session_state['problems']:
        user_data.total_problems += 1
        if problem.check_answer():
            print("Correct Answer")
            user_data.correct_problems += 1
    st.session_state['problems'] = []
    update_stats()

    home()
else:
    update_stats()

if st.session_state.stage == 0: 
    home()

if st.session_state.stage == 1:
    print("if statement 1 passed")
    st.session_state['problemkey'] = -1
    if st.session_state['generated'] == False:
        print("if statement 2 passed")
        print(st.session_state['additionproblems'])
        st.session_state['problems'] = []

        for _ in range(st.session_state['additionproblems']):
            generate_problems(SimpleAdditionProblem())
            
        for _ in range(st.session_state['lineslopeproblems']):
            generate_problems(LineSlopeProblem())
        
        for _ in range(st.session_state['quadradicproblems']):
            generate_problems(QuadraticProblem())

        st.session_state['generated'] = True
        render_problems(st.session_state['multichoice'])    
        st.button('Submit', on_click=set_state, args = [2])

    else:
        render_problems(st.session_state['multichoice'])    
        st.button('Submit', on_click=set_state, args = [2])


with open('data.json', 'w') as f:
    user_data_dict = dataclasses.asdict(user_data)
    user_data_dict = json.dump(user_data_dict, f)

'''
---
CHANGELOG
- more problem classes (12/4)
- fixed problem selection after clicking submit (12/4)
- reset stats button (12/6)
- cleaned up duplicate code/functions (12/6)
- multichoice supported for following classes: Addition, Linear Equation (12/6)
- multichoice option added (12/6)
- fixed line drawing on Linear Equations (12/6)
- creation of home() function (12/6)
- implement multi-select to sort problems by tag (12/8)
- fixed quadratic equation logic (12/14)
- adds remainder when quick generating questions (12/14)
- more efficient generation of multi-choice answers (12/15)
- fixed duplicate generation of multi-choice answers (12/15)
- multichoice addded for following classes: Quadratic (12/18)
- cleaned up code (12/18)

TODO:
- more problem classes

NOTE:
- multi-select is a blanket option, cannot be turned on for individual problem classes
- use of st.rerun() in update_stats() function to be changed with control flow
- not too focused on adding more classes because all classes follow a similar template,
fast to implement, and main challenges (graphs + 2 number answers) have been solved
'''