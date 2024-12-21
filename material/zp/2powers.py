"""
This module prints the first 20 powers of 2 into the console in markdown table format.
"""

def get_powers(base, n):
    """
    This function returns the first n powers of base.

    :param base: The base of the powers.
    :type base: int
    :param n: The number of powers to return.
    :type n: int
    :return: A list containing the first n powers of base.
    :rtype: list
    """

    res = []
    for i in range(n):
        res.append(pow(base, i))

    return res


def generate_table(powers):
    """
    This function generates a markdown table containing the powers of 2.

    :param powers: The list of powers of 2.
    :type powers: list
    :return: The markdown table.
    :rtype: str
    """

    # format should be like this:
    # |0-10|11-20|
    # |--|--|
    # |<table> <tr><th>Power</th><th>Value</th></tr><tr><td>2<sup><b>0</b></sup></td><td>1</td></tr> ... </table>| <table> ...

    text = "# Powers of 2\n\n"
    text += "|0-10|11-20|\n"
    text += "|--|--|\n"
    text += "|<table> <tr><th>Power</th><th>Value</th></tr>"
    for i in range(10):
        text += f"<tr><td>2<sup><b>{i}</b></sup></td><td>{powers[i]}</td></tr>"

    text += "</table>|<table> <tr><th>Power</th><th>Value</th></tr>"
    for i in range(10, 20):
        text += f"<tr><td>2<sup><b>{i}</b></sup></td><td>{powers[i]}</td></tr>"
    text += "</table>|\n"

    return text

def main():
    powers = get_powers(2, 20)
    text = generate_table(powers)
    print(text)
    with open("2powers.md", "w") as f:
        f.write(text)

if __name__ == "__main__":
    main()