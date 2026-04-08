from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from datetime import date
from .models import Book, Member, Borrow
from .serializers import (
    BookSerializer, MemberSerializer, 
    BorrowSerializer, UserSerializer
)
from django.contrib.auth.models import User

# ========== LIVRES ==========

@api_view(['GET', 'POST'])
def book_list(request):
    """GET: Liste des livres | POST: Créer un livre"""
    if request.method == 'GET':
        books = Book.objects.all()
        
        # Filtre par catégorie
        category = request.query_params.get('category')
        if category:
            books = books.filter(category__icontains=category)
        
        # Recherche par titre, auteur ou ISBN
        search = request.query_params.get('search')
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(isbn__icontains=search)
            )
        
        # Filtrer les disponibles
        available = request.query_params.get('available')
        if available == 'true':
            books = books.filter(available_copies__gt=0)
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    """GET: Détail d'un livre | PUT: Modifier | DELETE: Supprimer"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def borrow_book(request, pk):
    """Emprunter un livre"""
    book = get_object_or_404(Book, pk=pk)
    member_id = request.data.get('member_id')
    
    if not member_id:
        return Response({'error': 'member_id est requis'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    member = get_object_or_404(Member, pk=member_id)
    
    # Vérifier disponibilité
    if not book.is_available():
        return Response({'error': 'Ce livre n\'est pas disponible'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Créer l'emprunt
    from datetime import date, timedelta
    borrow = Borrow.objects.create(
        book=book,
        member=member,
        due_date=date.today() + timedelta(days=14)
    )
    
    # Décrémenter les copies
    book.available_copies -= 1
    book.save()
    
    serializer = BorrowSerializer(borrow)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ========== MEMBRES ==========

@api_view(['GET', 'POST'])
def member_list(request):
    """GET: Liste des membres | POST: Créer un membre"""
    if request.method == 'GET':
        members = Member.objects.all()
        
        # Filtrer par statut actif
        is_active = request.query_params.get('is_active')
        if is_active == 'true':
            members = members.filter(is_active=True)
        elif is_active == 'false':
            members = members.filter(is_active=False)
        
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Créer d'abord l'utilisateur
        user_data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'password': request.data.get('password')
        }
        
        user = User.objects.create_user(**user_data)
        
        # Créer le membre
        member_data = {
            'user': user.id,
            'phone': request.data.get('phone'),
            'address': request.data.get('address')
        }
        
        serializer = MemberSerializer(data=member_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        user.delete()  # Nettoyer si erreur
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def member_detail(request, pk):
    """GET: Détail d'un membre | PUT: Modifier | DELETE: Supprimer"""
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'GET':
        serializer = MemberSerializer(member)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user = member.user
        member.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def member_borrows(request, pk):
    """Récupérer les emprunts d'un membre"""
    member = get_object_or_404(Member, pk=pk)
    borrows = member.borrows.all()
    
    # Filtrer par statut
    is_returned = request.query_params.get('is_returned')
    if is_returned == 'true':
        borrows = borrows.filter(is_returned=True)
    elif is_returned == 'false':
        borrows = borrows.filter(is_returned=False)
    
    serializer = BorrowSerializer(borrows, many=True)
    return Response(serializer.data)

# ========== EMPRUNTS ==========

@api_view(['GET', 'POST'])
def borrow_list(request):
    """GET: Liste des emprunts | POST: Créer un emprunt"""
    if request.method == 'GET':
        borrows = Borrow.objects.all()
        
        # Filtrer par membre
        member_id = request.query_params.get('member_id')
        if member_id:
            borrows = borrows.filter(member_id=member_id)
        
        # Filtrer par livre
        book_id = request.query_params.get('book_id')
        if book_id:
            borrows = borrows.filter(book_id=book_id)
        
        # Filtrer par statut
        is_returned = request.query_params.get('is_returned')
        if is_returned == 'true':
            borrows = borrows.filter(is_returned=True)
        elif is_returned == 'false':
            borrows = borrows.filter(is_returned=False)
        
        # Emprunts en retard
        overdue = request.query_params.get('overdue')
        if overdue == 'true':
            borrows = borrows.filter(is_returned=False, due_date__lt=date.today())
        
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        book_id = request.data.get('book')
        member_id = request.data.get('member')
        
        book = get_object_or_404(Book, pk=book_id)
        member = get_object_or_404(Member, pk=member_id)
        
        # Vérifications
        if not book.is_available():
            return Response({'error': 'Livre non disponible'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'emprunt
        from datetime import date, timedelta
        borrow = Borrow.objects.create(
            book=book,
            member=member,
            due_date=request.data.get('due_date', date.today() + timedelta(days=14))
        )
        
        book.available_copies -= 1
        book.save()
        
        serializer = BorrowSerializer(borrow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
def borrow_detail(request, pk):
    """GET: Détail d'un emprunt | DELETE: Supprimer"""
    borrow = get_object_or_404(Borrow, pk=pk)
    
    if request.method == 'GET':
        serializer = BorrowSerializer(borrow)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        borrow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def return_book(request, pk):
    """Retourner un livre emprunté"""
    borrow = get_object_or_404(Borrow, pk=pk)
    
    if borrow.is_returned:
        return Response({'error': 'Ce livre a déjà été retourné'},
                       status=status.HTTP_400_BAD_REQUEST)
    
    borrow.return_date = date.today()
    borrow.is_returned = True
    borrow.save()
    
    # Incrémenter les copies disponibles
    borrow.book.available_copies += 1
    borrow.book.save()
    
    return Response({'status': 'Livre retourné avec succès'})

# ========== TABLEAU DE BORD ==========

@api_view(['GET'])
def dashboard(request):
    """Statistiques du tableau de bord"""
    total_books = Book.objects.count()
    total_members = Member.objects.filter(is_active=True).count()
    available_books = Book.objects.filter(available_copies__gt=0).count()
    active_borrows = Borrow.objects.filter(is_returned=False).count()
    overdue_borrows = Borrow.objects.filter(
        is_returned=False, 
        due_date__lt=date.today()
    ).count()
    
    # Emprunts récents
    recent_borrows = Borrow.objects.filter(
        is_returned=False
    ).order_by('-borrow_date')[:5]
    
    # Livres populaires
    popular_books = Book.objects.annotate(
        borrow_count=Count('borrows')
    ).order_by('-borrow_count')[:5]
    
    return Response({
        'total_books': total_books,
        'total_members': total_members,
        'available_books': available_books,
        'active_borrows': active_borrows,
        'overdue_borrows': overdue_borrows,
        'recent_borrows': BorrowSerializer(recent_borrows, many=True).data,
        'popular_books': BookSerializer(popular_books, many=True).data
    })
