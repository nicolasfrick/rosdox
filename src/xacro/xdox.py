import os
import re
import xml.dom.minidom
import xml.dom.minicompat
from rospkg import RosPack
from typing import List
from .tex_strings import *

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

	def subsection(self, name: str, label: str, text: str="") -> None:
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
		
		self.name = 'xacro_latex_doc'

		# set doc directory 
		self.doc_dir = None if outpth is None else os.path.dirname(outpth) if '.' in os.path.basename(outpth) else outpth
		if self.doc_dir is not None and not os.path.exists(self.doc_dir):
			os.makedirs(self.doc_dir, exist_ok=True)

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

		# tree graph 
		self.tree = "digraph G {\nrankdir=LR;\nfontname=\"Bitstream Vera Sans\";\nfontsize=25;\nnode [shape=box, fontname=\"Bitstream Vera Sans\", fontsize=3, color=blue, fontcolor=blue];\n"
		self.edges = ""

		self.rospack = RosPack()

		print("Creating latex documentation for", "launchfiles" if self.launchfile else "xacro", "in", self.doc_dir if self.doc_dir is not None else 'stdout')

		# reset path for xacro output
		return None if outpth is None else None if not '.' in os.path.basename(outpth) else outpth
	
	def traverseGroups(self, group: xml.dom.minidom.Element, files: dict, level: int) -> None:
		for child in group.childNodes:
			if child.nodeName == 'include':

				if child.hasAttribute("file"):
					file = self.resolvePath(child.getAttribute("file"))
					files.update( {file: {"ns": child.getAttribute("ns") if child.hasAttribute("ns") else None, 
														"if": child.getAttribute("if") if child.hasAttribute("if") else None, 
														"unless": child.getAttribute("unless") if child.hasAttribute("unless") else None, 
														"level": level,
														}} )
					
			elif child.nodeName == 'group':
				self.traverseGroups(child, files, level +1)

	def getTransitionLabel(self, ns: str, if_cond: str, unless_cond: str, group_level: int=1) -> str:
		return TREE_LABEL.format(("ns: " + ns  +"\n") if ns is not None else "",
															( "if: " + if_cond  +"\n") if if_cond is not None and not "allow_trajectory_execution" in if_cond else "",
															("unless: " + unless_cond +"\n") if unless_cond is not None else "",
															 )
		# TODO: add parent group's conditionals
		# return TREE_LABEL.format(((f"group {group_level}: " if group_level > 1 and ns is not None else "") + "ns: " + self.title_tex.escapeDollar(ns)  +"\n") if ns is not None else "",
		# 													((f"group {group_level}: " if group_level > 1 and if_cond is not None else "") + "if: " + self.title_tex.escapeDollar(if_cond)  +"\n") if if_cond is not None else "",
		# 													((f"group {group_level}: " if group_level > 1 and unless_cond is not None else "") + "unless: " + self.title_tex.escapeDollar(unless_cond)  +"\n") if unless_cond is not None else "",
		# 													 )

	def handleGroup(self, group: xml.dom.minidom.Element, root_filename: str) -> dict:
		files = {}
		# find file in groups
		self.traverseGroups(group, files, 1)
		for fl, item in files.items():
			# grow tree
			level = item["level"]
			label = self.getTransitionLabel(item["ns"], item["if"], item["unless"])

			# add parent label
			if level > 1:
				for other_item in files.values():
					other_level = other_item["level"]

					if other_level < level:
						other_label = self.getTransitionLabel(other_item["ns"], other_item["if"], other_item["unless"], level)
						label = other_label + label

			# grow tree
			root_fn = self.getFilename(root_filename)
			fn = self.getFilename(fl)
			self.addNode(fn, fn)
			self.addEdge(root_fn, fn, label)

		return files
	
	def subVarArg(self, input_str: str) -> str:
		match = re.search(r"\$\(\s*arg\s+([^)]+)\s*\)", input_str)
		if match:
			arg = match.group(1)
			subpath = re.sub(r'\$\(arg \S+\)', '', input_str)
			subpath = subpath.strip()
			return arg + subpath
		
		return input_str

	def resolvePath(self, filepath: str) -> str:
		match = re.search(r"\$\(\s*find\s+([^)]+)\s*\)", filepath)
		if match:
			pkg = match.group(1)
			pkg_path = self.rospack.get_path(pkg)
			subpath = re.sub(r'\$\(find \S+\)', '', filepath)
			subpath = subpath.strip()
			return pkg_path + subpath
		else:
			print("Cannot resolve", filepath)
			return ""
	
	def addNode(self, node_name: str, hlink: str, color: str="blue", shape: str="box") -> None:
		# label = HYPERLINK.format(self.title_tex.name2Ref(hlink), self.title_tex.escapeAll(hlink))
		# self.tree += f"\"{self.title_tex.escapeAll(node_name)}\" [label=\"{label}\"];\n"
		self.tree += f"\"{self.title_tex.escapeAll(node_name)}\" [label=\"{node_name}\", color=\"{color}\",shape=\"{shape}\"];\n"

	def addEdge(self, parent: str, child: str, label: str) -> None:
		self.edges += f"\"{self.title_tex.escapeAll(parent)}\" -> \"{self.title_tex.escapeAll(child)}\" [label=\"{self.title_tex.escapeAll(label)}\"];\n"

	def getTree(self) -> str:
		self.tree += self.edges + "}\n"
		return self.tree
	
	def writeTree(self) -> str:
		tree = self.getTree()
		if self.doc_dir is None:
			return tree + "\n\n"
		
		gv_path = os.path.join(self.doc_dir, "grapviz_tree.gv")
		with open(gv_path, "w") as fw:
			fw.write(tree)

		return "Tree saved to " + gv_path + "\n"

	def shortPath(self, filepath: str, rm: str) -> str:
		return filepath.replace(rm, "")
	
	def getFilename(self, filepath: str) -> str:
		return os.path.basename(filepath).replace(self.extension, "").replace(".xml", "")

	def isLaunchfile(self, filename: str) -> bool:
		return '.launch' in filename

	def addDoc(self, filepath: str, lib: xml.dom.minidom.Element) -> None:
		if self.rm_pattern not in filepath: # ignore
			name = self.getFilename(filepath)

			if name in self.docs.keys():
				infix = " root" if self.root_file in filepath else ""
				print(f"Replacing documentation for {self.doc_type}{infix} file: ", name)
				self.docs[name][self.LIB] = lib
			else:
				print(f"Adding documentation for {self.doc_type} included file: ", name)
				self.docs.update( {name: {self.LIB: lib, self.TEX: XTex(name, self.doc_dir), self.FILENAME: self.shortPath(filepath, self.rm_file_part)}} )

	def genDoc(self) -> None:
		# gen file list
		self.title_tex.subsection("Launchfiles Documentation", SEC_LABEL.format(self.doc_type))
		self.fileList( self.title_tex, {name: dct[self.FILENAME] for name, dct in self.docs.items()} )
		self.title_tex.newpage()

		# gen content per file
		for name, dct in self.docs.items():
			print("Generating latex documentation for", name)
			self._procDoc(name, dct[self.LIB], dct[self.TEX])
			self.title_tex.input(name)

	def fileList(self, tex: XTex, files: dict) -> None:
		tex.newpage()
		tex.subsubsection("File List", SUBSEC_LABEL.format(self.doc_type, "filelist"), "Here is a list of all files:")
		lststr = "".join( [tex.clistHyperEntry(FILE_LABEL.format(self.doc_type, name), tex.removePath(f, self.rm_file_part)) for name, f in files.items()] )
		tex.clist(lststr)

	def _procDoc(self, name: str, lib: xml.dom.minidom.Element, tex: XTex) -> None:        
		tex.subsubsection(name, FILE_LABEL.format(self.doc_type, name), "Content Documentation")

		self._procArgs(lib, tex)
		tex.newpage()
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

			# # remap launchfile member
			# if node.nodeName == 'group':
			# 	if node.hasAttribute("name"):
			# 		name = node.getAttribute("name")
			# 	if node.hasAttribute("ns"):
			# 		ns = node.getAttribute("ns")
			# 	if node.hasAttribute("if"):
			# 		if_cond = node.getAttribute("if")
			# 	if node.hasAttribute("unless"):
			# 		unless_cond = node.getAttribute("unless")

			# elif node.nodeName == 'include':
			# 	if node.hasAttribute("name"):
			# 		name = node.getAttribute("name")
			# 	if node.hasAttribute("file"):
			# 		file = node.getAttribute("file")
			# 		file = xdx.resolvePath(file)
			# 		process_file(file)
			# 	if node.hasAttribute("ns"):
			# 		ns = node.getAttribute("ns")
			# 	if node.hasAttribute("if"):
			# 		if_cond = node.getAttribute("if")
			# 	if node.hasAttribute("unless"):
			# 		unless_cond = node.getAttribute("unless")
						 
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
		res_str += self.writeTree()
		for dct in self.docs.values():
			res_str += dct[self.TEX].save()
		return  res_str
