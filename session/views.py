from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Session
from message.models import Message
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    SessionCreateSerializer,
    SessionUpdateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)


class SessionPagination(PageNumberPagination):
    """Custom pagination for sessions"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description='Filter by status', type=openapi.TYPE_STRING, enum=['active', 'completed', 'archived']),
        openapi.Parameter('page', openapi.IN_QUERY, description='Page number', type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description='Items per page', type=openapi.TYPE_INTEGER),
    ],
    responses={200: openapi.Response('List of sessions', SessionListSerializer)},
    tags=['Sessions'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='post',
    request_body=SessionCreateSerializer,
    responses={
        201: openapi.Response('Session created', SessionListSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Sessions'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def session_list_create(request):
    """List all sessions (GET) or Create new session (POST)"""
    if request.method == 'GET':
        # List sessions with pagination and filtering
        sessions = Session.objects.filter(user=request.user)
        
        # Filter by status
        status_filter = request.GET.get('status')
        if status_filter in ['active', 'completed', 'archived']:
            sessions = sessions.filter(status=status_filter)
        
        # Pagination
        paginator = SessionPagination()
        paginated_sessions = paginator.paginate_queryset(sessions, request)
        
        serializer = SessionListSerializer(paginated_sessions, many=True)
        
        return Response({
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        # Create new session
        serializer = SessionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            session = serializer.save()
            response_serializer = SessionListSerializer(session)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Session details', SessionDetailSerializer)},
    tags=['Sessions'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='patch',
    request_body=SessionUpdateSerializer,
    responses={
        200: openapi.Response('Session updated', SessionDetailSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Sessions'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def session_detail_update(request, session_id):
    """Get session with messages (GET) or Update session (PATCH)"""
    session = get_object_or_404(Session, pk=session_id, user=request.user)
    
    if request.method == 'GET':
        # Get session with all messages
        serializer = SessionDetailSerializer(session)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Update session
        serializer = SessionUpdateSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            session = serializer.save()
            response_serializer = SessionDetailSerializer(session)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=MessageCreateSerializer,
    responses={
        201: openapi.Response('Message added', MessageSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Sessions'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def session_add_message(request, session_id):
    """Add a message to a session"""
    session = get_object_or_404(Session, pk=session_id, user=request.user)
    
    serializer = MessageCreateSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save(session=session)
        
        # Update session statistics
        from django.db.models import Sum
        from django.utils import timezone
        session.message_count = session.messages.count()
        session.total_tokens_used = session.messages.aggregate(total=Sum('tokens_used'))['total'] or 0
        session.last_activity_at = timezone.now()
        session.save(update_fields=['message_count', 'total_tokens_used', 'last_activity_at'])
        
        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
