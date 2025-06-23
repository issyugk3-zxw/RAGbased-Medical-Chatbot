from django.urls import path
from . import views

# The API prefix /agentapi/ should be handled in the project's main urls.py
# For example: path('agentapi/session/', include('sessionapi.urls'))

urlpatterns = [
    path('create', views.create_session, name='create_session'),
    path('all', views.get_all_sessions, name='get_all_sessions'),
    path('delete', views.delete_session, name='delete_session'),
    path('<str:session_id>/message', views.add_message_to_session, name='add_message_to_session'),
    path('<str:session_id>/title', views.update_session_title, name='update_session_title'),
] 