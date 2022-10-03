import datetime
import io
import re
import logging

from django.shortcuts import render
from rest_framework import status
from apps.library.models import *
from django.http import JsonResponse, FileResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from apps.library.serializers import *
import pickle
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import jwt, datetime

logger = logging.getLogger('__name__')

@api_view(['GET', 'POST', 'DELETE'])
def books_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        books.query = pickle.loads(pickle.dumps(books.query))
        title = request.GET.get('title', None)
        if title is not None:
            books = books.filter(movie__icontains=title)
        movies_serializer = BookSerializer(books, many=True)

        logging.basicConfig(filename='info.log', filemode='w', format='%(asctime)s - %(name)s % - %(level)s - %(message)s')
        logging.warning('TEST')
        return render(request, 'index.html', {'books': movies_serializer.data})

    elif request.method == 'POST':
        book_data = JSONParser().parse(request)
        movie_serializer = BookSerializer(data=book_data)
        if movie_serializer.is_valid():
            movie_serializer.save()
            return JsonResponse(movie_serializer.data, status=status.HTTP_201_CREATED)
        logger.critical(status)
        return JsonResponse(movie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Book.objects.all().delete()
        return JsonResponse({'message': '{} Книги были удалены!'.format(count[0])},
                            status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
def sign_up(request):
    registration_data = JSONParser().parse(request)
    registration_serializer = RegistrationSerializer(data=registration_data)
    pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
    pswd = registration_data.get('email')
    if re.search(pattern, pswd):
        if registration_serializer.is_valid():
            registration_serializer.save()
            return JsonResponse(registration_serializer.data, status.HTTP_201_CREATED)
        print("email is invalid")
    return JsonResponse(registration_serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_list(request):
    users = User.objects.all()
    users.query = pickle.loads(pickle.dumps(users.query))
    print(users.query)
    users.reverse()
    print(users.reverse())

    email = request.GET.get('email', None)
    if email is not None:
        users = users.filter(user__icontains=email)
    register_serializer = RegistrationSerializer(users, many=True)
    return JsonResponse(register_serializer.data, safe=False)


@api_view(['GET', 'POST', 'DELETE'])
def books_by_id(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return JsonResponse({'message: Movie does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        movie_serializer = BookSerializer(book)
        return JsonResponse(movie_serializer.data)

    elif request.method == "PUT":
        new_data = JSONParser().parse(request)
        movie_serializer = BookSerializer(book, data=new_data)
        if movie_serializer.is_valid():
            movie_serializer.save()
            return JsonResponse(movie_serializer.data)
        return JsonResponse(movie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        book.delete()
        return JsonResponse({'message: the book was deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def unpublished_movies(request):
    books = Book.objects.filter(published=False)
    if request.method == 'GET':
        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)


class RegisterView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        container = JSONParser().parse(request)
        print(container)
        input_email = container.get("email")
        print(input_email)
        if re.search(pattern, input_email):
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response("Invalid email")
        return Response("Invalid email")


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Пользователь не найден")

        if not user.check_password(password):
            raise AuthenticationFailed("Не правильный пароль")

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        user.last_login = datetime.datetime.utcnow()
        user.is_active = True
        user.save()
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            "jwt": token,
        }
        return response


def get_login(request):
    logger.info('test')
    return render(request, 'index.html')

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Пользователь не авторизован")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Пользователь не авторизован")

        user = User.objects.filter(id=payload['id']).first()

        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):

        email = request.data['email']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Пользователь не найден")

        if user.is_active == True:
            user.is_active = False
            user.save()

        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Успешно вышли из аккаунта'
        }

        return response
