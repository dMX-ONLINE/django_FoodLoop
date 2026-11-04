from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
@require_POST
def universal_delete(
    request,
    model,
    pk,
    owner_field,
    redirect_url,
    success_message
):

    obj = get_object_or_404(
        model,
        pk=pk,
        **{owner_field: request.user}
    )

    obj.delete()

    messages.success(request, success_message)


    return redirect(redirect_url)
