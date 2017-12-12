from scripts.util import parser


def test_skip_blank_lines1():
    input = ["a", "b", "", " "]
    output = parser.skip_blank_lines(input)
    assert input == output


def test_skip_blank_lines2():
    expected = [" a", "b", "", " "]
    input = [" ", "\t", "\n"] + expected
    output = parser.skip_blank_lines(input)
    assert expected == output


def test_skip_blank_lines3():
    assert parser.skip_blank_lines([]) == []


def test_skip_blank_lines4():
    assert parser.skip_blank_lines(["", "# Comment", "   \t   # Another", "x"]) == ["x"]


def test_read_tabbed1():
    assert parser.read_tabbed([]) == ([], [])


def test_read_tabbed2():
    assert parser.read_tabbed(["a", "b"]) == ([], ["a", "b"])


def test_read_tabbed3():
    assert parser.read_tabbed(["\t1", "\t\t2", "a", "b", "\tc"]) == (["1", "2"], ["a", "b", "\tc"])


def test_read_until_blank1():
    assert parser.read_until_blank([]) == ([], [])


def test_read_until_blank2():
    assert parser.read_until_blank([" "]) == ([], [" "])


def test_read_until_blank3():
    assert parser.read_until_blank(["a"]) == (["a"], [])


def test_read_until_blank4():
    assert parser.read_until_blank(["a", "b", "\t", "c"]) == (["a", "b"], ["\t", "c"])



def test_parse_listing1():
    assert parser.parse_listing([]) == {}


def test_parse_listing2():
    assert parser.parse_listing(["", "a: b", "", "c: d"]) == {"a": "b", "c": "d"}


def test_parse_listing3():
    input = "#\n" + \
            "# Use 'p4 help client' to see more about client views and options.\n" + \
            "\n" + \
            "Client:	dusan.jakub_dusan-devbox2_--n-central-PSA-NPSA-1750-XML\n" + \
            "\n" + \
            "Update:	2017/11/07 07:55:29\n" + \
            "\n" + \
            "Access:	2017/12/11 05:58:02\n" + \
            "\n" + \
            "Owner:	dusan.jakub\n" + \
            "\n" + \
            "Host:	dusan-devbox2\n" + \
            "#Skipped: true\n" + \
            "\n" + \
            "# Skipped2:\n" + \
            "\n" + \
            "Description:\n" + \
            "\tCreated by PP4 on behalf of dusan.jakub.\n" + \
            "\tThis the next line."

    result = parser.parse_listing(input.split("\n"))
    assert result["Client"] == "dusan.jakub_dusan-devbox2_--n-central-PSA-NPSA-1750-XML"
    assert result["Update"] == "2017/11/07 07:55:29"
    assert result["Access"] == "2017/12/11 05:58:02"
    assert result["Owner"] == "dusan.jakub"
    assert result["Description"] == "Created by PP4 on behalf of dusan.jakub.\nThis the next line."
    assert "#Skipped" not in result
