from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Contact,Product,Customer,Cart,Payment,OrderPlaced
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import CustomerProfileForm
from django.views import View
from django.db.models import Q
from django.conf import settings
import razorpay
# Create your views here.

def base(request): 
    return render(request,'base.html')


def index(request):
    return render(request,'index.html')


def contact_us(request):
    context={}
    if request.method=="POST":
        # here request.post is dict
        name=request.POST.get("name")
        em=request.POST.get("email")
        sub=request.POST.get("subject")
        msz=request.POST.get("message")

        obj=Contact(name=name,email=em,subject=sub,message=msz)
        obj.save()
        context['message']=f"Dear {name}, Thanks for your time! "
    return render(request,'contact.html',context)


def about(request):
    return render(request,'about.html')





def register(request):
    context={}
    if request.method=="POST":
        uname=request.POST.get('username')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        password=request.POST.get('password')
        c_password=request.POST.get('confirm_password')

        if password!=c_password:
            context["errmsg"]="Password and Confirm password not matched"
            return render(request,"register.html",context)
            # here uname is a variable and username is a name of that form

        else:
            my_user=User.objects.create_user(uname,email,password)
            my_user.save()
            return redirect('login')
    else:
        return render(request,'register.html')



def user_login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        pass1 = request.POST.get("pass")
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            # Check if user is a staff/admin
            if user.is_staff:
                messages.error(request, "Admins should use the admin panel for login.")
                return redirect('login')  # Redirect to login for customers
            
            # Login customer and set session flag
            login(request, user)
            request.session['is_customer'] = True
            return redirect('profile')
        else:
            context["wrong"] = "Username and Password is Incorrect"
            return render(request, "login.html", context)
    return render(request, "login.html")



def profile(request):
    if request.method == "POST":
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            pincode = form.cleaned_data['pincode']

            # Check if a customer profile already exists
            customer, created = Customer.objects.get_or_create(user=user)
            customer.name = name
            customer.locality = locality
            customer.city = city
            customer.mobile = mobile
            customer.pincode = pincode
            customer.save()

            messages.success(request, "Congratulations! Profile saved successfully.")
    else:
        form = CustomerProfileForm()

    return render(request, 'profile.html', {'form': form})




def Logout(request):
    logout(request)
    return redirect('login')



def address(request):
    add= Customer.objects.filter(user=request.user)
    return render(request,'address.html',locals())



class CategoryView(View):
    def get(self, request, val):
        # Filter products by the category
        product = Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        # Pass the filtered products to the template
        return render(request, "category.html", locals())


@login_required(login_url='login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "productdetail.html", {"product": product})


@login_required(login_url='login')
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("showcart")



@login_required(login_url='login')
def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity * p.product.discounted_price
        amount=amount+value
    totalamount=amount+40
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'addtocart.html',locals())

def updateqty(request, x, cid):
    try:
        cart_item = Cart.objects.get(id=cid)
        if x == '1':
            cart_item.quantity += 1
        elif x == '0' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()
    except Cart.DoesNotExist:
        messages.error(request, "Cart item not found.")
    return redirect('showcart')



def remove_from_cart(request, product_id):
    cart_item = Cart.objects.filter(user=request.user, product__id=product_id).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Cart item not found.")
    return redirect('showcart')




class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value=p.quantity * p.product.discounted_price
            famount=famount+value
        totalamount=famount+40
        razoramount=int(totalamount*100)
        client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data={ "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12" }
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
             payment = Payment(
             user=user,
             amount=totalamount,
             razorpay_order_id=order_id,
             razorpay_payment_status=order_status
            )
             payment.save()
        return render(request,'checkout.html',locals())


def payment_done(request):
    # Extract parameters from GET request
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    # Ensure all parameters are present
    if not (order_id and payment_id and cust_id):
        messages.error(request, "Invalid payment parameters. Please try again.")
        return redirect("orders")  # Redirect to homepage if parameters are missing

    user = request.user

    # Fetch customer and payment details safely
    try:
        customer = get_object_or_404(Customer, id=cust_id)
        payment = get_object_or_404(Payment, razorpay_order_id=order_id)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("orders")

    # Update Payment details
    if not payment.paid:  # Avoid processing already-paid payments
        payment.paid = True
        payment.razorpay_payment_id = payment_id
        payment.save()

        # Place Orders and Clear the Cart
        cart = Cart.objects.filter(user=user)
        if not cart.exists():
            messages.error(request, "Your cart is empty. Cannot place order.")
            return redirect("orders")

        for item in cart:
            try:
                OrderPlaced.objects.create(
                    user=user,
                    customer=customer,
                    product=item.product,
                    quantity=item.quantity,
                    payment=payment
                )
                item.delete()  # Remove items from the cart after order is placed
            except Exception as e:
                messages.error(request, f"Failed to process item '{item.product.title}': {str(e)}")

    # Redirect to homepage after processing
    messages.success(request, "Your payment was successful! Your order has been placed.")
    return redirect("orders")



def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'orders.html',locals())