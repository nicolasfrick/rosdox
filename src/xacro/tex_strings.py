BRACES = "{}"
EMBRACED_ARG = "{{{}}}"
EMBRACING_STR_OPEN = "{{"
EMBRACING_STR_CLOSE = "}}"

NEWPAGE = "\n\\newpage\n\n"
NEWLINE = "\n\\vspace{2\\baselineskip}"
NEWLINE_FMT = "\n\\vspace{{2\\baselineskip}}"

PAGEREF = f"\pageref{EMBRACED_ARG}" # 1 arg
MBOX_FMT = f"\mbox{EMBRACING_STR_OPEN}{EMBRACED_ARG}{EMBRACING_STR_CLOSE}" # 1 arg
HYPERTARGET = f"\hypertarget{EMBRACED_ARG}{EMBRACED_ARG}" # 2 args
HYPERLINK = f"\hyperlink{EMBRACED_ARG}{EMBRACED_ARG}" # 2 args
MBOX_HYPERLINK = MBOX_FMT.format(HYPERLINK) # 2 args

# DOXY_SEC = f"\doxysection{EMBRACED_ARG} \label{EMBRACED_ARG}\n" # 2 args
# DOXY_SUBSEC = f"\doxysubsection{EMBRACED_ARG} \label{EMBRACED_ARG}\n{BRACES}\n" # 3 args
# DOXY_SUBSUBSEC = f"\doxysubsubsection{EMBRACED_ARG} \label{EMBRACED_ARG}\n{BRACES}\n" # 3 args
DOXY_SEC = f"\section{EMBRACED_ARG} \label{EMBRACED_ARG}\n" # 2 args
DOXY_SUBSEC = f"\subsection{EMBRACED_ARG} \label{EMBRACED_ARG}\n{BRACES}\n" # 3 args
DOXY_SUBSUBSEC = f"\subsubsection{EMBRACED_ARG} \label{EMBRACED_ARG}\n{BRACES}\n" # 3 args

DOXY_SEC_STR = "{{section}}"
DOXY_CLIST_STR = "{{DoxyCompactList}}"
DOXY_CLIST = f"\\begin{DOXY_CLIST_STR}\n{BRACES}\n\end{DOXY_CLIST_STR}\n" # 1arg
DOXY_CLIST_ENTRY = f"\item\contentsline{DOXY_SEC_STR}{EMBRACED_ARG}{EMBRACED_ARG}{EMBRACED_ARG}\n" # 3 args
DOXY_CLIST_HYPER_ENTRY = "\item\contentsline{{section}}{{\mbox{{\color{{blue}}\hypertarget{{{}}}{{{}}}}}}}{{\color{{blue}}\pageref{{{}}}}}{{{}}}" # 4 args

DOXY_CITEMIZE_STR = "{{DoxyCompactItemize}}"
DOXY_CITEMIZE = f"\doxysubsubsection*{EMBRACED_ARG}\n\\begin{DOXY_CITEMIZE_STR}\n{BRACES}\end{DOXY_CITEMIZE_STR}{NEWLINE_FMT}" # 1 arg
DOXY_CITEMIZE_CLIST = "    \item {} {}\n    \\begin{{DoxyCompactList}}\n      \small\item\em {}\n    \end{{DoxyCompactList}}\n" # 3 args name value \n doc

SEC_LABEL = "sw:{}_doc__sec" #  1 arg: doc_type
SUBSEC_LABEL = "sw:{}_doc__{}_subsec" #  2 arg: doc_type, filename
FILE_LABEL = "sw:{}_doc__{}_file" # 2 args: doc_type, filename
ARG_LABEL = "sw:{}_doc__{}_arg" # 2 args: doc_type, argname

INPUT = "\input{{{}}}\n"