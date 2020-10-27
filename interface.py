from tkinter import * 
from tkinter import filedialog 
from pathlib import Path
import os
import psutil
import subprocess
from threading  import Thread, Event
from queue import Queue, Empty
import json
#from os import O_NONBLOCK, read
#from fcntl import fcntl, F_GETFL, F_SETFL
#from time import sleep
import sys
import ast, inspect
import socket
import asyncio
import websockets
#Besoin de gerer la communication entre les programmes
#Besoin de terminer les processus correctement pour eviter le process zombie en cas de terminaison normale

info_array = []

class NonBlockingStreamReader:

    def __init__(self, stream):

        self.s = stream
        self.q = Queue()

        def stack_line(stream, queue):

            while True:
                #stream.flush()
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream
                output = self.readline(0.1)
                if not output:
                  print ('[No more data]')
                  #break
                print (output.rstrip().decode())


        self.thread_stack = Thread(target = stack_line,args = (self.s, self.q))
        self.thread_stack.daemon = True
        self.thread_stack.start()

    def readline(self, timeout = None):
        try:
            return self.q.get(block = timeout is not None,timeout = timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception): pass



class WsServer(object):
  def __init__(self, host='0.0.0.0', port=6171):
    self.host, self.port = host, port
    self.running = Event()
    self.serve = None
    self.loop = None
    self.msg = "init"
    #self.stop_event = Event()
    #self.stop = asyncio.get_event_loop().run_in_executor(None, self.stop_event.wait)

  async def sync(self, websocket, path):
    """Sync loop that exchange modules state with the client."""
    self.running.set()

    while self.running.is_set():
      if not websocket.open:
        break
      await websocket.send(self.msg.encode('UTF-8'))
      resp = await websocket.recv()
      print(resp)

  # async def close(self):
  #   self.serve.ws_server.close()
  #   await self.serve.ws_server.wait_closed()
  #   self.loop.stop()
  #   while(self.loop.is_running()):
  #       time.sleep(0.5)
  #   self.loop.close()
  #   self.loop=None


  def run_forever(self):
    """Run the sync loop forever."""
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    # async def echo_server(stop):
    #   async with websockets.serve(self.sync, self.host, self.port):
    #     await self.stop
    self.serve = websockets.serve(self.sync, self.host, self.port)

    #loop.run_until_complete(echo_server(stop))
    self.loop.run_until_complete(self.serve)
    self.loop.run_forever()

  def run_in_background(self):
    """Run the sync loop forever in background."""
    self.t = Thread(target=self.run_forever)
    self.t.daemon = True
    self.t.start()


def json_parser(pathname):
  ## On récupere la key du JSON ( le nom du fichier python) et le nested dictionnary qui gère les arguments du programme (peut être vide)
  file_param = {}
  with open(pathname) as json_file:
    data = json.load(json_file)
  for key, value in data.items():
    name_python_script = key
    for item in value: 
      file_param[item] = value[item]

  return Path(pathname).with_name(name_python_script),file_param


def update_dict(d, u):
  for key, _ in d.items():
      d[key].update(u)
  return d

def callback_update_json_file(frame):
  ## Callback pour gérer la mise à jour du fichier json si on modifie des valeurs par l'ihm
  ## callback un peu tricky parce qu'on veut conserver le formattage de base du fichier JSON (d'ou la fonction update_dict qui update en fonction d'une clé : permet de conserver le format {nom_fichier.py : {*args}})
  idx=get_index(info_array,frame)
  with open(info_array[idx]["json_pathname"], "r") as jsonFile:
    data = json.load(jsonFile)
  data = update_dict(data,info_array[idx]["file_params"])

  with open(info_array[idx]["json_pathname"], "w") as json_file:
    json.dump(data, json_file)

def donothing():
  filewin = Toplevel(window)
  filewin.title("test")
  button = Button(filewin, text="do nothing")
  button.pack()

def test_envoie(frame,msg):
  idx=get_index(info_array,frame)
  info_array[idx]["ws_server"].msg = "hellooo from server"


def formulaire_window_callback(frame,window,first_call):
  ## Callback qui gere la creation du formulaire
  ##le parametre first_call permet avec un boolean de rendre la fonction generique pour la creation ou le refresh du formulaire
  idx=get_index(info_array,frame)
  filewin = window
  if first_call == True:
    filewin = Toplevel(window)
    filewin.geometry("700x700")
    filewin.title("Parameters of "+str(info_array[idx]["filename"]))
  else :
      for widget in filewin.winfo_children():
        widget.destroy()
      _, file_param = json_parser(info_array[idx]["json_pathname"])
      info_array[idx]["file_params"].clear()
      info_array[idx]["file_params"].update(file_param)
  list_label = []
  list_champ = []
  row_counter = 0
  for key, val in info_array[idx]["file_params"].items(): ## création du formulaire basé sur le contenu du JSON : plus simple car pas d'a priori sur le nombre et les noms des champs qui peuvent être contenu dans le JSON
    list_label.append(Label(filewin, text=key))
    list_label[-1].grid(column=0, row=row_counter, sticky='w') ## on prend le dernier element ajouté et on gère les row de façon automatique
    list_champ.append(Entry(filewin, textvariable=StringVar(filewin, value=val)))
    list_champ[-1].grid(column=1, row=row_counter, sticky='sw', columnspan=2, padx=10)
    row_counter += 1
  update_button = Button(filewin, text="Update",command=lambda: callback_update_current_val(frame,list_label,list_champ))
  update_button.grid (column=1, row=row_counter+1,sticky='sw', pady=20)
  save_button = Button(filewin, text="Save",command=lambda: callback_update_json_file(frame))
  save_button.grid (column=2, row=row_counter+1,sticky='sw',pady=20)
  edit_button = Button(filewin, text="Edit",command=lambda:  open_file_callback(frame,"json_pathname"))
  edit_button.grid (column=3, row=row_counter+1,sticky='sw',pady=20)
  reload_button = Button(filewin, text="Reload",command=lambda:  formulaire_window_callback(frame,filewin,first_call=False))
  reload_button.grid (column=4, row=row_counter+1,sticky='sw',pady=20)


def delete_frame_callback(frame):
  ## Callback qui gère la mort du processus fils et la destruction de la frame associée 
  ## TODO besoin de séparer le côté os et le côté interface graphique
  idx=get_index(info_array,frame)
  for widget in frame.winfo_children():
    widget.destroy()
  frame.pack_forget()
  if psutil.pid_exists(info_array[idx]["pid"]): # securité pour eviter de kill un process deja terminé
    psutil.Process(info_array[idx]["pid"]).kill()
  else:
    print("already killed or no existence")
  del info_array[idx]

def convert_dict_to_args(dictionnary):
  args_string = ""
  for key,val in dictionnary.items():
    args_string +="-"+str(key)+" "+str(val)+" "
  args_list = list(args_string.split(" "))
  args_list = [val for val in args_list if val] ## enleve les espaces en trop (normalement que le dernier) 
  return args_list


def open_file_callback(frame,file):
  ## Callback qui gère l'ouverture d'un fichier 
  ## attention en fonction de l'os la primitive appelée est différente
  idx=get_index(info_array,frame)
  if not sys.platform == "win32":
    opener ="open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener,info_array[idx][file]])
  else:
    os.startfile(info_array[idx][file])

def callback_update_current_val(frame,list_label,list_champ):
  ## Callback qui met à jour les valeurs de l'ihm dans les valeurs courantes du dictionnaire
  ## L'idéal serait que ça soit automatique, tkinter gere cela ?
  idx = get_index(info_array,frame)
  current_dict = {}
  for i in range(len(list_champ)):
    name = list_label[i].cget("text")
    val = list_champ[i].get()
    current_dict[name] = val
  info_array[idx]["file_params"].update(current_dict)

def run_callback(frame):
  ##Callback qui lance le fichier python avec un pipe en écoute pour récuperer stdout
  ##Le trick ici est de devoir threader ce processus d'écoute pour éviter de bloquer le code (cf la classe NonBlockingStreamReader )
	idx=get_index(info_array,frame)
	args_list = convert_dict_to_args(info_array[idx]["file_params"])


	proc = subprocess.Popen(['python', info_array[idx]["pathname"],*args_list],
	                  shell=False,
	                  stdin=subprocess.PIPE,
	                 stdout=subprocess.PIPE,
	                 start_new_session = True # pour lancer un processus fils detaché de son parent : ici interface.py
	                 )
	info_array[idx]["pid"] = proc.pid
  #print(proc.pid)
	thread_read_stream = NonBlockingStreamReader(proc.stdout)

def run_debug_callback(frame):
	idx=get_index(info_array,frame)
	args_list = convert_dict_to_args(info_array[idx]["file_params"])
	list_functions = find_function_names_with_decorator(info_array[idx]["pathname"],"debug")
	list_args,list_variables,list_returns = find_variable_names_of_decorated_functions(info_array[idx]["pathname"],list_functions[1])
	print(list_functions,list_args,list_variables,list_returns)
	ws = WsServer()
	ws.run_in_background()
	proc = subprocess.Popen(['python', info_array[idx]["pathname"],*args_list],
                      shell=False,
                      stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     start_new_session = True # pour lancer un processus fils detaché de son parent : ici interface.py
                     )
	info_array[idx]["pid"] = proc.pid
	info_array[idx]["ws_server"] = ws 
  	#print(proc.pid)
	thread_read_stream = NonBlockingStreamReader(proc.stdout)


def find_variable_names_of_decorated_functions(file_pathname,function_name):
	#permet de trouver les variables des fonctions qui possèdent un decorateur specifique (@debug dans le cas du debugger)
	file = open(file_pathname).read()

	list_variables = []
	list_args = []
	list_returns = []
	root = ast.parse(file)

	for node in ast.walk(root):
		if isinstance(node, ast.FunctionDef):
			if node.name == function_name:
				for inner_node in ast.walk(node):
					if isinstance(inner_node, ast.Name) and isinstance(inner_node.ctx, ast.Store):
						list_variables.append(inner_node.id)
				##arguments
				#print([a.arg for a in node.args.args])
				for a in node.args.args:
					list_args.append(a.arg)
				##returns 
				for b in node.body:
					if isinstance(b, ast.Return):
							if isinstance(b.value, ast.Name):
								#print(b.value.id)
								list_returns.append(b.value.id)
	return list_args,list_variables,list_returns

def find_function_names_with_decorator(file_pathname,decorator):
	#permet de trouver les noms des fonctions qui possèdent un decorateur specifique (@debug dans le cas du debugger)
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

def clean_printing(func):
	print("-----------------------------------------")
	print(f"Calling {func.__name__}({func.get_signature})")
	print(f"Intern variables {func.locals!r}")
	print(f"{func.__name__!r} returned {func.get_output!r}")
	print("-----------------------------------------")

def get_name_from_path(path):
  return Path(path).name

def get_index(l,value):
   for i, dic in enumerate(l):
        if dic["frame_id"] == value:
            return i


def print_file():
  print(info_array)
  print(sys.getsizeof(f"Intern variables {info_array!r}"))

def open_by_argument():
	pathname_json_file = Path.cwd()




def browseFiles(): 
  pathname_json_file = filedialog.askopenfilename(initialdir = "/Documents/projet_perso", 
                                          title = "Select a File", 
                                          filetypes = [("Json files", 
                                                        ".json"), 
                                                       ("all files", 
                                                        ".*")])

  open_and_create_from_json(pathname_json_file)

def open_and_create_from_json(pathname_json_file):
  if pathname_json_file : #protection pour eviter la creation de la frame et des widgets si l'utilisateur ne veut pas ouvrir de scripts
    pathname_python,file_params = json_parser(pathname_json_file)
    filename = get_name_from_path(pathname_json_file)
    frame = Frame(window)
    frame.pack()

    run_button = Button(frame, 
                     text="Run", 
                     fg="red",
                     command= lambda : run_callback(frame))
    run_button.pack(side=LEFT)

    run_debug_button = Button(frame, 
                     text="Run_debug", 
                     fg="red",
                     command= lambda : run_debug_callback(frame))
    run_debug_button.pack(side=LEFT)

    test_envoie_button = Button(frame, 
                     text="test_envoie", 
                     fg="red",
                     command= lambda : test_envoie(frame,"jtenvoi ça"))
    test_envoie_button.pack(side=LEFT)


    label_name= Label(frame,text = filename,width = 50, height = 4, fg = "blue") 
    label_name.pack(side=LEFT)

    open_button = Button(frame, 
                     text="Open code", 
                     fg="red",
                     command=lambda: open_file_callback(frame,"pathname"))
    open_button.pack(side=LEFT)

    params_button = Button(frame, 
                     text="Params", 
                     fg="red",
                     command=lambda: formulaire_window_callback(frame,None,first_call=True))
    params_button.pack(side=LEFT)

    close_button = Button(frame, 
                     text="Close", 
                     fg="red",
                     command=lambda: delete_frame_callback(frame))
    close_button.pack(side=LEFT)

    info  = {"frame_id": frame,
              "filename": filename,
              "pathname": str(pathname_python), ##pour eviter d'avoir un type PathLib qui n'est pas itérable et qui bloque le popen
              "json_pathname": pathname_json_file,
              "file_params" : file_params,
              "pid": -2,
              "ws_server" : None}
    # Change label contents 
    #label_file_explorer.configure(text="File Opened: "+filename) 
    info_array.append(info)
       

                                                                                          
window = Tk() 
   
window.title('Python Launcher') 
    
window.geometry("700x700") 
   
window.config(background = "white") 

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=browseFiles)
filemenu.add_command(label="print", command=print_file)
menubar.add_cascade(label="File", menu=filemenu)

window.config(menu=menubar)

if len(sys.argv) == 2:   
	if ".json" in sys.argv[1]:
		pathname_json_file = Path(str(Path.cwd())+'/'+sys.argv[1])
		print(pathname_json_file)
		open_and_create_from_json(pathname_json_file)
	else : 
		print("invalid format must be python interface XXXX.json")   

window.mainloop() 