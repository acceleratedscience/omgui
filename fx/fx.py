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


def sample_line(count=10):
    """
    Generate sample data for a line chart
    """
    datasets = []

    for i in range(0, count):
        x = []
        y = []
        name = names[i]
        _date = datetime.now()
        _y = 100
        for _ in range(0, 30):
            _y += (random.randint(0, 100) - 50) * (random.randint(0, 100) - 50)
            x.append(_date.strftime("%Y-%m-%d"))
            y.append(_y)
            _date += timedelta(days=1)
        datasets.append({"x": x, "y": y, "name": name})

    return datasets


def sample_scatter(count=10):
    """
    Generate sample data for a scatter plot chart
    """
    datasets = []

    for i in range(0, count):
        x = []
        y = []
        name = names[i]
        for i in range(0, 30):
            x.append(
                (random.randint(0, 100))
                * (random.randint(0, 100))
                * (random.randint(0, 100))
            )
            y.append(random.randint(1, 100))
        datasets.append({"x": x, "y": y, "name": name})

    return datasets


def sample_bubble(count=10):
    """
    Generate sample data for a bubble plot chart
    """
    datasets = []

    for i in range(0, count):
        x = []
        y = []
        size = []
        name = names[i]
        for _ in range(0, 30):
            x.append(random.randint(0, 100) - 50)
            y.append(random.randint(1, 100) - 50)
            size.append(
                (random.randint(0, 10) * random.randint(0, 10) * random.randint(0, 10))
                / 10
            )
        datasets.append({"x": x, "y": y, "size": size, "name": name})

    return datasets


def sample_pie(count=5):
    """
    Generate sample data for a pie plot chart
    """
    values = []
    labels = []

    for i in range(0, count):
        values.append(random.randint(0, 100))
        labels.append(names[i])

    datasets = [{"values": values, "labels": labels}]

    return datasets


def sample_bar(count=5, groups=3):
    """
    Generate sample data for a bar plot chart
    """
    datasets = []
    key_options = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    for i in range(0, count):
        trace = {"keys": [], "values": [], "name": names[i]}
        for j in range(0, groups):
            trace["keys"].append(key_options[j])
            trace["values"].append(random.randint(0, 100))
        datasets.append(trace)

    return datasets


def sample_boxplot(count=4, group=True):
    """
    Generate sample data for a box plot chart.
    """
    datasets = []
    datapoints = 10

    for i in range(0, count):
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


def sample_histogram(count=2, bins=20):
    """
    Generate sample data for a histogram chart
    """
    datasets = []

    for i in range(0, count):
        trace = {"values": [], "name": names[i]}
        for _ in range(0, 100):
            trace["values"].append(random.gauss(mu=0, sigma=10))
        datasets.append(trace)

    return datasets
