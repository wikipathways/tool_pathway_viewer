from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.urls import reverse
from pathlib import Path
import re
import requests
import webcolors


# if settings.DEBUG:
#    print("debugging mode...")

CSS3_NAMES_TO_HEX = webcolors.CSS3_NAMES_TO_HEX
THEME_FILENAME_PARTS_BY_THEME = dict(plain="", dark=".dark")

NON_ALPHANUMERIC_DASH_CHAR_RE = re.compile(r"[^A-Za-z0-9\-]")
WPRE = re.compile(r"^WP\d+$")
HEXADECIMAL_RE = re.compile(r"^[0-9a-fA-F]+$")


def generate_gradient_svg(id, colors):
    """
    Generates an SVG linear gradient from a list of colors. Adapted from https://stackoverflow.com/questions/29335354/filling-an-svg-path-with-multiple-colors.

    Parameters:
    id (str): the id of the gradient
    colors (list): a list of colors in hex format, e.g., ['#FF0000', '#00FF00', '#0000FF']
    """
    text = f'<linearGradient id="{id}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{colors[0]}" stop-opacity=1 />'
    for i in range(1, len(colors)):
        text += f'<stop offset="{(i)*100/(len(colors))}%" stop-color="{colors[i - 1]}" stop-opacity=1 />'
        text += f'<stop offset="{(i)*100/(len(colors))}%" stop-color="{colors[i]}" stop-opacity=1 />'
    text += f'<stop offset="100%" stop-color="{colors[-1]}" stop-opacity=1 /></linearGradient>'
    return text


# decorator needed to allow external iframes to use it
@xframe_options_exempt
def embed(request, wpid):
    theme_filename_part = ""
    theme = request.GET.get("theme", "plain")
    if theme in THEME_FILENAME_PARTS_BY_THEME:
        theme_filename_part = THEME_FILENAME_PARTS_BY_THEME[theme]
    else:
        theme_filename_part = ""

    if not wpid:
        # the path in ../tool_pathway_viewer/urls.py should make it impossible to get here
        return HttpResponse(
            '<html><body><p>WikiPathways ID required. Example: "/embed/WP554"</p></body></html>'
        )

    if not WPRE.fullmatch(wpid):
        return HttpResponse(
            "<html><body><p>Invalid WikiPathways ID. Must must be of format WP + number, e.g., WP554</p></body></html>"
        )

    # TODO: should we convert the old revisions to git hashes and then support the "rev" query param?
    svg_url = f"https://raw.githubusercontent.com/wikipathways/wikipathways-assets/main/pathways/{wpid}/{wpid}.svg"
    svg_res = requests.get(svg_url)
    if svg_res.status_code != 200:
        return HttpResponse(
            f"<html><body><p>No SVG available for {svg_url}</p></body></html>"
        )

    svg_data = svg_res.text
    highlight_style = ""
    selector_color_dict: dict[str, list[str]] = {}
    for key, value in request.GET.items():
        validated_color = ""
        if key in CSS3_NAMES_TO_HEX:
            validated_color = key
        else:
            # if prefix '#' is present, remove it for consistency. We'll add it back later.
            if key[0] == "#":
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
                    if selector not in selector_color_dict:
                        selector_color_dict[selector] = [validated_color]
                    elif validated_color not in selector_color_dict[selector]:
                        selector_color_dict[selector].append(validated_color)
    custom_defs = ""
    for selector, colors in selector_color_dict.items():
        gradient_id = selector + "_gradient"
        highlight_style += (
            "#"
            + selector
            + " .Icon, ."
            + selector
            + ' .Icon, [name="'
            + selector
            + '"] .Icon { fill: url(#'
            + gradient_id
            + ");}\n"
        )
        highlight_style += (
            "#"
            + selector
            + ".Edge path, ."
            + selector
            + ".Edge path { stroke: url(#"
            + gradient_id
            + ");}\n"
        )
        custom_defs += generate_gradient_svg(gradient_id, colors)
    fracture = svg_data.split("<defs>")
    svg_data = fracture[0] + "<defs>" + custom_defs + fracture[1]
    return render(
        request,
        "embed.html",
        {"highlight_style": highlight_style, "svg_data": svg_data},
    )


def help(request):
    return redirect("https://wikipathways.org/help.html#widget")
