from django.urls import path
from .views.CreateNewAdmin_view import register_admin
from .views.AuthenticateAdmin_view import admin_login
from .views.UpdateLoggedinAdmin_view import update_loggedin_admin
from .views.LogoutAdmin_view import logout_admin
from .views.DeleteAdmin_view import delete_admin
from .views.DeleteUser_view import delete_user
from .views.AllAdminData_view import get_all_admins
from .views.ContactAdmin_view import send_contact_admin
from .views.UpdateOtherAdmin_view import update_other_admin
from .views.UpdateOtherUser_view import update_other_user
from .views.CreateNewUser_view import register_user
from .views.AllUserData_view import get_all_users
from .views.AllUserData_view import get_all_alarms
from .views.AllUserData_view import get_all_battery_monitoring
from .views.AllUserData_view import get_all_belt_tracking




urlpatterns = [
    path('authenticate-admin/', admin_login, name='authenticate-admin'),
    path ('update-admin/', update_loggedin_admin, name = 'update-admin'),
    path ('logout-admin/', logout_admin , name = 'logout-admin'),
    path('send-email-admin/', send_contact_admin, name='send-email-admin'),

    path ('delete-admin/', delete_admin , name = 'delete-admin'),
    path('delete-user/', delete_user, name='delete-user'),
    
    path('update-other-admin/<int:id>/', update_other_admin, name='update_other_admin'),
    path('update-other-user/<int:id>/', update_other_user, name='update_other_user'),

    path('create-user/', register_user, name='create-user'),
    path('create-admin/', register_admin, name='create-admin'),

    path ('view-all-admin/', get_all_admins , name = 'view-all-admin'),
    path ('view-all-user/', get_all_users , name = 'view-all-user'),
    path ('view-all-alarms/', get_all_alarms , name = 'view-all-alarms'),
    path ('view-all-battery-monitoring/', get_all_battery_monitoring , name = 'view-all-battery-monitoring'),
    path ('view-all-belt-tracking/', get_all_belt_tracking , name = 'view-all-belt-tracking'),
]