import os
import re
import xml.dom.minicompat
import xml.dom.minidom
from typing import Any
from .tex_strings import *

class XTree():
    def __init__(self) -> None:
        self.nodes = {}

    def appendNode(self, name: str, children: list) -> None:
        self.nodes.update( {name: children} )

class XTex():
    def __init__(self,
                            name: str,
                            filepath: str,
                            escape_seq: str="\_",
                            test_fmt: bool=False,
                            ) -> None:
        
        self.name = name
        self.filepath = None if filepath is None else os.path.join(filepath, name)
        self.tex = f"% Latex Documentation for {name}\n\n"
        self.escape_seq = escape_seq
        # self.cwd = os.getcwd()

        if test_fmt:
            self.testFmt()
            exit(0)

        # print(self.buildTree(None))

    def testFmt(self) -> None:
        print("PAGEREF", PAGEREF.format("testref"), "\n")
        print("HYPERTARGET", HYPERTARGET.format("testref", "teststr"), "\n")
        print("HYPERLINK", HYPERLINK.format("testref", "teststr"), "\n")
        print("MBOX_HYPERLINK", MBOX_HYPERLINK.format("testref", "teststr"), "\n")
        print("DOXY_SEC", DOXY_SEC.format("teststr", "testref"), "\n")
        print("DOXY_SUBSEC", DOXY_SUBSEC.format("teststr", "testref", "testtext"), "\n")
        print("DOXY_SUBSUBSEC", DOXY_SUBSUBSEC.format("teststr", "testref", "testtext"), "\n")
        print("DOXY_CLIST", DOXY_CLIST.format(DOXY_CLIST_ENTRY.format("teststr", "testref", "testtext")), "\n")
        print("DOXY_CLIST_HYPER_ENTRY", DOXY_CLIST_HYPER_ENTRY.format("hyperlink", "hypertext", "page", "testext"), "\n")
        print("DOXY_CITEMIZE", DOXY_CITEMIZE.format("testitem"), "\n")
        print("DOXY_CITEMIZE_CLIST", DOXY_CITEMIZE_CLIST.format("testitem", "testentry"), "\n")
        citemize_clists_str = ""
        for i in range(3):
            citemize_clists_str += DOXY_CITEMIZE_CLIST.format(f"testitem_{i}", f"testentry_{i}")
        print("DOXY_CITEMIZE_MULTI\n", DOXY_CITEMIZE.format(citemize_clists_str), "\n")

    def buildTree(self, link) -> str:
        tree = ["digraph G {\n"]
        tree += ["node [shape=box];\n"]
        self.addChildLinkNames(tree, link)

        # tree += ["node [shape=ellipse, color=blue, fontcolor=blue];\n"]
        # addChildJointNames(tree, link)

        tree += ["}\n"]

        return "".join(tree)
    
    def addChildLinkNames(self, tree: list, link) -> None:
        tree += [f"\"{link.name}\" [label=\"link.name\"];\n"]
        for child in link.children:
            self.addChildLinkNames(child, tree, link)

    def name2Ref(self, name: str) -> str:
        return self.name + "__" + name
    
    def removePath(self, pth: str, pattern: str) -> str:
        return pth.replace(pattern+"/", "")
    
    def escapeUnderscore(self, input_str: str) -> str:
        return input_str.replace("_", self.escape_seq)
    
    def escapeDollar(self, input_str: str) -> str:
        return input_str.replace("$", "\$")
    
    def escapeHash(self, input_str: str) -> str:
        return input_str.replace("#", "\#")
    
    def escapeBrackets(self, input_str: str) -> str:
        out = input_str.replace("[", "'")
        out = out.replace("]", "'")

        return out
    
    def rmWhiteSpace(self, input_str: str) -> str:
        out = re.sub(r' {2,}', ' ', input_str)
        return out

    def escapeAll(self, input_str: str) -> str:
        esc = self.escapeBrackets(input_str)
        esc = self.escapeDollar(esc)
        esc = self.escapeUnderscore(esc)
        esc = self.escapeHash(esc)
        esc = self.rmWhiteSpace(esc)
        return esc

    def newpage(self) -> None:
        self.tex +=  NEWPAGE

    def newline(self) -> None:
        self.tex += NEWLINE

    def hypertarget(self, target: str, name: str="") -> None:
        self.tex += HYPERTARGET.format(self.name2Ref(target), self.escapeAll(name))

    def section(self, name: str, label: str) -> None:
        self.tex += DOXY_SEC.format(self.escapeAll(name), label)

    def subsection(self, name: str, label: str, text: str) -> None:
        self.tex += DOXY_SUBSEC.format(self.escapeAll(name), label, self.escapeAll(text))

    def subsubsection(self, name: str, label: str, text: str) -> None:
        self.tex += DOXY_SUBSUBSEC.format(self.escapeAll(name), label, self.escapeAll(text))

    def clist(self, text: str) -> str:
        self.tex += DOXY_CLIST.format(text)

    def citem(self, title: str, text: str) -> str:
        self.tex += DOXY_CITEMIZE.format(title, text)

    def clistHyperEntry(self, link_target: str, hlink_text: str, text: str="") -> str:
        return DOXY_CLIST_HYPER_ENTRY.format(self.name2Ref(link_target), self.escapeAll(hlink_text), link_target, self.escapeAll(text))
    
    def clistEntry(self, name: str, value: str, text: str) -> str:
        return DOXY_CLIST_ENTRY.format(self.escapeAll(name), self.escapeAll(value), self.escapeAll(text))
    
    def citemVarEntry(self, name: str, value: str, text: str) -> str:
        return DOXY_CITEMIZE_CLIST.format(f"\\textbf{{{self.escapeAll(name)}}}"+":" , self.escapeAll(value), self.escapeAll(text))
    
    def citemParEntry(self, name: str, value: str) -> str:
        return DOXY_CITEMIZE_CLIST.format(f"\\textbf{{{self.escapeAll(name)}}}" , "", self.escapeAll(value))

    def save(self) -> str:
        if self.filepath is None:
            return self.tex  # to string
        
        with open(self.filepath + '.tex', 'w') as fw:
            fw.write(self.tex) # to file
        return f'Tex saved to {self.filepath}.tex'

class XDox():
    DOC = 'doc'
    FILENAME = 'fn'
    PKGNAME = 'pkg'

    def __init__(self) -> None:
        pass

    def init(self,
                    outpth: str,
                    rm_pattern: str,
                    input_filename: str,
                    rm_file_part: str = os.getcwd(),
                    ) -> None:
        
        self.name = 'xacro_latex_doc'
        # set doc directory 
        self.doc_dir = None if outpth is None else os.path.dirname(outpth) if '.' in os.path.basename(outpth) else outpth

        self.docs = {}
        self.args_documented = {}
        self.rm_pattern = rm_pattern if rm_pattern is not None else ''
        self.tex = XTex(self.name, self.doc_dir)
        self.tree = XTree()
        self.launchfile = self.isLaunchfile(input_filename)
        self.doc_type = 'launch' if self.launchfile else 'urdf'
        self.rm_file_part = rm_file_part

        print("Creating latex documentation for", "launchfiles" if self.launchfile else "xacro", "in", self.doc_dir if self.doc_dir is not None else 'stdout')

        # reset path for xacro output
        return None if outpth is None else None if not '.' in os.path.basename(outpth) else outpth

    def isLaunchfile(self, filename: str) -> bool:
        return '.launch' in filename

    def addDoc(self, name: str, filename: str, doc: xml.dom.minidom.Document) -> None:
        if self.rm_pattern not in filename: # ignore
            print(f"Adding documentation for {self.doc_type} file: ", name)
            pkg_name = filename.replace('/launch', '')
            pkg_name = pkg_name.split("/")[-1]
            self.docs.update( {name: {self.DOC: doc, self.FILENAME: filename, self.PKGNAME: pkg_name}} )

    def fileList(self, files: dict) -> None:
        self.tex.newpage()
        self.tex.section("File Index", f"sw:{self.name}_file_index")
        self.tex.subsection("File List", f"sw::{self.name}_file_list", "Here is a list of all files:")
        lststr = "".join( [self.tex.clistHyperEntry(f"sw:{self.name}__{name}_file_{self.doc_type}_doc", self.tex.removePath(f, self.rm_file_part)) for name, f in files.items()] )
        self.tex.clist(lststr)

    def genDoc(self) -> None:
        # gen file list
        self.fileList( {name: dct[self.FILENAME] for name, dct in self.docs.items()} )
        self.tex.newpage()
        self.tex.section("Launchfiles Documentation", f"sw:{self.name}__file_doc")

        # gen content per directory
        last_dir = ''
        for name, dct in self.docs.items():
            print("Generating latex documentation for", name)

            file_dir = os.path.dirname(dct[self.FILENAME])
            if file_dir != last_dir:
                # new directory
                if last_dir != '':
                    self.tex.newpage()
                self.tex.hypertarget(dct[self.PKGNAME])
                self.tex.subsection(name + " Package", f"sw:{self.name}__{dct[self.PKGNAME]}_pkg_{self.doc_type}_doc", "")
                last_dir = file_dir 
            
            # extract content
            self._procDoc(name, dct)

    def _procDoc(self, name: str, dct: dict) -> None:        
        doc = dct[self.DOC]
        lib: xml.dom.minidom.Element = doc.documentElement
        self.tex.subsubsection("File " + name, f"sw:{self.name}__{name}_file_{self.doc_type}_doc", "")

        # print(lib.toprettyxml())

        # self._procArgs(lib)
        # self.tex.newpage()
        # self._procParams(lib)
        # self.tex.newpage()
        # self._procGroups(lib)
        # self.tex.newpage()
        # self._procText(lib)
        # self.tex.newpage()
        # self._procComment(lib)
        # self.tex.newpage()
        # self._procIncludes(lib)
        # self.tex.newpage()

    def _procIncludes(self, lib: xml.dom.minidom.Element) -> None:
        include_list = ""
        includes = lib.getElementsByTagName("include")
        if len(includes) == 0:
            return 
        
        for i in includes:
            print(i.getAttribute("if"))
            print(i.hasChildNodes())

            exit(0)

    def _procGroups(self, lib: xml.dom.minidom.Element) -> None:
        group_list = ""
        groups = lib.getElementsByTagName("group")
        if len(groups) == 0:
            return 
        
        for g in groups:
            print(g.toprettyxml())

    def _procText(self, lib: xml.dom.minidom.Element) -> None:
        text_list = ""
        texts = lib.getElementsByTagName("#text")
        if len(texts) == 0:
            return 
        
        for t in texts:
            print(t.toprettyxml())

    def _procComment(self, lib: xml.dom.minidom.Element) -> None:
        com_list = ""
        comments = lib.getElementsByTagName("#comment")
        if len(comments) == 0:
            return 
        
        for c in comments:
            print(c.toprettyxml())

    def _procArgs(self, lib: xml.dom.minidom.Element) -> None:
        args_list = ""
        args = lib.getElementsByTagName("arg")
        if len(args) == 0:
            return 
        
        for a in args:
            n = a.getAttribute("name") if a.hasAttribute("name") else "?"
            v = a.getAttribute("value") if a.hasAttribute("value") else a.getAttribute("default") if a.hasAttribute("default") else "n/a"
            d = a.getAttribute("doc") if a.hasAttribute("doc") else "n/a"
            args_list += self.tex.citemVarEntry(n, v ,d)

        if "\item" in args_list:
            self.tex.citem("Args:~~~~~~\small{name}~~~~~~~~~~\small{default}", args_list)

    def _procParams(self, lib: xml.dom.minidom.Element) -> None:
        params_list = ""
        params = lib.getElementsByTagName("param")
        val = 'command'
        if len(params) == 0:
            return 
        
        for p in params:
            n = p.getAttribute("name") if p.hasAttribute("name") else "?"
            if p.hasAttribute("command"):
                c = p.getAttribute("command") 
                c = c.replace(") ", ")\\\\\n \small\item\em ")
            elif p.hasAttribute("value"):
                c = p.getAttribute("value")
                val = 'value'

            params_list += self.tex.citemParEntry(n, c)
            # add line breaks
            self.tex.newline()

        if "\item" in params_list:
            self.tex.citem(f"Params:\\hspace{{2cm}}\small{{name}}\\hspace{{2cm}}\\small{{{val}}}" + ("\\hspace{{2cm}}\\small{{args}}" if val == 'command' else ""), params_list)
            self.tex.newpage()

    def writeDoc(self) -> str:
        return self.tex.save()
