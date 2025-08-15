"""
URL configuration for PizzaProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from PizzaApp import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/',views.base),
    path('',views.index,name='index'),
    path('contact/',views.contact_us,name='contact'),
    path('about/',views.about,name='about'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.Logout,name='logout'),
    path('checkout/',views.checkout.as_view(),name='checkout'),
    path('profile/',views.profile,name='profile'),
    path('address/',views.address,name='address'),
    path('category/<slug:val>',views.CategoryView.as_view(),name='category'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('cart/',views.show_cart,name='showcart'),
    path("paymentdone/", views.payment_done, name="paymentdone"),
    path("orders/",views.orders,name="orders"),

    path('updateqty/<str:x>/<int:cid>/', views.updateqty, name='updateqty'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
