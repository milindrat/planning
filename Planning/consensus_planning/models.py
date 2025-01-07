from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# Create your models here.


class Item(models.Model):
    Sr_No = models.AutoField(primary_key=True)
    Item_Category_1=models.CharField(max_length=50)
    Item_code=models.CharField(max_length=100)
    Description=models.CharField(max_length=200)
    Item_Category_2=models.CharField(max_length=50)
    Location=models.CharField(max_length=50)
    Dc=models.CharField(max_length=50)
    Supplier=models.CharField(max_length=100)
    ABC_class_Revenue=models.CharField(max_length=50)
    ABC_percentage_Revenue=models.DecimalField(max_digits=10, decimal_places=2)
    On_hand=models.IntegerField()
    Available_on_hand=models.IntegerField()
    Days_of_supply=models.IntegerField()
    To_ship=models.IntegerField()
    To_receive=models.IntegerField()
    #user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    finalized_quantity = models.IntegerField(null=True, blank=True)
    last_submitted_quantity = models.IntegerField(null=True, blank=True, verbose_name="Last submitted quantity") 
    
    class Meta:
        permissions = [
            ("can_upload", "Can upload file"),
            ("can_edit", "Can edit"),
            ("can_view","can view page")
        ]

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Expecting the user to be passed explicitly

        # If finalized_quantity is updated, log the change
        if self.pk:  # Only check if it's an existing item (not a new one)
            previous_item = Item.objects.get(pk=self.pk)  # Get the existing item from the database

            if previous_item.finalized_quantity != self.finalized_quantity:
                # If finalized_quantity has changed, log the change
                if user is not None:
                    audit=ItemAudit.objects.create(
                        item=self,
                        user=user,
                        previous_finalized_quantity=previous_item.finalized_quantity,
                        new_finalized_quantity=self.finalized_quantity,
                        action='update'
                    )
                    print(audit.user_name)

        # Update last_submitted_quantity to the value of finalized_quantity
        if self.finalized_quantity is not None:
            self.last_submitted_quantity = self.finalized_quantity

        super().save(*args, **kwargs)  # Call the original save method 


# Assuming you're using the default User model

class ItemAudit(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # Link to the Item being edited
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user making the change
    previous_finalized_quantity = models.IntegerField(null=True, blank=True)
    new_finalized_quantity = models.IntegerField()
    #user_name = models.CharField(max_length=255) 
    timestamp = models.DateTimeField(auto_now=True)   # Timestamp when the change occurred
    action = models.CharField(max_length=20, choices=[('update', 'Update'), ('create', 'Create')])

    
    def save(self, *args, **kwargs):
        # Automatically set the user_name before saving the record
        if self.user:
            self.user_name = self.user.username  # Set the user_name to the username of the related user
        super().save(*args, **kwargs)


        

class MyAccountManager(BaseUserManager):
    def create_user(self,email,username,password=None):
        if not email:
            raise ValueError('User must have an email.')
        if not username:
            raise ValueError('User must have an username.')
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,username,password):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)

        return user


class Account(AbstractBaseUser):
    email=models.EmailField(verbose_name='email',max_length=60,unique=True)
    username=models.CharField(max_length=40,unique=True)
    fname = models.CharField(max_length=50, verbose_name="First Name", blank=True)
    lname = models.CharField(max_length=50, verbose_name="Last Name", blank=True)
    date_joined=models.DateTimeField(verbose_name='date joined',auto_now_add=True)
    last_login=models.DateTimeField(verbose_name='last login',auto_now=True)
    is_admin=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    hode_email=models.BooleanField(default=True)
    objects=MyAccountManager()
    USERNAME_FIELD='username'
    REQUIRED_FIELDS=['username']
