from django.db import models

# Create your models here.
from good.models import Goods, Size, Color
from userapp.models import UserInfo


class CartItem(models.Model):
    goodid = models.PositiveIntegerField()
    sizeid = models.PositiveIntegerField()
    colorid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    is_delete = models.BooleanField(default=False)
    user = models.ForeignKey(UserInfo,on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ['goodid','colorid','sizeid']

    def getGood(self):
        return Goods.objects.get(id=self.goodid)

    def getSize(self):
        return Size.objects.get(id=self.sizeid)

    def getColor(self):
        return Color.objects.get(id=self.colorid)

    def getTotalPrice(self):
        import math
        return math.ceil(float(self.getGood().price) * ((int)(self.count)))

    def __str__(self):
        return u'goodid:%s' % self.goodid




