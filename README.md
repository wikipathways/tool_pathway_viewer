# `tool_pathway_viewer`

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

### For Production on Toolforge

Refer to the Toolforge docs for [Deploying a Django application](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python#Deploying_a_Django_application).

Access the [tool on Toolforge](https://toolsadmin.wikimedia.org/tools/id/pathway-viewer):

```
ssh tools-login.wmflabs.org
become pathway-viewer
ls -lisha "$HOME"/www/python
```

Set it up the first time:

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

Edit `local_settings.py` as appropriate, e.g., specify `SECRET_KEY` ([Toolforge docs on secret keys](https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/#secret-key)).

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

If you just make a minor change to a file and push the change to the [GitHub repo](https://github.com/wikipathways/tool_pathway_viewer), you can probably deploy that change on Toolforge with just a subset of the commands above, e.g.:

```
ssh tools-login.wmflabs.org
become pathway-viewer
cd "$HOME"/www/python
git pull
cd "$HOME"/www/python/src
python manage.py collectstatic
python manage.py check --deploy
webservice --backend=kubernetes python3.7 restart
```

## How This Was Initially Generated

You probably don't need this, but just in case, here's how this configuration was initially setup to follow the [Wikitech guidelines](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python).

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

If doing the migration on Toolforge, first run this:

```
webservice --backend=kubernetes python3.7 shell
source "$HOME"/www/python/venv/bin/activate
cd "$HOME"/www/python/src
python manage.py migrate
```

Created `./uwsgi.ini` and `./src/app.py` Notice that `./src/app.py` appears to be essentially identical to `src/tool_pathway_viewer/wsgi.py`.
