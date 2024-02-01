This project is cloned from the Hanabi Learning Environment, published by DeepMind. 
It creates a graphical user interface for humans to play against artificial agents. 

It makes used of Poetry for the python dependency manager, and expect python 3.11 or higher (note that it can probably 
be run with another version of python but this would require to change the dependencies in `pyproject.toml`)

### Getting started
Install the learning environment:
```
sudo apt-get install g++            # if you don't already have a CXX compiler
sudo apt-get install python-pip     # if you don't already have pip
pip install .                       # or pip install git+repo_url to install directly from github
```
Install Poetry by following the instruction available at https://python-poetry.org/

Install the dependencies by running
```
poetry update
```
in the main directory. 

Run the GUI with 

```
poetry run python3 gui/gui.py
```

### Known Issues
 - The GUI does not detect or indicate when the game is lost
 - To start a new game, the gui.py must be stopped and started again
