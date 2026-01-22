from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CommandExecution
from .serializers import (
    CommandExecutionCreateSerializer,
    CommandExecutionListSerializer,
    CommandExecutionDetailSerializer
)
from users.views import is_admin


class CommandPagination(PageNumberPagination):
    """Custom pagination for command executions"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, description='Filter by user ID (Admin only)', type=openapi.TYPE_INTEGER),
        openapi.Parameter('command_type', openapi.IN_QUERY, description='Filter by command type', type=openapi.TYPE_STRING, enum=['shell', 'file_read', 'file_write', 'file_edit', 'other']),
        openapi.Parameter('status', openapi.IN_QUERY, description='Filter by status', type=openapi.TYPE_STRING, enum=['success', 'failed', 'error']),
        openapi.Parameter('date_from', openapi.IN_QUERY, description='Start date (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        openapi.Parameter('date_to', openapi.IN_QUERY, description='End date (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description='Page number', type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description='Items per page', type=openapi.TYPE_INTEGER),
    ],
    responses={200: openapi.Response('List of command executions', CommandExecutionListSerializer)},
    tags=['Commands'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    method='post',
    request_body=CommandExecutionCreateSerializer,
    responses={
        201: openapi.Response('Command execution logged', CommandExecutionCreateSerializer),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Commands'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def command_list_create(request):
    """List command executions (GET) or Create new command execution (POST)"""
    if request.method == 'GET':
        # Get command executions based on user role
        if is_admin(request.user):
            # Admin can see all commands, optionally filtered by user_id
            commands = CommandExecution.objects.all()
            
            # Filter by user_id if provided (admin only)
            user_id = request.GET.get('user_id')
            if user_id:
                try:
                    commands = commands.filter(user_id=int(user_id))
                except (ValueError, TypeError):
                    pass
        else:
            # Regular users see only their own commands
            commands = CommandExecution.objects.filter(user=request.user)
        
        # Filter by command_type
        command_type = request.GET.get('command_type')
        if command_type in ['shell', 'file_read', 'file_write', 'file_edit', 'other']:
            commands = commands.filter(command_type=command_type)
        
        # Filter by status
        status_filter = request.GET.get('status')
        if status_filter in ['success', 'failed', 'error']:
            commands = commands.filter(status=status_filter)
        
        # Filter by date range
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    commands = commands.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    commands = commands.filter(created_at__date__lte=date_to_parsed)
            except (ValueError, TypeError):
                pass
        
        # Pagination
        paginator = CommandPagination()
        paginated_commands = paginator.paginate_queryset(commands, request)
        
        serializer = CommandExecutionListSerializer(paginated_commands, many=True)
        
        return Response({
            'chat': 'Command executions retrieved successfully',
            'plan': [
                'Authenticate user',
                'Filter commands based on user role',
                'Apply query filters',
                'Paginate results',
                'Return command list'
            ],
            'execution': {
                'count': paginator.page.paginator.count,
                'results': serializer.data
            }
        })
    
    elif request.method == 'POST':
        # Create new command execution
        serializer = CommandExecutionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            command = serializer.save()
            # Return simplified response as per API spec
            return Response({
                'chat': 'Command execution logged successfully',
                'plan': [
                    'Authenticate user',
                    'Validate command data',
                    'Create command execution record',
                    'Return created command data'
                ],
                'execution': {
                    'id': str(command.id),
                    'command': command.command,
                    'command_type': command.command_type,
                    'status': command.status,
                    'created_at': command.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'chat': 'Command execution creation failed - validation errors',
            'plan': [
                'Authenticate user',
                'Validate command data',
                'Return validation errors'
            ],
            'execution': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
