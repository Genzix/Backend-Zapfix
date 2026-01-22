from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.db.models import Sum, Q, Min, Max
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import TokenUsage
from .serializers import TokenUsageCreateSerializer, TokenUsageResponseSerializer
from users.views import is_admin


@swagger_auto_schema(
    method='post',
    request_body=TokenUsageCreateSerializer,
    responses={
        201: openapi.Response('Token usage recorded', TokenUsageResponseSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Tokens'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tokens_create(request):
    """Record token usage"""
    serializer = TokenUsageCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        token_usage = serializer.save()
        response_serializer = TokenUsageResponseSerializer(token_usage)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, description='Filter by user ID (Admin only)', type=openapi.TYPE_INTEGER),
        openapi.Parameter('date_from', openapi.IN_QUERY, description='Start date (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        openapi.Parameter('date_to', openapi.IN_QUERY, description='End date (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        openapi.Parameter('group_by', openapi.IN_QUERY, description='Group by', type=openapi.TYPE_STRING, enum=['day', 'week', 'month', 'user', 'model']),
        openapi.Parameter('model_used', openapi.IN_QUERY, description='Filter by model', type=openapi.TYPE_STRING),
    ],
    responses={200: openapi.Response('Token usage statistics')},
    tags=['Tokens'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tokens_usage(request):
    """Get token usage statistics"""
    # Get base queryset based on user role
    if is_admin(request.user):
        # Admin can see all token usage, optionally filtered by user_id
        queryset = TokenUsage.objects.all()
        
        # Filter by user_id if provided (admin only)
        user_id = request.GET.get('user_id')
        if user_id:
            try:
                queryset = queryset.filter(user_id=int(user_id))
            except (ValueError, TypeError):
                pass
    else:
        # Regular users see only their own token usage
        queryset = TokenUsage.objects.filter(user=request.user)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        try:
            date_from_parsed = parse_date(date_from)
            if date_from_parsed:
                queryset = queryset.filter(created_at__date__gte=date_from_parsed)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            date_to_parsed = parse_date(date_to)
            if date_to_parsed:
                # Include the entire day
                date_to_parsed = date_to_parsed + timedelta(days=1)
                queryset = queryset.filter(created_at__date__lt=date_to_parsed)
        except (ValueError, TypeError):
            pass
    
    # Filter by model_used
    model_used = request.GET.get('model_used')
    if model_used:
        queryset = queryset.filter(model_used=model_used)
    
    # Calculate totals
    totals = queryset.aggregate(
        total_tokens=Sum('tokens_total'),
        total_tokens_input=Sum('tokens_input'),
        total_tokens_output=Sum('tokens_output'),
        total_cost=Sum('cost_usd')
    )
    
    total_tokens = totals['total_tokens'] or 0
    total_cost_usd = float(totals['total_cost']) if totals['total_cost'] else None
    
    # Determine date range for period
    if date_from and date_to:
        period_from = date_from
        period_to = date_to
    else:
        # Get actual date range from data
        date_range = queryset.aggregate(
            min_date=Min('created_at'),
            max_date=Max('created_at')
        )
        if date_range['min_date'] and date_range['max_date']:
            period_from = date_range['min_date'].date().isoformat()
            period_to = date_range['max_date'].date().isoformat()
        else:
            period_from = timezone.now().date().isoformat()
            period_to = timezone.now().date().isoformat()
    
    # Group by option
    group_by = request.GET.get('group_by', 'day')
    breakdown = []
    
    if group_by == 'day':
        # Group by day
        from django.db.models.functions import TruncDate
        grouped = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            tokens_total=Sum('tokens_total'),
            tokens_input=Sum('tokens_input'),
            tokens_output=Sum('tokens_output'),
            cost_usd=Sum('cost_usd')
        ).order_by('date')
        
        for item in grouped:
            breakdown.append({
                'group_key': item['date'].isoformat() if item['date'] else None,
                'tokens_total': item['tokens_total'] or 0,
                'tokens_input': item['tokens_input'] or 0,
                'tokens_output': item['tokens_output'] or 0,
                'cost_usd': float(item['cost_usd']) if item['cost_usd'] else None
            })
    
    elif group_by == 'week':
        # Group by week
        from django.db.models.functions import TruncWeek
        grouped = queryset.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            tokens_total=Sum('tokens_total'),
            tokens_input=Sum('tokens_input'),
            tokens_output=Sum('tokens_output'),
            cost_usd=Sum('cost_usd')
        ).order_by('week')
        
        for item in grouped:
            breakdown.append({
                'group_key': item['week'].isoformat() if item['week'] else None,
                'tokens_total': item['tokens_total'] or 0,
                'tokens_input': item['tokens_input'] or 0,
                'tokens_output': item['tokens_output'] or 0,
                'cost_usd': float(item['cost_usd']) if item['cost_usd'] else None
            })
    
    elif group_by == 'month':
        # Group by month
        from django.db.models.functions import TruncMonth
        grouped = queryset.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            tokens_total=Sum('tokens_total'),
            tokens_input=Sum('tokens_input'),
            tokens_output=Sum('tokens_output'),
            cost_usd=Sum('cost_usd')
        ).order_by('month')
        
        for item in grouped:
            breakdown.append({
                'group_key': item['month'].strftime('%Y-%m') if item['month'] else None,
                'tokens_total': item['tokens_total'] or 0,
                'tokens_input': item['tokens_input'] or 0,
                'tokens_output': item['tokens_output'] or 0,
                'cost_usd': float(item['cost_usd']) if item['cost_usd'] else None
            })
    
    elif group_by == 'user':
        # Group by user (admin only)
        if is_admin(request.user):
            grouped = queryset.values('user_id', 'user__username').annotate(
                tokens_total=Sum('tokens_total'),
                tokens_input=Sum('tokens_input'),
                tokens_output=Sum('tokens_output'),
                cost_usd=Sum('cost_usd')
            ).order_by('user_id')
            
            for item in grouped:
                breakdown.append({
                    'group_key': f"{item['user__username']} (ID: {item['user_id']})",
                    'tokens_total': item['tokens_total'] or 0,
                    'tokens_input': item['tokens_input'] or 0,
                    'tokens_output': item['tokens_output'] or 0,
                    'cost_usd': float(item['cost_usd']) if item['cost_usd'] else None
                })
    
    elif group_by == 'model':
        # Group by model
        grouped = queryset.values('model_used').annotate(
            tokens_total=Sum('tokens_total'),
            tokens_input=Sum('tokens_input'),
            tokens_output=Sum('tokens_output'),
            cost_usd=Sum('cost_usd')
        ).order_by('model_used')
        
        for item in grouped:
            breakdown.append({
                'group_key': item['model_used'] or 'Unknown',
                'tokens_total': item['tokens_total'] or 0,
                'tokens_input': item['tokens_input'] or 0,
                'tokens_output': item['tokens_output'] or 0,
                'cost_usd': float(item['cost_usd']) if item['cost_usd'] else None
            })
    
    return Response({
        'total_tokens': total_tokens,
        'total_cost_usd': total_cost_usd,
        'period': {
            'from': period_from if isinstance(period_from, str) else period_from.isoformat(),
            'to': period_to if isinstance(period_to, str) else period_to.isoformat()
        },
        'breakdown': breakdown
    })
