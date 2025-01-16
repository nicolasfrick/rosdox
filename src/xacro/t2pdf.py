#!/usr/bin/env python

""" 
Code modified from https://github.com/jeroenjanssens/tikz2pdf.git.

Copyright (c) 2013, Jeroen Janssens
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

  Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

  Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import os
import re
import sys
import shutil
import logging
import argparse
import subprocess

from time import sleep
from tempfile import mkdtemp

class TikZ2PDF(object):

    def __init__(self, tikz_file, pdf_filename, **command_line_arguments):

        self.log = logging.getLogger('tikz2pdf')
        self.log.setLevel(logging.INFO)
        if command_line_arguments.get("debug"):
            self.log.setLevel(logging.DEBUG)

        self.environ = os.environ.copy()
        self.existing_texinputs = self.environ.get("TEXINPUTS", "")

        self.argument_pattern = re.compile(r"^ *% *tikz2pdf-([^=$ ]*) *=? *(.*)")

        self.tikz_file = tikz_file
        self.pdf_filename = pdf_filename
        self.tikz_filename = os.path.abspath(tikz_file.name)
        self.tikz_dir = os.path.abspath(os.path.dirname(tikz_file.name))
        self.work_dir = mkdtemp(prefix="tikz2pdf-")
        self.template_dir = None
        self.tex_filename = os.path.join(self.work_dir, "final.tex")
        self.log.info("Processing TikZ file: %s", self.tikz_filename)

        if command_line_arguments.get("edit"):
            self.open_tikz_editor()
        self.process(**command_line_arguments)
        if command_line_arguments.get("view"):
            self.open_pdf_viewer()
        if self.arguments.get("watch"):
            self.previous_mtimes = self.get_mtimes()
            try:
                while True:
                    self.wait_for_changes()
                    self.process(**command_line_arguments)
            except KeyboardInterrupt:
                pass

        # Delete temporary directory
        shutil.rmtree(self.work_dir)

        # Close files
        self.tikz_file.close()
        try:
            self.arguments["template"].close()
        except KeyError:
            pass


    def wait_for_changes(self):
        self.log.info("Waiting for changes...")
        while True:
            current_mtimes = self.get_mtimes()
            if set(current_mtimes.items()) - set(self.previous_mtimes.items()):
                self.previous_mtimes = current_mtimes
                break
            sleep(0.1)


    def get_mtimes(self):
        files = [self.tikz_filename]
        if self.arguments.get("template"):
            files.append(os.path.abspath(self.arguments["template"].name))
        return {f: os.path.getmtime(f) for f in files}

    def process(self, **command_line_arguments):
        self.arguments = self.get_arguments(**command_line_arguments)
        for k, v in self.arguments.items():
            self.log.debug("Parameter '%s' is set to '%s'", k, v)

        tikz_tex = self.get_tikz().decode("utf-8")
        if r"\documentclass" in tikz_tex:
            final_tex = tikz_tex
        else:
            # Load template
            template_tex = self.get_template()
            final_tex = template_tex.replace("%tikz2pdf-tikz", tikz_tex)

        with open(self.tex_filename, mode="w", encoding="utf-8") as f:
            f.write(final_tex)
        self.set_texinputs()
        self.compile()


    def set_texinputs(self):
        new_texinputs = self.existing_texinputs.split(":")
        new_texinputs.append(os.getcwd())
        new_texinputs.append(self.tikz_dir)
        if self.template_dir:
            new_texinputs.append(self.template_dir)
        new_texinputs.append(".")
        new_texinputs.extend(
            [
                os.path.abspath(os.path.expanduser(x))
                for x in self.arguments.get("include_directory", [])
            ]
        )
        self.environ["TEXINPUTS"] = os.pathsep.join(new_texinputs)
        self.log.debug("$TEXINPUTS is set to '%s'", self.environ["TEXINPUTS"])

    def get_template(self):
        if self.arguments.get("template"):
            template_filename = self.arguments["template"].name
            self.template_dir = os.path.abspath(os.path.dirname(template_filename))
            self.log.debug("Reading template from %s ", os.path.abspath(template_filename))
            self.arguments["template"].close()
            self.arguments["template"] = open(template_filename, "r", encoding="utf-8")
            template_tex = self.arguments["template"].read()
            if "%tikz2pdf-tikz" not in template_tex:
                self.log.error("Error: Template does not contain '%tikz2pdf-tikz'")
                shutil.rmtree(self.work_dir)
                sys.exit(1)
        else:
            template_tex = r"""\documentclass{article}
\usepackage{tikz}
\pagestyle{empty}
\usepackage[active,tightpage]{preview}
\PreviewEnvironment[]{tikzpicture}
\PreviewEnvironment[]{tabular}
\begin{document}
%tikz2pdf-tikz
\end{document}
"""
            self.log.debug("Using default template")
        return template_tex


    def get_tikz(self):
        self.tikz_file.close()
        self.tikz_file = open(self.tikz_filename, "rb")
        return self.tikz_file.read()


    def compile(self):
        for i in range(self.arguments["number"]):
            self.log.info("Compiling (%d/%d) ...", i + 1, self.arguments["number"])
            if self.arguments["quiet"]:
                p = subprocess.Popen(
                    [self.arguments["bin"], "-halt-on-error", "final.tex"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.work_dir,
                    env=self.environ,
                )
            else:
                p = subprocess.Popen(
                    [self.arguments["bin"], "-halt-on-error", "final.tex"],
                    cwd=self.work_dir,
                    env=self.environ,
                )
            return_code = p.wait()
            if return_code:
                self.log.error("Error: %s failed to compile.", self.arguments["bin"])
                stdout, _ = p.communicate()
                print("\n".join(stdout.decode("utf-8").splitlines()[-10:]))
                return

        subprocess.call(["cp", os.path.join(self.work_dir, "final.pdf"), self.pdf_filename])
        self.log.info("Figure written on %s", self.pdf_filename)

    
    def get_arguments(self, **command_line_arguments):
        # Custom argument parser
        parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
        parser.add_argument("--bin", type=str)
        parser.add_argument("--include-directory", action="append")
        parser.add_argument("--number", type=int)
        parser.add_argument("--output", type=str)
        parser.add_argument("--template", type=argparse.FileType("r", encoding="utf-8"))
        parser.add_argument("--xelatex", action="store_const", const="xelatex", dest="bin")
        parser.add_argument("--pdflatex", action="store_const", const="pdflatex", dest="bin")
        parser.add_argument("--preview", action="store_true")
        self.parser = parser

        # Files to look for parameters
        configs = [
            os.path.expanduser("~/.tikz2pdf"),
            os.path.join(self.tikz_dir, ".tikz2pdf"),
            os.path.join(os.getcwd(), ".tikz2pdf"),
            self.tikz_filename,
        ]

        arguments = {}
        for config in configs:
            if os.path.isfile(config):
                with open(config, "r", encoding="utf-8") as f:
                    arguments.update(self.read_arguments_from_file(f))
            else:
                self.log.debug("File %s not found", config)

        # Command-line arguments have the highest priority
        self.log.debug("Reading parameters from command line")
        arguments.update(command_line_arguments)
        arguments["number"] = arguments.get("number", 1)
        arguments["bin"] = arguments.get("bin", "pdflatex")
        return arguments


    def read_arguments_from_file(self, f):
        self.log.debug("Reading parameters from file %s", os.path.abspath(f.name))
        arguments = []
        for line in f:
            match = re.search(self.argument_pattern, line)
            if match:
                arg, value = map(str.strip, match.groups())
                arguments.append(f"--{arg}")
                if value:
                    if arg == "template":
                        value = os.path.expanduser(value)
                        if not os.path.isabs(value):
                            value = os.path.join(os.path.dirname(self.tikz_file.name), value)
                        arguments.append(value)
                    else:
                        arguments.extend(value.split())
        return vars(self.parser.parse_args(arguments))


    def open_tikz_editor(self):
        self.log.info("Opening TikZ editor...")
        subprocess.Popen([self.environ.get("EDITOR", "vi"), self.tikz_filename], stdout=subprocess.PIPE)

    def open_pdf_viewer(self):
        self.log.info("Opening PDF viewer...")
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", self.pdf_filename], stdout=subprocess.PIPE)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.pdf_filename], stdout=subprocess.PIPE)


def t2pdf_main():
    parser = argparse.ArgumentParser(description="tikz2pdf - compile TikZ to PDF", argument_default=argparse.SUPPRESS)
    parser.add_argument('tikz_files', nargs='*', type=argparse.FileType('rb'), default=sys.stdin, help="TikZ file(s)", metavar="TIKZ")
    parser.add_argument('-b', '--bin', type=str, help="binary to use for compiling (default: pdflatex)")
    parser.add_argument('-d', '--debug', action='store_true', default=False, help="print debug information")
    parser.add_argument('-e', '--edit', action='store_true', default=False, help="open TikZ file in default editor")
    parser.add_argument('-i', '--interactive', action='store_true', default=False, help="start interactive session (same as -evw)")
    parser.add_argument('-c', '--include-dir', action='append', help="additional directory to add to TEXINPUTS")
    parser.add_argument('-n', '--number', type=int, help="number of iterations to compile (default: 1)", metavar="N")
    parser.add_argument('-o', '--output', nargs='*', type=str, help="output PDF file or directory (with trailing slash)", metavar="PDF")
    parser.add_argument('-p', '--pdflatex', action='store_const', const='pdflatex', dest='bin', help="use pdflatex as compiler")
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help="suppress compiler output")
    parser.add_argument('-t', '--template', type=argparse.FileType('rb'), help="LaTeX file to use as template", metavar="TEX") 
    parser.add_argument('-v', '--view', action='store_true', default=False, help="open PDF file in default viewer")
    parser.add_argument('-w', '--watch', action='store_true', default=False, help="recompile when TikZ file or template has changed")
    parser.add_argument('-x', '--xelatex', action='store_const', const='xelatex', dest='bin', help="use xelatex as compiler")

    args = vars(parser.parse_args())
    tikz_files = args.pop('tikz_files')
    output = args.pop('output', ['./'])

    if args['interactive']:
        args['edit'] = True
        args['view'] = True
        args['watch'] = True

    if len(output) == 1 and output[0][-1] == os.path.sep:
        d = os.path.abspath(output[0])
        if tikz_files is not sys.stdin:
            pdf_filenames = map(lambda x: os.path.join(d, os.path.splitext(os.path.basename(x.name))[0]) + '.pdf', tikz_files)
        else:
            pdf_filenames = ['out.pdf']
    elif len(output) != len(tikz_files):
        logging.log.error("Error: Number of output files does not match number of input files. Consider specifying a directory with a trailing slash")
        exit(1)
    else:
        d = os.path.curdir
        pdf_filenames = map(lambda x: os.path.abspath(os.path.join(d, x)), output)

    log_format = "tikz2pdf: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)

    for tikz_file, pdf_filename in zip(tikz_files, pdf_filenames):
        TikZ2PDF(tikz_file, pdf_filename, **args)


if __name__ == '__main__':
    exit(t2pdf_main())
