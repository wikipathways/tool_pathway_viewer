# `tool_pathway_viewer`

The configuration must follow the [Wikitech guidelines](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python).

## Install

### Dev

*On remote*
First time only:
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

Start server:
```
cd ~/Documents/tool_pathway_viewer/src
python manage.py runserver
```

*On local*
```
ssh -L 8000:localhost:8000 -N nixos
```
Then visit http://localhost:8000

### Production

https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Deploying_a_Django_application
https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/#secret-key

We want files at:
* `$HOME/www/python/src/app.py`
* `$HOME/www/python/venv/`
* `$HOME/www/python/uwsgi.ini`

```
webservice --backend=kubernetes python3.7 shell
mkdir -p "$HOME"/www/python
python3 -m venv "$HOME"/www/python/venv
source "$HOME"/www/python/venv/bin/activate
pip install --upgrade pip wheel
```

```
git clone https://github.com/wikipathways/tool_pathway_viewer.git "$HOME"/www/python
pip install -r "$HOME"/www/python/requirements.txt
```

Exit out of webservice shell.

Doublecheck where exactly `local_settings.py.template` is located.

```
cp "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.template "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.
chmod o-r "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
```

Edit `local_settings.py` as appropriate.

```
manage.py check --deploy
python manage.py collectstatic
```
