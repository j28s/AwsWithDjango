from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=8, verbose_name="이름")

    def __str__(self):
        return self.name

    class Meta:
        db_table = '조직도'
        verbose_name = '조직도'
        verbose_name_plural = '조직도'


