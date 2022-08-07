from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import User
from django.db.models import Q
from api.serializers import UserSerializer


@api_view(http_method_names=["GET"])
def teacher_list_view(request):
    if request.is_secure():
        request.protocol = "https://"
    else:
        request.protocol = "http://"
    q = request.GET.get("q", "")
    query = (
        Q(first_name__icontains=q)
        | Q(last_name__icontains=q)
        | Q(username__icontains=q)
    )
    teachers = User.objects.filter(is_staff=True).filter(query).all()
    context = {"request": request}
    serialized = UserSerializer(teachers, many=True, context=context)
    return Response(serialized.data)


@api_view(http_method_names=["GET"])
def student_list_view(request):
    q = request.GET.get("q", "")
    if request.is_secure():
        request.protocol = "https://"
    else:
        request.protocol = "http://"
    query = (
        Q(first_name__icontains=q)
        | Q(last_name__icontains=q)
        | Q(username__icontains=q)
    )
    students = User.objects.filter(is_staff=False).filter(query).all()
    context = {"request": request}
    serialized = UserSerializer(students, many=True, context=context)
    return Response(serialized.data)
