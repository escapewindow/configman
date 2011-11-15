import unittest
import ConfigParser
import os
import tempfile
from cStringIO import StringIO
import contextlib

import configman.datetime_util as dtu
import configman.config_manager as config_manager
from ..value_sources.for_configparse import ValueSource


def stringIO_context_wrapper(a_stringIO_instance):
    @contextlib.contextmanager
    def stringIS_context_manager(dummy1, dummy2):
        yield a_stringIO_instance
    return stringIS_context_manager

class TestCase(unittest.TestCase):
    def _some_namespaces(self):
        """set up some namespaces"""
        n = config_manager.Namespace(doc='top')
        n.add_option('aaa', '2011-05-04T15:10:00','the a',
          short_form='a',
          from_string_converter=dtu.datetime_from_ISO_string
        )
        n.c = config_manager.Namespace(doc='c space')
        n.c.add_option('fred', 'stupid', 'husband from Flintstones')
        n.c.add_option('wilma', 'waspish', 'wife from Flintstones')
        n.d = config_manager.Namespace(doc='d space')
        n.d.add_option('fred', 'crabby', 'male neighbor from I Love Lucy')
        n.d.add_option('ethel', 'silly', 'female neighbor from I Love Lucy')
        n.x = config_manager.Namespace(doc='x space')
        n.x.add_option('size', 100, 'how big in tons', short_form='s')
        n.x.add_option('password', 'secret', 'the password')
        return n

    def test_for_configparse_basics(self):
        """test basic use of for_configparse"""
        tmp_filename = os.path.join(tempfile.gettempdir(), 'test.ini')
        open(tmp_filename, 'w').write("""
; comment
[top_level]
name=Peter
awesome:
; comment
[othersection]
foo=bar  ; other comment
        """)

        try:
            o = ValueSource(tmp_filename)
            v = o.get_values(None, None)
            r = {'othersection.foo': 'bar',
                 'name': 'Peter',
                 'awesome': ''}
            # in the case of this implementation of a ValueSource,
            # the two parameters to get_values are dummies.  That may
            # not be true for all ValueSource implementations
            self.assertEqual(o.get_values(0, False), r)
            self.assertEqual(o.get_values(1, True), r)
            self.assertEqual(o.get_values(2, False), r)
            self.assertEqual(o.get_values(3, True), r)

            # XXX (peterbe): commented out because I'm not sure if
            # OptionsByIniFile get_values() should depend on the configuration
            # manager it is given as first argument or not.
            #c = config_manager.ConfigurationManager([],
                                        #manager_controls=False,
                                        ##use_config_files=False,
                                        #auto_help=False,
                                        #argv_source=[])
            #self.assertEqual(o.get_values(c, True), {})
            #self.assertRaises(config_manager.NotAnOptionError,
            #                  o.get_values, c, False)

            #c.option_definitions.add_option('limit', default=0)
            #self.assertEqual(o.get_values(c, False), {'limit': '20'})
            #self.assertEqual(o.get_values(c, True), {'limit': '20'})
        finally:
            if os.path.isfile(tmp_filename):
                os.remove(tmp_filename)


    def test_for_configparse_basics_2(self):
        tmp_filename = os.path.join(tempfile.gettempdir(), 'test.ini')
        open(tmp_filename, 'w').write("""
; comment
[top_level]
name=Peter
awesome:
; comment
[othersection]
foo=bar  ; other comment
        """)

        try:
            o = ValueSource(tmp_filename)
            c = config_manager.ConfigurationManager([],
                                        manager_controls=False,
                                        #use_config_files=False,
                                        use_auto_help=False,
                                        argv_source=[])

            self.assertEqual(o.get_values(c, False),
                             {'othersection.foo': 'bar',
                              'name': 'Peter',
                              'awesome': ''})
            self.assertEqual(o.get_values(c, True),
                             {'othersection.foo': 'bar',
                              'name': 'Peter',
                              'awesome': ''})
        finally:
            if os.path.isfile(tmp_filename):
                os.remove(tmp_filename)

    def test_write_ini(self):
        n = self._some_namespaces()
        c = config_manager.ConfigurationManager(
          [n],
          manager_controls=False,
          #use_config_files=False,
          use_auto_help=False,
          argv_source=[]
        )
        expected = """[top_level]
# name: aaa
# doc: the a
# converter: configman.datetime_util.datetime_from_ISO_string
aaa=2011-05-04T15:10:00

[c]
# c space

# name: c.fred
# doc: husband from Flintstones
# converter: str
fred=stupid

# name: c.wilma
# doc: wife from Flintstones
# converter: str
wilma=waspish

[d]
# d space

# name: d.ethel
# doc: female neighbor from I Love Lucy
# converter: str
ethel=silly

# name: d.fred
# doc: male neighbor from I Love Lucy
# converter: str
fred=crabby

[x]
# x space

# name: x.password
# doc: the password
# converter: str
password=secret

# name: x.size
# doc: how big in tons
# converter: int
size=100
"""
        out = StringIO()
        c.write_config('ini', opener=stringIO_context_wrapper(out))
        received = out.getvalue()
        out.close()
        self.assertEqual(expected.strip(), received.strip())
