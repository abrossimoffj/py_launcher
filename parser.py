import ast, inspect

def findDecorators(file_pathname,decorator):
	file = open(file_pathname).read()
	target = ast.parse(file)
	#res = {}
	list_names = []
	def visit_FunctionDef(node):
		#res[node.name] = [ast.dump(e) for e in node.decorator_list]
		for e in node.decorator_list:
			if decorator in ast.dump(e):
				list_names.append(node.name)

	V = ast.NodeVisitor()
	V.visit_FunctionDef = visit_FunctionDef
	V.visit(target)
	return list_names

print(findDecorators("decorator.py","debug"))