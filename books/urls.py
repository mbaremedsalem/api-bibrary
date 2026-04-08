from django.urls import path
from . import views

urlpatterns = [
    # Livres
    path('books/', views.book_list, name='book-list'),
    path('books/<int:pk>/', views.book_detail, name='book-detail'),
    path('books/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),
    
    # Membres
    path('members/', views.member_list, name='member-list'),
    path('members/<int:pk>/', views.member_detail, name='member-detail'),
    path('members/<int:pk>/borrows/', views.member_borrows, name='member-borrows'),
    
    # Emprunts
    path('borrows/', views.borrow_list, name='borrow-list'),
    path('borrows/<int:pk>/', views.borrow_detail, name='borrow-detail'),
    path('borrows/<int:pk>/return/', views.return_book, name='return-book'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]