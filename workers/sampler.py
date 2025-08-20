# Generator functions to create sample data for various chart types

import random
from datetime import datetime, timedelta

names = [
    "Lion",
    "Tiger",
    "Elephant",
    "Giraffe",
    "Zebra",
    "Panda",
    "Kangaroo",
    "Koala",
    "Monkey",
    "Wolf",
    "Bear",
    "Fox",
    "Deer",
    "Eagle",
    "Owl",
    "Penguin",
    "Dolphin",
    "Whale",
    "Shark",
    "Octopus",
    "Cheetah",
    "Leopard",
    "Hippo",
    "Rhino",
    "Gorilla",
    "Chimpanzee",
    "Flamingo",
    "Crocodile",
    "Kangaroo",
    "Platypus",
]


def line(trace_count=5):
    """
    Generate sample data for a line chart
    """
    datasets = []

    for i in range(0, trace_count):
        trace = {"x": [], "y": [], "name": names[i]}
        _date = datetime.now()
        _y = 100

        for _ in range(0, 30):
            _y += (random.randint(0, 100) - 50) * (random.randint(0, 100) - 50)
            trace["x"].append(_date.strftime("%Y-%m-%d"))
            trace["y"].append(_y)
            _date += timedelta(days=1)

        datasets.append(trace)

    return datasets


def scatter(trace_count=10):
    """
    Generate sample data for a scatter plot chart
    """
    datasets = []

    for i in range(0, trace_count):
        trace = {"x": [], "y": [], "name": names[i]}

        for i in range(0, 30):
            trace["x"].append(
                (random.randint(0, 100))
                * (random.randint(0, 100))
                * (random.randint(0, 100))
            )
            trace["y"].append(random.randint(1, 100))

        datasets.append(trace)

    return datasets


def bubble(trace_count=5):
    """
    Generate sample data for a bubble plot chart
    """
    datasets = []

    for i in range(0, trace_count):
        trace = {"x": [], "y": [], "size": [], "name": names[i]}

        for _ in range(0, 30):
            trace["x"].append(random.randint(0, 100) - 50)
            trace["y"].append(random.randint(1, 100) - 50)
            trace["size"].append(
                (random.randint(0, 10) * random.randint(0, 10) * random.randint(0, 10))
                / 10
            )

        datasets.append(trace)

    return datasets


def pie(slice_count=5):
    """
    Generate sample data for a pie plot chart
    """
    datasets = [{"values": [], "labels": []}]

    for i in range(0, slice_count):
        datasets[0]["values"].append(random.randint(0, 100))
        datasets[0]["labels"].append(names[i])

    return datasets


def bar(trace_count=5, groups=3):
    """
    Generate sample data for a bar plot chart
    """
    datasets = []
    key_options = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    for i in range(0, trace_count):
        trace = {"keys": [], "values": [], "name": names[i]}

        for j in range(0, groups):
            trace["keys"].append(key_options[j])
            trace["values"].append(random.randint(0, 100))

        datasets.append(trace)

    return datasets


def boxplot(trace_count=4, group=False):
    """
    Generate sample data for a box plot chart.
    """
    datasets = []
    datapoints = 10

    for i in range(0, trace_count):
        trace = {"name": names[i], "data": []}

        # Add data points
        for _ in range(0, datapoints):
            trace["data"].append(random.random())

        # Add group for each data point
        if group:
            trace["groups"] = []
            for i in range(0, datapoints):
                trace["groups"].append("Group A" if i <= 5 else "Group B")

        datasets.append(trace)

    return datasets


def histogram(trace_count=2):
    """
    Generate sample data for a histogram chart
    """
    datasets = []
    datapoints = 100

    for i in range(0, trace_count):
        trace = {"values": [], "name": names[i]}
        for _ in range(0, datapoints):
            trace["values"].append(random.gauss(mu=0, sigma=10))
        datasets.append(trace)

    return datasets
