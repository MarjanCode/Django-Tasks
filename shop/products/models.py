from django.db import models

class Product(models.Model):
    STATUS_CHOICES = [
        ('Phones', 'phones'),
        ('Smart watches', 'smart watches'),
        ('Cameras', 'cameras'),
        ('Headphones', 'headphones'),
        ('Computers', 'computers'),
        ('Gaming', 'gaming'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=STATUS_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=30)
    brand = models.CharField(max_length=50)
    builtin_memory = models.CharField(max_length=50)
    protection_class = models.CharField(max_length=50)
    screen_diagonal = models.FloatField()
    screen_type = models.CharField(max_length=100)
    battery_capacity = models.IntegerField()
    main_camera = models.CharField(max_length=100)
    front_camera = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
       

class Image(models.Model):
    product= models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Image for {self.product.name}"
      
class Review(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    product= models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review for {self.product.name}"


    
