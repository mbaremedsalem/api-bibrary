from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Member, Borrow

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Member
        fields = '__all__'

class BorrowSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    member_name = serializers.ReadOnlyField(source='member.user.username')
    
    class Meta:
        model = Borrow
        fields = '__all__'