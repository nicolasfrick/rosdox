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
	
	def citemHlinkVarEntry(self, name: str, value: str, text: str) -> str:
		return DOXY_CITEMIZE_CLIST.format(f"\\textbf{{{name}}}"+":" , self.escapeAll(value), self.escapeAll(text))
	
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
	ARG = 'arg'
	PARAM = 'param'
	REMAP = 'remap'
	GROUP = 'group'
	INCLUDE = 'include'
	NODE = 'node'

	LAUNCHFILE_ARG = ARG
	LAUNCHFILE_PARAM = PARAM
	LAUNCHFILE_INCLUDE = INCLUDE
	LAUNCHFILE_GROUP = GROUP
	LAUNCHFILE_NODE = NODE
	LAUNCHFILE_REMAP = REMAP

	def __init__(self) -> None:
		pass

	def init(self,
					input_filename: str,
					outpth: str,
					rm_pattern: str,
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
		self.docs = {}
		self.args_documented = []
		self.edges_documented = []

		# tree graph 
		self.tree = "digraph G {\nranksep=0.02;\nnodesep=0.5;\nrankdir=LR;\nfontname=\"Bitstream Vera Sans\";\nfontsize=25;\nnode [shape=box, fontname=\"Bitstream Vera Sans\", fontsize=3, color=blue, fontcolor=blue];\n"
		self.edges = ""

		self.rospack = RosPack()
		self.printInfo("Creating latex documentation for", "launchfiles" if self.launchfile else "xacro", "in", self.doc_dir if self.doc_dir is not None else 'stdout')

		# reset path for xacro output
		return None if outpth is None else None if not '.' in os.path.basename(outpth) else outpth
	
	def printInfo(self, *msg) -> None:
		if self.info:
			print(*msg)

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

	def getTransitionLabel(self, node: xml.dom.minidom.Element) -> str:
		label = TREE_LABEL.format(("ns: " + node.getAttribute("ns")  +"; ") if node.hasAttribute("ns") else "",
															  ( "if: " + node.getAttribute("if")  +"; ") if node.hasAttribute("if") else "",      # and not "allow_trajectory_execution" in if_cond
															  ("unless: " + node.getAttribute("unless") +";\n") if node.hasAttribute("unless") else "",
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
	
	def addNode(self, node_name: str, hlink: str, color: str="blue", shape: str="box") -> None:
		label = HYPERLINK.format(self.title_tex.name2Ref(hlink), self.title_tex.escapeAll(node_name))
		self.tree += f"\"{self.title_tex.escapeAll(node_name)}\" [label=\"{label}\", color=\"{color}\",shape=\"{shape}\"];\n"

	def addEdge(self, parent: str, child: str, label: str) -> None:
		# add hyperlink
		if not "allow_trajectory_execution" in label:
			label = label.replace(";", ";\n")
		label = self.title_tex.escapeVarArg(label)
		args = label.replace("'", " ").split(" ")
		for arg in args:
			if arg in self.args_documented:
				label = label.replace(arg, HYPERLINK.format(self.title_tex.name2Ref(arg), f" {self.title_tex.escapeAll(arg)}"))
			else:
				label = label.replace(arg, f"{self.title_tex.escapeAll(arg)}") 

		# avoid doubled entries
		edge = f"\"{self.title_tex.escapeAll(parent)}\" -> \"{self.title_tex.escapeAll(child)}\" [label=\"{label}\"];\n"
		if edge in self.edges_documented:
			return
		
		# add edge
		self.edges_documented.append(edge)
		self.edges += edge

	def cleanHlink(self, match: re.Match) -> str:
		content = match.group(1) 
		updated_content = content.replace("\\", "")  
		return f"\\hyperlink{{{updated_content}}}"
	
	def cleanTikzTree(self, tikz_tree: str) -> str:
		"""Workaround d2t formattings that result
		 	  in compilation errors with tex commands.
		"""

		# $\backslash$hyperlink -> \hyperlink
		pattern = r"\$\\backslash\$hyperlink"
		replacement = r"\\hyperlink"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		# \{ -> {
		pattern = r"\\\{"
		replacement = r"{"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		# \} -> }
		pattern = r"\\\}"
		replacement = r"}"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

		# rm $\backslash$
		pattern = r"\$\\backslash\$"
		replacement = r"" 
		tikz_tree = re.sub(pattern, replacement, tikz_tree)
		
		# \hyperlink{a\_b\_c} -> \hyperlink{a_b_c}
		pattern = r"\\hyperlink\{([^}]+)\}"
		tikz_tree = re.sub(pattern, self.cleanHlink, tikz_tree)

		#  " "hyperlink -> \hyperlink
		pattern = r" hyperlink"
		replacement = r"\\hyperlink"
		tikz_tree = re.sub(pattern, replacement, tikz_tree)

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

	def addDoc(self, filepath: str, lib: xml.dom.minidom.Element) -> None:
		 # ignore file
		if self.rm_pattern in filepath:
			return
		
		# add/ update doc
		name = self.getFilename(filepath)
		if name in self.docs.keys():
			self.printInfo("Ignoring duplicatet file", name)
			return
		else:
			self.printInfo(f"Adding documentation for {self.doc_type}{'' if self.docs else ' root'} file: ", name)
			self.docs.update( {name: {self.TEX: XTex(name, self.doc_dir), 
															  self.FILENAME: self.title_tex.removePath(filepath, self.rm_file_part),
															  self.ARG: {},
															  self.PARAM: {},
															  self.NODE: {},
															  self.INCLUDE: {},
															  self.REMAP: [],
															  }
											  } )

		# process elements
		self.procDoc(name, lib)

	def procDoc(self, file_name: str, parent: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		for node in parent.childNodes:
			if node.nodeType == parent.ELEMENT_NODE:

				if node.nodeName == self.LAUNCHFILE_NODE:
					self.procNode(file_name, node, group_attrs)

				elif node.nodeName == self.LAUNCHFILE_INCLUDE:
					self.procInclude(file_name, node, group_attrs)

				elif node.nodeName == self.LAUNCHFILE_GROUP:
					self.procGroup(file_name, node, group_attrs)

				elif node.nodeName == self.LAUNCHFILE_ARG:
					self.procArg(file_name, node, group_attrs)

				elif node.nodeName == self.LAUNCHFILE_PARAM:
					self.procParam(file_name, node, group_attrs)

				elif node.nodeName == self.LAUNCHFILE_REMAP:
					self.procRemap(file_name, node, group_attrs)

	def procNode(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		node_name =  node.getAttribute("name")
		assert(node_name)

		self.docs[file_name][self.NODE].update( {
			node_name : {"ns": node.getAttribute("ns") if node.hasAttribute("ns") else None,
										"pkg": node.getAttribute("pkg") if node.hasAttribute("pkg") else None,
										"type": node.getAttribute("type") if node.hasAttribute("type") else None,
										"if": node.getAttribute("if") if node.hasAttribute("if") else None,
										"unless": node.getAttribute("unless") if node.hasAttribute("unless") else None,
										"args": node.getAttribute("args") if node.hasAttribute("args") else None,
										"group_attrs": group_attrs,
									  }
		  })

	def procInclude(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		incl_filename =  node.getAttribute("file")
		assert(incl_filename)
		
		self.docs[file_name][self.INCLUDE].update( {
			incl_filename : { "ns": node.getAttribute("ns") if node.hasAttribute("ns") else None,
											"if": node.getAttribute("if") if node.hasAttribute("if") else None,
											"unless": node.getAttribute("unless") if node.hasAttribute("unless") else None,
											"group_attrs": group_attrs,
										  }
		  })
		
	def procArg(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		arg_name =  node.getAttribute("name")
		assert(arg_name)

		doc = node.getAttribute("doc") if node.hasAttribute("doc") else None
		if doc is not None:
			self.args_documented.append(arg_name)
		
		self.docs[file_name][self.ARG].update( {
			arg_name:  {"if": node.getAttribute("if") if node.hasAttribute("if") else None,
									"unless": node.getAttribute("unless") if node.hasAttribute("unless") else None,
									"value": node.getAttribute("value") if node.hasAttribute("value") else None,
									"default": node.getAttribute("default") if node.hasAttribute("default") else None,
									"doc": doc,
									"group_attrs": group_attrs,
								  }
		  })
		
	def procParam(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		param_name =  node.getAttribute("name")
		assert(param_name)

		self.docs[file_name][self.PARAM].update( {
			param_name:  {"if": node.getAttribute("if") if node.hasAttribute("if") else None,
											"unless": node.getAttribute("unless") if node.hasAttribute("unless") else None,
											"value": node.getAttribute("value") if node.hasAttribute("value") else None,
											"command": node.getAttribute("command") if node.hasAttribute("command") else None,
											"group_attrs": group_attrs,
										}
		  })
		
	def procRemap(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		# remaps 
		self.docs[file_name][self.REMAP].append( {"if": node.getAttribute("if") if node.hasAttribute("if") else None,
																							"unless": node.getAttribute("unless") if node.hasAttribute("unless") else None,
																							"from": node.getAttribute("from") if node.hasAttribute("from") else None,
																							"to": node.getAttribute("to") if node.hasAttribute("to") else None, 
																							"group_attrs": group_attrs,} )
						 
	def procGroup(self, file_name: str, node: xml.dom.minidom.Element, group_attrs: dict=None) -> None:
		ns = node.getAttribute("ns") if node.hasAttribute("ns") else None
		if_cond = node.getAttribute("if") if node.hasAttribute("if") else None
		unless_cond = node.getAttribute("unless") if node.hasAttribute("unless") else None

		if group_attrs is None: # add attributes
			group_attrs = {"ns": ns, "if": if_cond, "unless": unless_cond,}
		else: # extend attributes
			group_attrs["ns"] = ns if group_attrs["ns"] is None else group_attrs["ns"] if ns is None else group_attrs["ns"] + " " + ns 
			group_attrs["if"] = if_cond if group_attrs["if"] is None else group_attrs["if"] if if_cond is None else group_attrs["if"] + " " + if_cond
			group_attrs["unless"] = unless_cond if group_attrs["unless"] is None else group_attrs["unless"] if unless_cond is None else group_attrs["unless"] + " " + unless_cond

		# recursion
		self.procDoc(file_name, node, group_attrs)

	def procText(self, file_name: str, node: xml.dom.minidom.Element) -> None:
		pass

	def procComment(self, file_name: str, node: xml.dom.minidom.Element) -> None:
		pass

	def genDoc(self) -> None:
		# gen file list
		self.title_tex.subsection("Launchfiles Documentation", SEC_LABEL.format(self.doc_type))
		self.docFiles( self.title_tex, {name: dct[self.FILENAME] for name, dct in self.docs.items()} )
		self.title_tex.newpage()

		# gen content per file
		for name, dct in self.docs.items():
			self.printInfo("Generating latex documentation for", name)
			self.title_tex.input(name)
			tex: XTex = dct[self.TEX]
			tex.subsubsection(name, self.formatFileLabel(name), "Content Documentation")

			self.docArgs(dct[self.ARG], tex)
			tex.newpage()
			self.docParams(dct[self.PARAM], tex)
			tex.newpage()
			self.docIncludes(dct[self.INCLUDE], tex)
			tex.newpage()
			self.docNodes(dct[self.NODE], tex)
			tex.newpage()
			self.docRemaps(dct[self.REMAP], tex)
			tex.newpage()

	def docFiles(self, tex: XTex, files: dict) -> None:
		tex.subsubsection("File List", SUBSEC_LABEL.format(self.doc_type, "filelist"), "Here is a list of all files:")
		lststr = "".join( [tex.clistHyperEntry(self.formatFileLabel(name), file) for name, file in files.items()] )
		tex.clist(lststr)

	def fmtConditionals(self, group_attrs: Union[None, dict], if_cond: Union[None, str], unless_cond: Union[None, str]) -> str:
		conditionals = "" if if_cond is None else "if condition: " + if_cond + "\n" \
									+ "" if unless_cond is None else "unless condition: " + "\n" 
		if group_attrs is None:
			return conditionals
		else:
			return "" if group_attrs["ns"] is None else "group namespaces: " + group_attrs["ns"] + "\n" \
						+ "" if group_attrs["if"] is None else "group if conditions: " + group_attrs["if"] + "\n" \
						+ "" if group_attrs["unless"] is None else "group unless conditions: " + group_attrs["unless"] + "\n" \
						+ conditionals

	def docArgs(self, args: dict, tex: XTex) -> None:
		args_list = ""
		for name, dct in args.items():
			hlink = HYPERLINK.format(self.title_tex.name2Ref(name), f"{self.title_tex.escapeAll(name)}")
			conditionals = self.fmtConditionals(dct["group_attrs"], dct["if"], dct["unless"])
			value = dct["value"] if dct["value"] is not None else "default: " + dct["default"] if dct["default"] is not None else "n/a"
			doc = "" if dct["doc"] is None else dct["doc"]
			args_list += tex.citemHlinkVarEntry(hlink, value, conditionals + doc)

		if "\item" in args_list:
			# surround with a list if entries are present
			tex.citem(f"Args:\\hspace{{2cm}}\small{{name}}\\hspace{{2cm}}\\small{{value}}\\hspace{{2cm}}\\small{{documentation}}", args_list)

	def docParams(self, params: dict, tex: XTex) -> None:
		params_list = ""
		for name, dct in params.items():
			conditionals = self.fmtConditionals(dct["group_attrs"], dct["if"], dct["unless"])
			value = "n/a" if dct["value"] is None else dct["value"]
			command = conditionals if dct["command"] is None else conditionals + "command:\n" + dct["command"]
			params_list += tex.citemVarEntry(name, value, command)

		if "\item" in params_list:
			# surround with a list if entries are present
			tex.citem(f"Params:\\hspace{{2cm}}\small{{name}}\\hspace{{2cm}}\\small{{value}}\\hspace{{2cm}}\\small{{documentation}}", params_list)

	def docIncludes(self, includes: dict, tex: XTex) -> None:
		includes_list = ""
		for name, dct in includes.items():
			conditionals = self.fmtConditionals(dct["group_attrs"], dct["if"], dct["unless"])
			ns = "" if dct["ns"] is None else dct["ns"]
			print(name)
			exit(0)
			# includes_list += tex.citemVarEntry(name.replace(""), ns, conditionals)

		if "\item" in includes_list:
			# surround with a list if entries are present
			tex.citem(f"Includes:\\hspace{{2cm}}\small{{file}}\\hspace{{2cm}}\\small{{namespace}}\\hspace{{2cm}}\\small{{conditionals}}", includes_list)

	def docNodes(self, nodes: dict, tex: XTex) -> None:
		nodes_list = ""
		for name, dct in nodes.items():
			conditionals = self.fmtConditionals(dct["group_attrs"], dct["if"], dct["unless"])
			conditionals += "" if dct["ns"] is None else "namespace: " + dct["ns"] + "\n"
			conditionals += "" if dct["pkg"] is None else "package: " + dct["pkg"] + "\n"
			conditionals += "" if dct["args"] is None else "args: " + dct["args"]
			node_type = "n/a" if dct["type"] is None else dct["type"]
			nodes_list += tex.citemHlinkVarEntry(name, node_type, conditionals)

		if "\item" in nodes_list:
			# surround with a list if entries are present
			tex.citem(f"Nodes:\\hspace{{2cm}}\small{{name}}\\hspace{{2cm}}\\small{{type}}\\hspace{{2cm}}\\small{{documentation}}", nodes_list)

	def docRemaps(self, remaps: list, tex: XTex) -> None:
		remaps_list = ""
		for dct in remaps:
			conditionals = self.fmtConditionals(dct["group_attrs"], dct["if"], dct["unless"])
			remap_from = "n/a" if dct["from"] is None else dct["from"]
			remap_to = "n/a" if dct["to"] is None else dct["to"]
			remaps_list += tex.citemVarEntry(remap_from, remap_to, conditionals)

		if "\item" in remaps_list:
			# surround with a list if entries are present
			tex.citem(f"Remaps:\\hspace{{2cm}}\small{{from}}\\hspace{{2cm}}\\small{{to}}\\hspace{{2cm}}\\small{{conditionals}}", remaps_list)

	def writeDoc(self) -> None:
		res_str = self.title_tex.save()
		res_str += self.saveTree()
		for dct in self.docs.values():
			res_str += dct[self.TEX].save()

		self.printInfo(res_str)
