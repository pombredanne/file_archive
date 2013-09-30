import contextlib
import os
import shutil
import tempfile

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from file_archive import FileStore
from file_archive.errors import CreationError


@contextlib.contextmanager
def temp_dir(make=True):
    path = tempfile.mkdtemp(prefix='test_file_archive_')
    try:
        if make:
            yield path
        else:
            yield path + 'internal'
    finally:
        shutil.rmtree(path)


class TestCreate(unittest.TestCase):
    """Tests the creation of a new file store on disk.
    """
    def test_create(self):
        with temp_dir(False) as d:
            FileStore.create_store(d)
            self.assertTrue(os.path.isdir(d))
            self.assertTrue(os.path.isfile(os.path.join(d, 'database')))
        with temp_dir(True) as d:
            FileStore.create_store(d)
            self.assertTrue(os.path.isfile(os.path.join(d, 'database')))

    def test_create_nonempty(self):
        with temp_dir() as d:
            with open(os.path.join(d, 'somefile'), 'wb') as fp:
                fp.write("I'm not empty\n")
            with self.assertRaises(CreationError):
                FileStore.create_store(d)
        with temp_dir() as d:
            FileStore.create_store(d)
            with self.assertRaises(CreationError):
                FileStore.create_store(d)


class TestStore(unittest.TestCase):
    """Tests opening the store and using it.
    """
    def setUp(self):
        self.path = tempfile.mkdtemp(prefix='test_file_archive_')
        FileStore.create_store(self.path)
        self.store = FileStore(self.path)
        testfiles = os.path.join(os.path.dirname(__file__), 'testfiles')
        self.t = lambda f: os.path.join(testfiles, f)

    def tearDown(self):
        self.store.close()
        self.store = None
        shutil.rmtree(self.path)

    def test_req_empty(self):
        self.assertEqual(list(self.store.query({})), [])

    def test_putfile(self):
        h1 = self.store.add_file(self.t('file1.bin'), {})
        self.assertEqual(h1, '6edc650f52e26ce867b3765e0563dc3e445cdaa9')
        self.assertTrue(os.path.isfile(os.path.join(
                self.path,
                'objects',
                '6e',
                'dc650f52e26ce867b3765e0563dc3e445cdaa9')))

    def test_put_twice(self):
        self.assertIsNotNone(self.store.add_file(self.t('file1.bin'), {}))
        with self.assertRaises(KeyError):
            self.store.add_file(self.t('file1.bin'), {})

    def test_reqs(self):
        def assert_one(cond, expected):
            entry = self.store.query_one(cond)
            if entry is None:
                self.assertIsNone(expected)
            else:
                self.assertEqual(entry['hash'], expected)
        def assert_many(cond, expected):
            entries = self.store.query(cond)
            hashes = set(entry['hash'] for entry in entries)
            self.assertEqual(hashes, set(expected))

        files = [
                ('file1.bin', {}),
                ('file2.bin', {'a': 'aa', 'c': 12, 'd': 'common'}),
                 ('file3.bin', {'a': 'bb', 'c': 41}),
                 ('file4.bin', {'c': '12', 'd': 'common'}),
            ]

        h = []
        for i, (f, m) in enumerate(files):
            if i % 2 == 0:
                r = self.store.add_file(self.t(f), m)
            else:
                with open(self.t(f), 'rb') as fp:
                    r = self.store.add_file(fp, m)
            h.append(r)

        assert_one({'c': 41}, h[2])
        assert_many({'c': 41}, [h[2]])
        assert_many({'c': '41'}, [])
        assert_one({'c': '41'}, None)
        assert_many({}, h)
        assert_many({'c': '12'}, [h[3]])
        assert_many({'d': 'common'}, [h[1], h[3]])
        assert_many({'a': 'aa', 'c': 12}, [h[1]])
        assert_many({'a': 'bb', 'c': 12}, [])
        assert_many({'a': 'aa', 'c': 5}, [])

        # TODO : range queries

        self.store.remove(h[1])
        assert_many({'a': 'aa'}, [])
        assert_many({'d': 'common'}, [h[3]])
