from django.db.models import Q, Subquery, F, Count, Max, Sum, Func
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from faker import Faker

from apps.models import Product, Car, Category


# Create your views here.


def add_product(request):
    faker = Faker()
    for _ in range(10):
        Product.objects.create(name=faker.name(),
                               description=faker.sentence(),
                               price=faker.random_number(digits=3))
    return HttpResponse(content={"success"})


def django_orm(request):
    # barcha productlarni olish
    products = Product.objects.all()

    # sqldagi querysini chiqarish
    query = str(Product.objects.all().query)

    # filter qilish
    products = Product.objects.filter(price__gt=600)

    # Q ma'lum bir shatga to'g'ri keladigan query yozish va or operatoridan foydalanish
    products = Product.objects.filter(Q(price__gt=600) | Q(name__startswith='Brenda'))

    # xuddi tepadagi narsani Q siz yozish
    products = Product.objects.filter(price__gt=600) | Product.objects.filter(name__startswith='Brenda')

    # and operatoridan foydalanish
    products = Product.objects.filter(price__lt=600, name__startswith='Brenda')

    # tepadagi and operatoridan foydalanishni 2-versiyasi
    products = Product.objects.filter(price__lt=600) & Product.objects.filter(name__startswith='Brenda')

    # teapadagi and operatoridan foydalanishni 3-versiyasi
    products = Product.objects.filter(Q(price__lt=600) & Q(name__startswith='Brenda'))

    # not operatoridan foydalanish
    products = Product.objects.filter(~Q(price__gt=600) & Q(name__startswith='Brenda'))

    # inkor ma'nosini berishni 2 - usuli
    products = Product.objects.exclude(Q(price__gt=600))

    # values_listdan foydalanish bizga tuple qaytaradi
    products = Product.objects.all().values_list('id', 'name')

    # values_list bilan deyarli bir xil faqat dictionary qaytaradi
    products = Product.objects.all().values('id', 'name')

    # values bilan deyarli bir xil faqat only id ni yozmasak ham qo'shib yuboradi
    products = Product.objects.all().only('name')

    # ikkala tabledan name va pricelarni olib bitta o'zgaruvchiga berib yuborayapmiz va buning uchun union foydalanayapmiz
    products = Product.objects.all().values_list(
        "name", "price"
    ).union(
        Car.objects.all().values_list(
            "name", "price"
        ))

    # subquerydan foydalanish lekin subqueryni olib tashlasak ham xuddi shu natija chiqadi
    cars = Car.objects.all()
    products = Product.objects.filter(name__in=Subquery(cars.values('name')))

    # order by dan foydalanish
    products = Product.objects.order_by('-name')

    # F dan foydalanib shu modelga tegishli description fieldini olib kelib name bilan solishtiryapmiz
    products = Product.objects.filter(name=F('description'))

    # fayllar uchun ham bir xil
    products = Product.objects.filter(
        Q(image='') | Q(image=None)
    )

    # mana shunday join qilib ishlatib ketaveramiz
    products = Product.objects.filter(category__name='Texnika')

    # category tomndan ham chaqirib ishlataveramzi
    products = Category.objects.filter(product__name='Nusratullo')

    # eng qimmat product
    products = Product.objects.order_by('-price')[0]

    # eng qimmat productlar 5 ligi
    products = Product.objects.order_by('-price')[0:6]


    # bu yerda duplicat bo'lmagan namelarni olyapmiz
    products = Product.objects.values('name').annotate(name_count = Count('name')).filter(name_count = 1)

    # bu yerda esa duplicat bo'lgan namelarni olish
    products = Product.objects.values('name').annotate(name_count=Count('name')).exclude(name_count=1)


    # prodcutni name duplicat bo'lganini olib categoryni namega teng bo'lganini chiqarish
    products = Product.objects.values(
        'name'
    ).annotate(
        name_count=Count('name')
    ).filter(name_count=2)
    records = Category.objects.filter(name__in=[item['name'] for item in products])

    # Q dan foydalanish
    products = Product.objects.filter(
        Q(name__startswith='R') | Q(name__startswith='D')
    )

    # eng katta id ga ega productni topish
    products = Product.objects.all().aggregate(Max('id'))
    print(products['id__max'])

    # barcha pricelarni yig'indisini qaytaryapti
    products = Product.objects.all().aggregate(Sum('price'))
    print(products['price__sum'])

    # databasedan randomniy product olishni samarali usuli
    product = Product.objects.order_by('?').first()

    # Nusrat so'ziga yaqin bo'gan so'zni topish
    products = Product.objects.annotate(
        like_zeus=Func(F('name'), function='levenshtein', template="%(function)s(%(expressions)s, 'Nusrat')"))

    # productlar nechtaligini olish
    products_count = Product.objects.all().count()

    # bir vaqtning o'zida bir nechta category yaratish
    # Category.objects.bulk_create(
    #     [Category(name="Apple"),
    #      Category(name="Hello"),
    #      Category(name="Mortal")]
    # )

    products_count = Product.objects.all().count()
    # print(products_count)
    # har bitta so'rov yuborganimizni xuddi shu productdan yana bitta yaratadi
    # product = Product.objects.first()
    product.pk = None # chunki pk unique agar None qo'ysak databasega borganda avtomatik id qo'yib ketadi
    # product.save()
    # products_count = Product.objects.all().count()
    # print(products_count)


    # delete qilish barcha kategoriyalarni
    # Category.objects.all().delete()

    # oddiy stringni datatimega o'tkazish
    # date_str = "2018-03-11"
    # from datetime import datetime
    # user = Product.objects.get(id=1)
    # temp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    # a2 = Product(name='s',price=12.3,description='ds',date=temp_date)
    # a2.save()

    # namelarini o'sish tartibida pricelarini kamayish tartibida chiqarish
    products = Product.objects.order_by('name', '-price')

    # bu order by qiladi alphabet bo'yicha va katta harflarni birinchiga qo'yadi
    products = Product.objects.order_by('name')
    # print([product.name for product in products])

    # agar katta harflarni ahamiyatini yo'qatmoqchi bo'lsak mana shunday query yozib qo'yamiz
    products = Product.objects.order_by(Lower('name')).values_list('name',flat=True)
    # print([product for product in products])

    # productlarni categorysi bo'yicha order_by qilish
    products = Product.objects.order_by('category__name')

    # categorylarni order_by qilish va uni annotate qilib qo'shinmcha fieldaga berib yuborish
    # products = Category.objects.annotate(
    #     hero_count=Count("name")
    # ).order_by(
    #     "-hero_count"
    # )


    # rasm chiqarish
    # @admin.register(Product)
    # class ProductModelAdmin(admin.ModelAdmin):
    #     list_display = 'name', 'id'
    #     date_hierarchy = 'created_at'
    #     readonly_fields = ["botirjon"]
    #
    #     def botirjon(self, obj: Product):
    #         head = obj.image
    #         return mark_safe(f'<img src="{head.url}" width="200" height="200" />')
    #


    # csv fileni databasega import qilish
    # class ExportCsvMixin:
    #     def export_as_csv(self, request, queryset):
    #         meta = self.model._meta
    #         field_names = [field.name for field in meta.fields]
    #
    #         response = HttpResponse(content_type='text/csv')
    #         response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    #         writer = csv.writer(response)
    #
    #         writer.writerow(field_names)
    #         for obj in queryset:
    #             row = writer.writerow([getattr(obj, field) for field in field_names])
    #
    #         return response
    #
    #     export_as_csv.short_description = "Export Selected"
    #
    #
    # class CsvImportForm(forms.Form):
    #     csv_file = forms.FileField()

    # @admin.register(Tag)
    # class TagModelAdmin(admin.ModelAdmin, ExportCsvMixin):
    #     actions = ['export_as_csv']
    #     change_list_template = "apps/tags_changelist.html"
    #
    #     def get_urls(self):
    #         urls = super().get_urls()
    #         my_urls = [
    #             path('import-csv/', self.import_csv),
    #         ]
    #         return my_urls + urls
    #
    #     def import_csv(self, request):
    #         if request.method == "POST":
    #             csv_file = request.FILES["csv_file"]
    #             decoded_file = csv_file.read().decode('utf-8')
    #             io_string = io.StringIO(decoded_file)
    #             bulk = []
    #             for row in csv.DictReader(io_string):
    #                 row.pop('id')
    #                 bulk.append(Tag(**row))
    #                 # Tag.objects.update_or_create(row, id=row['id'])
    #                 # Tag.objects.create(id=row["id"], name=row["name"])
    #             Tag.objects.bulk_create(bulk)
    #             self.message_user(request, "Your csv file has been imported")
    #             return redirect("..")
    #         form = CsvImportForm()
    #         context = {
    #             "form": form
    #         }
    #         return render(request, 'apps/csv_form.html', context)


    # nechta qo'shilganlik soni bo'yicha order_by qilish

    # @admin.register(Origin, site=client_admin_site)
    # class OriginAdmin(admin.ModelAdmin):
    #     list_display = ('name', 'hero_count', 'villain_count')
    #
    #     def get_queryset(self, request):
    #         queryset = super().get_queryset(request)
    #         queryset = queryset.annotate(
    #             _hero_count=Count("hero", distinct=True),
    #             _villain_count=Count("villain", distinct=True),
    #         ).order_by('_hero_count', '_villain_count')
    #         return queryset
    #
    #     def hero_count(self, obj):
    #         return obj._hero_count
    #
    #     def villain_count(self, obj):
    #         return obj._villain_count



    #modellarni qay tartibda chiqarish kerakligi bu yerda raqamga qarab tartiblab chiqaradi, admin panelda


    # class ClientAdminSite(AdminSite):
    #     site_header = "Client uchun adminka"
    #     site_title = "Client Events Admin Portal"
    #     index_title = "Welcome to Client Researcher Events Portal"
    #     login_form = CustomAuthForm
    #     login_template = 'admin/custom/custom_login.html'
    #
    #     def get_app_list(self, request, app_label=None):
    #         """
    #         Return a sorted list of all the installed apps that have been
    #         registered in this site.
    #         """
    #
    #         ordering = {
    #             "Categories": 0,
    #             'Heroes': 1,
    #             "Products": 2,
    #             "Entitys": 3,
    #             "Origins": 4,
    #             "Tags": 6,
    #             "Groups": 1,
    #             "Users": 2,
    #         }
    #         app_dict = self._build_app_dict(request)
    #         # a.sort(key=lambda x: b.index(x[0]))
    #         # Sort the apps alphabetically.
    #         app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
    #
    #         # Sort the models alphabetically within each app.
    #         for app in app_list:
    #             app['models'].sort(key=lambda x: ordering[x['name']])
    #
    #         return app_list
    #
    #
    # client_admin_site = ClientAdminSite(name='client_admin')
    #
    #
    # # @admin.register(Product, Category, site=client_admin_site)
    # # class CategoryProductAdmin(admin.ModelAdmin):
    # #     list_display = 'name', 'id'
    #
    #
    # @admin.register(Tag, site=client_admin_site)
    # class TagModelAdmin(admin.ModelAdmin):
    #     pass
    #
    #
    # @admin.register(User, site=client_admin_site)
    # class CustomUserAdmin(UserAdmin):
    #     pass


    # agar birinchi marta yaratayotgan bo'lsa hero_countini 1 taga oshirib ketadi. Bu yerda  databasedan F yordamida her_countni olib kelib ishlatayapti
    # va pre_save va post_save degan narsa bor pre_save yaratishdan oldin 1 qo'shyapti

    # from django.db.models import F
    # from django.db.models.signals import pre_save
    # from django.dispatch import receiver
    #
    # from apps.models import Hero, Category, Villain
    #
    #
    # @receiver(pre_save, sender=Hero, dispatch_uid="update_hero_count")
    # def update_hero_count(sender, **kwargs):
    #     hero = kwargs['instance']
    #     if not hero.pk:
    #         Category.objects.filter(pk=hero.category_id).update(hero_count=F('hero_count') + 1)
