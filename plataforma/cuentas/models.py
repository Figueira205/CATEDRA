from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    """Usuarios identificados por correo electrónico (sin nombre de usuario)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not (extra["is_staff"] and extra["is_superuser"]):
            raise ValueError("Un superusuario necesita is_staff e is_superuser.")
        return self._create_user(email, password, **extra)


class Usuario(AbstractUser):
    """Estudiantes, profesores y administración comparten este modelo.

    - Estudiante: usuario normal (is_staff=False). Solo usa «Mi cuenta».
    - Profesor/editor: is_staff=True + grupo «Editores» o «Colaboradores».
    - Administración: superusuario.
    """

    username = None
    email = models.EmailField("correo electrónico", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.email
