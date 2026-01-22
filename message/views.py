from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Message
from .serializers import MessageSerializer, MessageCreateSerializer, MessageUpdateSerializer


class MessagePagination(PageNumberPagination):
    """Custom pagination for messages"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('session_id', openapi.IN_QUERY, description='Filter by session ID', type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        openapi.Parameter('role', openapi.IN_QUERY, description='Filter by role', type=openapi.TYPE_STRING, enum=['user', 'assistant', 'system']),
        openapi.Parameter('page', openapi.IN_QUERY, description='Page number', type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description='Items per page', type=openapi.TYPE_INTEGER),
    ],
    responses={200: openapi.Response('List of messages', MessageSerializer)},
    tags=['Messages'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_list(request):
    """List messages with filtering options"""
    messages = Message.objects.filter(session__user=request.user)
    
    # Filter by session_id
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            messages = messages.filter(session_id=session_id)
        except (ValueError, TypeError):
            pass
    
    # Filter by role
    role = request.GET.get('role')
    if role in ['user', 'assistant', 'system']:
        messages = messages.filter(role=role)
    
    # Filter by model_used
    model_used = request.GET.get('model_used')
    if model_used:
        messages = messages.filter(model_used=model_used)
    
    # Order by sequence_number and created_at
    messages = messages.order_by('sequence_number', 'created_at')
    
    # Pagination
    paginator = MessagePagination()
    paginated_messages = paginator.paginate_queryset(messages, request)
    
    serializer = MessageSerializer(paginated_messages, many=True)
    
    return Response({
        'count': paginator.page.paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'results': serializer.data
    })


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Message details', MessageSerializer)},
    tags=['Messages'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='put',
    request_body=MessageUpdateSerializer,
    responses={
        200: openapi.Response('Message updated', MessageSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Messages'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='patch',
    request_body=MessageUpdateSerializer,
    responses={
        200: openapi.Response('Message updated', MessageSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Messages'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='delete',
    responses={204: openapi.Response('Message deleted successfully')},
    tags=['Messages'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def message_detail(request, message_id):
    """Get, update, or delete a specific message"""
    message = get_object_or_404(Message, pk=message_id, session__user=request.user)
    
    if request.method == 'GET':
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Full update
        serializer = MessageUpdateSerializer(message, data=request.data)
        if serializer.is_valid():
            updated_message = serializer.save()
            
            # Update session statistics
            session = updated_message.session
            session.message_count = session.messages.count()
            session.total_tokens_used = session.messages.aggregate(total=Sum('tokens_used'))['total'] or 0
            session.last_activity_at = timezone.now()
            session.save(update_fields=['message_count', 'total_tokens_used', 'last_activity_at'])
            
            response_serializer = MessageSerializer(updated_message)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        # Partial update
        serializer = MessageUpdateSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            updated_message = serializer.save()
            
            # Update session statistics
            session = updated_message.session
            session.message_count = session.messages.count()
            session.total_tokens_used = session.messages.aggregate(total=Sum('tokens_used'))['total'] or 0
            session.last_activity_at = timezone.now()
            session.save(update_fields=['message_count', 'total_tokens_used', 'last_activity_at'])
            
            response_serializer = MessageSerializer(updated_message)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        session = message.session
        message.delete()
        
        # Update session statistics after deletion
        session.message_count = session.messages.count()
        session.total_tokens_used = session.messages.aggregate(total=Sum('tokens_used'))['total'] or 0
        session.last_activity_at = timezone.now()
        session.save(update_fields=['message_count', 'total_tokens_used', 'last_activity_at'])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
