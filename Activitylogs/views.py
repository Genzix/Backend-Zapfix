from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.views import is_admin, AdminPermission


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('List of users with statistics')},
    tags=['Admin Dashboard'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminPermission])
def admin_users_list(request):
    """Get all users with their statistics - Admin only"""
    users = User.objects.all().order_by('-date_joined')
    
    users_data = []
    for user in users:
        # Get user statistics
        total_sessions = user.sessions.count()
        total_tokens_used = user.token_usages.aggregate(
            total=Sum('tokens_total')
        )['total'] or 0
        total_commands_executed = user.command_executions.count()
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or None,
            'last_name': user.last_name or None,
            'is_active': user.is_active,
            'created_at': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'total_sessions': total_sessions,
            'total_tokens_used': total_tokens_used,
            'total_commands_executed': total_commands_executed
        })
    
    return Response({
        'users': users_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminPermission])
def admin_activity_summary(request):
    """Get activity summary for all users - Admin only"""
    # Base queryset
    users = User.objects.all()
    
    # Filter by user_id if provided
    user_id = request.GET.get('user_id')
    if user_id:
        try:
            users = users.filter(id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    date_filter = Q()
    if date_from:
        try:
            date_from_parsed = parse_date(date_from)
            if date_from_parsed:
                date_filter &= Q(created_at__date__gte=date_from_parsed)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            date_to_parsed = parse_date(date_to)
            if date_to_parsed:
                date_to_parsed = date_to_parsed + timedelta(days=1)
                date_filter &= Q(created_at__date__lt=date_to_parsed)
        except (ValueError, TypeError):
            pass
    
    # Filter by activity_type if provided
    activity_type = request.GET.get('activity_type')
    activity_filter = Q()
    if activity_type:
        from .models import ActivityLog
        activity_filter = Q(activity_type=activity_type)
    
    # Calculate summary statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    
    # Get total sessions (with date filter if provided)
    from session.models import Session
    sessions_qs = Session.objects.all()
    if date_from or date_to:
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    sessions_qs = sessions_qs.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    date_to_parsed = date_to_parsed + timedelta(days=1)
                    sessions_qs = sessions_qs.filter(created_at__date__lt=date_to_parsed)
            except (ValueError, TypeError):
                pass
    if user_id:
        try:
            sessions_qs = sessions_qs.filter(user_id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    total_sessions = sessions_qs.count()
    
    # Get total messages
    from message.models import Message
    messages_qs = Message.objects.all()
    if date_from or date_to:
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    messages_qs = messages_qs.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    date_to_parsed = date_to_parsed + timedelta(days=1)
                    messages_qs = messages_qs.filter(created_at__date__lt=date_to_parsed)
            except (ValueError, TypeError):
                pass
    if user_id:
        try:
            messages_qs = messages_qs.filter(session__user_id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    total_messages = messages_qs.count()
    
    # Get total commands
    from CommandExecution.models import CommandExecution
    commands_qs = CommandExecution.objects.all()
    if date_from or date_to:
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    commands_qs = commands_qs.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    date_to_parsed = date_to_parsed + timedelta(days=1)
                    commands_qs = commands_qs.filter(created_at__date__lt=date_to_parsed)
            except (ValueError, TypeError):
                pass
    if user_id:
        try:
            commands_qs = commands_qs.filter(user_id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    total_commands = commands_qs.count()
    
    # Get total tokens
    from Tokenusage.models import TokenUsage
    tokens_qs = TokenUsage.objects.all()
    if date_from or date_to:
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    tokens_qs = tokens_qs.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    date_to_parsed = date_to_parsed + timedelta(days=1)
                    tokens_qs = tokens_qs.filter(created_at__date__lt=date_to_parsed)
            except (ValueError, TypeError):
                pass
    if user_id:
        try:
            tokens_qs = tokens_qs.filter(user_id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    total_tokens = tokens_qs.aggregate(total=Sum('tokens_total'))['total'] or 0
    
    # Get user activity breakdown
    user_activity = []
    for user in users:
        # Get user-specific stats with date filters
        user_sessions_qs = user.sessions.all()
        user_commands_qs = user.command_executions.all()
        user_tokens_qs = user.token_usages.all()
        
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    user_sessions_qs = user_sessions_qs.filter(created_at__date__gte=date_from_parsed)
                    user_commands_qs = user_commands_qs.filter(created_at__date__gte=date_from_parsed)
                    user_tokens_qs = user_tokens_qs.filter(created_at__date__gte=date_from_parsed)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    date_to_parsed = date_to_parsed + timedelta(days=1)
                    user_sessions_qs = user_sessions_qs.filter(created_at__date__lt=date_to_parsed)
                    user_commands_qs = user_commands_qs.filter(created_at__date__lt=date_to_parsed)
                    user_tokens_qs = user_tokens_qs.filter(created_at__date__lt=date_to_parsed)
            except (ValueError, TypeError):
                pass
        
        sessions_count = user_sessions_qs.count()
        commands_count = user_commands_qs.count()
        tokens_used = user_tokens_qs.aggregate(total=Sum('tokens_total'))['total'] or 0
        
        # Get last activity (most recent session, command, or token usage)
        last_session = user_sessions_qs.order_by('-last_activity_at').first()
        last_command = user_commands_qs.order_by('-created_at').first()
        last_token = user_tokens_qs.order_by('-created_at').first()
        
        last_activity = None
        if last_session and last_session.last_activity_at:
            last_activity = last_session.last_activity_at
        if last_command and last_command.created_at:
            if not last_activity or last_command.created_at > last_activity:
                last_activity = last_command.created_at
        if last_token and last_token.created_at:
            if not last_activity or last_token.created_at > last_activity:
                last_activity = last_token.created_at
        
        user_activity.append({
            'user_id': user.id,
            'username': user.username,
            'sessions_count': sessions_count,
            'commands_count': commands_count,
            'tokens_used': tokens_used,
            'last_activity': last_activity.isoformat() if last_activity else None
        })
    
    return Response({
        'summary': {
            'total_users': total_users,
            'active_users': active_users,
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_commands': total_commands,
            'total_tokens': total_tokens
        },
        'user_activity': user_activity
    })


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('User details with statistics')},
    tags=['Admin Dashboard'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, AdminPermission])
def admin_user_details(request, user_id):
    """Get detailed activity for a specific user - Admin only"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get user statistics
    total_sessions = user.sessions.count()
    active_sessions = user.sessions.filter(status='active').count()
    # Count messages across all user sessions
    from message.models import Message
    total_messages = Message.objects.filter(session__user=user).count()
    total_commands = user.command_executions.count()
    total_tokens_used = user.token_usages.aggregate(
        total=Sum('tokens_total')
    )['total'] or 0
    
    # Get tokens by model
    from Tokenusage.models import TokenUsage
    tokens_by_model = TokenUsage.objects.filter(user=user).values('model_used').annotate(
        total=Sum('tokens_total')
    ).order_by('-total')
    
    tokens_by_model_dict = {}
    for item in tokens_by_model:
        tokens_by_model_dict[item['model_used']] = item['total']
    
    # Get recent sessions (last 10)
    from session.models import Session
    recent_sessions = user.sessions.order_by('-created_at')[:10]
    recent_sessions_data = []
    for session in recent_sessions:
        recent_sessions_data.append({
            'id': str(session.id),
            'title': session.title,
            'created_at': session.created_at.isoformat(),
            'message_count': session.message_count,
            'tokens_used': session.total_tokens_used
        })
    
    # Get recent commands (last 10)
    from CommandExecution.models import CommandExecution
    recent_commands = user.command_executions.order_by('-created_at')[:10]
    recent_commands_data = []
    for command in recent_commands:
        recent_commands_data.append({
            'id': str(command.id),
            'command': command.command[:100] + '...' if len(command.command) > 100 else command.command,
            'command_type': command.command_type,
            'status': command.status,
            'created_at': command.created_at.isoformat()
        })
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.date_joined.isoformat() if user.date_joined else None
        },
        'statistics': {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_messages': total_messages,
            'total_commands': total_commands,
            'total_tokens_used': total_tokens_used,
            'tokens_by_model': tokens_by_model_dict
        },
        'recent_sessions': recent_sessions_data,
        'recent_commands': recent_commands_data
    })
