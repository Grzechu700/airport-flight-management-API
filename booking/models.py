from django.db import models
from django.contrib.auth import get_user_model


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user}"

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]
