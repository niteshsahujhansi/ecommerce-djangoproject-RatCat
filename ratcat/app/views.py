# from itertools import product
# from unicodedata import category
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import Customer, Product, OrderPlaced, cart
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required # for function based view
from django.utils.decorators import method_decorator # for class based view

# def home(request):
#     return render(request, 'app/home.html')

class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles': mobiles})


# def product_detail(request):
#     return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False 
        if request.user.is_authenticated:
            item_already_in_cart = cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html' , {'product': product, 'item_already_in_cart':item_already_in_cart})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cartt = cart.objects.filter(user=user)
        # print(cartt)
        amount = 0.0
        shipping_amount = 70
        totalamount = 0.0
        cart_product = [p for p in cart.objects.all() if p.user==user]
        # print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
        return render(request, 'app/addtocart.html', {'carts':cartt, 'totalamount':totalamount, 'amount':amount})

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity +=1
        c.save()
        amount = 0.0
        shipping_amount = 70
        totalamount = 0.0
        cart_product = [p for p in cart.objects.all() if p.user==request.user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
        data={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity -=1
        c.save()
        amount = 0.0
        shipping_amount = 70
        totalamount = 0.0
        cart_product = [p for p in cart.objects.all() if p.user==request.user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
        data={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70
        totalamount = 0.0
        cart_product = [p for p in cart.objects.all() if p.user==request.user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
        data={
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'orderplaced':op})

# def change_password(request):
#  return render(request, 'app/changepassword.html')

# def mobile(request):
#  return render(request, 'app/mobile.html')

def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category = 'M')
    elif data == 'Redmi' or data == 'Oppo':
        mobiles = Product.objects.filter(category = 'M').filter(brand = data)
    elif data == 'below':
        mobiles = Product.objects.filter(category = 'M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category = 'M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

def topwear(request, data=None):
    if data == None:
        topwear = Product.objects.filter(category = 'TW')
    elif data == 'Roadster':
        topwear = Product.objects.filter(category = 'TW').filter(brand = data)
    elif data == 'below':
        topwear = Product.objects.filter(category = 'TW').filter(discounted_price__lt=1000)
    elif data == 'above':
        topwear = Product.objects.filter(category = 'TW').filter(discounted_price__gt=1000)
    return render(request, 'app/topwear.html', {'topwear':topwear})

# def login(request):
#  return render(request, 'app/login.html')
# direct url 

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations!! Registered Successfully")
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70
    totalamount = 0.0
    cart_product = [p for p in cart.objects.all() if p.user==request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'totalamount':totalamount, 'cartitems':cart_items})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cartt = cart.objects.filter(user=user)
    for c in cartt:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('orders')


# def profile(request):
#     return render(request, 'app/profile.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile Updated Successfully')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})