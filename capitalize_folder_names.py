"""
Beschreibung:
Dieses Skript durchsucht ein angegebenes Verzeichnis (oder das aktuelle Arbeitsverzeichnis) nach Unterverzeichnissen und passt deren Namen an:
- Der erste Buchstabe jedes Verzeichnisnamens wird großgeschrieben.
- Leerzeichen in Verzeichnisnamen werden durch Unterstriche (_) ersetzt.

Funktionsweise:
1. Das Skript durchsucht rekursiv ein Zielverzeichnis nach Unterverzeichnissen.
2. Verzeichnisse, deren Namen nicht den oben genannten Anforderungen entsprechen, werden in die Liste der zu ändernden Verzeichnisse aufgenommen.
3. Alle betroffenen Verzeichnisse werden umbenannt, beginnend mit den tiefsten Verzeichnissen (um Konflikte zu vermeiden).

Verwendung:
1. Stelle sicher, dass Python 3.x installiert ist.
2. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     python capitalize_and_format_folder_names.py /pfad/zum/verzeichnis

Ausgabe:
- Gibt die Anzahl der betroffenen Verzeichnisse und deren alte sowie neue Namen aus.
- Am Ende bestätigt das Skript, dass die Umbenennung abgeschlossen ist.

Hinweise:
- Das Skript ändert keine Verzeichnisse, deren Namen bereits korrekt formatiert sind.
- Es werden keine Dateien umbenannt, nur Verzeichnisse.

Abhängigkeiten:
- Python 3.x

"""


from sys import argv
import os


path = os.getcwd()
if (len(argv) >= 2):
    path = argv[1]

print('Searching for folders in ' + path)

# Go through all folders and capitalize the folder names
dirsList = []
for root, dirs, _ in os.walk(path):
    for dir in dirs:
        changedDirName = dir.capitalize().replace(' ', '_')
        if (changedDirName != dir):
            dirsList.append((root, dir, changedDirName))

print(f"Found {len(dirsList)} folders where name shall be capitalized.")

for (root, dir, changedDirName) in reversed(dirsList):
    print(f"Renaming folder {dir} to {changedDirName} ...")
    old_dir_name = os.path.join(root, dir)
    new_dir_name = os.path.join(root, changedDirName)
    os.rename(old_dir_name, new_dir_name)

print('Complete.')
