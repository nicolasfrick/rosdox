import os
import re
import xml.dom.minidom
import xml.dom.minicompat
from .tex_strings import *

class XTree():
    def __init__(self):
        pass

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

        if test_fmt:
            self.testFmt()
            exit(0)

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
    
    def input(self, filepath: str) -> None:
        self.tex += INPUT.format(filepath)

    def save(self) -> str:
        if self.filepath is None:
            return self.tex  + "\n\n" # to string
        
        with open(self.filepath + '.tex', 'w') as fw:
            fw.write(self.tex) # to file
        return f'Tex saved to {self.filepath}.tex\n'

class XDox():
    DOC = 'doc'
    LIB = 'lib'
    TEX = 'tex'
    FILENAME = 'fn'
    PKGNAME = 'pkg'

    def __init__(self) -> None:
        pass

    def init(self,
                    outpth: str,
                    rm_pattern: str,
                    input_filename: str,
                    rm_file_part: str = os.getcwd(),
                    ) -> str:
        
        # set doc directory 
        self.doc_dir = None if outpth is None else os.path.dirname(outpth) if '.' in os.path.basename(outpth) else outpth
        self.name = 'xacro_latex_doc'

        self.rm_pattern = rm_pattern if rm_pattern is not None else ''
        self.launchfile = self.isLaunchfile(input_filename)
        self.doc_type = 'launch' if self.launchfile else 'xacro'
        self.extension = "." + self.doc_type
        self.rm_file_part = rm_file_part
        
        self.title_tex = XTex("Titlepage", self.doc_dir)
        self.root_file = self.getFilename(input_filename)
        self.current_file = self.root_file
        self.docs = {self.root_file: {self.LIB: None, self.TEX: XTex(self.root_file, self.doc_dir), self.FILENAME: self.shortPath(input_filename, self.rm_file_part)}}
        self.args_documented = {}

        print("Creating latex documentation for", "launchfiles" if self.launchfile else "xacro", "in", self.doc_dir if self.doc_dir is not None else 'stdout')

        # reset path for xacro output
        return None if outpth is None else None if not '.' in os.path.basename(outpth) else outpth
    
    def shortPath(self, filepath: str, rm: str) -> str:
        return filepath.replace(rm, "")
    
    def getFilename(self, filepath: str) -> str:
        return os.path.basename(filepath).replace(self.extension, "")

    def isLaunchfile(self, filename: str) -> bool:
        return '.launch' in filename

    def addDoc(self, filepath: str, lib: xml.dom.minidom.Element) -> None:
        if self.rm_pattern not in filepath: # ignore
            name = self.getFilename(filepath)
            print(f"Adding documentation for {self.doc_type} file: ", name)

            if name in self.docs.keys():
                self.docs[name][self.LIB] = lib
            else:
                self.docs.update( {name: {self.LIB: lib, self.TEX: XTex(name, self.doc_dir), self.FILENAME: self.shortPath(filepath, self.rm_file_part)}} )

    def genDoc(self) -> None:
        # gen file list
        self.fileList( self.title_tex, {name: dct[self.FILENAME] for name, dct in self.docs.items()} )
        self.title_tex.newpage()
        self.title_tex.section("Launchfiles Documentation", SEC_LABEL.format(self.doc_type))

        # gen content per file
        for name, dct in self.docs.items():
            print("Generating latex documentation for", name)
            self._procDoc(name, dct[self.LIB], dct[self.TEX])
            self.title_tex.input(os.path.join(self.doc_dir, name))

    def fileList(self, tex: XTex, files: dict) -> None:
        tex.newpage()
        tex.subsection("File List", SUBSEC_LABEL.format(self.doc_type, "filelist"), "Here is a list of all files:")
        lststr = "".join( [tex.clistHyperEntry(FILE_LABEL.format(self.doc_type, name), tex.removePath(f, self.rm_file_part)) for name, f in files.items()] )
        tex.clist(lststr)

    def _procDoc(self, name: str, lib: xml.dom.minidom.Element, tex: XTex) -> None:        
        tex.subsection(name, FILE_LABEL.format(self.doc_type, name), "Content Documentation")

        # print(lib.toprettyxml())

        # self._procArgs(lib, tex)
        # tex.newpage()
        # self._procParams(lib, tex)
        # tex.newpage()
        # self._procGroups(lib, tex)
        # tex.newpage()
        # self._procText(lib, tex)
        # tex.newpage()
        # self._procComment(lib, tex)
        # tex.newpage()
        # self._procIncludes(lib, tex)
        # tex.newpage()

    def _procIncludes(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
        include_list = ""
        includes = lib.getElementsByTagName("include")
        if len(includes) == 0:
            return 
        
        for i in includes:
            print(i.getAttribute("if"))
            print(i.hasChildNodes())

            exit(0)

    def _procGroups(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
        group_list = ""
        groups = lib.getElementsByTagName("group")
        if len(groups) == 0:
            return 
        
        for g in groups:
            print(g.toprettyxml())

    def _procText(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
        text_list = ""
        texts = lib.getElementsByTagName("#text")
        if len(texts) == 0:
            return 
        
        for t in texts:
            print(t.toprettyxml())

    def _procComment(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
        com_list = ""
        comments = lib.getElementsByTagName("#comment")
        if len(comments) == 0:
            return 
        
        for c in comments:
            print(c.toprettyxml())

    def _procArgs(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
        args_list = ""
        args = lib.getElementsByTagName("arg")
        if len(args) == 0:
            return 
        
        for a in args:
            n = a.getAttribute("name") if a.hasAttribute("name") else "?"
            v = a.getAttribute("value") if a.hasAttribute("value") else a.getAttribute("default") if a.hasAttribute("default") else "n/a"
            d = a.getAttribute("doc") if a.hasAttribute("doc") else "n/a"
            args_list += tex.citemVarEntry(n, v ,d)

        if "\item" in args_list:
            tex.citem("Args:~~~~~~\small{name}~~~~~~~~~~\small{default}", args_list)

    def _procParams(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
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

            params_list += tex.citemParEntry(n, c)
            # add line breaks
            tex.newline()

        if "\item" in params_list:
            tex.citem(f"Params:\\hspace{{2cm}}\small{{name}}\\hspace{{2cm}}\\small{{{val}}}" + ("\\hspace{{2cm}}\\small{{args}}" if val == 'command' else ""), params_list)
            tex.newpage()

    def writeDoc(self) -> str:
        res_str = self.title_tex.save()
        for dct in self.docs.values():
            res_str += dct[self.TEX].save()
        return  res_str
