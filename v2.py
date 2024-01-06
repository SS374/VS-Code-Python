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


next_st_key = 1


def get_next_st_key():
    global next_st_key
    ans = next_st_key
    next_st_key += 1
    return ans


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


def get_integer_multi_choices(
    answer: int, min_val: int, max_val: int
) -> typing.List[int]:
    candidates = set(range(min_val, max_val)) - {answer}
    multi_choices = random.sample(list(candidates), 3) + [answer]
    random.shuffle(multi_choices)
    return multi_choices


# FULLY COMPLETED
class SimpleAdditionProblem(Problem):
    def __init__(self):
        self.a = random.randint(1, 10)
        self.b = random.randint(1, 10)
        self.answer = self.a + self.b
        self.multi_choices = get_integer_multi_choices(self.answer, 2, 21)
        self.key = get_next_st_key()
        self.tags_ = ["Arthimethic"]
        self.level_ = "Elementary"
    
    @property
    def tags(self) -> typing.List[str]:
        return self.tags_
    
    @property
    def level(self) -> str:
        return self.level_

    def render(self) -> None:
        st.write(
            f"""
        Bob has {self.a} apples, Carl has {self.b} apples. How many
        apples do they have together?
        """
        )

    def get_answer(self, multichoice) -> None:
        if multichoice:
            self.user_answer = st.selectbox("Answer", self.multi_choices)
        else:
            self.user_answer = st.number_input("Answer", step=1, key=self.key)

    def check_answer(self):
        return self.user_answer == self.answer


class LineSlopeProblem(Problem):
    def __init__(self):
        self.m = random.randint(-5, 5)
        self.answer = self.m
        self.multi_choices = get_integer_multi_choices(self.answer, -5, 6)
        self.key = get_next_st_key()
        self.tags_ = ["Alegebra", "Graphing"]
        self.level_ = "Middle"
    
    @property
    def tags(self) -> typing.List[str]:
        return self.tags_
    
    @property
    def level(self) -> str:
        return self.level_
       

    def render(self) -> None:
        st.write("What is the slope of the line below?")
        st.write(px.line(x=[-10, -5], y=[5, self.m * 5 + 5]))

    def get_answer(self, multichoice) -> None:
        print(self.answer)
        if multichoice:
            self.user_answer = st.selectbox("Answer", self.multi_choices)
        else:
            self.user_answer = st.number_input("Answer", step=1, key=self.key)

    def check_answer(self):
        return self.user_answer == self.m


def get_integer_pair_multi_choices(
    answer: typing.Tuple[int, int], min_val: int, max_val: int
) -> typing.List[typing.Tuple[int, int]]:
    candidates = list(set(range(min_val, max_val)) - set(answer))
    multi_choices = {answer}
    while len(multi_choices) < 4:
        multi_choices.add((random.choice(candidates), random.choice(candidates)))
    multi_choices = list(multi_choices)
    random.shuffle(multi_choices)
    return multi_choices


class QuadraticProblem(Problem):
    def __init__(self):
        self.root0 = random.randint(-10, 10)
        self.root1 = random.randint(-10, 10)
        while self.root0 == self.root1:
            self.root1 = random.randint(-10, 10)
        self.constant = random.randint(-10, 10)


        self.answer = {self.root0 * -1, self.root1 * -1}
        self.multi_choices = get_integer_pair_multi_choices(tuple(self.answer), -10, 10)

        self.key1 = get_next_st_key()
        self.key2 = get_next_st_key()
        self.tags_ = ["Algebra"]
        self.level_ = "Middle"
    
    @property
    def tags(self) -> typing.List[str]:
        return self.tags_
    
    @property
    def level(self) -> str:
        return self.level_

    def render(self) -> None:
        a = self.constant
        b = self.constant * (self.root0 + self.root1)
        c = self.constant * self.root0 * self.root1
        print(self.root0, self.root1)
        st.write(
            f"""
        What are the roots of the equation {a}x^2 + {b}x + {c} = 0
        """
        )

    def get_answer(self, multichoice=False) -> None:
        print(self.answer)
        if multichoice:
            self.user_answer = st.selectbox("Answer", self.multi_choices)
        else:
            self.user_answer = {
                st.number_input("Answer", step=1, key=self.key1),
                st.number_input("Answer", step=1, key=self.key2),
            }

    def check_answer(self):
        return set(self.user_answer) == self.answer


problem_types = [SimpleAdditionProblem, LineSlopeProblem, QuadraticProblem]


def render_problems(multichoice=False):
    print("Rendering Problems...")
    for problem in st.session_state["problems"]:
        problem.render()
        problem.get_answer(multichoice)
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
if os.path.exists("data.json"):
    with open("data.json", "r") as read_file:
        user_data_dict = json.load(read_file)
        user_data = UserData(**user_data_dict)
else:
    user_data = UserData(
        0,
        0,
        {},
        {},
        
    )

if "stage" not in st.session_state:
    st.session_state.stage = 0


# STATISTICS
def update_stats():
    global user_data

    st.write("Your stats:")
    st.write("Total problems:", user_data.total_problems)
    st.write("Correct problems:", user_data.correct_problems)
    if user_data.total_problems > 0:  # Prevent DivisionByZero Error
        st.write(
            "Percentage correct:",
            int(user_data.correct_problems / user_data.total_problems * 100 // 1),
            "%",
        )
    else:
        st.write("Percentage correct:", 0, "%")

    if st.button("Reset Stats", type="primary", key = get_next_st_key()):  # Reset Stats Button
        if os.path.exists("data.json"):
            os.remove("data.json")
        user_data = UserData(
            0,
            0,
            {},
            {},
        )
        st.rerun()

update_stats()


def gen_random_problem_set():
    st.header("Random Problem Set")
    num_problems = st.number_input("Problems", step=1)
    if st.button("Submit"):
        print("generated problems")
        return [random.choice(problem_types)() for _ in range(num_problems)]


def gen_quick_practice():
    st.header("Quick Practice")

    multiselect_problems = st.multiselect(
        "Choose question type(s)", ["Addition", "Line Slope", "Quadratic"]
    )
    multiselect_total = st.number_input("Choose the total amount of problems.", step=1)

    multichoice = st.checkbox(
        "Multiple Choice Questions",
    )

    if st.button("Submit", key=get_next_st_key()):
        problems = []

        excess = multiselect_total % len(multiselect_problems)
        rate = multiselect_total // len(multiselect_problems)

        problemdict = {
            "Addition": SimpleAdditionProblem,
            "Line Slope": LineSlopeProblem,
            "Quadratic": QuadraticProblem,
        }

        excessadded = False
        for problem in multiselect_problems:
            if not excessadded:
                factor = rate + excess
            else:
                factor = rate
            for _ in range(factor):
                problems.append(problemdict[problem]())

        return problems


def gen_by_problem():
    st.header("By Problem")

    problemdict = {
            SimpleAdditionProblem: 0,
            LineSlopeProblem: 0,
            QuadraticProblem: 0,
        }

    problemdict[SimpleAdditionProblem] = st.number_input("Addition Problems", step=1)
    problemdict[LineSlopeProblem] = st.number_input("Line Slope Problems", step=1)
    problemdict[QuadraticProblem] = st.number_input("Quadratic Problems", step=1)

    

    multichoice = st.checkbox(
        "Multiple Choice Questions", key = get_next_st_key()
    )

    if st.button("Submit", key=get_next_st_key()):
        problems = []
        for problem in problemdict:
            for i in range(problemdict[problem]):
                problems.append(problem())
    
        return problems

        


TABS = [
    ["Random", gen_random_problem_set],
    ["By Problem", gen_by_problem],
    ["Quick Practice", gen_quick_practice],
]


def submit(problems):
    print("SUBMITTING PROBLEMS")
    print(user_data)
    for problem in problems:
        user_data.total_problems += 1
        if problem.check_answer():
            print("Correct Answer")
            user_data.correct_problems += 1
    print(user_data)


if "multichoice" not in st.session_state:
    st.session_state['multichoice'] = False

if "problems" not in st.session_state:
    tab_containers = st.tabs([name for name, _ in TABS])

    for container, (_, tab_function) in zip(tab_containers, TABS):
        with container:
            problems= tab_function()
            if problems is not None:
                st.session_state["problems"] = problems
                st.rerun()

else:
    for p in st.session_state["problems"]:
        p.render()
        p.get_answer(False)

    if st.button("Submit"):
        submit(st.session_state["problems"])
        del st.session_state["problems"]

        with open("data.json", "w") as f:
            user_data_dict = dataclasses.asdict(user_data)
            user_data_dict = json.dump(user_data_dict, f)

        st.rerun()
        


