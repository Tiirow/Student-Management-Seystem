# ============================================================
# SYSTEM LOGS MIDDLEWARE
# ============================================================

import traceback

from django.contrib.auth.models import AnonymousUser

from .models import ErrorLog


class ErrorLoggingMiddleware:
    """
    Middleware-kan wuxuu qabtaa errors-ka Django request-ka
    kadibna wuxuu ku kaydiyaa database-ka ErrorLog.
    """

    def __init__(self, get_response):

        self.get_response = get_response

    # ========================================================
    # REQUEST
    # ========================================================

    def __call__(self, request):

        response = self.get_response(request)

        return response

    # ========================================================
    # EXCEPTION
    # ========================================================

    def process_exception(self, request, exception):

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        user = getattr(
            request,
            'user',
            None
        )

        if isinstance(
            user,
            AnonymousUser
        ):

            user = None

        # ----------------------------------------------------
        # TRACEBACK
        # ----------------------------------------------------

        error_traceback = traceback.format_exc()

        # ----------------------------------------------------
        # ERROR LOG
        # ----------------------------------------------------

        try:

            ErrorLog.objects.create(

                user=user,

                error_type=(
                    exception.__class__.__name__
                ),

                message=str(exception),

                traceback=error_traceback,

                path=request.path,

                method=request.method,

            )

        except Exception:

            # ------------------------------------------------
            # ErrorLog laftiisa haddii uu error sameeyo,
            # original error-ka lama qarinayo.
            # ------------------------------------------------

            pass

        # ----------------------------------------------------
        # RETURN NONE
        # ----------------------------------------------------
        #
        # None waxay Django u sheegaysaa:
        #
        # "Exception-kan ha iga qarin,
        # Django ha sii wado handling-kiisa."
        #
        # ----------------------------------------------------

        return None
    #Middleware-ka aad samaysay wuxuu qabtaa Django exceptions, 
        # kadibna wuxuu isku dayaa inuu database-ka ku kaydiyo ErrorLog