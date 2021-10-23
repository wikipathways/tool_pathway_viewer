from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import logging
import re
import requests
from urllib.parse import unquote, urlencode
import webcolors


logger = logging.Logger('catch_all')

#if settings.DEBUG:
#    print("debugging mode...")

CSS3_NAMES_TO_HEX = webcolors.CSS3_NAMES_TO_HEX

WPRE = re.compile(r"^WP\d+$")
HEXADECIMAL_RE = re.compile(r"^[0-9a-fA-F]+$")


# This is just a proxy for simolecule. The tools.wmflabs.org server security settings don't
# allow loading content from another domain name, so this proxy is needed to allow
# for loading the metabolite structure SVGs from the simolecule.com domain.
#
# TODO: can I handle this by adding www.simolecule.com to ALLOWED_HOSTS in settings.py?
# If so, we wouldn't need this proxy.
def simolecule(request):
    simolecule_base = "https://www.simolecule.com/cdkdepict/depict/bow/svg"
    param_string = "?" + request.GET.urlencode()
    url = simolecule_base + param_string
    r = requests.get(url)
    svg = r.text
    return HttpResponse(svg)

def index_and_old_toolforge_url(request):
    wpid = request.GET.get('id', '')

    if not wpid:
        # show the help page
        return redirect('/embed/')

    if not WPRE.match(wpid):
        return HttpResponse("<html><body><p>Invalid id - must be of format WP554</p></body></html>")

    params_except_id = request.GET.copy()
    # remove 'id' param
    try:
        del params_except_id['id']
    except KeyError:
        pass

    params_str = params_except_id.urlencode()
    if params_str:
        params_str = "?" + params_str

    return redirect('/embed/' + wpid + params_str)


def old_pathway_widget_php(request):
    wpid = request.GET.get('id')
    if not wpid:
        # normal index page
        return HttpResponse("<html><body><p>Please specify an WikiPathways ID like /embed/WP554</p></body></html>")

    if not WPRE.match(wpid):
        # a WikiPathways ID was provided, but it's in the wrong format
        return HttpResponse("<html><body><p>Invalid id - must be of format WP554</p></body></html>")

    ##################################################
    # translate from old widget highlight color format
    ##################################################

    # /wpi/PathwayWidget.php?id=WP554
    # /embed/WP554

    # /wpi/PathwayWidget.php?id=WP554&rev=116804
    # /embed/WP554?rev=116804

    # /wpi/PathwayWidget.php?id=WP528&label=PEMT&colors=green
    # /embed/WP528?green=PEMT

    # /wpi/PathwayWidget.php?id=WP528&label[]=PEMT&label[]=Choline&label[]=CHKA&colors=green,red,blue
    # /embed/WP528?green=PEMT&red=Choline&blue=CHKA

    # /wpi/PathwayWidget.php?id=WP528&xref=10400,Entrez Gene&colors=green
    # /embed/WP528?green=Entrez_Gene_10400

    # /wpi/PathwayWidget.php?id=WP528&xref[]=10400,Entrez%20Gene&xref[]=62-49-7,CAS&xref[]=1119,Entrez%20Gene&colors=green,red,blue
    # /embed/WP528?green=Entrez_Gene_10400&red=CAS_62-49-7&blue=Entrez_Gene_1119

    targets_by_color = dict()
    raw_colors_str = request.GET.get("colors")
    if raw_colors_str:
        colors = []
        for raw_color in raw_colors_str.split(","):
            validated_color = ""
            if raw_color in CSS3_NAMES_TO_HEX:
                validated_color = webcolors.name_to_hex(raw_color)
            else:
                # if prefix '#' is present, remove it for consistency. We'll add it back later.
                if raw_color[0] == '#':
                    raw_color = raw_color[1:]

                # valid lengths for color hex codes for the old widget were 3 or 6
                if (len(raw_color) in [3, 6]) and (HEXADECIMAL_RE.fullmatch(raw_color) is not None):
                    validated_color = webcolors.normalize_hex("#" + raw_color)

            if validated_color:
                # Removing the '#' prefix from query param key, because
                # it must be URL encoded and that looks ugly.
                #
                # The old widget lightened the specified highlight colors.
                # To try matching that, let's add an alpha transparency of 80 to the hex value:
                color = validated_color[1:] + "80"

                colors.append(color)
                targets_by_color[color] = []
            else:
                logger.warn("redirect/views.py: unable to parse highlight color: " + raw_color)

        targets = []
        for target in (request.GET.getlist("xref") + request.GET.getlist("xref[]")):
            parts = target.split(",")
            identifier = parts[0]
            datasource = unquote(parts[1]).replace(" ", "_")
            targets.append(datasource + "_" + identifier)
        for target in (request.GET.getlist("label") + request.GET.getlist("label[]")):
            targets.append(target)

        color_count = len(colors)
        final_color = colors[color_count - 1]
        for t, target in enumerate(targets):
            color = None
            if t < color_count:
                color = colors[t]
            else:
                color = final_color

            targets_by_color[color].append(target)

    params = dict()

    # add highlight colors to query params
    for k, v in targets_by_color.items():
        if len(v) > 0:
            params[k] = ",".join(v)

    # add revision number to query params
    rev = request.GET.get("rev")
    if rev:
        params["rev"] = rev

    params_str = ""
    if params:
        params_str = "?" + urlencode(params)

    return redirect('/embed/' + wpid + params_str)
