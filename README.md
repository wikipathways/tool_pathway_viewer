# `tool_pathway_viewer`

Thise code can be used to create custom, interactive pathway visualizations which can be integrated into websites by means of our PathwayWidget (http://www.wikipathways.org/index.php/PathwayWidget). By embedding a short HTML code snippet, a specified pathway will be displayed in an interactive pathway viewer from WikiPathways, allowing pan and zoom, search and annotation panel popups. The PathwayWidget syntax also supports specifying a list of pathway elements and a corresponding list of colors to highlight, for example, specific genes and color them based on data values or any other criteria relevant to the site. This highlighting is supported for Entrez Gene (NCBIGene), Ensembl, HGNC, Wikidata, ChEBI and HMDB identifiers.

The Pathway Widget has been described in:
**WikiPathways: capturing the full diversity of pathway knowledge** 
Martina Kutmon, Anders Riutta, ..., Chris T. Evelo, Alexander R. Pico
Nucleic Acids Research, Volume 44, Issue D1, 4 January 2016, Pages D488–D494, https://doi.org/10.1093/nar/gkv1024

## Install

### For Development

**First time only**:
```
git clone https://github.com/wikipathways/tool_pathway_viewer.git
cd tool_pathway_viewer
pip install -r requirements.txt
```

Doublecheck where exactly `local_settings.py.txt` is located.

```
cp "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.txt "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
chmod o-r "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
```

Edit `local_settings.py` as appropriate.

**Every time**:

Start server:
```
cd ~/Documents/tool_pathway_viewer/src
python manage.py runserver
```

If you're developing a remote machine, create a tunnel to view from your local machine:
```
ssh -L 8000:localhost:8000 -N <remote-machine-address>
```

Then visit http://localhost:8000

### For Production on ToolForge

Refer to the ToolForge docs for [Deploying a Django application](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Deploying_a_Django_application).

```
webservice --backend=kubernetes python3.7 shell
mkdir -p "$HOME"/www
git clone https://github.com/wikipathways/tool_pathway_viewer.git "$HOME"/www/python
python3 -m venv "$HOME"/www/python/venv
source "$HOME"/www/python/venv/bin/activate
pip install --upgrade pip wheel
pip install -r "$HOME"/www/python/requirements.txt
cp "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.txt "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
chmod o-rwx "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
```

Edit `local_settings.py` as appropriate, e.g., specify `SECRET_KEY` ([ToolForge docs on secret keys](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/#secret-key)).

Also, check `www/python/uwsgi.ini`. It probably doesn't need to be changed, but check anyway.

Then collect static files and run a deploy check:

```
cd "$HOME"/www/python/src
python manage.py collectstatic
python manage.py check --deploy
```

Exit out of webservice shell and start server:

```
webservice --backend=kubernetes python3.7 start
```

For reference, here are all the commands for controlling the web server:

```
webservice --backend=kubernetes python3.7 status
webservice --backend=kubernetes python3.7 start
webservice --backend=kubernetes python3.7 stop
webservice --backend=kubernetes python3.7 restart
```

## How This Was Initially Generated

The configuration must follow the [Wikitech guidelines](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python).

This is how this was all initially set up.

```
cd ~/Documents # or whatever dir you prefer
mkdir tool_pathway_viewer
cd tool_pathway_viewer
mkdir src
django-admin startproject tool_pathway_viewer src
cd src
django-admin startapp embed
django-admin startapp redirect
```

Sometimes this needs to be run:

```
python manage.py migrate
```

If doing the migration on ToolForge, first run this:

```
webservice --backend=kubernetes python3.7 shell
source "$HOME"/www/python/venv/bin/activate
cd "$HOME"/www/python/src
python manage.py migrate
```

Created `./uwsgi.ini` and `./src/app.py` Notice that `./src/app.py` appears to be essentially identical to `src/tool_pathway_viewer/wsgi.py`.
