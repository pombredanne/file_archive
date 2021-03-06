from __future__ import division, unicode_literals

import tdparser
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from file_archive.parser import parse_expression, parse_expressions


class TestParser(unittest.TestCase):
    def test_single(self):
        self.assertEqual(parse_expression('key1=-12'),
                         {'key1': {'type': 'int', 'equal': -12}})
        self.assertEqual(parse_expression('key2 = "41"'),
                         {'key2': {'type': 'str', 'equal': '41'}})
        self.assertEqual(parse_expression('key3:int'),
                         {'key3': {'type': 'int'}})
        self.assertEqual(parse_expression('41 < key4'),
                         {'key4': {'type': 'int', 'gt': 41}})
        with self.assertRaises(tdparser.MissingTokensError):
            parse_expression('key4=')
        self.assertEqual(parse_expression('key5 >0'),
                         {'key5': {'type': 'int', 'gt': 0}})
        with self.assertRaises(tdparser.LexerError):
            parse_expression('key6!"somethg')
        with self.assertRaises(tdparser.ParserError):
            parse_expression('"foo" = "bar"')
        with self.assertRaises(tdparser.ParserError):
            parse_expression('key7 = key8')
        with self.assertRaises(tdparser.ParserError):
            parse_expression('"value"')

    def test_strings(self):
        self.assertEqual(parse_expression(r'key1="some string"'),
                         {'key1': {'type': 'str', 'equal': "some string"}})
        self.assertEqual(parse_expression(r'key1="some \"string\""'),
                         {'key1': {'type': 'str', 'equal': 'some "string"'}})
        with self.assertRaises(tdparser.LexerError):
            parse_expression(r'key1="some \"string')
        with self.assertRaises(tdparser.LexerError):
            parse_expression(r'key1="some \"string\"')
        with self.assertRaises(tdparser.LexerError):
            self.assertEqual(parse_expression(r'key1="'), None)

    def test_multi(self):
        self.assertEqual(parse_expression('key1=-12 key2 = "4 2" '
                                          'key3:int 41< key4'),
                         {'key1': {'type': 'int', 'equal': -12},
                          'key2': {'type': 'str', 'equal': '4 2'},
                          'key3': {'type': 'int'},
                          'key4': {'type': 'int', 'gt': 41}})
        self.assertEqual(parse_expression('key1>2  key1<4 '),
                         {'key1': {'type': 'int', 'gt': 2, 'lt': 4}})
        with self.assertRaises(tdparser.ParserError):
            parse_expression('key1="str" key1<2')
        with self.assertRaises(tdparser.ParserError):
            parse_expression('key1="str" key1="otherstr"')

    def test_multi_splitted(self):
        self.assertEqual(parse_expressions(['key1=-12', 'key2 = "4 2"',
                                            'key3:str', '41< key4']),
                         {'key1': {'type': 'int', 'equal': -12},
                          'key2': {'type': 'str', 'equal': '4 2'},
                          'key3': {'type': 'str'},
                          'key4': {'type': 'int', 'gt': 41}})
        self.assertEqual(parse_expressions(['key1>2 ', ' key1<4 ']),
                         {'key1': {'type': 'int', 'gt': 2, 'lt': 4}})
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['key1="str"', 'key1<2'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['key1="str"', 'key1="otherstr"'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['key1="str" key1<2'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['"value"'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['2:str'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['"somevalue":int'])
        with self.assertRaises(tdparser.ParserError):
            parse_expressions(['key1:notatype'])
