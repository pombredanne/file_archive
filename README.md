file_archive: A file store with searchable metadata

[![Build Status](https://travis-ci.org/remram44/file_archive.png?branch=master)](https://travis-ci.org/remram44/file_archive)
[![Coverage Status](https://coveralls.io/repos/remram44/file_archive/badge.png?branch=master)](https://coveralls.io/r/remram44/file_archive?branch=master)

# Introduction

This is a file archiving system. You submit it files with a set of metadata, as
key-value pairs, and it allows you to later retrieve the files that match
conditions on these metadata.

It uses a flat file-store where files are stored under their 40 characters SHA1
hash, and a SQLite3 database for the metadata.

Its purpose is to be used as a persistent file store for the VisTrails workflow
and provenance management system: http://www.vistrails.org/

# Warning

Note that this project is still alpha and changing fast. The API, command-line
interface and storage format are subject to change between each release.
