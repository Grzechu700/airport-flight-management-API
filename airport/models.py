from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "airport"
        ordering = ["name"]


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "airplane_type"
        ordering = ["name"]


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "crew"
        ordering = ["last_name"]
