# py_launcher

Interface graphique pour lancement de scripts python : le script se base sur l'utilisation de fichiers json pour la définition des arguments des scripts python 
python test.py -param1 24 -param2 teee -parem3 rr3 devient {"test.py": {"param1": "24", "param2": "teee", "param3": "rr3"}} dans le fichier test.json correspondant

L'interface intègre aussi un débuggueur qui permet de désactiver les print internes et de récupérer l'état de toutes les variables internes des fonctions décorée avec le décorateur @debug 
