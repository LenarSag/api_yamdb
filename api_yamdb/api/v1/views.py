from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet, PatchModelMixin
from .permissions import (
    IsSuperUser,
    IsSuperUserOrReadOnly,
    ReadOrAuthenticatedOrInAuthorModerAdmin
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserCreateSerializer,
    UserRecieveTokenSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CategoryViewSet(ListCreateDestroyViewSet):
    """Вьюсет получения, добавления и удаления категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (
        IsSuperUserOrReadOnly,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'name',
    )
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет получения, добавления и удаления жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (
        IsSuperUserOrReadOnly,
    )
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'name',
    )
    lookup_field = 'slug'


class TitleViewSet(
    ListCreateDestroyViewSet,
    mixins.RetrieveModelMixin,
    PatchModelMixin
):
    """Вьюсет получения, добавления и удаления произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('rating')
    serializer_class = TitleSerializer
    permission_classes = (
        IsSuperUserOrReadOnly,
    )
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = TitleFilter

    def perform_update(self, serializer):
        self.perform_create(serializer)

    def perform_create(self, serializer):
        serializer.save(
            category=get_object_or_404(
                Category,
                slug=self.request.data.get('category')
            ),
            genre=Genre.objects.filter(
                slug__in=self.request.data.getlist('genre')
            ),
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """Функция для создания новых пользователей."""
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Функция для получения токена."""
    serializer = UserRecieveTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        message = {'confirmation_code': 'Некорректный код подтверждения'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    message = {'token': str(AccessToken.for_user(user))}
    return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет получения/создания/обновления/удаления пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUser,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        url_path=r'(?P<username>[\w.@+-]+)',
    )
    def user_by_username(self, request, username):
        """Извлечение данных пользователя админом."""
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @user_by_username.mapping.patch
    def update_user_by_username(self, request, username):
        """Обновление пользователя админом."""
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @user_by_username.mapping.delete
    def delete_user_by_username(self, request, username):
        """Удаление пользователя админом."""
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def myself(self, request):
        """Позволяет пользователю получить информацию о себе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @myself.mapping.patch
    def update_myself(self, request):
        """Позволяет пользователю обновить информацию о себе."""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(
    ListCreateDestroyViewSet,
    mixins.RetrieveModelMixin,
    PatchModelMixin
):
    """Вьюсет получения/создания/обновления/удаления комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (ReadOrAuthenticatedOrInAuthorModerAdmin,)

    def get_queryset(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        ).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review,
                id=self.kwargs.get('review_id')
            )
        )


class ReviewViewSet(
    ListCreateDestroyViewSet,
    mixins.RetrieveModelMixin,
    PatchModelMixin
):
    """Вьюсет получения/создания/обновления/удаления ревью."""

    serializer_class = ReviewSerializer
    permission_classes = (ReadOrAuthenticatedOrInAuthorModerAdmin,)

    def get_queryset(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title,
                id=self.kwargs.get('title_id')
            )
        )
