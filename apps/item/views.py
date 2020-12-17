from django.shortcuts import get_object_or_404, redirect, render, HttpResponse, HttpResponseRedirect
from .models import Item, SubCategory, MainCategory, Label
from django.views.generic import ListView, DetailView, View
from .filters import ItemFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..order.forms import CartAddProductForm
from ..order.views import add_to_cart
from itertools import chain


# Create your views here.
def contact_view(request):
    return render(request, "contact.html", None)


class HomeView(ListView):
    model = Item
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ItemFilter(self.request.GET, queryset=self.get_queryset())
        paginator = Paginator(context['filter'].qs, 12)
        page = self.request.GET.get('page')
        try:
            filter_qs_paged = paginator.page(page)
        except PageNotAnInteger:
            filter_qs_paged = paginator.page(1)
        except EmptyPage:
            filter_qs_paged = paginator.page(paginator.num_pages)
        context['filter_qs_paged'] = filter_qs_paged
        context['main_categories'] = MainCategory.objects.all()

        return context

    def get_queryset(self):
        if ('main_category_slug' in self.kwargs) and ('sub_category_slug' not in self.kwargs):
            return Item.objects.filter(sub_category__main_category__slug=self.kwargs['main_category_slug'])
        if 'sub_category_slug' in self.kwargs:
            return Item.objects.filter(sub_category__slug=self.kwargs['sub_category_slug'])
        else:
            return Item.objects.all()


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CartAddProductForm
        # 得到前9个热销
        item = Item.objects.get(slug=self.object.slug)
        related_items_qs = Item.objects.filter(sub_category__slug=item.sub_category.slug)
        if related_items_qs.exists():
            related_items_qs = related_items_qs.order_by('-sales_volume')[:9]
            if related_items_qs.count() < 9:
                related_items_qs = list(related_items_qs)
                related_items_qs.extend([None] * (9 - len(related_items_qs)))
            context['related_items_qs'] = related_items_qs
        return context

    def post(self, request, *args, **kwargs):
        form = CartAddProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Write Your Logic here
            self.object = self.get_object()
            context = super().get_context_data(**kwargs)
            context['form'] = CartAddProductForm
            add_to_cart(request, self.object.slug, form.cleaned_data['quantity'])
            return redirect("order:order-summary")

        else:
            self.object = self.get_object()
            context = super().get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context=context)
