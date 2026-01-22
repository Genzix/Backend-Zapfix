from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserProfile
from .serializers import UserCreateSerializer


def is_admin(user):
    """Check if user is an admin"""
    try:
        return user.profile.is_admin
    except (UserProfile.DoesNotExist, AttributeError):
        return False


class AdminPermission(BasePermission):
    """Permission class to check if user is admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and is_admin(request.user)


@swagger_auto_schema(
    method='post',
    request_body=UserCreateSerializer,
    responses={
        201: openapi.Response('User registered successfully'),
        400: openapi.Response('Bad request - validation errors')
    },
    tags=['Authentication'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminPermission])
def user_register(request):
    """Register a new user (Admin only)"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Get user data for response
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.profile.role,
            'admin_id': user.profile.admin_id.id if user.profile.admin_id else None
        }
        
        return Response({
            'success': True,
            'user': user_data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password', format='password'),
        }
    ),
    responses={
        200: openapi.Response('Login successful'),
        400: openapi.Response('Bad request - missing credentials'),
        401: openapi.Response('Unauthorized - invalid credentials'),
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login (for both admin and regular users)"""
    from django.contrib.auth import authenticate
    from rest_framework_simplejwt.tokens import RefreshToken
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'success': False,
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        user_exists = User.objects.filter(username=username).exists()
        error_msg = 'Invalid password' if user_exists else 'User does not exist'
        
        return Response({
            'success': False,
            'error': error_msg
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is active
    if not user.is_active:
        return Response({
            'success': False,
            'error': 'User account is inactive'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Auto-create profile if missing
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Create profile with default role 'user' (will need admin_id later)
        profile = UserProfile(user=user, role='user')
        profile.save(validate=False)
        user.refresh_from_db()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # Prepare user data
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.profile.role,
        'admin_id': user.profile.admin_id.id if user.profile.admin_id else None
    }
    
    return Response({
        'success': True,
        'token': str(access_token),
        'refresh_token': str(refresh),
        'user': user_data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist (optional)'),
        }
    ),
    responses={
        200: openapi.Response('Logout successful'),
        400: openapi.Response('Bad request - invalid token'),
    },
    tags=['Authentication'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """User logout - blacklist the refresh token"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    try:
        # Get the refresh token from the request body (optional)
        refresh_token = request.data.get('refresh_token')
        
        if refresh_token:
            try:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # If token is already blacklisted or invalid, continue
                pass
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Root API endpoint showing available endpoints"""
    return Response({
        'message': 'ZapFix Backend API',
        'version': '1.0',
        'documentation': {
            'swagger': '/swagger/ - Interactive API documentation',
            'redoc': '/redoc/ - Alternative API documentation',
            'schema_json': '/swagger.json - OpenAPI schema (JSON)',
            'schema_yaml': '/swagger.yaml - OpenAPI schema (YAML)'
        },
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/ (POST) - Register new user (Admin only)',
                'login': '/api/auth/login/ (POST) - User login',
                'logout': '/api/auth/logout/ (POST) - User logout',
            },
            'sessions': {
                'list': '/api/sessions/ (GET) - Get all sessions',
                'create': '/api/sessions/ (POST) - Create new session',
                'detail': '/api/sessions/{session_id}/ (GET) - Get session with messages',
                'update': '/api/sessions/{session_id}/ (PATCH) - Update session',
                'add_message': '/api/sessions/{session_id}/messages/ (POST) - Add message to session',
            },
            'commands': {
                'list': '/api/commands/ (GET) - Get command history',
                'create': '/api/commands/ (POST) - Log command execution',
            },
            'tokens': {
                'create': '/api/tokens/ (POST) - Record token usage',
                'usage': '/api/tokens/usage/ (GET) - Get token usage statistics',
            },
            'admin': {
                'users': '/api/admin/users/ (GET) - Get all users (Admin only)',
                'activity': '/api/admin/activity/ (GET) - Get activity summary (Admin only)',
                'user_details': '/api/admin/user/{user_id}/details/ (GET) - Get user details (Admin only)',
            }
        }
    })
