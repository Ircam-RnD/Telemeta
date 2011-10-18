# -*- coding: utf-8 -*-
# Copyright (C) 2007 Samalyse SARL
# Copyright (c) 2007-2011 Parisson SARL

# This software is a computer program whose purpose is to backup, analyse,
# transcode and stream any audio content with its metadata over a web frontend.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#
# Authors: Olivier Guilyardi <olivier@samalyse.com>
#          Guillaume Pellerin <yomguy@parisson.com>

from django.conf.urls.defaults import *
from telemeta.models import MediaItem, MediaCollection, MediaItemMarker
from telemeta.web.base import GeneralView, AdminView, CollectionView, ItemView, \
                                InstrumentView, PlaylistView, ProfileView, GeoView, \
                                LastestRevisionsFeed
from jsonrpc import jsonrpc_site
import os.path
import telemeta.config

telemeta.config.check()

# initialization
general_view = GeneralView()
admin_view = AdminView()
collection_view = CollectionView()
item_view = ItemView()
instrument_view = InstrumentView()
playlist_view = PlaylistView()
profile_view = ProfileView()
geo_view = GeoView()

# query sets for Django generic views
all_items = { 'queryset': MediaItem.objects.enriched().order_by('code', 'old_code') }
all_collections = { 'queryset': MediaCollection.objects.enriched(), }

# CREM collections
all_collections_unpublished = { 'queryset': MediaCollection.objects.filter(code__contains='_I_'), }
all_collections_published = { 'queryset': MediaCollection.objects.filter(code__contains='_E_'), }


# ID's regular expressions
export_extensions = "|".join(item_view.list_export_extensions())

htdocs = os.path.dirname(__file__) + '/htdocs'

urlpatterns = patterns('',
    url(r'^$', general_view.index, name="telemeta-home"),

    # items
    url(r'^items/$', 'django.views.generic.list_detail.object_list', 
        dict(all_items, paginate_by=20, template_name="telemeta/mediaitem_list.html"),
        name="telemeta-items"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/$', item_view.item_detail, 
        name="telemeta-item-detail"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/dc/$', item_view.item_detail, 
        {'template': 'telemeta/mediaitem_detail_dc.html'},
        name="telemeta-item-dublincore"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/dc/xml/$', item_view.item_detail, 
        {'format': 'dublin_core_xml'},
        name="telemeta-item-dublincore-xml"),
    url(r'^items/download/(?P<public_id>[A-Za-z0-9._-]+)\.(?P<extension>' 
            + export_extensions + ')$', 
        item_view.item_export,
        name="telemeta-item-export"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/visualize/(?P<visualizer_id>[0-9a-z_]+)/(?P<width>[0-9A-Z]+)x(?P<height>[0-9A-Z]+)/$', 
        item_view.item_visualize,
        name="telemeta-item-visualize"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/analyze/xml/$', 
        item_view.item_analyze_xml,
        name="telemeta-item-analyze-xml"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/item_xspf.xml$', 
        item_view.item_playlist, 
        dict(template="telemeta/mediaitem_xspf.xml", mimetype="application/xspf+xml"),
        name="telemeta-item-xspf"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/edit/$', item_view.item_edit,
        dict(template='telemeta/mediaitem_edit.html'), name="telemeta-item-edit"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/copy/$', item_view.item_copy,
        dict(template='telemeta/mediaitem_copy.html'), name="telemeta-item-copy"),
    url(r'^item/add/$', item_view.item_add,
        dict(template='telemeta/mediaitem_add.html'), name="telemeta-item-add"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/player/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', item_view.item_detail,
        dict(template='telemeta/mediaitem_player.html'), name="telemeta-item-player"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/performances/$', item_view.item_performances_edit,
        dict(template='telemeta/mediaitem_performances_edit.html'), name="telemeta-item-performances_edit"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/keywords/$', item_view.item_keywords_edit,
        dict(template='telemeta/mediaitem_keywords_edit.html'), name="telemeta-item-keywords_edit"),
    url(r'^items/(?P<public_id>[A-Za-z0-9._-]+)/delete/$', item_view.item_delete, name="telemeta-item-delete"),
        
    # Markers
    url(r'^markers/(?P<marker_id>[A-Za-z0-9]+)/$', item_view.item_detail, name="telemeta-item-detail-marker"),
        
    # collections
    url(r'^collections/$', 'django.views.generic.list_detail.object_list',
        dict(all_collections, paginate_by=20, template_name="telemeta/collection_list.html"), name="telemeta-collections"),
    url(r'^collections_unpublished/$', 'django.views.generic.list_detail.object_list',
        dict(all_collections_unpublished, paginate_by=20, template_name="telemeta/collection_list.html"), name="telemeta-collections-unpublished"),
    url(r'^collections_published/$', 'django.views.generic.list_detail.object_list',
        dict(all_collections_published, paginate_by=20, template_name="telemeta/collection_list.html"), name="telemeta-collections-published"),
    url(r'^collections/?page=(?P<page>[0-9]+)$', 
        'django.views.generic.list_detail.object_list',
        dict(all_collections, paginate_by=20)),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/$', collection_view.collection_detail,
        dict(template="telemeta/collection_detail.html"), name="telemeta-collection-detail"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/dc/$', collection_view.collection_detail,
        dict(template="telemeta/collection_detail_dc.html"), name="telemeta-collection-dublincore"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/collection_xspf.xml$', 
        collection_view.collection_playlist, 
        dict(template="telemeta/collection_xspf.xml", mimetype="application/xspf+xml"),
        name="telemeta-collection-xspf"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/collection.m3u$',
        collection_view.collection_playlist, 
        dict(template="telemeta/collection.m3u", mimetype="audio/mpegurl"),
        name="telemeta-collection-m3u"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/edit/$', collection_view.collection_edit,
        dict(template='telemeta/collection_edit.html'), name="telemeta-collection-edit"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/copy/$', collection_view.collection_copy,
        dict(template='telemeta/collection_edit.html'), name="telemeta-collection-copy"),
    url(r'^collection/add/$', collection_view.collection_add,
        dict(template='telemeta/collection_add.html'), name="telemeta-collection-add"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/add_item/$', item_view.item_add,
        dict(template='telemeta/mediaitem_add.html'), name="telemeta-collection-additem"),
    url(r'^collections/(?P<public_id>[A-Za-z0-9._-]+)/delete/$', collection_view.collection_delete, name="telemeta-collection-delete"),
    
    # search
    url(r'^search/$', general_view.search, name="telemeta-search"),
    url(r'^search/collections/$', general_view.search, {'type': 'collections'}, 
        name="telemeta-search-collections"),
    url(r'^search/items/$', general_view.search, {'type': 'items'}, 
        name="telemeta-search-items"),
    url(r'^search/criteria/$', general_view.edit_search, name="telemeta-search-criteria"),
    url(r'^complete_location/$', general_view.complete_location, name="telemeta-complete-location"),

    # administration        
    url(r'^admin/$', admin_view.admin_index, name="telemeta-admin"),        
    url(r'^admin/general/$', admin_view.admin_general, name="telemeta-admin-general"),        
    url(r'^admin/enumerations/$', admin_view.admin_enumerations, name="telemeta-admin-enumerations"),       
    url(r'^admin/users/$', admin_view.admin_users, name="telemeta-admin-users"),       
    
    # instruments administration
    url(r'^admin/instruments/$', 
        instrument_view.edit_instrument ,
        name="telemeta-instrument-edit"),        
    url(r'^admin/instruments/add/$', 
        instrument_view.add_to_instrument,
        name="telemeta-instrument-add"),        
    url(r'^admin/instruments/update/$', 
        instrument_view.update_instrument,
        name="telemeta-instrument-update"),        
    url(r'^admin/instruments/'
        + r'(?P<value_id>[0-9]+)/$',
        instrument_view.edit_instrument_value,
        name="telemeta-instrument-record-edit"),   
    url(r'^admin/instruments/'
        + r'(?P<value_id>[0-9]+)/update/$',
        instrument_view.update_instrument_value, 
        name="telemeta-instrument-record-update"),   
        
    # enumerations administration
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/$', 
        admin_view.edit_enumeration ,
        name="telemeta-enumeration-edit"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/add/$', 
        admin_view.add_to_enumeration,
        name="telemeta-enumeration-add"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/update/$', 
        admin_view.update_enumeration,
        name="telemeta-enumeration-update"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/'
        + r'(?P<value_id>[0-9]+)/$',
        admin_view.edit_enumeration_value,
        name="telemeta-enumeration-record-edit"),   
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/'
        + r'(?P<value_id>[0-9]+)/update/$',
        admin_view.update_enumeration_value, 
        name="telemeta-enumeration-record-update"),   

    # Geographic browsing
    url(r'^geo/$', geo_view.list_continents, name="telemeta-geo-continents"),
    url(r'^geo/(?P<continent>[a-z_]+)/$', geo_view.list_countries, 
        name="telemeta-geo-countries"),
    url(r'^geo/collections/(?P<continent>[a-z_]+)/(?P<country>[a-z_]+)/$', 
        geo_view.list_country_collections, 
        name="telemeta-geo-country-collections"),
    url(r'^geo/items/(?P<continent>[a-z_]+)/(?P<country>[a-z_]+)/$', 
        geo_view.list_country_items, 
        name="telemeta-geo-country-items"),
    url(r'^geo/country_info/(?P<id>[0-9a-z]+)/$', 
        geo_view.country_info, name="telemeta-country-info"),

    # CSS+Images (FIXME: for developement only)
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/css'},
        name="telemeta-css"),
    url(r'images/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/images'},
        name="telemeta-images"),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/js'},
        name="telemeta-js"),
    url(r'^swf/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/swf'},
        name="telemeta-swf"),
    url(r'^timeside/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/timeside'},
        name="telemeta-timeside"),

    # Flat pages
    url(r'^pages/(?P<path>.*)$', general_view.render_flatpage, name="telemeta-flatpage"),

    # OAI-PMH Data Provider
    url(r'^oai/.*$', general_view.handle_oai_request, name="telemeta-oai"),

    # Authentication
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'telemeta/login.html'},
        name="telemeta-login"),
    #url(r'^login/$', 'ipauth.views.login', {'template_name': 'telemeta/login.html'},
    #    name="telemeta-login"),
    url(r'^logout/$', general_view.logout, name="telemeta-logout"),

    # Users
    url(r'^users/$', general_view.users, name="telemeta-users"),
    
    # Profiles
    url(r'^users/(?P<username>[A-Za-z0-9._-]+)/profile/$', profile_view.profile_detail, name="telemeta-profile-detail"),
    url(r'^users/(?P<username>[A-Za-z0-9._-]+)/profile/edit/$', profile_view.profile_edit, name="telemeta-profile-edit"),
    
    # Registration
    url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'telemeta/registration/password_change_form.html'}, name="telemeta-password-change"),
    url(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'telemeta/registration/password_change_done.html'}, name="telemeta-password-change-done"),
    
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'telemeta/registration/password_reset_form.html', 'email_template_name': 'telemeta/registration/password_reset_email.html'}, name="telemeta-password-reset"),
    url(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'telemeta/registration/password_reset_done.html'}, name="telemeta-password-reset-done"),
    url(r'^accounts/password_reset_confirm/(?P<uidb36>[A-Za-z0-9._-]+)/(?P<token>[A-Za-z0-9._-]+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'telemeta/registration/password_reset_confirm.html'}, name="telemeta-password-reset-confirm"),
    url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'telemeta/registration/password_reset_complete.html'}, name="telemeta-password-reset-complete"),
    url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'telemeta/registration/password_reset_complete.html'}, name="telemeta-password-reset-complete"),
       
    # JSON RPC
    url(r'json/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
    # for the graphical browser/web console only, omissible
    # url(r'json/browse/', 'jsonrpc.views.browse', name="jsonrpc_browser"), 
    
    # Playlists
    url(r'^playlists/(?P<public_id>[a-zA-Z0-9]+)/(?P<resource_type>[a-zA-Z0-9]+)/csv/$', playlist_view.playlist_csv_export, name="telemeta-playlist-csv-export"),
    
    # RSS feeds
    url(r'^rss/$', LastestRevisionsFeed(), name="telemeta-rss"),

)


