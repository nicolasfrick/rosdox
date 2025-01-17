import os
import sys
import re
import dot2tex as d2t
import xml.dom.minidom
import xml.dom.minicompat
from rospkg import RosPack
from typing import Union
from .tex_strings import *
from .t2pdf import t2pdf_main

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
	
	def escapeVarArg(self, input_str: str) -> str:
		return input_str.replace("(", "'").replace(")", "'").replace("$","")
	
	def rmWhiteSpace(self, input_str: str) -> str:
		out = re.sub(r' {2,}', ' ', input_str)
		return out

	def escapeAll(self, input_str: str) -> str:
		esc = self.escapeBrackets(input_str)
		esc = self.escapeDollar(esc)
		esc = self.escapeUnderscore(esc)
		esc = self.escapeHash(esc)
		esc = self.escapeVarArg(esc)
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

	LAUNCHFILE_NODE = 'node'
	LAUNCHFILE_GROUP = 'group'
	LAUNCHFILE_INCLUDE = 'include'

	def __init__(self) -> None:
		pass

	def init(self,
					outpth: str,
					rm_pattern: str,
					input_filename: str,
					rm_file_part: str = os.getcwd(),
					info: bool=True,
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
		self.info = info
		
		self.title_tex = XTex(self.name, self.doc_dir)
		self.root_file = self.getFilename(input_filename)
		self.current_file = self.root_file
		self.docs = {self.root_file: {self.LIB: None, self.TEX: XTex(self.root_file, self.doc_dir), self.FILENAME: self.title_tex.removePath(input_filename, self.rm_file_part)}}
		self.args_documented = {}
		self.edges_documented = []

		# tree graph 
		self.tree = "digraph G {\nrankdir=LR;\nfontname=\"Bitstream Vera Sans\";\nfontsize=25;\nnode [shape=box, fontname=\"Bitstream Vera Sans\", fontsize=3, color=blue, fontcolor=blue];\n"
		self.edges = ""

		self.rospack = RosPack()

		self.printInfo("Creating latex documentation for", "launchfiles" if self.launchfile else "xacro", "in", self.doc_dir if self.doc_dir is not None else 'stdout')

		# reset path for xacro output
		return None if outpth is None else None if not '.' in os.path.basename(outpth) else outpth
	
	def printInfo(self, *msg) -> None:
		if self.info:
			print(*msg)

	def getTransitionLabel(self, node: xml.dom.minidom.Element) -> str:
		label = TREE_LABEL.format(("ns: " + node.getAttribute("ns")  +" ") if node.hasAttribute("ns") else "",
															  ( "if: " + node.getAttribute("if")  +" ") if node.hasAttribute("if") else "",      # and not "allow_trajectory_execution" in if_cond
															  ("unless: " + node.getAttribute("unless") +"\n") if node.hasAttribute("unless") else "",
															  )
		return label
	
	def handleLaunchGroup(self, node: xml.dom.minidom.Element, root_filename: str, included_files: list, parent_label: str= "") -> None:
		group_label = self.getTransitionLabel(node)

		for child in node.childNodes:
			if child.nodeName == self.LAUNCHFILE_GROUP:
					self.handleLaunchGroup(child, root_filename, included_files, parent_label + group_label)
						
			elif child.nodeName == self.LAUNCHFILE_INCLUDE:
					file = self.handleLaunchFile(child, root_filename, parent_label + group_label)
					included_files.append(file)

			elif child.nodeName == self.LAUNCHFILE_NODE:
				self.handleLaunchNode(child, root_filename, parent_label + group_label)

	def handleLaunchFile(self, node: xml.dom.minidom.Element, root_filename: str, parent_label: str= "") -> str:
		assert(node.hasAttribute("file"))
		file = node.getAttribute("file")

		# grow tree
		fn = self.getFilename(file)
		label = self.getTransitionLabel(node)				
		self.addNode(fn, root_filename)
		self.addEdge(root_filename, fn, parent_label + label)

		return file
	
	def handleLaunchNode(self, node: xml.dom.minidom.Element, root_filename: str, parent_label: str= "") -> None:
			# format name
			node_name = f'{node.getAttribute("pkg") if node.hasAttribute("pkg") else ""} : \
											{node.getAttribute("type") if node.hasAttribute("type") else ""} :\
											{node.getAttribute("name") if node.hasAttribute("name") else ""}' # concatenate names

			# grow tree
			label = self.getTransitionLabel(node)		
			self.addNode(node_name, root_filename, shape="ellipse")
			self.addEdge(root_filename, node_name, parent_label + label)

	def handleElement(self, node: xml.dom.minidom.Element, root_filepath: Union[None, str]) -> list:
		included_files = []
		if root_filepath is None:
			return included_files
		root_filename = self.getFilename(root_filepath)

		# handle includes and nodes indirectly
		if node.nodeName == self.LAUNCHFILE_GROUP:
				files = []
				self.handleLaunchGroup(node, root_filename, files)
				included_files.extend(files)
					
        # handle includes directly
		elif node.nodeName == self.LAUNCHFILE_INCLUDE:
				file = self.handleLaunchFile(node, root_filename)
				included_files.append(file)

        # handle nodes directly
		elif node.nodeName == self.LAUNCHFILE_NODE:
			self.handleLaunchNode(node, root_filename)

		return [self.resolvePath(f) for f in included_files]
	
	def subVarArg(self, input_str: str) -> str:
		"""$(arg v)/path -> v/path"""
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
		label = HYPERLINK.format(self.title_tex.name2Ref(hlink), self.title_tex.escapeAll(node_name))
		self.tree += f"\"{self.title_tex.escapeAll(node_name)}\" [label=\"{label}\", color=\"{color}\",shape=\"{shape}\"];\n"

	def addEdge(self, parent: str, child: str, label: str) -> None:
		edge = f"\"{self.title_tex.escapeAll(parent)}\" -> \"{self.title_tex.escapeAll(child)}\" [label=\"{self.title_tex.escapeAll(label)}\"];\n"
		if edge in self.edges_documented:
			return
		self.edges_documented.append(edge)
		self.edges += edge

	def cleanHlink(self, match: re.Match) -> str:
		content = match.group(1) 
		updated_content = content.replace("\\", "")  
		return f"\\hyperlink{{{updated_content}}}"
	
	def cleanTikzTree(self, tikz_tree: str) -> str:
		pattern = r"\$\\backslash\$hyperlink"
		replacement = r"\\hyperlink"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		pattern = r"\\\{"
		replacement = r"{"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		pattern = r"\\\}"
		replacement = r"}"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		pattern = r"\$\\backslash\$"
		replacement = r"" 
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		pattern = r"\\hyperlink\{([^}]+)\}"
		tikz_tree = re.sub(pattern, self.cleanHlink, tikz_tree)

		return tikz_tree

	def saveTree(self) -> str:
		# terminate tree
		self.tree += self.edges + "}\n"
		tree_path = os.path.join(self.doc_dir, "grapviz_tree")

		# gen tex file
		tikz_tree = d2t.dot2tex(self.tree, 
														format='tikz', 
														crop=True,
														figonly=True,
														)
		tikz_tree = self.cleanTikzTree(tikz_tree)

		# gen standalone tex file
		tikz_tree_standalone = d2t.dot2tex(self.tree, 
																				format='tikz', 
																				crop=True,
																				figonly=False,
																				)

		# dot to string
		if self.doc_dir is None:
			return tikz_tree + "\n\n"
		# dot to file
		with open(tree_path + ".gv", "w") as fw:
			fw.write(self.tree)
		# tikz to tex file
		with open(tree_path + ".tex", "w") as fw:
			fw.write(tikz_tree)
		# tikz to standalone tex file
		t2pdf_path = tree_path + "_standalone.tex"
		with open(t2pdf_path, "w") as fw:
			fw.write(tikz_tree_standalone)
		# tikz to pdf
		sys.argv[1:] = [t2pdf_path, f"--output={tree_path + '.pdf'}", "--quiet" ]
		t2pdf_main()

		return "Tree saved to " + self.doc_dir + "/grapviz_tree.tex\n"
	
	def getFilename(self, filepath: str) -> str:
		return os.path.basename(filepath).replace(self.extension, "").replace(".xml", "")

	def isLaunchfile(self, filename: str) -> bool:
		return '.launch' in filename

	def formatFileLabel(self, name: str) -> str:
		assert("/" not in name and "." not in name) # filename w/o extension 
		return FILE_LABEL.format(self.doc_type, name)
	
	def formatArgLabel(self, name: str) -> str:
		assert("$" not in name and "(" not in name and ")" not in name) # argname w/o braces
		return ARG_LABEL.format(self.doc_type, name)

	def addDoc(self, filepath: str, lib: xml.dom.minidom.Element) -> None:
		if self.rm_pattern not in filepath: # ignore
			name = self.getFilename(filepath)

			if name in self.docs.keys():
				infix = " root" if self.root_file in filepath else ""
				self.printInfo(f"Replacing documentation for {self.doc_type}{infix} file: ", name)
				self.docs[name][self.LIB] = lib
			else:
				self.printInfo(f"Adding documentation for {self.doc_type} included file: ", name)
				self.docs.update( {name: {self.LIB: lib, self.TEX: XTex(name, self.doc_dir), self.FILENAME: self.title_tex.removePath(filepath, self.rm_file_part)}} )

	def genDoc(self) -> None:
		# gen file list
		self.title_tex.subsection("Launchfiles Documentation", SEC_LABEL.format(self.doc_type))
		self.fileList( self.title_tex, {name: dct[self.FILENAME] for name, dct in self.docs.items()} )
		self.title_tex.newpage()

		# gen content per file
		for name, dct in self.docs.items():
			self.printInfo("Generating latex documentation for", name)
			self._procDoc(name, dct[self.LIB], dct[self.TEX])
			self.title_tex.input(name)

	def fileList(self, tex: XTex, files: dict) -> None:
		tex.newpage()
		tex.subsubsection("File List", SUBSEC_LABEL.format(self.doc_type, "filelist"), "Here is a list of all files:")
		lststr = "".join( [tex.clistHyperEntry(self.formatFileLabel(name), file) for name, file in files.items()] )
		tex.clist(lststr)

	def _procDoc(self, name: str, lib: xml.dom.minidom.Element, tex: XTex) -> None:        
		tex.subsubsection(name, self.formatFileLabel(name), "Content Documentation")

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
			self.printInfo(i.getAttribute("if"))
			self.printInfo(i.hasChildNodes())

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
			self.printInfo(g.toprettyxml())

	def _procText(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
		text_list = ""
		texts = lib.getElementsByTagName("#text")
		if len(texts) == 0:
			return 
		
		for t in texts:
			self.printInfo(t.toprettyxml())

	def _procComment(self, lib: xml.dom.minidom.Element, tex: XTex) -> None:
		com_list = ""
		comments = lib.getElementsByTagName("#comment")
		if len(comments) == 0:
			return 
		
		for c in comments:
			self.printInfo(c.toprettyxml())

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

	def writeDoc(self) -> None:
		res_str = self.title_tex.save()
		res_str += self.saveTree()
		for dct in self.docs.values():
			res_str += dct[self.TEX].save()

		self.printInfo(res_str)
