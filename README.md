# PracticaSD

Treball de Sistemes Distribuits

## Execució en linux

```bash
python3 -m http.server & #inicialitza servidor http per a llegir fitxers
python3 server.py & #inicia el servidor de "cloud"
python3 webpage/main.py & #inicia la pàgina web de control del "cloud"
<navegadorweb> localhost:5000 #obre la pàgina web de control, cal canviar <navegdorweb> pel nom del navegador web que feu servir
```

## Execució en windows

```powershell
python -m http.server
python server.py
python webpage/main.py
<navegadorweb> localhost:5000 #obre la pàgina web de control, cal canviar <navegdorweb> pel nom del navegador web que feu servir
```
Desconeixem la comanda per executar en segon pla en windows, així que s'hauria d'executar cadascuna d'aquestes comandes en una powershell o una cmd diferent. En principi haurien de funcionar tant per powershell com per cmd

Tots els drets reservats a David Llop Roig (david.llop@estudiants.urv.cat) i Joan Ribé Vidal (joan.ribe@estudiants.urv.cat)
