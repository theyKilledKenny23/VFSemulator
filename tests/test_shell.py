import unittest
import shlex


class TestParser(unittest.TestCase):
    """Тесты парсера аргументов."""

    def test_simple_args(self):
        self.assertEqual(shlex.split("ls a b"), ["ls", "a", "b"])

    def test_quoted_arg(self):
        self.assertEqual(
            shlex.split('ls "my folder" file.txt'),
            ["ls", "my folder", "file.txt"],
        )

    def test_single_quotes(self):
        self.assertEqual(
            shlex.split("cd 'home user'"),
            ["cd", "home user"],
        )

    def test_empty_input(self):
        self.assertEqual(shlex.split(""), [])

    def test_invalid_quotes(self):
        with self.assertRaises(ValueError):
            shlex.split('ls "unclosed')


class TestCommandDispatch(unittest.TestCase):
    """Тесты диспетчера команд."""

    def setUp(self):
        self.commands = {"ls", "cd", "help", "exit"}

    def test_known_command(self):
        self.assertIn("ls", self.commands)

    def test_unknown_command(self):
        self.assertNotIn("foo", self.commands)


if __name__ == "__main__":
    unittest.main()