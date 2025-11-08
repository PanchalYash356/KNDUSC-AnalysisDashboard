
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.contrib import messages
import pandas as pd
import json
from .models import UploadedFile, Product


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']


            if not file.name.endswith('.xlsx'):
                messages.error(request, 'Please upload a valid Excel file (.xlsx)')
                return render(request, 'upload.html')


            df = pd.read_excel(file)


            required_columns = ['zipcode', 'product_id', 'product_name', 'mrp', 'sale_price', 'brand']
            if not all(col in df.columns for col in required_columns):
                missing = set(required_columns) - set(df.columns)
                messages.error(request, f'Missing columns: {", ".join(missing)}')
                return render(request, 'upload.html')


            Product.objects.all().delete()


            products = []
            for _, row in df.iterrows():
                products.append(Product(
                    zipcode=str(row['zipcode']).strip(),
                    product_id=str(row['product_id']).strip(),
                    product_name=str(row['product_name']).strip(),
                    mrp=float(row['mrp']),
                    sale_price=float(row['sale_price']),
                    brand=str(row['brand']).strip()
                ))

            Product.objects.bulk_create(products, batch_size=1000)


            UploadedFile.objects.create(file=file)

            messages.success(request, f'Successfully uploaded {len(products)} products!')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')

    return render(request, 'upload.html')


def dashboard_view(request):

    if not Product.objects.exists():
        return render(request, 'dashboard.html', {'no_data': True})


    total_zipcodes = Product.objects.values('zipcode').distinct().count()
    total_products = Product.objects.count()


    zipcode_stats = Product.objects.values('zipcode').annotate(
        product_count=Count('id'),
        avg_price=Avg('sale_price'),
        avg_discount=Avg(F('mrp') - F('sale_price')),
        total_revenue=Sum('sale_price')
    ).order_by('-product_count')[:10]


    top_products = Product.objects.values('product_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]


    brand_stats = Product.objects.values('brand').annotate(
        product_count=Count('id'),
        avg_mrp=Avg('mrp'),
        avg_sale_price=Avg('sale_price'),
        total_revenue=Sum('sale_price')
    ).order_by('-product_count')[:10]


    price_stats = {
        'total_revenue_mrp': float(Product.objects.aggregate(Sum('mrp'))['mrp__sum'] or 0),
        'total_revenue_sale': float(Product.objects.aggregate(Sum('sale_price'))['sale_price__sum'] or 0),
        'avg_discount': float(Product.objects.aggregate(
            avg_discount=Avg(F('mrp') - F('sale_price'))
        )['avg_discount'] or 0),
        'avg_mrp': float(Product.objects.aggregate(Avg('mrp'))['mrp__avg'] or 0),
        'avg_sale_price': float(Product.objects.aggregate(Avg('sale_price'))['sale_price__avg'] or 0)
    }


    inventory = Product.objects.values('zipcode', 'product_name').annotate(
        count=Count('id')
    ).order_by('zipcode', '-count')[:50]


    top_products_data = [
        {'product_name': p['product_name'][:30] + '...' if len(p['product_name']) > 30 else p['product_name'],
         'count': p['count']}
        for p in top_products
    ]

    brand_stats_data = [
        {'brand': b['brand'], 'product_count': b['product_count'],
         'avg_mrp': float(b['avg_mrp'] or 0), 'avg_sale_price': float(b['avg_sale_price'] or 0),
         'total_revenue': float(b['total_revenue'] or 0)}
        for b in brand_stats
    ]

    context = {
        'total_zipcodes': total_zipcodes,
        'total_products': total_products,
        'zipcode_stats': list(zipcode_stats),
        'top_products': top_products_data,
        'brand_stats': brand_stats_data,
        'price_stats': price_stats,
        'inventory': list(inventory),
        'no_data': False
    }

    return render(request, 'dashboard.html', context)


def analytics_api(request):

    if not Product.objects.exists():
        return JsonResponse({'error': 'No data available'})

    try:
        # Zipcode data for bar chart - order by product count for better visualization
        zipcode_data = Product.objects.values('zipcode').annotate(
            product_count=Count('id')
        ).order_by('-product_count')[:15]

        # Price range distribution
        price_ranges = [
            {'range': '₹0-₹100', 'count': Product.objects.filter(sale_price__lte=100).count()},
            {'range': '₹101-₹500', 'count': Product.objects.filter(sale_price__gt=100, sale_price__lte=500).count()},
            {'range': '₹501-₹1000', 'count': Product.objects.filter(sale_price__gt=500, sale_price__lte=1000).count()},
            {'range': '₹1000+', 'count': Product.objects.filter(sale_price__gt=1000).count()},
        ]

        # Top products for horizontal bar chart
        top_products_chart = Product.objects.values('product_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Brand performance
        brand_performance = Product.objects.values('brand').annotate(
            product_count=Count('id')
        ).order_by('-product_count')[:8]

        # Prepare response data
        response_data = {
            'zipcodes': [str(item['zipcode']) for item in zipcode_data],
            'product_counts': [item['product_count'] for item in zipcode_data],
            'price_ranges': price_ranges,
            'top_products': [
                {
                    'product_name': item['product_name'][:25] + '...' if len(item['product_name']) > 25 else item['product_name'],
                    'count': item['count']
                }
                for item in top_products_chart
            ],
            'brands': [item['brand'] or 'Unknown' for item in brand_performance],
            'brand_counts': [item['product_count'] for item in brand_performance],
        }

        return JsonResponse(response_data)

    except Exception as e:
        import traceback
        print(f"API Error: {str(e)}")
        return JsonResponse({'error': f'Server error: {str(e)}'})


def test_api(request):
    """Test API endpoint to verify it's working"""
    try:
        # Simple test data
        test_data = {
            'message': 'API is working!',
            'status': 'success',
            'product_count': Product.objects.count(),
            'has_data': Product.objects.exists(),
            'available_endpoints': [
                '/analytics/api/',
                '/test-api/'
            ]
        }
        return JsonResponse(test_data)
    except Exception as e:
        return JsonResponse({'error': str(e)})


# Additional view for full-screen sections
def analytics_section_api(request, section):
    """API for individual dashboard sections"""
    if not Product.objects.exists():
        return JsonResponse({'error': 'No data available'})

    try:
        if section == 'geo-analysis':
            # Geographical analysis data
            data = Product.objects.values('zipcode').annotate(
                total_products=Count('id'),
                total_revenue=Sum('sale_price'),
                avg_price=Avg('sale_price'),
                brand_diversity=Count('brand', distinct=True)
            ).order_by('-total_revenue')[:20]

            return JsonResponse({
                'geographical_data': list(data),
                'summary': {
                    'top_zipcode': data[0]['zipcode'] if data else 'N/A',
                    'total_revenue_all': float(Product.objects.aggregate(Sum('sale_price'))['sale_price__sum'] or 0),
                    'avg_products_per_zipcode': Product.objects.values('zipcode').annotate(
                        count=Count('id')
                    ).aggregate(avg=Avg('count'))['avg'] or 0
                }
            })

        elif section == 'product-analysis':
            # Product intelligence data
            data = Product.objects.values('product_name').annotate(
                zipcode_coverage=Count('zipcode', distinct=True),
                total_quantity=Count('id'),
                avg_price=Avg('sale_price'),
                total_revenue=Sum('sale_price'),
                avg_discount=Avg(F('mrp') - F('sale_price'))
            ).order_by('-total_revenue')[:20]

            return JsonResponse({
                'product_analysis': list(data),
                'metrics': {
                    'total_unique_products': Product.objects.values('product_name').distinct().count(),
                    'highest_revenue_product': data[0]['product_name'] if data else 'N/A',
                    'widest_coverage': max([p['zipcode_coverage'] for p in data]) if data else 0
                }
            })

        elif section == 'sales-analysis':
            price_segments = [
                {'segment': 'Budget (0-100)', 'count': Product.objects.filter(sale_price__lte=100).count(),
                 'revenue': float(
                     Product.objects.filter(sale_price__lte=100).aggregate(Sum('sale_price'))['sale_price__sum'] or 0)},
                {'segment': 'Mid-range (101-500)',
                 'count': Product.objects.filter(sale_price__gt=100, sale_price__lte=500).count(),
                 'revenue': float(
                     Product.objects.filter(sale_price__gt=100, sale_price__lte=500).aggregate(Sum('sale_price'))[
                         'sale_price__sum'] or 0)},
                {'segment': 'Premium (501-1000)',
                 'count': Product.objects.filter(sale_price__gt=500, sale_price__lte=1000).count(),
                 'revenue': float(
                     Product.objects.filter(sale_price__gt=500, sale_price__lte=1000).aggregate(Sum('sale_price'))[
                         'sale_price__sum'] or 0)},
                {'segment': 'Luxury (1000+)', 'count': Product.objects.filter(sale_price__gt=1000).count(),
                 'revenue': float(
                     Product.objects.filter(sale_price__gt=1000).aggregate(Sum('sale_price'))['sale_price__sum'] or 0)},
            ]

            return JsonResponse({
                'price_segments': price_segments,
                'sales_metrics': {
                    'total_revenue': float(Product.objects.aggregate(Sum('sale_price'))['sale_price__sum'] or 0),
                    'avg_order_value': float(Product.objects.aggregate(Avg('sale_price'))['sale_price__avg'] or 0),
                    'total_products_sold': Product.objects.count(),
                    'avg_discount_value': float(Product.objects.aggregate(
                        avg_discount=Avg(F('mrp') - F('sale_price'))
                    )['avg_discount'] or 0)
                }
            })

    except Exception as e:
        return JsonResponse({'error': str(e)})