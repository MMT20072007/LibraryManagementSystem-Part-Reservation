from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import date, timedelta

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    price = models.PositiveIntegerField()

class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

def clean(self):
    super().clean()
    if self.start_date > self.end_date:
        raise ValidationError('End date must be after start date.')
    if date.today() > self.start_date:
        raise ValidationError('Start date must be in the future.')
    if not self.user.is_superuser and not self.user.is_staff:
        reservations_this_month = Reservation.objects.filter(user=self.user, start_date__month=date.today().month).count()
        reservations_last_month = Reservation.objects.filter(user=self.user, start_date__month=date.today().month-1).count()
        total_payment = Reservation.objects.filter(user=self.user, start_date__range=[date.today()-timedelta(days=30), date.today()]).aggregate(Sum('book__price'))
        if reservations_last_month > 3 or total_payment > 300000:
            self.end_date = self.start_date + timedelta(days=14)  # Special members can reserve books for 2 weeks
        else:
            self.end_date = self.start_date + timedelta(days=7)  # Normal members can reserve books for 1 week

class MemberStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_special_member = models.BooleanField(default=False)

class ReservationList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reservations = models.ManyToManyField(Reservation)
