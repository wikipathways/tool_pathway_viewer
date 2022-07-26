from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from pathlib import Path
import re
import requests
import webcolors


#if settings.DEBUG:
#    print("debugging mode...")

CSS3_NAMES_TO_HEX = webcolors.CSS3_NAMES_TO_HEX
THEME_FILENAME_PARTS_BY_THEME = dict(plain='', dark='.dark')

NON_ALPHANUMERIC_DASH_CHAR_RE = re.compile(r"[^A-Za-z0-9\-]")
WPRE = re.compile(r"^WP\d+$")
HEXADECIMAL_RE = re.compile(r"^[0-9a-fA-F]+$")


def embed(request, wpid):
    theme_filename_part = ''
    theme = request.GET.get('theme', 'plain')
    if theme in THEME_FILENAME_PARTS_BY_THEME:
        theme_filename_part = THEME_FILENAME_PARTS_BY_THEME[theme]
    else:
        theme_filename_part = ''

    if not wpid:
        # the path in ../tool_pathway_viewer/urls.py should make it impossible to get here
        return HttpResponse('<html><body><p>WikiPathways ID required. Example: "/embed/WP554"</p></body></html>')

    if not WPRE.fullmatch(wpid):
        return HttpResponse('<html><body><p>Invalid WikiPathways ID. Must must be of format WP + number, e.g., WP554</p></body></html>')
      
    # TODO: should we convert the old revisions to git hashes and then support the "rev" query param?
    svg_url = f'https://raw.githubusercontent.com/wikipathways/wikipathways-assets/main/pathways/{wpid}/{wpid}.svg'
    svg_res = requests.get(svg_url)
    if svg_res.status_code != 200:
        return HttpResponse(f'<html><body><p>No SVG available for {svg_url}</p></body></html>')

    svg_data = svg_res.text
    highlight_style = ''
    for key, value in request.GET.items():
        validated_color = ""
        if key in CSS3_NAMES_TO_HEX:
            validated_color = key
        else:
            # if prefix '#' is present, remove it for consistency. We'll add it back later.
            if key[0] == '#':
                key = key[1:]

            # valid lengths for color hex codes: 3, 6 or 8
            if (len(key) in [3, 6, 8]) and (HEXADECIMAL_RE.fullmatch(key) is not None):
                validated_color = "#" + key

        if validated_color != "":
            for raw_selector in value.split(","):
                # The sub and find steps are to guard against malicious input.
                # If the selector, with any characters other than alphanumeric
                # or dash converted to unscores, are not already in the SVG,
                # we don't include that selector.

                selector = NON_ALPHANUMERIC_DASH_CHAR_RE.sub("_", raw_selector)

                if svg_data.find(selector) > -1:
                    highlight_style += ('#' + selector + ' .Icon, .' + selector + ' .Icon, [name="' + selector + '"] .Icon { fill: ' + validated_color + ';}\n')
                    highlight_style += ('#' + selector + '.Edge path, .' + selector + '.Edge path { stroke: ' + validated_color + ';}\n')

    return render(
            request, "embed.html", {"highlight_style": highlight_style, "svg_data": svg_data}
    )

def help(request):
    return render(
            request, "help.html"
    )
