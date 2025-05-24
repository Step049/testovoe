from django.db import models

#создание класса к счастью у проекта с рандомами можно найти пример инфы о пользователях
#адрес полностью взят с сайта, хотя по идее требований к полноте адреса нет

class User(models.Model):
    gender = models.CharField(max_length=10)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    picture_thumbnail = models.URLField()
    picture_large = models.URLField()

    class Meta:
        ordering = ['id']


# полный адресс для подробной инфы
    @property
    def address(self):
        return f"{self.street}, {self.city}, {self.state} {self.postcode}"