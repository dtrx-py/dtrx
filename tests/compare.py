#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# compare.py -- High-level tests for dtrx.
# Copyright © 2006-2009 Brett Smith <brettcsmith@brettcsmith.org>.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import fcntl
import os
import re
import struct

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

import sys
import tempfile
import termios

import yaml

try:
    set
except NameError:
    from sets import Set as set

if os.path.exists("scripts/dtrx") and os.path.exists("tests"):
    os.chdir("tests")
elif os.path.exists("../scripts/dtrx") and os.path.exists("../tests"):
    pass
else:
    print("ERROR: Can't run tests in this directory!")
    sys.exit(2)

DTRX_SCRIPT = os.path.realpath("../scripts/dtrx")
SHELL_CMD = ["sh", "-se"]
ROOT_DIR = os.path.realpath(os.curdir)
NUM_TESTS = 0


class ExtractorTestError(Exception):
    pass


class StatusWriter(object):
    def __init__(self):
        try:
            size = fcntl.ioctl(
                sys.stdout.fileno(), termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)
            )
        except IOError:
            self.show = self.show_file
        else:
            self.width = struct.unpack("HHHH", size)[1] - 1
            self.last_width = self.width
            self.show = self.show_term

    def show_term(self, message):
        sys.stdout.write(message.ljust(self.last_width) + "\r")
        sys.stdout.flush()
        self.last_width = max(self.width, len(message))

    def show_file(self, message):
        if message:
            print(message)

    def clear(self):
        self.show("")


class ExtractorTest(object):
    status_writer = StatusWriter()

    def __init__(self, **kwargs):
        global NUM_TESTS
        NUM_TESTS += 1
        self.test_num = NUM_TESTS
        setattr(self, "name", kwargs["name"])
        setattr(self, "options", kwargs.get("options", "-n").split())
        setattr(self, "filenames", kwargs.get("filenames", "").split())
        for key in (
            "directory",
            "prerun",
            "posttest",
            "baseline",
            "error",
            "input",
            "output",
            "cleanup",
        ):
            setattr(self, key, kwargs.get(key, None))
        for key in ("grep", "antigrep"):
            value = kwargs.get(key, [])
            if isinstance(value, str):
                value = [value]
            setattr(self, key, value)
        if self.input and (not self.input.endswith("\n")):
            self.input = self.input + "\n"

    def start_proc(self, command, stdin=None, output=None):
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=output, stderr=output
        )
        if stdin:
            process.stdin.write(bytes(str(stdin).encode("utf-8")))
        process.stdin.close()
        return process

    def get_results(self, command, stdin=None):
        print("Output from %s:" % (" ".join(command),), file=self.outbuffer)
        self.outbuffer.flush()
        status = self.start_proc(command, stdin, self.outbuffer).wait(5)
        process = subprocess.Popen(["find"], stdout=subprocess.PIPE)
        output = process.stdout.read(-1).decode("ascii", errors="ignore")
        process.stdout.close()
        process.wait()
        return status, set(output.split("\n"))

    def run_script(self, key):
        commands = getattr(self, key)
        if commands is not None:
            if self.directory:
                directory_hint = "../"
            else:
                directory_hint = ""
            self.start_proc(SHELL_CMD + [directory_hint], commands).wait()

    def get_shell_results(self):
        self.run_script("prerun")
        return self.get_results(SHELL_CMD + self.filenames, self.baseline)

    def get_extractor_results(self):
        self.run_script("prerun")
        return self.get_results(
            [DTRX_SCRIPT] + self.options + self.filenames, self.input
        )

    def get_posttest_result(self):
        if not self.posttest:
            return 0
        return self.start_proc(SHELL_CMD, self.posttest).wait()

    def clean(self):
        self.run_script("cleanup")
        if self.directory:
            target = os.path.join(ROOT_DIR, self.directory)
            extra_options = []
        else:
            target = ROOT_DIR
            extra_options = [
                "(",
                "(",
                "-type",
                "d",
                "!",
                "-name",
                "CVS",
                "!",
                "-name",
                ".svn",
                ")",
                "-or",
                "-name",
                "test-text",
                "-or",
                "-name",
                "test-onefile",
                ")",
            ]
        status = subprocess.call(
            ["find", target, "-mindepth", "1", "-maxdepth", "1"]
            + extra_options
            + ["-exec", "rm", "-rf", "{}", ";"]
        )
        if status != 0:
            raise ExtractorTestError("cleanup exited with status code %s" % (status,))

    def show_pass(self):
        self.status_writer.show(
            "Passed %i/%i: %s" % (self.test_num, NUM_TESTS, self.name)
        )
        return "passed"

    def show_report(self, status, message=None):
        self.status_writer.clear()
        self.outbuffer.seek(0, 0)
        sys.stdout.write(self.outbuffer.read(-1))
        if message is None:
            last_part = ""
        else:
            last_part = ": %s" % (message,)
        print("%s: %s%s\n" % (status, self.name, last_part))
        return status.lower()

    def compare_results(self, actual):
        posttest_result = self.get_posttest_result()
        self.clean()
        status, expected = self.get_shell_results()
        self.clean()
        if expected != actual:
            print("Only in baseline results:", file=self.outbuffer)
            print("\n".join(expected.difference(actual)), file=self.outbuffer)
            print("Only in actual results:", file=self.outbuffer)
            print("\n".join(actual.difference(expected)), file=self.outbuffer)
            return self.show_report("FAILED")
        elif posttest_result != 0:
            print("Posttest gave status code", posttest_result, file=self.outbuffer)
            return self.show_report("FAILED")
        return self.show_pass()

    def have_error_mismatch(self, status):
        if self.error and (status == 0):
            return "dtrx did not return expected error"
        elif (not self.error) and (status != 0):
            return "dtrx returned error code %s" % (status,)
        return None

    def grep_output(self, output):
        for pattern in self.grep:
            if not re.search(pattern.replace(" ", "\\s+"), output, re.MULTILINE):
                return "output did not match %s" % (pattern)
        for pattern in self.antigrep:
            if re.search(pattern.replace(" ", "\\s+"), output, re.MULTILINE):
                return "output matched antigrep %s" % (self.antigrep)
        return None

    def check_output(self, output):
        if (self.output is not None) and (self.output.strip() != output.strip()):
            return "output did not match provided text:\n{}\nVS:\n{}".format(
                repr(self.output), repr(output)
            )
        return None

    def check_results(self):
        self.clean()
        status, actual = self.get_extractor_results()
        self.outbuffer.seek(0, 0)
        self.outbuffer.readline()
        output = self.outbuffer.read(-1)
        problem = (
            self.have_error_mismatch(status)
            or self.check_output(output)
            or self.grep_output(output)
        )
        if problem:
            return self.show_report("FAILED", problem)
        if self.baseline is not None:
            return self.compare_results(actual)
        else:
            self.clean()
            return self.show_pass()

    def run(self):
        self.outbuffer = tempfile.TemporaryFile(mode="w+")
        if self.directory:
            os.mkdir(self.directory)
            os.chdir(self.directory)
        try:
            result = self.check_results()
        except ExtractorTestError as error:
            result = self.show_report("ERROR", error)
        self.outbuffer.close()
        if self.directory:
            os.chdir(ROOT_DIR)
            subprocess.call(["chmod", "-R", "700", self.directory])
            subprocess.call(["rm", "-rf", self.directory])
        return result


class TestsRunner(object):
    outcomes = ["error", "failed", "passed"]

    def __init__(self):
        with open("tests.yml", "rb") as test_db:
            self.test_data = yaml.load(
                test_db.read(-1).decode("utf-8", errors="ignore"),
                Loader=yaml.FullLoader,
            )
        self.name_regexps = [re.compile(s) for s in sys.argv[1:]]
        self.tests = [
            ExtractorTest(**data) for data in self.test_data if self.wanted_test(data)
        ]
        self.add_subdir_tests()

    def wanted_test(self, data):
        if not self.name_regexps:
            return True
        return any([r.search(data["name"]) for r in self.name_regexps])

    def add_subdir_tests(self):
        for odata in self.test_data:
            if (
                (not self.wanted_test(odata))
                or "directory" in odata
                or ("baseline" not in odata)
            ):
                continue
            data = odata.copy()
            data["name"] += " in .."
            data["directory"] = "inside-dir"
            data["filenames"] = " ".join(
                ["../%s" % filename for filename in data.get("filenames", "").split()]
            )
            self.tests.append(ExtractorTest(**data))

    def run(self):
        results = {}
        for outcome in self.outcomes:
            results[outcome] = 0
        for test in self.tests:
            results[test.run()] += 1
        if self.tests:
            self.tests[-1].status_writer.clear()
        print(
            "Totals:",
            ", ".join(["%s %s" % (results[key], key) for key in self.outcomes]),
        )
        return (results["error"] + results["failed"]) == 0


runner = TestsRunner()
if not runner.run():
    sys.exit(1)
