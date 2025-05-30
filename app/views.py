from django.shortcuts import render,HttpResponseRedirect,redirect ,get_object_or_404
from django.views import View
from app.models import *
from app.forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import  Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ProductView(View):
 
 def get(self,request):
  topwears=Product.objects.filter(category="TW")
  bottomwear=Product.objects.filter(category="BW")
  mobiles=Product.objects.filter(category='M')
  return render(request, 'app/home.html',{'topwears':topwears,'bottomwear':bottomwear,'mobiles':mobiles})

class ProductDetailView(View):
    def get(self,request,pk):
         product=Product.objects.get(pk=pk)
         item_already_in_cart=False
         if request.user.is_authenticated:
          item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
         return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart})


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    
    if product_id is None:
        # Handle the case where no product_id is provided
        messages.error(request, "No product ID provided.")
        return HttpResponseRedirect('/cart')

    try:
        product = Product.objects.get(id=product_id)
        Cart(user=user, product=product).save()
        messages.success(request, "Product added to cart successfully.")
    except Product.DoesNotExist:
        # Handle the case where the product does not exist
        messages.error(request, "The product does not exist.")
    
    return HttpResponseRedirect('/cart')

def plus_cart(request):
  if request.method=="GET":
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity+=1
    c.save()
    
    amount=0.0
    shipping_amount=70.00
    
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    for p in cart_product:
        
        temp_amount=(p.quantity * p.product.discounted_price)
        amount+=temp_amount
        

    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount+shipping_amount
        }

    return JsonResponse(data)
  
def minus_cart(request):
  if request.method=="GET":
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity-=1
    c.save()
    
    amount=0.0
    shipping_amount=70.00
    
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    for p in cart_product:
        
        temp_amount=(p.quantity * p.product.discounted_price)
        amount+=temp_amount
        

    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount+shipping_amount
        }

    return JsonResponse(data)
  
@login_required  
def remove_cart(request):
  if request.method=="GET":
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    
    c.delete()
    
    amount=0.0
    shipping_amount=70.00
    
    cart_product=[p for p in Cart.objects.all() if p.user==request.user]
    for p in cart_product:
        
        temp_amount=(p.quantity * p.product.discounted_price)
        amount+=temp_amount
        

    data={
      
      'amount':amount,
      'totalamount':amount+shipping_amount
        }

    return JsonResponse(data)
@login_required
def show_cart(request):
  if request.user.is_authenticated:
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.00
    total_amount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user==user]

    if cart_product:
      for p in cart_product:
        temp_amount=(p.quantity * p.product.discounted_price)
        amount+=temp_amount
        total_amount=amount+shipping_amount

        return render(request,'app/showcart.html',{'carts':cart,'total_amount':total_amount,'amount':amount})
      
    else:
      return render(request,'app/emptycart.html')

@login_required
def checkout(request):
  user=request.user
  add=Customer.objects.filter(user=user)
  cart_items=Cart.objects.filter(user=user)
  amount=0.0
  shipping_amount=70.0
  total_amount=0.0
  cart_product=[p for p in Cart.objects.all() if p.user==user]
  if cart_product:
    for p in cart_product:
        temp_amount=(p.quantity * p.product.discounted_price)
        amount+=temp_amount
    total_amount=amount+shipping_amount
  context={'add':add,'total_amount':total_amount,'cart_items':cart_items}
  return render(request,'app/checkout.html',context)

@login_required
def payment_done(request):
  user=request.user
  custid=request.GET.get('custid')
  customer=Customer.objects.get(id=custid)
  cart=Cart.objects.filter(user=user)

  for c in cart:
    OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
    c.delete()

  return redirect('orders')

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def address(request):
 add=Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})

@login_required
def orders(request):
 op=OrderPlaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html',{'Order_Placed':op})


def change_password(request):
 return render(request, 'app/changepassword.html')

def mobile(request,data=None):
   if data==None:
     mobiles=Product.objects.filter(category='M')
   elif data=='Motorola' or data=='SAMSUNG':
     mobiles=Product.objects.filter(category='M').filter(brand=data)
   elif data=='Below':
     mobiles=Product.objects.filter(category='M').filter(discounted_price__lt=20000)
   elif data=='Above':
     mobiles=Product.objects.filter(category='M').filter(discounted_price__gt=20000)

   return render(request, 'app/mobile.html',{'mobiles':mobiles})

def laptop(request,data=None):
   if data==None:
     laptop=Product.objects.filter(category='L')
   elif data=='ASUS' or data=='Acer' or data=='Lenovo' or data=='HP':
     laptop=Product.objects.filter(category='L').filter(brand=data)
   elif data=='Below':
     laptop=Product.objects.filter(category='L').filter(discounted_price__lt=40000)
   elif data=='Above':
     laptop=Product.objects.filter(category='L').filter(discounted_price__gt=40000)

   return render(request, 'app/laptop.html',{'laptop':laptop})

def tops(request,data=None):
  if data==None:
    topwear=Product.objects.filter(category='TW')
  elif data=='Dokotoo' or data=='ANRABESS' or data=='QINSEN':
    topwear=Product.objects.filter(category='TW').filter(brand=data)
  elif data=='Below':
    topwear=Product.objects.filter(category='TW').filter(discounted_price__lt=500)
  elif data=='Above':
    topwear=Product.objects.filter(category='TW').filter(discounted_price__gt=500)
  return render(request,'app/topwear.html',{'topwear':topwear})

def bottoms(request,data=None):
  if data==None:
    bottomwear=Product.objects.filter(category='BW')
  elif data=='AEROPOSTALE' or data=='NIMIN' or data=='Sidefeel' or data=='Lee':
    bottomwear=Product.objects.filter(category='BW').filter(brand=data)
  elif data=='Below':
    bottomwear=Product.objects.filter(category='BW').filter(discounted_price__lt=1000)
  elif data=='Above':
    bottomwear=Product.objects.filter(category='BW').filter(discounted_price__gt=1000)
  return render(request,'app/bottomwear.html',{'bottomwear':bottomwear})



class CustomerRegistrationView(View):
  def get(self,request):
    form=CustomerRegistrationForm()
    return render(request, 'app/customerregistration.html',{'form':form})
  def post(self,request):
    form=CustomerRegistrationForm(request.POST)
    if form.is_valid():
      
      form.save()
      messages.success(request,'Account Registered Successfully')
      return render(request, 'app/customerregistration.html',{'form':form})

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
  def get(self,request):
    form=CustomerProfileForm()
    return render(request,'app/profile.html',{'form':form})
  def post(self,request):
    form=CustomerProfileForm(request.POST)
    if form.is_valid():
      usr=request.user
      name=form.cleaned_data['name']
      locality=form.cleaned_data['locality']
      city=form.cleaned_data['city']
      state=form.cleaned_data['state']
      zipcode=form.cleaned_data['zipcode']
      reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
      reg.save()
      messages.success(request,'Profile Created Successfully')
    return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})