"""tool_pathway_viewer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from redirect import views

#############
# URL Formats
#############

# OLD
# https://www.wikipathways.org/wpi/PathwayWidget.php?id=WP528&xref[]=10400,Entrez Gene&xref[]=62-49-7,CAS&xref[]=1119,Entrez Gene&colors=green,red,blue

# NEW
# https://pathway-viewer.toolforge.org/?id=WP528&lightgreen=Entrez_Gene_10400&pink=CAS_62-49-7&lightblue=Entrez_Gene_1119

# ALL REDIRECT TO
# https://pathway-viewer.toolforge.org/embed/WP528&lightgreen=Entrez_Gene_10400&pink=CAS_62-49-7&lightblue=Entrez_Gene_1119

urlpatterns = [
    # views.index_and_old_toolforge_url in src/redirect/views.py
    path("", views.index_and_old_toolforge_url),
    path("PathwayWidget.php", views.old_pathway_widget_php),
    path("wpi/PathwayWidget.php", views.old_pathway_widget_php),
    # embed.urls in src/embed/urls.py
    path("embed/", include("embed.urls")),
    # views.simolecule in src/redirect/views.py
    path("simolecule/", views.simolecule, name="simolecule"),
    # not really using admin
    path("admin/", admin.site.urls),
]
