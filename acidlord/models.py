from django.db import models


class Strain(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    sort_description = models.CharField(max_length=500)


class Agronom(models.Model):
    nickname = models.CharField(max_length=50, unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, unique=True, blank=False)
    email = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=50, blank=False)


class Customer(models.Model):
    nickname = models.CharField(max_length=50, unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, unique=True, blank=False)
    email = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=50, blank=False)


class Harvest(models.Model):
    strain_id = models.ForeignKey(to=Strain, on_delete=models.CASCADE)
    agronom = models.ForeignKey(to=Agronom, on_delete=models.DO_NOTHING)
    gen_quantity = models.FloatField(blank=False)
    unit_price = models.FloatField(blank=False)
    harvest_time = models.DateTimeField(blank=False, auto_now_add=True)
    shelf_life = models.CharField(max_length=30, blank=False)
    description = models.CharField(max_length=500, blank=False)
    photo = models.CharField(max_length=200, blank=True)


class ShoppingCart(models.Model):
    customer_id = models.ForeignKey(to=Customer, on_delete=models.CASCADE)


class Harvest2Cart(models.Model):
    cart_id = models.ForeignKey(to=ShoppingCart, on_delete=models.CASCADE)
    harvest_id = models.ForeignKey(to=Harvest, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=False)
    final_price = models.FloatField(blank=False)


class Order(models.Model):
    cart_id = models.ForeignKey(to=ShoppingCart, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=150, blank=False)
    order_time = models.DateTimeField(blank=False, auto_now_add=True)
    done = models.BooleanField(blank=False, default=False)
    returned = models.BooleanField(blank=False, default=False)


class Feedback(models.Model):
    customer_id = models.ForeignKey(to=Customer, on_delete=models.DO_NOTHING)
    feedback_time = models.DateTimeField(blank=False, auto_now_add=True)
    text = models.CharField(max_length=1000, blank=False)


class Vacation(models.Model):
    date = models.DateTimeField(blank=False)
    description = models.CharField(max_length=400, blank=False)


class Agronom2Vacation(models.Model):
    agronom = models.ForeignKey(to=Agronom, on_delete=models.DO_NOTHING)
    vacation = models.ForeignKey(to=Vacation, on_delete=models.DO_NOTHING)


class Prob(models.Model):
    agronom = models.ForeignKey(to=Agronom, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(to=Customer, on_delete=models.DO_NOTHING)
    harvest = models.ForeignKey(to=Harvest, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(blank=False, auto_now_add=True)