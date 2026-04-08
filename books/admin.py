from django.contrib import admin

from books.models import *

# Register your models here.



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    pass
