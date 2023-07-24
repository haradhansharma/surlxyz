from django.http import HttpResponseRedirect
from django.shortcuts import render


def set_concent(request):
    """
    Set user consent status and redirect back to the referring URL.

    This method is called by JS from the base template after checking whether the user has given consent or not.
    We do not allow general browsing of our site without consent except for pages that do not require consent.

    Parameters:
        request (HttpRequest): The incoming request object containing user information and session data.

    Returns:
        HttpResponseRedirect: Redirects the user back to the referring URL after setting the consent status in the session.

    """
    # Set the 'consent_given' key in the session to 'True' indicating that the user has given consent.
    request.session['concent_given'] = 'True'

    # Get the referring URL from the request's META information.
    # The referring URL is the page that the user came from before reaching the current page.
    referrer = request.META.get('HTTP_REFERER')

    # Redirect the user back to the referring URL.
    # This ensures the user is taken back to the page they were on when they clicked the consent button.
    return HttpResponseRedirect(referrer)