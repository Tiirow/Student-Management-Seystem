from django.urls import path

from . import views


app_name = 'system_logs'


urlpatterns = [

    # ========================================================
    # SYSTEM LOGS DASHBOARD
    # ========================================================
    #
    # Hal meel oo lagu arko:
    #
    # 📋 Audit Trail
    # 🚨 Error Logs
    #
    # URL:
    #
    # /dashboard/logs/
    #
    # Navigation-ka wuxuu isticmaali doonaa URL-kan oo keliya.
    #
    # ========================================================

    path(
        '',
        views.system_logs_dashboard,
        name='logs_dashboard'
    ),


    # ========================================================
    # AUDIT TRAIL
    # ========================================================
    #
    # Old URL waa la ilaalinayaa
    # si backward compatibility loo helo.
    #
    # URL:
    #
    # /dashboard/logs/audit-trail/
    #
    # ========================================================

    path(
        'audit-trail/',
        views.audit_trail,
        name='audit_trail'
    ),


    # ========================================================
    # ERROR LOGS
    # ========================================================
    #
    # Old URL waa la ilaalinayaa
    # si backward compatibility loo helo.
    #
    # URL:
    #
    # /dashboard/logs/error-logs/
    #
    # ========================================================

    path(
        'error-logs/',
        views.error_logs,
        name='error_logs'
    ),

]
