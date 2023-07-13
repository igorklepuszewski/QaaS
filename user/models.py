from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

# Create your models here.


class Role(models.Model):
    ADMIN = 1
    CREATOR = 2
    PARTICIPANT = 3
    ROLE_CHOICES = (
        (ADMIN, "admin"),
        (CREATOR, "creator"),
        (PARTICIPANT, "participant"),
    )

    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")

        user = self.model(email=self.normalize_email(email), username=username)
        if password is not None:
            user.set_password(password)
        user.save(using=self._db)
        user.roles.add(Role.PARTICIPANT)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        if not password:
            raise ValueError("A superuser must have a password.")
        user = self.create_user(
            email=self.normalize_email(email), username=username, password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.roles.add(Role.ADMIN, Role.CREATOR, Role.PARTICIPANT)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    roles = models.ManyToManyField(
        Role,
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def check_role(self, role):
        return self.roles.filter(id=role).exists()
