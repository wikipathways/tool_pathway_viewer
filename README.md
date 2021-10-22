# `tool_pathway_viewer`

## Install

### Dev

#### First time only:
```
git clone https://github.com/wikipathways/tool_pathway_viewer.git
cd tool_pathway_viewer
# if you're using Nix, the following line is not needed:
pip install -r requirements.txt
```

Doublecheck where exactly `local_settings.py.template` is located.

```
cp "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.template "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.
chmod o-r "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
```

Edit `local_settings.py` as appropriate.
Download a collection of sample SVGs to a local directory. If it's not where `local_settings.py` says it is, update as appropriate.

#### Every time:

Start server:
```
cd ~/Documents/tool_pathway_viewer/src
python manage.py runserver
```

If you're developing a remote machine, create a tunnel to view from your local machine:
```
ssh -L 8000:localhost:8000 -N nixos
```

Then visit http://localhost:8000

### Production

https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Deploying_a_Django_application
https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/#secret-key

```
webservice --backend=kubernetes python3.7 shell
mkdir -p "$HOME"/www
git clone https://github.com/wikipathways/tool_pathway_viewer.git "$HOME"/www/python
python3 -m venv "$HOME"/www/python/venv
source "$HOME"/www/python/venv/bin/activate
pip install --upgrade pip wheel
pip install -r "$HOME"/www/python/requirements.txt
```

Doublecheck where exactly `local_settings.py.template` is located.

```
cp "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py.template "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
chmod o-r "$HOME"/www/python/src/tool_pathway_viewer/local_settings.py
```

Edit `local_settings.py` as appropriate, e.g., specify the secret.

```
cd "$HOME"/www/python/src
python manage.py collectstatic
python manage.py check --deploy
```

Exit out of webservice shell when done.

If you need to stop the webservice:
```
webservice --backend=kubernetes stop
```

## How Initially Generated

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

Created `./uwsgi.ini` and `./src/app.py` Notice that `./src/app.py` appears to be essentially identical to `src/tool_pathway_viewer/wsgi.py`.
